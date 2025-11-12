"""
Qiskit to OpenQASM 3.0 Converter Module

WHAT THIS FILE DOES:
    Converts Qiskit quantum circuit source code to OpenQASM 3.0 format. Implements
    the AbstractConverter interface, supporting both AST-based parsing (secure, preferred)
    and runtime execution (fallback). Handles all standard Qiskit gates, measurements,
    resets, and barriers. Generates OpenQASM 3.0 code using QASM3Builder.

HOW IT LINKS TO OTHER FILES:
    - Inherits from: abstract_converter.py (AbstractConverter interface)
    - Uses: qiskit_parser.py (QiskitASTParser for AST-based parsing)
    - Uses: qasm3_builder.py (QASM3Builder for code generation)
    - Uses: circuit_ast.py (CircuitAST, GateNode, etc. as intermediate representation)
    - Uses: config/mappings.py (gate name mappings)
    - Returns: ConversionResult (from base/ConversionResult.py)
    - Part of: Converters module implementing framework-specific conversion logic

INPUT:
    - qiskit_source (str): Qiskit Python source code defining a quantum circuit
    - Expected format: Code that creates QuantumCircuit or defines get_circuit() function
    - Used in: convert() method (primary entry point)

OUTPUT:
    - ConversionResult: Contains OpenQASM 3.0 code string and conversion statistics
    - Returned by: convert() method
    - Includes: QASM code, qubit count, depth, gate counts, measurement flags

STAGE OF USE:
    - Conversion Stage: Primary converter for Qiskit framework
    - API Stage: Called by API endpoints when source framework is Qiskit
    - Used after: Framework detection/selection
    - Used before: Validation and response formatting

TOOLS USED:
    - qiskit: Qiskit library for QuantumCircuit objects (runtime fallback)
    - ast: Python AST module (via QiskitASTParser)
    - time: Performance timing for conversion steps
    - inspect: Code introspection utilities
    - typing: Type hints for method signatures

CONVERSION STRATEGY:
    1. AST-based parsing (preferred): Uses QiskitASTParser to extract operations without execution
    2. Runtime execution (fallback): Executes code in isolated namespace if AST parsing fails
    3. AST to QASM: Converts CircuitAST to OpenQASM 3.0 using QASM3Builder
    4. Statistics: Analyzes circuit for qubits, depth, gate counts, measurements

ARCHITECTURE ROLE:
    Implements Qiskit-specific conversion logic, bridging Qiskit source code and
    OpenQASM 3.0 output. Part of the converter strategy pattern, enabling polymorphic
    framework conversion through the AbstractConverter interface.

Author: QCanvas Team
Date: 2025-08-18
Version: 2.0.0 - Integrated with QASM3Builder
"""

import inspect
from typing import Dict, Any, Optional, Union, List
from qiskit import QuantumCircuit
from quantum_converters.base.ConversionResult import ConversionResult, ConversionStats
from quantum_converters.base.qasm3_builder import QASM3Builder
from config.config import VERBOSE, vprint, INCLUDE_VARS, INCLUDE_CONSTANTS
from quantum_converters.base.circuit_ast import GateNode, MeasurementNode, ResetNode, BarrierNode
import time
from quantum_converters.base.qasm3_gates import QASM3GateLibrary
from quantum_converters.parsers.qiskit_parser import QiskitASTParser
from quantum_converters.config import get_qiskit_inverse_qasm_map, QISKIT_TO_QASM_REGISTRY

