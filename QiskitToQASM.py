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
from dataclasses import dataclass
from qiskit import QuantumCircuit, transpile, assemble

@dataclass
class QiskitConversionStats:
    """Statistics about the converted Qiskit circuit."""
    n_qubits: int
    n_clbits: int
    depth: Optional[int]
    has_parameters: bool
    basis_gates: Optional[list]


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
            import qiskit
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
        if not hasattr(circuit, 'qasm') or not hasattr(circuit, 'num_qubits'):
            raise ValueError("get_circuit() must return a valid qiskit.QuantumCircuit object")
        
        return circuit
    
    def _analyze_qiskit_circuit(self, qc: 'QuantumCircuit') -> QiskitConversionStats:
        """
        Analyze a Qiskit circuit and extract statistics.
        
        Args:
            qc: Qiskit QuantumCircuit object
            
        Returns:
            QiskitConversionStats: Circuit analysis statistics
        """
        try:
            # Get basic circuit properties
            try:
                n_qubits = qc.num_qubits
            except AttributeError:
                n_qubits = len(getattr(qc, "qubits", []))
            
            try:
                n_clbits = qc.num_clbits
            except AttributeError:
                n_clbits = len(getattr(qc, "clbits", []))
            
            try:
                depth = qc.depth()
            except Exception:
                depth = None
            
            # Check for parameters
            try:
                has_parameters = bool(getattr(qc, "parameters", []))
            except Exception:
                has_parameters = False
            
            # Get basis gates
            try:
                basis_gates = list(qc.count_ops().keys()) if hasattr(qc, "count_ops") else None
            except Exception:
                basis_gates = None
            
            return QiskitConversionStats(
                n_qubits=n_qubits,
                n_clbits=n_clbits,
                depth=depth,
                has_parameters=has_parameters,
                basis_gates=basis_gates
            )
            
        except Exception as e:
            # Return minimal stats if analysis fails
            return QiskitConversionStats(
                n_qubits=0,
                n_clbits=0,
                depth=None,
                has_parameters=False,
                basis_gates=None
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
            raise ImportError(
                "Qiskit OpenQASM 3.0 support requires Qiskit >= 0.46. "
                "Please upgrade with: pip install --upgrade qiskit"
            )
        
        try:
            # Use Qiskit's native OpenQASM 3.0 export
            qasm3_program = qasm3.dumps(qc)
            return qasm3_program
        except Exception as e:
            raise RuntimeError(f"Failed to convert circuit to OpenQASM 3.0: {str(e)}")
    
    def convert(self, qiskit_source: str) -> tuple[str, QiskitConversionStats]:
        """
        Convert Qiskit source code to OpenQASM 3.0 format.
        
        Args:
            qiskit_source (str): Complete Qiskit source code defining get_circuit() function
            
        Returns:
            tuple[str, QiskitConversionStats]: OpenQASM 3.0 program and conversion statistics
            
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
            >>> qasm_program, stats = converter.convert(source)
            >>> print(f"Circuit has {stats.n_qubits} qubits and depth {stats.depth}")
        """
        # Execute source code and extract circuit
        qc = self._execute_qiskit_source(qiskit_source)
        
        # Analyze the circuit
        stats = self._analyze_qiskit_circuit(qc)
        
        # Convert to OpenQASM 3.0
        qasm3_program = self._convert_to_qasm3(qc)
        
        return qasm3_program, stats


# Public API function for easy module usage
def convert_qiskit_to_qasm3(qiskit_source: str) -> str:
    """
    Convert Qiskit quantum circuit source code to OpenQASM 3.0 format.
    
    This is a convenience function that creates a converter instance and performs
    the conversion in a single call, returning only the OpenQASM 3.0 program.
    
    Args:
        qiskit_source (str): Complete Qiskit source code defining get_circuit() function
        
    Returns:
        str: OpenQASM 3.0 program string
        
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
        >>> qasm_program = convert_qiskit_to_qasm3(source)
        >>> print(qasm_program)
    """
    converter = QiskitToQASM3Converter()
    qasm_program, _ = converter.convert(qiskit_source)
    return qasm_program


def convert_qiskit_to_qasm3_with_stats(qiskit_source: str) -> tuple[str, Dict[str, Any]]:
    """
    Convert Qiskit source code to OpenQASM 3.0 with detailed statistics.
    
    Args:
        qiskit_source (str): Complete Qiskit source code defining get_circuit() function
        
    Returns:
        tuple[str, Dict[str, Any]]: OpenQASM 3.0 program and statistics dictionary
        
    Example:
        >>> qasm_program, stats = convert_qiskit_to_qasm3_with_stats(source)
        >>> print(f"Converted circuit with {stats['n_qubits']} qubits")
    """
    converter = QiskitToQASM3Converter()
    qasm_program, stats_obj = converter.convert(qiskit_source)
    
    # Convert stats object to dictionary for easier use
    stats_dict = {
        'n_qubits': stats_obj.n_qubits,
        'n_clbits': stats_obj.n_clbits,
        'depth': stats_obj.depth,
        'has_parameters': stats_obj.has_parameters,
        'basis_gates': stats_obj.basis_gates
    }
    
    return qasm_program, stats_dict