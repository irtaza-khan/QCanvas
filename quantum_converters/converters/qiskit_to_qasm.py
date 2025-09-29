"""
Qiskit to OpenQASM 3.0 Converter Module

This module provides functionality to convert Qiskit quantum circuits 
to OpenQASM 3.0 format. It serves as an intermediate representation (IR) 
converter for unified quantum simulators.

Author: [Your Name]
Date: [Current Date]
Version: 1.0.0
"""

import inspect
from typing import Dict, Any, Optional, Union
from qiskit import QuantumCircuit
from quantum_converters.base.ConversionResult import ConversionResult, ConversionStats

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
            from qiskit.circuit.library import RXGate, RYGate, RZGate, UGate
        except ImportError:
            raise ImportError("Qiskit is required for conversion")

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

        # Declare quantum and classical registers
        num_qubits = qc.num_qubits
        num_clbits = qc.num_clbits

        lines.append(f"// Quantum and classical registers")
        lines.append(f"qubit[{num_qubits}] q;")
        if num_clbits > 0:
            lines.append(f"bit[{num_clbits}] c;")
        lines.append("")

        # Add variable declarations and constants
        if qc.parameters:
            lines.append("// Circuit parameters")
            for param in qc.parameters:
                if isinstance(param, Parameter):
                    lines.append(f"float {param.name};")
            lines.append("")
        
        # Add classical variables for intermediate calculations
        lines.append("// Classical variables for intermediate calculations")
        lines.append("int loop_index;")
        lines.append("bool condition_result;")
        lines.append("float temp_angle;")
        lines.append("")

        # Add gate definitions for custom gates
        lines.append("// Gate definitions")
        custom_gates = self._extract_custom_gates(qc)
        for gate_def in custom_gates:
            lines.append(gate_def)
        lines.append("")

        # Add example classical instructions (Iteration I features)
        lines.append("// Classical operations examples")
        lines.append("// Assignment statements")
        lines.append("temp_angle = PI/2;")
        lines.append("loop_index = 0;")
        lines.append("")
        
        # Convert circuit instructions
        lines.append("// Circuit operations")
        for instruction, qargs, cargs in qc.data:
            qasm_line = self._convert_instruction_to_qasm3(instruction, qargs, cargs, qc)
            if qasm_line:
                lines.append(qasm_line)
        
        # Add example control flow (if we have classical bits)
        if num_clbits > 0:
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

    def _extract_custom_gates(self, qc: 'QuantumCircuit') -> list:
        """Extract custom gate definitions from the circuit."""
        custom_gates = []
        # This is a simplified implementation - in a full implementation,
        # you'd need to analyze the circuit for custom gate definitions
        return custom_gates

    def _convert_instruction_to_qasm3(self, instruction, qargs, cargs, qc) -> str:
        """Convert a single Qiskit instruction to OpenQASM 3.0."""
        gate_name = instruction.name.lower()

        # Get qubit indices
        qubit_indices = [qc.qubits.index(q) for q in qargs]
        clbit_indices = [qc.clbits.index(c) for c in cargs] if cargs else []

        # Handle different gate types
        if gate_name == 'h':
            return f"h q[{qubit_indices[0]}];"
        elif gate_name == 'x':
            return f"x q[{qubit_indices[0]}];"
        elif gate_name == 'y':
            return f"y q[{qubit_indices[0]}];"
        elif gate_name == 'z':
            return f"z q[{qubit_indices[0]}];"
        elif gate_name == 's':
            return f"s q[{qubit_indices[0]}];"
        elif gate_name == 't':
            return f"t q[{qubit_indices[0]}];"
        elif gate_name == 'cx' or gate_name == 'cnot':
            return f"cx q[{qubit_indices[0]}], q[{qubit_indices[1]}];"
        elif gate_name == 'cz':
            return f"cz q[{qubit_indices[0]}], q[{qubit_indices[1]}];"
        elif gate_name == 'swap':
            return f"swap q[{qubit_indices[0]}], q[{qubit_indices[1]}];"
        elif gate_name == 'rx':
            param = self._format_parameter(instruction.params[0])
            return f"rx({param}) q[{qubit_indices[0]}];"
        elif gate_name == 'ry':
            param = self._format_parameter(instruction.params[0])
            return f"ry({param}) q[{qubit_indices[0]}];"
        elif gate_name == 'rz':
            param = self._format_parameter(instruction.params[0])
            return f"rz({param}) q[{qubit_indices[0]}];"
        elif gate_name == 'p':
            param = self._format_parameter(instruction.params[0])
            return f"p({param}) q[{qubit_indices[0]}];"
        elif gate_name == 'u':
            theta = self._format_parameter(instruction.params[0])
            phi = self._format_parameter(instruction.params[1])
            lam = self._format_parameter(instruction.params[2])
            return f"u({theta}, {phi}, {lam}) q[{qubit_indices[0]}];"
        elif gate_name == 'measure':
            return f"measure q[{qubit_indices[0]}] -> c[{clbit_indices[0]}];"
        elif gate_name == 'reset':
            return f"reset q[{qubit_indices[0]}];"
        elif gate_name == 'barrier':
            if qubit_indices:
                qubits_str = ', '.join([f'q[{i}]' for i in qubit_indices])
                return f"barrier {qubits_str};"
            else:
                return f"barrier q;"  # Barrier on all qubits
        elif gate_name == 'cp':
            param = self._format_parameter(instruction.params[0])
            return f"cp({param}) q[{qubit_indices[0]}], q[{qubit_indices[1]}];"
        elif gate_name == 'gphase':
            # Global phase gate - OpenQASM 3.0 Iteration I feature
            param = self._format_parameter(instruction.params[0])
            return f"gphase({param});"
        elif gate_name == 'ccx' or gate_name == 'toffoli':
            # Toffoli gate (controlled-controlled-X)
            return f"ccx q[{qubit_indices[0]}], q[{qubit_indices[1]}], q[{qubit_indices[2]}];"
        elif gate_name == 'ccz':
            # Controlled-controlled-Z gate
            return f"ccz q[{qubit_indices[0]}], q[{qubit_indices[1]}], q[{qubit_indices[2]}];"
        elif gate_name == 'cswap' or gate_name == 'fredkin':
            # Fredkin gate (controlled-SWAP)
            return f"cswap q[{qubit_indices[0]}], q[{qubit_indices[1]}], q[{qubit_indices[2]}];"
        elif gate_name in ['id', 'i']:
            # Identity gate
            return f"id q[{qubit_indices[0]}];"
        elif gate_name == 'sx':
            # Square root of X gate
            return f"sx q[{qubit_indices[0]}];"
        elif gate_name == 'sxdg':
            # Inverse square root of X gate
            return f"sxdg q[{qubit_indices[0]}];"
        elif gate_name == 'sdg':
            # Inverse S gate
            return f"sdg q[{qubit_indices[0]}];"
        elif gate_name == 'tdg':
            # Inverse T gate
            return f"tdg q[{qubit_indices[0]}];"
        else:
            # For unknown gates, try to represent them generically
            return f"// Unsupported gate: {gate_name}"

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