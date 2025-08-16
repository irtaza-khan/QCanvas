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
        
        # Extract the get_circuit function
        get_circuit = namespace.get("get_circuit")
        if not callable(get_circuit):
            raise ValueError(
                "Qiskit source code must define a callable function 'get_circuit()' "
                "that returns a qiskit.QuantumCircuit object"
            )
        
        try:
            # Execute the function to get the circuit
            circuit = get_circuit()
        except Exception as e:
            raise RuntimeError(f"Failed to execute get_circuit() function: {str(e)}")
        
        # Validate that we got a QuantumCircuit
        if not isinstance(circuit, QuantumCircuit):
            raise ValueError("get_circuit() must return a valid qiskit.QuantumCircuit object")
        
        return circuit
    
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
        Convert Qiskit QuantumCircuit to OpenQASM 3.0 string.
        
        Args:
            qc: Qiskit QuantumCircuit object
            
        Returns:
            str: OpenQASM 3.0 representation
            
        Raises:
            ImportError: If qiskit.qasm3 module is not available
            RuntimeError: If conversion fails
        """
        try:
            import qiskit.qasm3 as qasm3
        except ImportError:
            # Fallback to older qiskit versions
            try:
                from qiskit import qasm
                print("Warning: Using legacy QASM 2.0 export, will convert to QASM 3.0 format")
                # Use legacy export and convert format
                qasm2_program = qc.qasm()
                # Convert QASM 2.0 to QASM 3.0 format
                if qasm2_program.startswith('OPENQASM 2.0;'):
                    qasm3_program = qasm2_program.replace('OPENQASM 2.0;', 'OPENQASM 3.0;')
                    lines = qasm3_program.split('\n')
                    if 'include "qelib1.inc";' in lines:
                        lines[lines.index('include "qelib1.inc";')] = 'include "stdgates.inc";'
                    return '\n'.join(lines)
                else:
                    return qasm2_program
            except Exception:
                raise ImportError(
                    "Qiskit OpenQASM 3.0 support requires Qiskit >= 0.46, or basic QASM export failed. "
                    "Please upgrade with: pip install --upgrade qiskit"
                )
        
        try:
            # Use Qiskit's native OpenQASM 3.0 export
            qasm3_program = qasm3.dumps(qc)

            # Normalize symbolic pi expressions to decimal numbers
            import numpy as np
            import re

            lines = qasm3_program.split('\n')
            processed_lines = []
            for line in lines:
                original = line
                # Replace -pi/expr and pi/expr
                def _replace_pi_div(m):
                    sign = -1.0 if m.group('sign') == '-' else 1.0
                    den = float(m.group('den'))
                    return str(sign * (np.pi / den))
                line = re.sub(r'(?P<sign>-?)\bpi/(?P<den>[0-9]*\.?[0-9]+)', _replace_pi_div, line)

                # Replace -pi*expr and pi*expr
                def _replace_pi_mul(m):
                    sign = -1.0 if m.group('sign') == '-' else 1.0
                    mul = float(m.group('mul'))
                    return str(sign * (np.pi * mul))
                line = re.sub(r'(?P<sign>-?)\bpi\*(?P<mul>[0-9]*\.?[0-9]+)', _replace_pi_mul, line)

                # Replace bare pi and -pi when used as parameters
                def _replace_pi_only(m):
                    sign = -1.0 if m.group('sign') == '-' else 1.0
                    return str(sign * np.pi)
                line = re.sub(r'(?P<sign>-?)\bpi\b(?=[\s\),;])', _replace_pi_only, line)

                processed_lines.append(line)

            return '\n'.join(processed_lines)
        except Exception as e:
            raise RuntimeError(f"Failed to convert circuit to OpenQASM 3.0: {str(e)}")
    
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