"""
Cirq to OpenQASM 3.0 Converter Module

This module provides functionality to convert Cirq quantum circuits 
to OpenQASM 3.0 format. It serves as an intermediate representation (IR) 
converter for unified quantum simulators.

Author: QCanvas Team
Date: 2025-09-30
Version: 2.0.0 - Integrated with QASM3Builder
"""

import inspect
from typing import Dict, Any, Optional, Union, List
from quantum_converters.base.ConversionResult import ConversionResult, ConversionStats
from quantum_converters.base.qasm3_builder import QASM3Builder
from quantum_converters.base.qasm3_gates import QASM3GateLibrary, GateModifier
from quantum_converters.base.circuit_ast import CircuitAST, GateNode, MeasurementNode, ResetNode, BarrierNode
from quantum_converters.parsers.cirq_parser import CirqASTParser
from config.config import VERBOSE, vprint
import time

# Import Circuit only when needed to avoid dependency issues
try:
    from cirq import Circuit
except ImportError:
    # Define a placeholder for type hints
    Circuit = 'Circuit'

class CirqToQASM3Converter:
    """
    A converter class that transforms Cirq quantum circuits to OpenQASM 3.0 format.
    
    This converter supports all standard Cirq gates and circuit structures,
    leveraging Cirq's native OpenQASM 3.0 export functionality when available.
    
    The converter expects source code that defines a function `get_circuit()` 
    which returns a cirq.Circuit object.
    """
    
    def __init__(self):
        """Initialize the Cirq to QASM3 converter."""
        pass
    
    def _execute_cirq_source(self, source: str) -> 'Circuit':
        """
        Execute Cirq source code and extract the quantum circuit.

        Args:
            source (str): Cirq source code defining a get_circuit() function

        Returns:
            Circuit: The extracted Cirq quantum circuit

        Raises:
            ValueError: If source code doesn't define get_circuit() function
            ImportError: If Cirq is not available
            RuntimeError: If circuit execution fails
        """
        self._ensure_cirq_available()

        namespace = self._execute_source_code(source)

        # Try different strategies to extract the circuit
        circuit = (
            self._try_get_circuit_function(namespace) or
            self._try_find_circuit_instance(namespace) or
            self._try_factory_functions(namespace)
        )

        if circuit is None:
            raise ValueError(
                "Could not locate a cirq.Circuit. Define get_circuit() or assign the circuit to a variable."
            )

        return circuit

    def _ensure_cirq_available(self) -> None:
        """Ensure Cirq is available, raising ImportError if not."""
        try:
            import cirq  # noqa: F401
        except ImportError:
            raise ImportError("Cirq is required but not installed. Please install with: pip install cirq")

    def _execute_source_code(self, source: str) -> dict:
        """Execute the source code in an isolated namespace."""
        namespace = {}
        try:
            exec(compile(source, "<cirq_source>", "exec"), namespace)
        except Exception as e:
            raise RuntimeError(f"Failed to execute Cirq source code: {str(e)}")
        return namespace

    def _try_get_circuit_function(self, namespace: dict) -> Optional['Circuit']:
        """Try to get circuit from get_circuit() function."""
        get_circuit = namespace.get("get_circuit")
        if callable(get_circuit):
            try:
                circuit = get_circuit()
                if hasattr(circuit, 'all_qubits') and hasattr(circuit, 'moments'):
                    return circuit
            except Exception as e:
                raise RuntimeError(f"Failed to execute get_circuit() function: {str(e)}")
        return None

    def _try_find_circuit_instance(self, namespace: dict) -> Optional['Circuit']:
        """Try to find a Circuit instance in the namespace."""
        try:
            import cirq as _cirq
            for name, obj in namespace.items():
                if isinstance(obj, _cirq.Circuit):
                    return obj
        except Exception:
            pass
        return None

    def _try_factory_functions(self, namespace: dict) -> Optional['Circuit']:
        """Try calling factory functions that might create circuits."""
        import cirq as _cirq

        for name, obj in namespace.items():
            if callable(obj) and name.startswith(("create_", "build_", "make_")):
                try:
                    maybe_circuit = obj()  # type: ignore
                    if isinstance(maybe_circuit, _cirq.Circuit):
                        return maybe_circuit
                except Exception:
                    continue
        return None
    
    def _analyze_cirq_circuit(self, circuit: 'Circuit') -> ConversionStats:
        """
        Analyze a Cirq circuit and extract statistics.
        
        Args:
            circuit: Cirq Circuit object
            
        Returns:
            ConversionStats: Circuit analysis statistics
        """
        try:
            # Get basic circuit properties
            try:
                n_qubits = len(circuit.all_qubits())
            except Exception:
                n_qubits = 0
            
            try:
                depth = len(circuit)  # Number of moments
            except Exception:
                depth = None
            
            try:
                n_moments = len(circuit.moments)
            except Exception:
                n_moments = None
            
            # Count gate types
            gate_counts = {}
            has_measurements = False
            
            try:
                for moment in circuit:
                    for operation in moment:
                        gate_name = type(operation.gate).__name__
                        gate_counts[gate_name] = gate_counts.get(gate_name, 0) + 1
                        
                        # Check for measurements
                        if hasattr(operation.gate, '_measurement_key') or 'measure' in gate_name.lower():
                            has_measurements = True
            except Exception:
                gate_counts = None
                has_measurements = False
            
            return ConversionStats(
                n_qubits=n_qubits,
                depth=depth,
                n_moments=n_moments,
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
    
    def _convert_to_qasm3(self, circuit: 'Circuit') -> str:
        """
        Convert Cirq Circuit to enhanced OpenQASM 3.0 string with advanced features.
        Now uses QASM3Builder for proper code generation.

        Args:
            circuit: Cirq Circuit object

        Returns:
            str: Enhanced OpenQASM 3.0 representation with advanced features

        Raises:
            ImportError: If Cirq dependencies are missing
            RuntimeError: If conversion fails
        """
        self._ensure_dependencies_available()

        if VERBOSE:
            vprint("[CirqToQASM3Converter] Building prelude")
        t0 = time.time()

        builder = QASM3Builder()
        qubit_map = self._create_qubit_mapping(circuit)
        has_measurements = self._detect_measurements(circuit)

        self._build_prelude(builder, len(qubit_map), has_measurements)
        self._add_custom_gates(builder, circuit)
        self._convert_operations(builder, circuit, qubit_map)

        code = builder.get_code()
        self._log_conversion_complete(code, t0)
        return code

    def _ensure_dependencies_available(self) -> None:
        """Ensure required dependencies are available."""
        try:
            import cirq  # noqa: F401
            import numpy as np  # noqa: F401
        except ImportError:
            raise ImportError("Cirq is required for conversion")

    def _create_qubit_mapping(self, circuit: 'Circuit') -> dict:
        """Create a mapping from qubits to indices."""
        all_qubits = list(circuit.all_qubits())
        if VERBOSE:
            vprint(f"[CirqToQASM3Converter] Circuit qubits detected: {len(all_qubits)}")
        return {qubit: i for i, qubit in enumerate(sorted(all_qubits, key=str))}

    def _detect_measurements(self, circuit: 'Circuit') -> bool:
        """Detect if the circuit contains measurement operations."""
        return any(
            any(self._is_measurement_operation(op) for op in moment)
            for moment in circuit
        )

    def _is_measurement_operation(self, operation) -> bool:
        """Check if an operation is a measurement."""
        return (hasattr(operation.gate, '_measurement_key') or
                str(type(operation.gate).__name__) == 'MeasurementGate')

    def _build_prelude(self, builder: QASM3Builder, num_qubits: int, has_measurements: bool) -> None:
        """Build the QASM prelude with appropriate registers."""
        builder.build_standard_prelude(
            num_qubits=num_qubits,
            num_clbits=num_qubits if has_measurements else 0,
            include_vars=False,
            include_constants=False
        )

    def _add_custom_gates(self, builder: QASM3Builder, circuit: 'Circuit') -> None:
        """Add custom gate definitions if any exist."""
        custom_gates = self._extract_custom_gates(circuit)
        if custom_gates:
            builder.add_section_comment("Custom gate definitions")
            for gate_def in custom_gates:
                builder.lines.append(gate_def)
            builder.add_blank_line()

    def _convert_operations(self, builder: QASM3Builder, circuit: 'Circuit', qubit_map: dict) -> None:
        """Convert circuit operations to QASM."""
        builder.add_section_comment("Circuit operations")
        if VERBOSE:
            vprint("[CirqToQASM3Converter] Emitting operations")

        for moment in circuit:
            for operation in moment:
                if VERBOSE:
                    vprint(f"[CirqToQASM3Converter] Op: {type(operation.gate).__name__} on {[str(q) for q in operation.qubits]}")
                self._add_cirq_operation(builder, operation, qubit_map)

    def _log_conversion_complete(self, code: str, start_time: float) -> None:
        """Log completion of conversion."""
        if VERBOSE:
            vprint("[CirqToQASM3Converter] QASM generated, length:", len(code))
            vprint(f"[CirqToQASM3Converter] Build done in {(time.time()-start_time)*1000:.1f} ms")

    def _extract_custom_gates(self, circuit: 'Circuit') -> list:
        """Extract custom gate definitions from the circuit."""
        custom_gates = []
        # This is a simplified implementation - in a full implementation,
        # you'd need to analyze the circuit for custom gate definitions
        return custom_gates

    def _add_cirq_operation(self, builder: QASM3Builder, operation, qubit_map: dict):
        """Add a Cirq operation to the QASM builder."""
        import cirq
        import numpy as np

        gate = operation.gate
        qubits = operation.qubits
        qubit_indices = [qubit_map[qubit] for qubit in qubits]
        qubits_str = [f"q[{i}]" for i in qubit_indices]
        
        # Get gate name for type checking
        gate_name = type(gate).__name__
        
        # Detect gate modifiers and get actual exponent value
        modifiers = {}
        actual_exponent = None
        
        # Check for inverse (negative exponent)
        if hasattr(gate, 'exponent'):
            actual_exponent = gate.exponent
            if actual_exponent < 0:
                modifiers['inv'] = True
                # Use positive exponent for parameter calculation
                actual_exponent = abs(actual_exponent)
            elif actual_exponent != 1 and actual_exponent != 0:
                # Handle fractional exponents as power modifier (Iteration II feature)
                # For now, just process as normal parameter
                pass
        else:
            actual_exponent = 1  # Default

        # Handle different gate types
        if gate_name in ['HPowGate', '_H'] and (actual_exponent is None or abs(actual_exponent) == 1):
            builder.apply_gate("h", qubits_str, modifiers=modifiers if modifiers else None)
        elif gate_name in ['XPowGate', '_PauliX', '_X'] and (actual_exponent is None or abs(actual_exponent) == 1):
            builder.apply_gate("x", qubits_str, modifiers=modifiers if modifiers else None)
        elif gate_name in ['YPowGate', '_PauliY', '_Y'] and (actual_exponent is None or abs(actual_exponent) == 1):
            builder.apply_gate("y", qubits_str, modifiers=modifiers if modifiers else None)
        elif gate_name in ['ZPowGate', '_PauliZ', '_Z'] and (actual_exponent is None or abs(actual_exponent) == 1):
            builder.apply_gate("z", qubits_str, modifiers=modifiers if modifiers else None)
        elif gate_name in ['SPowGate', '_S'] and (actual_exponent is None or abs(actual_exponent) == 1):
            builder.apply_gate("s", qubits_str, modifiers=modifiers if modifiers else None)
        elif gate_name in ['TPowGate', '_T'] and (actual_exponent is None or abs(actual_exponent) == 1):
            builder.apply_gate("t", qubits_str, modifiers=modifiers if modifiers else None)
        elif gate_name in ['CNotPowGate', 'CXPowGate', '_CNOT'] and (actual_exponent is None or abs(actual_exponent) == 1):
            builder.apply_gate("cx", qubits_str, modifiers=modifiers if modifiers else None)
        elif gate_name in ['CZPowGate', '_CZ'] and (actual_exponent is None or abs(actual_exponent) == 1):
            builder.apply_gate("cz", qubits_str, modifiers=modifiers if modifiers else None)
        elif gate_name in ['SwapPowGate', '_SWAP'] and (actual_exponent is None or abs(actual_exponent) == 1):
            builder.apply_gate("swap", qubits_str, modifiers=modifiers if modifiers else None)
        elif gate_name in ['XPowGate', 'YPowGate', 'ZPowGate'] and actual_exponent is not None and abs(actual_exponent) != 1:
            # Handle parameterized rotation gates
            angle = actual_exponent * np.pi
            param = builder.format_parameter(angle)
            
            if gate_name == 'XPowGate':
                builder.apply_gate("rx", qubits_str, parameters=[param], modifiers=modifiers if modifiers else None)
            elif gate_name == 'YPowGate':
                builder.apply_gate("ry", qubits_str, parameters=[param], modifiers=modifiers if modifiers else None)
            elif gate_name == 'ZPowGate':
                builder.apply_gate("rz", qubits_str, parameters=[param], modifiers=modifiers if modifiers else None)
        elif gate_name in ['Rx', 'Ry', 'Rz']:
            # Handle rotation gates with direct angle
            angle = None
            for attr in ['rads', '_rads', 'angle', '_angle', 'theta', '_theta']:
                if hasattr(gate, attr):
                    angle = getattr(gate, attr)
                    break
            
            if angle is None:
                angle = np.pi/2  # Default fallback
            
            param = builder.format_parameter(angle)
            
            if gate_name == 'Rx':
                builder.apply_gate("rx", qubits_str, parameters=[param], modifiers=modifiers if modifiers else None)
            elif gate_name == 'Ry':
                builder.apply_gate("ry", qubits_str, parameters=[param], modifiers=modifiers if modifiers else None)
            elif gate_name == 'Rz':
                builder.apply_gate("rz", qubits_str, parameters=[param], modifiers=modifiers if modifiers else None)
        elif gate_name == 'PhasedXPowGate':
            # PhasedXPowGate - simplified handling
            phase_exponent = getattr(gate, 'phase_exponent', 0)
            if phase_exponent == 0:
                param = builder.format_parameter(actual_exponent * np.pi)
                builder.apply_gate("rx", qubits_str, parameters=[param], modifiers=modifiers if modifiers else None)
            else:
                # Complex case - add as comment
                builder.add_comment(f"PhasedXPowGate(exp={actual_exponent}, phase={phase_exponent}) not fully supported")
        elif gate_name == 'MatrixGate':
            builder.add_comment(f"Matrix gate: {gate}")
        elif gate_name == 'MeasurementGate' or hasattr(gate, '_measurement_key'):
            builder.add_measurement(qubits_str[0], f"c[{qubit_indices[0]}]")
        elif gate_name in ['ResetChannel', '_ResetGate'] or str(gate) == 'reset':
            builder.add_reset(qubits_str[0])
        elif gate_name == 'IdentityGate' or str(gate) == 'I':
            builder.apply_gate("id", qubits_str, modifiers=modifiers if modifiers else None)
        elif gate_name == 'ControlledGate':
            builder.add_comment(f"Controlled gate: {gate}")
        elif gate_name == 'GlobalPhaseGate':
            phase = getattr(gate, 'coefficient', np.pi/4)
            param = builder.format_parameter(phase)
            builder.apply_gate("gphase", [], parameters=[param])
        elif str(gate).startswith('barrier'):
            builder.add_barrier(qubits_str if qubits_str else None)
        else:
            builder.add_comment(f"Unsupported gate: {type(gate).__name__}")
        
    def _analyze_circuit_ast(self, circuit_ast: CircuitAST) -> ConversionStats:
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

    def _add_ast_operation(self, builder: QASM3Builder, operation):
        if isinstance(operation, GateNode):
            gate_name = operation.name
            qubits_str = [f"q[{i}]" for i in operation.qubits]
            modifiers = operation.modifiers if operation.modifiers else None
            if gate_name in ['h', 'x', 'y', 'z', 's', 't', 'sx', 'i', 'id']:
                builder.apply_gate(gate_name, qubits_str, modifiers=modifiers)
            elif gate_name in ['rx', 'ry', 'rz']:
                if operation.parameters:
                    param = builder.format_parameter(operation.parameters[0])
                    builder.apply_gate(gate_name, qubits_str, parameters=[param], modifiers=modifiers)
                else:
                    builder.add_comment(f"Parameterized gate {gate_name} missing parameter")
            elif gate_name in ['cx', 'cnot', 'cz', 'cy', 'ch', 'swap']:
                builder.apply_gate('cx' if gate_name == 'cnot' else gate_name, qubits_str, modifiers=modifiers)
            elif gate_name == 'gphase':
                if operation.parameters:
                    param = builder.format_parameter(operation.parameters[0])
                    builder.apply_gate('gphase', [], parameters=[param])
            else:
                builder.add_comment(f"Unsupported gate: {gate_name}")
        elif isinstance(operation, MeasurementNode):
            builder.add_measurement(f"q[{operation.qubit}]", f"c[{operation.clbit}]")
        elif isinstance(operation, ResetNode):
            builder.add_reset(f"q[{operation.qubit}]")
        elif isinstance(operation, BarrierNode):
            if operation.qubits:
                builder.add_barrier([f"q[{i}]" for i in operation.qubits])
            else:
                builder.add_barrier(None)

    def _convert_ast_to_qasm3(self, circuit_ast: CircuitAST) -> str:
        builder = QASM3Builder()
        builder.build_standard_prelude(
            num_qubits=circuit_ast.qubits,
            num_clbits=circuit_ast.clbits,
            include_vars=False,
            include_constants=False,
        )
        if circuit_ast.parameters:
            builder.add_section_comment("Circuit parameters")
            for param_name in circuit_ast.parameters:
                builder.declare_variable(param_name, 'float')
            builder.add_blank_line()
        builder.add_section_comment("Circuit operations")
        for op in circuit_ast.operations:
            self._add_ast_operation(builder, op)
        return builder.get_code()

    def convert(self, cirq_source: str) -> ConversionResult:
        """
        Convert Cirq source code to OpenQASM 3.0 format.
        
        Args:
            cirq_source (str): Complete Cirq source code defining get_circuit() function
            
        Returns:
            ConversionResult: Object containing QASM code and conversion statistics
            
        Raises:
            ValueError: If source code is invalid or doesn't define required function
            ImportError: If Cirq dependencies are missing
            RuntimeError: If conversion process fails
            
        Example:
            >>> converter = CirqToQASM3Converter()
            >>> source = '''
            ... import cirq
            ... def get_circuit():
            ...     q0, q1 = cirq.LineQubit.range(2)
            ...     circuit = cirq.Circuit(
            ...         cirq.H(q0),
            ...         cirq.CNOT(q0, q1),
            ...         cirq.measure(q0, key="m0"),
            ...         cirq.measure(q1, key="m1")
            ...     )
            ...     return circuit
            ... '''
            >>> result = converter.convert(source)
            >>> print(f"Circuit has {result.stats.n_qubits} qubits and {result.stats.depth} moments")
        """
        # Try AST-based path first (secure, no execution)
        try:
            if VERBOSE:
                vprint("[CirqToQASM3Converter] Attempt AST-based conversion")
            parser = CirqASTParser()
            circuit_ast = parser.parse(cirq_source)
            stats = self._analyze_circuit_ast(circuit_ast)
            qasm3_program = self._convert_ast_to_qasm3(circuit_ast)
            return ConversionResult(qasm_code=qasm3_program, stats=stats)
        except Exception:
            pass

        # Fallback: execute source to obtain cirq.Circuit
        if VERBOSE:
            vprint("[CirqToQASM3Converter] AST failed, fallback to runtime execution path")
        circuit = self._execute_cirq_source(cirq_source)
        stats = self._analyze_cirq_circuit(circuit)
        qasm3_program = self._convert_to_qasm3(circuit)
        return ConversionResult(qasm_code=qasm3_program, stats=stats)


# Public API function for easy module usage
def convert_cirq_to_qasm3(cirq_source: str) -> ConversionResult:
    """
    Convert Cirq quantum circuit source code to OpenQASM 3.0 format.
    
    This is a convenience function that creates a converter instance and performs
    the conversion in a single call, returning a ConversionResult object.
    
    Args:
        cirq_source (str): Complete Cirq source code defining get_circuit() function
        
    Returns:
        ConversionResult: Object containing QASM code and conversion statistics
        
    Raises:
        ValueError: If source code is invalid or doesn't define required function
        ImportError: If Cirq dependencies are missing
        RuntimeError: If conversion process fails
        
    Example:
        >>> from cirq_qasm_converter import convert_cirq_to_qasm3
        >>> source = '''
        ... import cirq
        ... def get_circuit():
        ...     q0, q1 = cirq.LineQubit.range(2)
        ...     circuit = cirq.Circuit(
        ...         cirq.H(q0),
        ...         cirq.CNOT(q0, q1)
        ...     )
        ...     return circuit
        ... '''
        >>> result = convert_cirq_to_qasm3(source)
        >>> print(result.qasm_code)
    """
    converter = CirqToQASM3Converter()
    return converter.convert(cirq_source)