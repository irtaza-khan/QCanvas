"""
Qiskit to OpenQASM 3.0 Converter Module

This module provides functionality to convert Qiskit quantum circuits 
to OpenQASM 3.0 format. It serves as an intermediate representation (IR) 
converter for unified quantum simulators.

Author: QCanvas Team
Date: 2025-09-30
Version: 2.0.0 - Integrated with QASM3Builder
"""

import inspect
from typing import Dict, Any, Optional, Union
from qiskit import QuantumCircuit
from quantum_converters.base.ConversionResult import ConversionResult, ConversionStats
from quantum_converters.base.qasm3_builder import QASM3Builder
from quantum_converters.base.qasm3_gates import QASM3GateLibrary, GateModifier

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
        pass
    
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
        try:
            from qiskit import QuantumCircuit
        except ImportError:
            raise ImportError("Qiskit is required but not installed. Please install with: pip install qiskit")
        
        # Create isolated namespace for executing user code
        namespace = {}
        
        try:
            # Execute the source code in the isolated namespace
            exec(compile(source, "<qiskit_source>", "exec"), namespace)
        except Exception as e:
            raise RuntimeError(f"Failed to execute Qiskit source code: {str(e)}")
        
        # Prefer a get_circuit() function if present
        get_circuit = namespace.get("get_circuit")
        if callable(get_circuit):
            try:
                circuit = get_circuit()
                if isinstance(circuit, QuantumCircuit):
                    return circuit
            except Exception as e:
                # If explicit getter exists but fails, surface the error
                raise RuntimeError(f"Failed to execute get_circuit() function: {str(e)}")

        # Fallback: search for any QuantumCircuit instances created by the code
        try:
            for name, obj in namespace.items():
                if isinstance(obj, QuantumCircuit):
                    return obj
        except Exception:
            pass

        # Secondary fallback: try calling simple factory functions with no parameters
        # or with a single integer parameter commonly named n or n_qubits
        for name, obj in namespace.items():
            if callable(obj) and name.startswith(("create_", "build_", "make_")):
                try:
                    # Try no-arg call
                    maybe_circuit = obj()  # type: ignore
                    if isinstance(maybe_circuit, QuantumCircuit):
                        return maybe_circuit
                except TypeError:
                    # Try with common integer default, e.g., 2 or 4 qubits
                    for trial_n in (2, 3, 4):
                        try:
                            maybe_circuit = obj(trial_n)
                            if isinstance(maybe_circuit, QuantumCircuit):
                                return maybe_circuit
                        except Exception:
                            continue
                except Exception:
                    continue

        raise ValueError(
            "Could not locate a QuantumCircuit. Define get_circuit() or assign the circuit to a variable."
        )
    
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
            
            # Check for parameters
            try:
                has_parameters = bool(getattr(qc, "parameters", []))
            except Exception:
                has_parameters = False
            
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
            
        except Exception as e:
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
        builder = QASM3Builder()
        gate_lib = QASM3GateLibrary()

        # Get circuit dimensions
        num_qubits = qc.num_qubits
        num_clbits = qc.num_clbits

        # Build standard prelude - include constants/vars for advanced features
        # Check if circuit has parameters or complex features
        has_parameters = bool(qc.parameters)
        has_measurements = any(instr.operation.name == 'measure' for instr in qc.data)
        has_advanced_ops = any(instr.operation.name in ['barrier', 'reset'] for instr in qc.data)
        has_advanced_features = has_parameters or has_advanced_ops or has_measurements
        
        builder.build_standard_prelude(
            num_qubits=num_qubits,
            num_clbits=num_clbits,
            include_vars=has_advanced_features,
            include_constants=has_advanced_features
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
        for circuit_instruction in qc.data:
            # Use modern Qiskit 1.2+ named attributes
            instruction = circuit_instruction.operation
            qargs = circuit_instruction.qubits
            cargs = circuit_instruction.clbits
            self._add_qiskit_operation(builder, instruction, qargs, cargs, qc)
        
        # No demo control flow; emit only operations present in the source circuit

        return builder.get_code()

    def _extract_custom_gates(self, qc: 'QuantumCircuit') -> list:
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
        modifiers = {}
        
        # Check for inverse gates (gates ending with 'dg')
        if gate_name.endswith('dg'):
            modifiers['inv'] = True
            # Remove 'dg' suffix to get base gate
            base_gate = gate_name[:-2]  # sdg -> s, tdg -> t
            gate_name = base_gate

        # Handle different gate types
        if gate_name in ['h', 'x', 'y', 'z', 's', 't', 'sx', 'id', 'i']:
            builder.apply_gate(gate_name, qubits_str, modifiers=modifiers if modifiers else None)
        elif gate_name in ['rx', 'ry', 'rz', 'p']:
            param = builder.format_parameter(instruction.params[0])
            builder.apply_gate(gate_name, qubits_str, parameters=[param], modifiers=modifiers if modifiers else None)
        elif gate_name == 'u':
            theta = builder.format_parameter(instruction.params[0])
            phi = builder.format_parameter(instruction.params[1])
            lam = builder.format_parameter(instruction.params[2])
            builder.apply_gate('u', qubits_str, parameters=[theta, phi, lam], modifiers=modifiers if modifiers else None)
        elif gate_name in ['cx', 'cnot', 'cz', 'cy', 'ch', 'swap']:
            builder.apply_gate('cx' if gate_name == 'cnot' else gate_name, qubits_str, modifiers=modifiers if modifiers else None)
        elif gate_name == 'cp':
            param = builder.format_parameter(instruction.params[0])
            builder.apply_gate('cp', qubits_str, parameters=[param], modifiers=modifiers if modifiers else None)
        elif gate_name in ['crx', 'cry', 'crz']:
            param = builder.format_parameter(instruction.params[0])
            builder.apply_gate(gate_name, qubits_str, parameters=[param], modifiers=modifiers if modifiers else None)
        elif gate_name == 'gphase':
            param = builder.format_parameter(instruction.params[0])
            builder.apply_gate('gphase', [], parameters=[param])
        elif gate_name in ['ccx', 'toffoli']:
            builder.apply_gate('ccx', qubits_str, modifiers=modifiers if modifiers else None)
        elif gate_name == 'ccz':
            builder.apply_gate('ccz', qubits_str, modifiers=modifiers if modifiers else None)
        elif gate_name in ['cswap', 'fredkin']:
            builder.apply_gate('cswap', qubits_str, modifiers=modifiers if modifiers else None)
        elif gate_name == 'measure':
            builder.add_measurement(qubits_str[0], f"c[{clbit_indices[0]}]")
        elif gate_name == 'reset':
            builder.add_reset(qubits_str[0])
        elif gate_name == 'barrier':
            builder.add_barrier(qubits_str if qubits_str else None)
        else:
            builder.add_comment(f"Unsupported gate: {gate_name}")
    
    def convert(self, qiskit_source: str) -> ConversionResult:
        """
        Convert Qiskit source code to OpenQASM 3.0 format.
        
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
        # Execute source code and extract circuit
        qc = self._execute_qiskit_source(qiskit_source)
        
        # Analyze the circuit
        stats = self._analyze_qiskit_circuit(qc)
        
        # Convert to OpenQASM 3.0
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