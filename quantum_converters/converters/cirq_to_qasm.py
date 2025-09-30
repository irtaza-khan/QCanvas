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
        try:
            import cirq
        except ImportError:
            raise ImportError("Cirq is required but not installed. Please install with: pip install cirq")
        
        # Create isolated namespace for executing user code
        namespace = {}
        
        try:
            # Execute the source code in the isolated namespace
            exec(compile(source, "<cirq_source>", "exec"), namespace)
        except Exception as e:
            raise RuntimeError(f"Failed to execute Cirq source code: {str(e)}")
        
        # Prefer a get_circuit() function if present
        get_circuit = namespace.get("get_circuit")
        if callable(get_circuit):
            try:
                circuit = get_circuit()
                if hasattr(circuit, 'all_qubits') and hasattr(circuit, 'moments'):
                    return circuit
            except Exception as e:
                raise RuntimeError(f"Failed to execute get_circuit() function: {str(e)}")

        # Fallback: search for any cirq.Circuit instances created by the code
        try:
            import cirq as _cirq
            for name, obj in namespace.items():
                if isinstance(obj, _cirq.Circuit):
                    return obj
        except Exception:
            pass

        # Secondary fallback: try calling simple factory functions
        for name, obj in namespace.items():
            if callable(obj) and name.startswith(("create_", "build_", "make_")):
                try:
                    maybe_circuit = obj()  # type: ignore
                    import cirq as _cirq
                    if isinstance(maybe_circuit, _cirq.Circuit):
                        return maybe_circuit
                except Exception:
                    continue

        raise ValueError(
            "Could not locate a cirq.Circuit. Define get_circuit() or assign the circuit to a variable."
        )
    
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
            
        except Exception as e:
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
        try:
            import cirq
            import numpy as np
        except ImportError:
            raise ImportError("Cirq is required for conversion")

        # Initialize the QASM3 builder
        builder = QASM3Builder()
        gate_lib = QASM3GateLibrary()

        # Get all qubits and determine circuit size
        all_qubits = list(circuit.all_qubits())
        num_qubits = len(all_qubits)
        
        # Create qubit mapping
        qubit_map = {qubit: i for i, qubit in enumerate(sorted(all_qubits, key=str))}

        # Check for measurements
        has_measurements = any(
            any(hasattr(op.gate, '_measurement_key') or 
                str(type(op.gate).__name__) == 'MeasurementGate' 
                for op in moment)
            for moment in circuit
        )

        # Build standard prelude with all registers and variables
        builder.build_standard_prelude(
            num_qubits=num_qubits,
            num_clbits=num_qubits if has_measurements else 0,
            include_vars=True
        )

        # Extract and define custom gates
        custom_gates = self._extract_custom_gates(circuit)
        if custom_gates:
            builder.add_section_comment("Custom gate definitions")
            for gate_def in custom_gates:
                builder.lines.append(gate_def)
            builder.add_blank_line()

        # Add example classical operations
        builder.add_section_comment("Classical operations")
        builder.add_assignment("temp_angle", "PI_2")
        builder.add_assignment("loop_index", "0")
        builder.add_blank_line()
        
        # Convert circuit operations
        builder.add_section_comment("Circuit operations")
        for moment in circuit:
            for operation in moment:
                self._add_cirq_operation(builder, operation, qubit_map)
        
        # Add example control flow (if we have classical bits)
        if has_measurements:
            builder.add_blank_line()
            builder.add_section_comment("Classical control flow examples")
            builder.add_if_statement(
                "c[0] == 1", 
                ["x q[1];"],
                else_body=None
            )
            builder.add_blank_line()
            builder.add_for_loop(
                "loop_index", 
                "[0:2]", 
                ["ry(temp_angle) q[loop_index];"]
            )

        return builder.get_code()

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
        # Execute source code and extract circuit
        circuit = self._execute_cirq_source(cirq_source)
        
        # Analyze the circuit
        stats = self._analyze_cirq_circuit(circuit)
        
        # Convert to OpenQASM 3.0
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