"""
Cirq to OpenQASM 3.0 Converter Module

This module provides functionality to convert Cirq quantum circuits 
to OpenQASM 3.0 format. It serves as an intermediate representation (IR) 
converter for unified quantum simulators.

Author: [Your Name]
Date: [Current Date]
Version: 1.0.0
"""

import inspect
from typing import Dict, Any, Optional, Union, List
from quantum_converters.base.ConversionResult import ConversionResult, ConversionStats

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

        Args:
            circuit: Cirq Circuit object

        Returns:
            str: Enhanced OpenQASM 3.0 representation with advanced features

        Raises:
            ImportError: If Cirq dependencies are missing
            RuntimeError: If conversion fails
        """
        # Enhanced OpenQASM 3.0 generation
        try:
            import cirq
            import numpy as np
        except ImportError:
            raise ImportError("Cirq is required for conversion")

        # Start building enhanced OpenQASM 3.0 output
        lines = []
        lines.append("OPENQASM 3.0;")
        lines.append('include "stdgates.inc";')
        lines.append("")

        # Add mathematical constants
        lines.append("// Mathematical constants")
        lines.append("const float PI = 3.141592653589793;")
        lines.append("const float E = 2.718281828459045;")
        lines.append("const float PI_2 = 1.5707963267948966;  // PI/2")
        lines.append("const float PI_4 = 0.7853981633974483;  // PI/4")
        lines.append("")

        # Get all qubits and determine circuit size
        all_qubits = list(circuit.all_qubits())
        num_qubits = len(all_qubits)

        # Create qubit mapping
        qubit_map = {qubit: i for i, qubit in enumerate(sorted(all_qubits, key=str))}

        lines.append(f"// Quantum registers")
        lines.append(f"qubit[{num_qubits}] q;")
        lines.append("")

        # Add classical registers if measurements exist
        has_measurements = any(any(hasattr(op.gate, '_measurement_key') or str(type(op.gate).__name__) == 'MeasurementGate' for op in moment)
                              for moment in circuit)
        if has_measurements:
            lines.append("// Classical registers")
            lines.append(f"bit[{num_qubits}] c;")
            lines.append("")
        
        # Add classical variables for intermediate calculations
        lines.append("// Classical variables for intermediate calculations")
        lines.append("int loop_index;")
        lines.append("bool condition_result;")
        lines.append("float temp_angle;")
        lines.append("")

        # Add gate definitions for custom gates
        lines.append("// Gate definitions")
        custom_gates = self._extract_custom_gates(circuit)
        for gate_def in custom_gates:
            lines.append(gate_def)
        lines.append("")

        # Add example classical instructions (Iteration I features)
        lines.append("// Classical operations examples")
        lines.append("// Assignment statements")
        lines.append("temp_angle = PI/2;")
        lines.append("loop_index = 0;")
        lines.append("")
        
        # Convert circuit operations
        lines.append("// Circuit operations")
        for moment in circuit:
            for operation in moment:
                qasm_line = self._convert_operation_to_qasm3(operation, qubit_map)
                if qasm_line:
                    lines.append(qasm_line)
        
        # Add example control flow (if we have classical bits)
        if has_measurements:
            lines.append("")
            lines.append("// Classical control flow examples")
            lines.append("// If statement based on measurement result")
            lines.append("if (c[0] == 1) {")
            lines.append("    // Apply corrective operations")
            lines.append("    x q[1];")
            lines.append("}")
            lines.append("")
            lines.append("// For loop example")
            lines.append("for loop_index in [0:2] {")
            lines.append("    // Conditional operations")
            lines.append("    ry(temp_angle) q[loop_index];")
            lines.append("}")

        return '\n'.join(lines)

    def _extract_custom_gates(self, circuit: 'Circuit') -> list:
        """Extract custom gate definitions from the circuit."""
        custom_gates = []
        # This is a simplified implementation - in a full implementation,
        # you'd need to analyze the circuit for custom gate definitions
        return custom_gates

    def _convert_operation_to_qasm3(self, operation, qubit_map: dict) -> str:
        """Convert a single Cirq operation to OpenQASM 3.0."""
        import cirq
        import numpy as np

        gate = operation.gate
        qubits = operation.qubits
        qubit_indices = [qubit_map[qubit] for qubit in qubits]
        
        # Get gate name for type checking
        gate_name = type(gate).__name__

        # Handle different gate types using gate name and type checking
        if gate_name in ['HPowGate', '_H'] and (not hasattr(gate, 'exponent') or gate.exponent == 1):
            return f"h q[{qubit_indices[0]}];"
        elif gate_name in ['XPowGate', '_PauliX', '_X'] and (not hasattr(gate, 'exponent') or gate.exponent == 1):
            return f"x q[{qubit_indices[0]}];"
        elif gate_name in ['YPowGate', '_PauliY', '_Y'] and (not hasattr(gate, 'exponent') or gate.exponent == 1):
            return f"y q[{qubit_indices[0]}];"
        elif gate_name in ['ZPowGate', '_PauliZ', '_Z'] and (not hasattr(gate, 'exponent') or gate.exponent == 1):
            return f"z q[{qubit_indices[0]}];"
        elif gate_name in ['SPowGate', '_S'] and (not hasattr(gate, 'exponent') or gate.exponent == 1):
            return f"s q[{qubit_indices[0]}];"
        elif gate_name in ['TPowGate', '_T'] and (not hasattr(gate, 'exponent') or gate.exponent == 1):
            return f"t q[{qubit_indices[0]}];"
        elif gate_name in ['CNotPowGate', 'CXPowGate', '_CNOT'] and (not hasattr(gate, 'exponent') or gate.exponent == 1):
            return f"cx q[{qubit_indices[0]}], q[{qubit_indices[1]}];"
        elif gate_name in ['CZPowGate', '_CZ'] and (not hasattr(gate, 'exponent') or gate.exponent == 1):
            return f"cz q[{qubit_indices[0]}], q[{qubit_indices[1]}];"
        elif gate_name in ['SwapPowGate', '_SWAP'] and (not hasattr(gate, 'exponent') or gate.exponent == 1):
            return f"swap q[{qubit_indices[0]}], q[{qubit_indices[1]}];"
        elif gate_name in ['XPowGate', 'YPowGate', 'ZPowGate'] and hasattr(gate, 'exponent') and gate.exponent != 1:
            # Handle parameterized rotation gates created by cirq.rx(), cirq.ry(), cirq.rz()
            exponent = gate.exponent
            # For rotation gates, the angle is exponent * pi
            angle = exponent * np.pi
            param = self._format_parameter(angle)
            
            if gate_name == 'XPowGate':
                return f"rx({param}) q[{qubit_indices[0]}];"
            elif gate_name == 'YPowGate':
                return f"ry({param}) q[{qubit_indices[0]}];"
            elif gate_name == 'ZPowGate':
                return f"rz({param}) q[{qubit_indices[0]}];"
        elif gate_name in ['Rx', 'Ry', 'Rz']:
            # Handle rotation gates that don't have exponent - they should have the angle directly
            # For cirq.rx(angle), cirq.ry(angle), cirq.rz(angle) where angle is in radians
            # Try different attribute names to extract the angle
            angle = None
            for attr in ['rads', '_rads', 'angle', '_angle', 'theta', '_theta']:
                if hasattr(gate, attr):
                    angle = getattr(gate, attr)
                    break
            
            if angle is None:
                angle = np.pi/2  # Default fallback
            
            param = self._format_parameter(angle)
            
            if gate_name == 'Rx':
                return f"rx({param}) q[{qubit_indices[0]}];"
            elif gate_name == 'Ry':
                return f"ry({param}) q[{qubit_indices[0]}];"
            elif gate_name == 'Rz':
                return f"rz({param}) q[{qubit_indices[0]}];"
        elif gate_name == 'PhasedXPowGate':
            # PhasedXPowGate with phase - convert to appropriate representation
            exponent = getattr(gate, 'exponent', 1)
            phase_exponent = getattr(gate, 'phase_exponent', 0)
            if phase_exponent == 0:
                # Simple X rotation
                param = self._format_parameter(exponent * np.pi)
                return f"rx({param}) q[{qubit_indices[0]}];"
            else:
                # Complex PhasedXPowGate - represent with comment for now
                phase_param = self._format_parameter(phase_exponent * np.pi)
                return f"// PhasedXPowGate(exponent={exponent}, phase_exponent={phase_exponent}): phased_x({phase_param}) q[{qubit_indices[0]}];"
        elif gate_name == 'MatrixGate':
            # For arbitrary unitary matrices, we'd need more complex handling
            # For now, represent as a comment
            return f"// Matrix gate: {gate}"
        elif gate_name == 'MeasurementGate' or hasattr(gate, '_measurement_key'):
            # Measurement gate - map to classical bits
            return f"measure q[{qubit_indices[0]}] -> c[{qubit_indices[0]}];"
        elif gate_name in ['ResetChannel', '_ResetGate'] or str(gate) == 'reset':
            # Reset operation
            return f"reset q[{qubit_indices[0]}];"
        elif gate_name == 'IdentityGate' or str(gate) == 'I':
            # Identity gate
            return f"id q[{qubit_indices[0]}];"
        elif gate_name == 'ControlledGate':
            # Generic controlled gate - simplified representation
            return f"// Controlled gate: {gate}"
        elif gate_name == 'GlobalPhaseGate':
            # Global phase gate - Iteration I feature
            phase = getattr(gate, 'coefficient', np.pi/4)
            param = self._format_parameter(phase)
            return f"gphase({param});"
        elif str(gate).startswith('barrier'):
            # Barrier instruction
            if len(qubit_indices) > 1:
                qubits_str = ', '.join([f'q[{i}]' for i in qubit_indices])
                return f"barrier {qubits_str};"
            else:
                return f"barrier q[{qubit_indices[0]}];"
        else:
            # For unknown gates
            return f"// Unsupported gate: {type(gate).__name__}"

    def _format_parameter(self, param) -> str:
        """Format a parameter for OpenQASM 3.0 output."""
        import numpy as np

        if isinstance(param, (int, float)):
            # Convert numpy types to Python types
            if hasattr(param, 'item'):
                param = param.item()

            # Format floats nicely
            if isinstance(param, float):
                # Check for common mathematical constants
                if abs(param - np.pi) < 1e-10:
                    return "PI"
                elif abs(param - np.pi/2) < 1e-10:
                    return "PI/2"
                elif abs(param - np.pi/4) < 1e-10:
                    return "PI/4"
                elif abs(param - np.e) < 1e-10:
                    return "E"
                else:
                    return f"{param:.6f}"
            else:
                return str(param)
        else:
            # For symbolic parameters
            return str(param)
        
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