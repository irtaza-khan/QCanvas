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
from cirq import Circuit
from quantum_converters.base.ConversionResult import ConversionResult, ConversionStats

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
        
        # Extract the get_circuit function
        get_circuit = namespace.get("get_circuit")
        if not callable(get_circuit):
            raise ValueError(
                "Cirq source code must define a callable function 'get_circuit()' "
                "that returns a cirq.Circuit object"
            )
        
        try:
            # Execute the function to get the circuit
            circuit = get_circuit()
        except Exception as e:
            raise RuntimeError(f"Failed to execute get_circuit() function: {str(e)}")
        
        # Validate that we got a Circuit
        if not hasattr(circuit, 'all_qubits') or not hasattr(circuit, 'moments'):
            raise ValueError("get_circuit() must return a valid cirq.Circuit object")
        
        return circuit
    
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
        Convert Cirq Circuit to OpenQASM 3.0 string without comments.
        
        Args:
            circuit: Cirq Circuit object
            
        Returns:
            str: OpenQASM 3.0 representation without comments
            
        Raises:
            ImportError: If Cirq OpenQASM 3.0 support is not available
            RuntimeError: If conversion fails
        """
        try:
            import cirq
            import numpy as np
        except ImportError:
            raise ImportError("Cirq is required for conversion")
        
        try:
            # Try newer Cirq API first (version parameter)
            if hasattr(circuit, 'to_qasm') and 'version' in inspect.signature(circuit.to_qasm).parameters:
                qasm3_program = circuit.to_qasm(version="3.0")
            else:
                # Try older API with cirq.qasm function
                try:
                    qasm3_program = cirq.qasm(circuit, args=cirq.QasmArgs(version="3.0"))
                except Exception:
                    # Fallback to default QASM (usually 2.0) and add QASM 3.0 header
                    qasm_program = circuit.to_qasm() if hasattr(circuit, 'to_qasm') else cirq.qasm(circuit)
                    # Convert QASM 2.0 header to QASM 3.0
                    if qasm_program.startswith('OPENQASM 2.0;'):
                        qasm3_program = qasm_program.replace('OPENQASM 2.0;', 'OPENQASM 3.0;')
                        # Add include statement if not present
                        if 'include' not in qasm3_program:
                            lines = qasm3_program.split('\n')
                            lines.insert(1, 'include "stdgates.inc";')
                            qasm3_program = '\n'.join(lines)
                    else:
                        qasm3_program = qasm_program
            
            # Remove all comments from the output
            lines = qasm3_program.split('\n')
            clean_lines = []
            for line in lines:
                # Remove full-line comments
                if not line.strip().startswith('//'):
                    # Remove end-of-line comments
                    line = line.split('//')[0].strip()
                    if line:  # Only keep non-empty lines
                        clean_lines.append(line)
            
            # Convert symbolic expressions to decimal values
            processed_lines = []
            import re
            for line in clean_lines:
                # Replace -pi/expr and pi/expr with decimal values
                def _replace_pi_div(m):
                    sign = -1.0 if m.group('sign') == '-' else 1.0
                    den = float(m.group('den'))
                    return str(sign * (np.pi / den))
                line = re.sub(r'(?P<sign>-?)\bpi/(?P<den>[0-9]*\.?[0-9]+)', _replace_pi_div, line)

                # Replace -pi*expr and pi*expr with decimal values
                def _replace_pi_mul(m):
                    sign = -1.0 if m.group('sign') == '-' else 1.0
                    mul = float(m.group('mul'))
                    return str(sign * (np.pi * mul))
                line = re.sub(r'(?P<sign>-?)\bpi\*(?P<mul>[0-9]*\.?[0-9]+)', _replace_pi_mul, line)

                # Replace bare pi (and -pi) with decimal values in parameter contexts
                def _replace_pi_only(m):
                    sign = -1.0 if m.group('sign') == '-' else 1.0
                    return str(sign * np.pi)
                line = re.sub(r'(?P<sign>-?)\bpi\b(?=[\s\),;])', _replace_pi_only, line)

                processed_lines.append(line)
            
            return '\n'.join(processed_lines)
            
        except Exception as e:
            raise RuntimeError(f"Failed to convert Cirq circuit to OpenQASM 3.0: {str(e)}")
        
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