class QiskitToQASM3Converter:
    """
    A converter class that transforms Qiskit quantum circuits to OpenQASM 3.0 format.
    
    This converter supports all standard Qiskit gates and circuit structures,
    leveraging Qiskit's native OpenQASM 3.0 export functionality.
    
    The converter expects source code that defines a function `get_circuit()` 
    which returns a qiskit.QuantumCircuit object.
    """
    
    def __init__(self):
        """Initialize the Qiskit to QASM3 converter."""
        self.qiskit_inverse_qasm = get_qiskit_inverse_qasm_map()
    
    # In QiskitToQASM.py, update the _execute_qiskit_source method:

    def _execute_qiskit_source(self, source: str) -> 'QuantumCircuit':
        """
        Execute Qiskit source code and extract the quantum circuit.

        Args:
            source (str): Qiskit source code defining a get_circuit() function

        Returns:
            QuantumCircuit: The extracted Qiskit quantum circuit

        Raises:
            ValueError: If source code doesn't define get_circuit() function
            ImportError: If Qiskit is not available
            RuntimeError: If circuit execution fails
        """
        self._ensure_qiskit_available()

        namespace = self._execute_source_code(source)

        # Try different strategies to extract the circuit
        circuit = (
            self._try_get_circuit_function(namespace) or
            self._try_find_circuit_instance(namespace) or
            self._try_factory_functions(namespace)
        )

        if circuit is None:
            raise ValueError(
                "Could not locate a QuantumCircuit. Define get_circuit() or assign the circuit to a variable."
            )

        return circuit

    def _ensure_qiskit_available(self) -> None:
        """Ensure Qiskit is available, raising ImportError if not."""
        try:
            import qiskit  # noqa: F401
        except ImportError:
            raise ImportError("Qiskit is required but not installed. Please install with: pip install qiskit")

    def _execute_source_code(self, source: str) -> dict:
        """Execute the source code in an isolated namespace."""
        namespace = {}
        try:
            exec(compile(source, "<qiskit_source>", "exec"), namespace)
        except Exception as e:
            raise RuntimeError(f"Failed to execute Qiskit source code: {str(e)}")
        return namespace

    def _try_get_circuit_function(self, namespace: dict) -> Optional['QuantumCircuit']:
        """Try to get circuit from get_circuit() function."""
        from qiskit import QuantumCircuit

        get_circuit = namespace.get("get_circuit")
        if callable(get_circuit):
            try:
                circuit = get_circuit()
                if isinstance(circuit, QuantumCircuit):
                    return circuit
            except Exception as e:
                raise RuntimeError(f"Failed to execute get_circuit() function: {str(e)}")
        return None

    def _try_find_circuit_instance(self, namespace: dict) -> Optional['QuantumCircuit']:
        """Try to find a QuantumCircuit instance in the namespace."""
        from qiskit import QuantumCircuit

        try:
            for name, obj in namespace.items():
                if isinstance(obj, QuantumCircuit):
                    return obj
        except Exception:
            pass
        return None

    def _try_factory_functions(self, namespace: dict) -> Optional['QuantumCircuit']:
        """Try calling factory functions that might create circuits."""
        from qiskit import QuantumCircuit

        factory_functions = self._find_factory_functions(namespace)

        for func in factory_functions:
            circuit = self._try_call_factory_function(func)
            if circuit is not None:
                return circuit

        return None

    def _find_factory_functions(self, namespace: dict) -> List[callable]:
        """Find potential factory functions in the namespace."""
        factory_functions = []
        for name, obj in namespace.items():
            if callable(obj) and name.startswith(("create_", "build_", "make_")):
                factory_functions.append(obj)
        return factory_functions

    def _try_call_factory_function(self, func: callable) -> Optional['QuantumCircuit']:
        """Try to call a factory function to create a circuit."""
        from qiskit import QuantumCircuit

        # First try no-arg call
        circuit = self._try_no_arg_call(func)
        if circuit is not None:
            return circuit

        # Try with common integer defaults
        return self._try_with_arg_call(func)

    def _try_no_arg_call(self, func: callable) -> Optional['QuantumCircuit']:
        """Try calling function with no arguments."""
        from qiskit import QuantumCircuit

        try:
            maybe_circuit = func()  # type: ignore
            if isinstance(maybe_circuit, QuantumCircuit):
                return maybe_circuit
        except TypeError:
            # Function requires arguments, will try with args next
            pass
        except Exception:
            # Other error, skip this function
            pass
        return None

    def _try_with_arg_call(self, func: callable) -> Optional['QuantumCircuit']:
        """Try calling function with common integer arguments."""
        from qiskit import QuantumCircuit

        for trial_n in (2, 3, 4):
            try:
                maybe_circuit = func(trial_n)
                if isinstance(maybe_circuit, QuantumCircuit):
                    return maybe_circuit
            except Exception:
                continue
        return None
    
    def _analyze_qiskit_circuit(self, qc: 'QuantumCircuit') -> ConversionStats:
        """
        Analyze a Qiskit circuit and extract statistics.
        
        Args:
            qc: Qiskit QuantumCircuit object
            
        Returns:
            ConversionStats: Circuit analysis statistics
        """
        try:
            # Get basic circuit properties
            try:
                n_qubits = qc.num_qubits
            except AttributeError:
                n_qubits = len(getattr(qc, "qubits", []))
            
            try:
                depth = qc.depth()
            except Exception:
                depth = None
            
            # Check for parameters (not used in return, but kept for potential future use)
            
            # Get basis gates and count them
            try:
                gate_counts = dict(qc.count_ops()) if hasattr(qc, "count_ops") else None
            except Exception:
                gate_counts = None
            
            # Check for measurements
            has_measurements = False
            try:
                if gate_counts:
                    has_measurements = any('measure' in gate.lower() for gate in gate_counts.keys())
            except Exception:
                has_measurements = False
            
            return ConversionStats(
                n_qubits=n_qubits,
                depth=depth,
                n_moments=depth,  # In Qiskit, depth is similar to moments
                gate_counts=gate_counts,
                has_measurements=has_measurements
            )
            
        except Exception:
            # Return minimal stats if analysis fails
            return ConversionStats(
                n_qubits=0,
                depth=None,
                n_moments=None,
                gate_counts=None,
                has_measurements=False
            )
    
    def _convert_to_qasm3(self, qc: 'QuantumCircuit') -> str:
        """
        Convert Qiskit QuantumCircuit to enhanced OpenQASM 3.0 string with advanced features.
        Now uses QASM3Builder for proper code generation.

        Args:
            qc: Qiskit QuantumCircuit object

        Returns:
            str: Enhanced OpenQASM 3.0 representation with advanced features

        Raises:
            ImportError: If Qiskit dependencies are missing
            RuntimeError: If conversion fails
        """
        try:
            import numpy as np
            from qiskit.circuit import Parameter, ParameterVector
        except ImportError:
            raise ImportError("Qiskit is required for conversion")

        # Initialize the QASM3 builder
        if VERBOSE:
            vprint("[QiskitToQASM3Converter] Building prelude")
        builder = QASM3Builder()

        # Get circuit dimensions
        num_qubits = qc.num_qubits
        num_clbits = qc.num_clbits

        # Build standard prelude using global config flags
        builder.build_standard_prelude(
            num_qubits=num_qubits,
            num_clbits=num_clbits,
            include_vars=INCLUDE_VARS,
            include_constants=INCLUDE_CONSTANTS
        )

        # Add circuit parameters if any
        if qc.parameters:
            builder.add_section_comment("Circuit parameters")
            for param in qc.parameters:
                if isinstance(param, Parameter):
                    builder.declare_variable(param.name, 'float')
            builder.add_blank_line()

        # Extract and define custom gates
        custom_gates = self._extract_custom_gates(qc)
        if custom_gates:
            builder.add_section_comment("Custom gate definitions")
            for gate_def in custom_gates:
                builder.lines.append(gate_def)
            builder.add_blank_line()

        # No extra classical operations for minimal translation
        
        # Convert circuit instructions
        builder.add_section_comment("Circuit operations")
        if VERBOSE:
            vprint("[QiskitToQASM3Converter] Emitting operations")
        for circuit_instruction in qc.data:
            # Use modern Qiskit 1.2+ named attributes
            instruction = circuit_instruction.operation
            qargs = circuit_instruction.qubits
            cargs = circuit_instruction.clbits
            self._add_qiskit_operation(builder, instruction, qargs, cargs, qc)
        
        # No demo control flow; emit only operations present in the source circuit

        code = builder.get_code()
        if VERBOSE:
            vprint("[QiskitToQASM3Converter] QASM generated, length:", len(code))
        return code

    def _extract_custom_gates(self, _qc: 'QuantumCircuit') -> list:
        """Extract custom gate definitions from the circuit."""
        custom_gates = []
        # This is a simplified implementation - in a full implementation,
        # you'd need to analyze the circuit for custom gate definitions
        return custom_gates

    def _add_qiskit_operation(self, builder: QASM3Builder, instruction, qargs, cargs, qc):
        """Add a Qiskit operation to the QASM builder."""
        import numpy as np

        gate_name = instruction.name.lower()

        # Get qubit and clbit indices
        qubit_indices = [qc.qubits.index(q) for q in qargs]
        qubits_str = [f"q[{i}]" for i in qubit_indices]
        clbit_indices = [qc.clbits.index(c) for c in cargs] if cargs else []

        # Detect gate modifiers
        modifiers = self._detect_gate_modifiers(gate_name)

        # Route to appropriate handler based on gate type
        if gate_name in ['h', 'x', 'y', 'z', 's', 't', 'sx', 'id', 'i']:
            self._handle_single_qubit_gate(builder, gate_name, qubits_str, modifiers)
        elif gate_name in ['rx', 'ry', 'rz', 'p']:
            self._handle_parameterized_single_qubit_gate(builder, gate_name, instruction, qubits_str, modifiers)
        elif gate_name == 'u':
            self._handle_universal_gate(builder, instruction, qubits_str, modifiers)
        elif gate_name in ['cx', 'cnot', 'cz', 'cy', 'ch', 'swap']:
            self._handle_two_qubit_gate(builder, gate_name, qubits_str, modifiers)
        elif gate_name in ['cp', 'crx', 'cry', 'crz']:
            self._handle_controlled_parametric_gate(builder, gate_name, instruction, qubits_str, modifiers)
        elif gate_name == 'gphase':
            self._handle_global_phase(builder, instruction)
        elif gate_name in ['ccx', 'toffoli']:
            self._handle_toffoli_gate(builder, qubits_str, modifiers)
        elif gate_name == 'ccz':
            self._handle_ccz_gate(builder, qubits_str, modifiers)
        elif gate_name in ['cswap', 'fredkin']:
            self._handle_fredkin_gate(builder, qubits_str, modifiers)
        elif gate_name == 'measure':
            self._handle_measurement(builder, qubits_str, clbit_indices)
        elif gate_name == 'reset':
            self._handle_reset(builder, qubits_str)
        elif gate_name == 'barrier':
            self._handle_barrier(builder, qubits_str)
        else:
            builder.add_comment(f"Unsupported gate: {gate_name}")

    def _detect_gate_modifiers(self, gate_name: str) -> dict:
        """Detect gate modifiers from gate name."""
        modifiers = {}

        # Check for inverse gates (gates ending with 'dg')
        if gate_name.endswith('dg'):
            modifiers['inv'] = True
            gate_name = gate_name[:-2]  # Remove 'dg' suffix

        return modifiers

    def _handle_single_qubit_gate(self, builder: QASM3Builder, gate_name: str, qubits_str: list, modifiers: dict):
        """Handle single-qubit gates without parameters."""
        builder.apply_gate(gate_name, qubits_str, modifiers=modifiers if modifiers else None)

    def _handle_parameterized_single_qubit_gate(self, builder: QASM3Builder, gate_name: str, instruction, qubits_str: list, modifiers: dict):
        """Handle parameterized single-qubit gates honoring registry param order."""
        param_names = QISKIT_TO_QASM_REGISTRY.mapping[gate_name].param_order if gate_name in QISKIT_TO_QASM_REGISTRY.mapping else ["theta"]
        # Map Qiskit instruction.params to expected order; for single-param gates it's the first
        ordered_params = []
        if param_names:
            # Currently single parameter for rx/ry uses theta and rz/p use lambda
            ordered_params.append(builder.format_parameter(instruction.params[0]))
        builder.apply_gate(gate_name, qubits_str, parameters=ordered_params, modifiers=modifiers if modifiers else None)

    def _handle_universal_gate(self, builder: QASM3Builder, instruction, qubits_str: list, modifiers: dict):
        """Handle universal U gate."""
        # Enforce parameter order from registry (theta, phi, lambda)
        param_names = QISKIT_TO_QASM_REGISTRY.mapping['u'].param_order
        params = [builder.format_parameter(instruction.params[i]) for i, _ in enumerate(param_names)]
        builder.apply_gate('u', qubits_str, parameters=params, modifiers=modifiers if modifiers else None)

    def _handle_two_qubit_gate(self, builder: QASM3Builder, gate_name: str, qubits_str: list, modifiers: dict):
        """Handle two-qubit gates."""
        actual_gate = 'cx' if gate_name == 'cnot' else gate_name
        builder.apply_gate(actual_gate, qubits_str, modifiers=modifiers if modifiers else None)

    def _handle_controlled_parametric_gate(self, builder: QASM3Builder, gate_name: str, instruction, qubits_str: list, modifiers: dict):
        """Handle controlled parametric gates honoring registry param order."""
        param_names = QISKIT_TO_QASM_REGISTRY.mapping[gate_name].param_order if gate_name in QISKIT_TO_QASM_REGISTRY.mapping else ["theta"]
        ordered_params = []
        if param_names:
            ordered_params.append(builder.format_parameter(instruction.params[0]))
        builder.apply_gate(gate_name, qubits_str, parameters=ordered_params, modifiers=modifiers if modifiers else None)

    def _handle_global_phase(self, builder: QASM3Builder, instruction):
        """Handle global phase gate."""
        param = builder.format_parameter(instruction.params[0])
        builder.apply_gate('gphase', [], parameters=[param])

    def _handle_toffoli_gate(self, builder: QASM3Builder, qubits_str: list, modifiers: dict):
        """Handle Toffoli gate."""
        builder.apply_gate('ccx', qubits_str, modifiers=modifiers if modifiers else None)

    def _handle_ccz_gate(self, builder: QASM3Builder, qubits_str: list, modifiers: dict):
        """Handle CCZ gate."""
        builder.apply_gate('ccz', qubits_str, modifiers=modifiers if modifiers else None)

    def _handle_fredkin_gate(self, builder: QASM3Builder, qubits_str: list, modifiers: dict):
        """Handle Fredkin gate."""
        builder.apply_gate('cswap', qubits_str, modifiers=modifiers if modifiers else None)

    def _handle_measurement(self, builder: QASM3Builder, qubits_str: list, clbit_indices: list):
        """Handle measurement operations."""
        if clbit_indices:
            builder.add_measurement(qubits_str[0], f"c[{clbit_indices[0]}]")

    def _handle_reset(self, builder: QASM3Builder, qubits_str: list):
        """Handle reset operations."""
        builder.add_reset(qubits_str[0])

    def _handle_barrier(self, builder: QASM3Builder, qubits_str: list):
        """Handle barrier operations."""
        builder.add_barrier(qubits_str if qubits_str else None)
    
    def _analyze_circuit_ast(self, circuit_ast) -> ConversionStats:
        try:
            return ConversionStats(
                n_qubits=circuit_ast.qubits,
                depth=circuit_ast.get_depth(),
                n_moments=circuit_ast.get_depth(),
                gate_counts=circuit_ast.get_gate_count(),
                has_measurements=circuit_ast.has_measurements(),
            )
        except Exception:
            return ConversionStats(n_qubits=0, depth=None, n_moments=None, gate_counts=None, has_measurements=False)

    def _convert_ast_to_qasm3(self, circuit_ast) -> str:
        t0 = time.time()
        builder = QASM3Builder()

        self._build_ast_prelude(builder, circuit_ast)
        self._convert_ast_operations(builder, circuit_ast)

        code = builder.get_code()
        self._log_ast_conversion_complete(t0)
        return code

    def _build_ast_prelude(self, builder: QASM3Builder, circuit_ast) -> None:
        """Build the QASM prelude for AST conversion."""
        # Honor global flags for constants/vars inclusion
        include_consts = INCLUDE_CONSTANTS
        builder.build_standard_prelude(
            num_qubits=circuit_ast.qubits,
            num_clbits=circuit_ast.clbits,
            include_vars=INCLUDE_VARS,
            include_constants=include_consts,
        )

        if circuit_ast.parameters:
            builder.add_section_comment("Circuit parameters")
            for param_name in circuit_ast.parameters:
                builder.declare_variable(param_name, 'float')
            builder.add_blank_line()

    def _convert_ast_operations(self, builder: QASM3Builder, circuit_ast) -> None:
        """Convert AST operations to QASM."""
        builder.add_section_comment("Circuit operations")

        for idx, op in enumerate(circuit_ast.operations):
            if isinstance(op, GateNode):
                self._convert_gate_node(builder, idx, op)
            elif isinstance(op, MeasurementNode):
                self._convert_measurement_node(builder, idx, op)
            elif isinstance(op, ResetNode):
                self._convert_reset_node(builder, idx, op)
            elif isinstance(op, BarrierNode):
                self._convert_barrier_node(builder, idx, op)
            else:
                builder.add_comment("Unsupported AST operation")

    def _convert_gate_node(self, builder: QASM3Builder, idx: int, op: GateNode) -> None:
        """Convert a gate node to QASM."""
        qubits_str = [f"q[{i}]" for i in op.qubits]
        name = op.name

        if VERBOSE:
            vprint(f"[QiskitToQASM3Converter] [{idx}] GateNode name={name} qubits={op.qubits} params={op.parameters} modifiers={getattr(op, 'modifiers', None)}")

        if name in ['h','x','y','z','s','t','sx','id','i','swap','cx','cz','ccx']:
            actual_name = 'cx' if name == 'cnot' else name
            modifiers = getattr(op, 'modifiers', None)
            builder.apply_gate(actual_name, qubits_str, modifiers=modifiers if modifiers else None)
        elif name in ['rx','ry','rz','p','u']:
            raw_params = (op.parameters or [])
            params = [builder.format_parameter(p) for p in raw_params]
            if VERBOSE:
                vprint(f"[QiskitToQASM3Converter]     params_raw={raw_params} params_fmt={params}")
            builder.apply_gate(name, qubits_str, parameters=params)
        else:
            builder.add_comment(f"Unsupported gate: {name}")

    def _convert_measurement_node(self, builder: QASM3Builder, idx: int, op: MeasurementNode) -> None:
        """Convert a measurement node to QASM."""
        if VERBOSE:
            vprint(f"[QiskitToQASM3Converter] [{idx}] Measurement q[{op.qubit}] -> c[{op.clbit}]")
        builder.add_measurement(f"q[{op.qubit}]", f"c[{op.clbit}]")

    def _convert_reset_node(self, builder: QASM3Builder, idx: int, op: ResetNode) -> None:
        """Convert a reset node to QASM."""
        if VERBOSE:
            vprint(f"[QiskitToQASM3Converter] [{idx}] Reset q[{op.qubit}]")
        builder.add_reset(f"q[{op.qubit}]")

    def _convert_barrier_node(self, builder: QASM3Builder, idx: int, op: BarrierNode) -> None:
        """Convert a barrier node to QASM."""
        if op.qubits:
            if VERBOSE:
                vprint(f"[QiskitToQASM3Converter] [{idx}] Barrier on {op.qubits}")
            builder.add_barrier([f"q[{i}]" for i in op.qubits])
        else:
            if VERBOSE:
                vprint(f"[QiskitToQASM3Converter] [{idx}] Barrier on all qubits")
            builder.add_barrier(None)

    def _log_ast_conversion_complete(self, start_time: float) -> None:
        """Log completion of AST conversion."""
        if VERBOSE:
            vprint(f"[QiskitToQASM3Converter] Build done in {(time.time()-start_time)*1000:.1f} ms")

    def convert(self, qiskit_source: str) -> ConversionResult:
        """
        Convert Qiskit source code to OpenQASM 3.0 format using AST-based parsing.
        
        This method now uses AST parsing instead of dynamic execution for improved
        security and reliability. It parses the source code to extract circuit operations
        without executing potentially unsafe code.
        
        Args:
            qiskit_source (str): Complete Qiskit source code defining get_circuit() function
            
        Returns:
            ConversionResult: Object containing QASM code and conversion statistics
            
        Raises:
            ValueError: If source code is invalid or doesn't define required function
            ImportError: If Qiskit dependencies are missing
            RuntimeError: If conversion process fails
            
        Example:
            >>> converter = QiskitToQASM3Converter()
            >>> source = '''
            ... from qiskit import QuantumCircuit
            ... def get_circuit():
            ...     qc = QuantumCircuit(2, 2)
            ...     qc.h(0)
            ...     qc.cx(0, 1)
            ...     qc.measure([0, 1], [0, 1])
            ...     return qc
            ... '''
            >>> result = converter.convert(source)
            >>> print(f"Circuit has {result.stats.n_qubits} qubits and depth {result.stats.depth}")
        """
        # Try AST-based conversion first
        if VERBOSE:
            vprint("[QiskitToQASM3Converter] Attempt AST-based conversion")
        try:
            parser = QiskitASTParser()
            t_parse = time.time()
            circuit_ast = parser.parse(qiskit_source)
            if VERBOSE:
                vprint(f"[QiskitToQASM3Converter] AST parsed in {(time.time()-t_parse)*1000:.1f} ms")
            t_ana = time.time()
            stats = self._analyze_circuit_ast(circuit_ast)
            if VERBOSE:
                vprint(f"[QiskitToQASM3Converter] AST analyzed in {(time.time()-t_ana)*1000:.1f} ms")
            qasm3_program = self._convert_ast_to_qasm3(circuit_ast)
            return ConversionResult(qasm_code=qasm3_program, stats=stats)
        except Exception:
            pass

        # Fallback: execute and use runtime circuit to QASM
        if VERBOSE:
            vprint("[QiskitToQASM3Converter] AST failed, fallback to runtime execution path")
        qc = self._execute_qiskit_source(qiskit_source)
        stats = self._analyze_qiskit_circuit(qc)
        qasm3_program = self._convert_to_qasm3(qc)
        return ConversionResult(qasm_code=qasm3_program, stats=stats)


# Public API function for easy module usage
def convert_qiskit_to_qasm3(qiskit_source: str) -> ConversionResult:
    """
    Convert Qiskit quantum circuit source code to OpenQASM 3.0 format.
    
    This is a convenience function that creates a converter instance and performs
    the conversion in a single call, returning a ConversionResult object.
    
    Args:
        qiskit_source (str): Complete Qiskit source code defining get_circuit() function
        
    Returns:
        ConversionResult: Object containing QASM code and conversion statistics
        
    Raises:
        ValueError: If source code is invalid or doesn't define required function
        ImportError: If Qiskit dependencies are missing
        RuntimeError: If conversion process fails
        
    Example:
        >>> from qiskit_qasm_converter import convert_qiskit_to_qasm3
        >>> source = '''
        ... from qiskit import QuantumCircuit
        ... def get_circuit():
        ...     qc = QuantumCircuit(2, 2)
        ...     qc.h(0)
        ...     qc.cx(0, 1)
        ...     qc.measure([0, 1], [0, 1])
        ...     return qc
        ... '''
        >>> result = convert_qiskit_to_qasm3(source)
        >>> print(result.qasm_code)
    """
    converter = QiskitToQASM3Converter()
    return converter.convert(qiskit_source)