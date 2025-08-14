"""
PennyLane to OpenQASM 3.0 Converter Module

This module provides functionality to convert PennyLane quantum circuits 
containing basic gates to OpenQASM 3.0 format. It serves as an intermediate 
representation (IR) converter for unified quantum simulators.

Author: [Your Name]
Date: [Current Date]
Version: 1.0.0
"""

import pennylane as qml
import numpy as np
import re
from typing import List, Dict, Any, Union
from quantum_converters.base.ConversionResult import ConversionResult, ConversionStats

class PennyLaneToQASM3Converter:
    """
    A converter class that transforms PennyLane quantum circuits to OpenQASM 3.0 format.
    
    This converter supports basic quantum gates including:
    - Single-qubit gates: PauliX, PauliY, PauliZ, Hadamard, S, T, Identity
    - Parameterized gates: RX, RY, RZ, PhaseShift
    - Two-qubit gates: CNOT, CZ, SWAP
    - Three-qubit gates: Toffoli
    
    Attributes:
        gate_mapping (Dict[str, str]): Maps PennyLane gate names to OpenQASM 3.0 equivalents
    """
    
    def __init__(self):
        """Initialize the converter with gate mappings."""
        self.gate_mapping = {
            # Single-qubit Pauli gates
            'PauliX': 'x',
            'PauliY': 'y', 
            'PauliZ': 'z',
            
            # Single-qubit gates
            'Hadamard': 'h',
            'S': 's',
            'T': 't',
            'Identity': 'id',
            
            # Parameterized single-qubit gates
            'RX': 'rx',
            'RY': 'ry',
            'RZ': 'rz',
            'PhaseShift': 'p',
            
            # Two-qubit gates
            'CNOT': 'cx',
            'CZ': 'cz',
            'SWAP': 'swap',
            
            # Three-qubit gates
            'Toffoli': 'ccx'
        }
    
    def _extract_circuit_info(self, circuit_code: str) -> Dict[str, Any]:
        """
        Extract circuit information from PennyLane code string.
        
        Args:
            circuit_code (str): The PennyLane circuit code as a string
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - num_qubits (int): Number of qubits in the circuit
                - operations (List[str]): List of operation strings
        """
        # Find device definition to determine number of qubits
        device_match = re.search(r'qml\.device\([^,]+,\s*wires=(\d+)', circuit_code)
        num_qubits = int(device_match.group(1)) if device_match else 2
        
        # Extract quantum operations from the circuit function
        operations = []
        lines = circuit_code.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for lines that start with qml. (quantum operations)
            if line.startswith('qml.') and not line.startswith('qml.expval') and not line.startswith('qml.device'):
                operations.append(line)
        
        return {
            'num_qubits': num_qubits,
            'operations': operations
        }
    
    def _parse_operation(self, op_line: str) -> Dict[str, Any]:
        """
        Parse a single PennyLane operation line to extract gate name, parameters, and wires.
        
        Args:
            op_line (str): A single line of PennyLane operation code
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - gate (str): Gate name
                - params (List[str]): List of parameters
                - wires (List[int]): List of wire indices
        """
        # Remove qml. prefix for processing
        op_line = op_line.replace('qml.', '').strip()
        
        # Handle gates with parameters and/or wires
        if '(' in op_line:
            gate_name = op_line.split('(')[0]
            params_and_wires = op_line.split('(')[1].rstrip(')')
            
            # Separate parameters from wires
            parts = params_and_wires.split('wires=')
            
            if len(parts) > 1:
                # Has explicit wires parameter
                param_part = parts[0].rstrip(', ')
                wire_part = parts[1]
            else:
                # Only wires specified, no parameters
                param_part = ''
                wire_part = params_and_wires
            
            # Parse parameters
            params = []
            if param_part and param_part != '':
                param_part = param_part.strip()
                # Handle list format [param1, param2]
                if param_part.startswith('[') and param_part.endswith(']'):
                    param_part = param_part[1:-1]
                
                # Split multiple parameters
                if ',' in param_part:
                    params = [p.strip() for p in param_part.split(',')]
                else:
                    params = [param_part] if param_part else []
            
            # Parse wire indices
            wire_part = wire_part.strip()
            # Handle list format [wire1, wire2]
            if wire_part.startswith('[') and wire_part.endswith(']'):
                wire_part = wire_part[1:-1]
            
            # Split multiple wires
            if ',' in wire_part:
                wires = [int(w.strip()) for w in wire_part.split(',')]
            else:
                wires = [int(wire_part)]
                
        else:
            # Gate without parameters or parentheses
            gate_name = op_line
            params = []
            wires = []
        
        return {
            'gate': gate_name,
            'params': params,
            'wires': wires
        }
    
    def _evaluate_parameter(self, param_str: str) -> Union[float, str]:
        """
        Evaluate numerical expressions in parameters, including numpy constants.
        
        Args:
            param_str (str): Parameter string that may contain mathematical expressions
            
        Returns:
            Union[float, str]: Evaluated numerical value or original string if evaluation fails
        """
        try:
            # Replace common numpy expressions with their values
            param_str = param_str.replace('np.pi', str(np.pi))
            param_str = param_str.replace('numpy.pi', str(np.pi))
            param_str = param_str.replace('np.e', str(np.e))
            param_str = param_str.replace('numpy.e', str(np.e))
            
            # Define allowed names for safe evaluation
            allowed_names = {
                "__builtins__": {},
                "pi": np.pi,
                "e": np.e,
                "sqrt": np.sqrt,
                "sin": np.sin,
                "cos": np.cos,
                "tan": np.tan,
            }
            
            # Safely evaluate the mathematical expression
            result = eval(param_str, allowed_names)
            return float(result)
            
        except Exception:
            # If evaluation fails, try direct float conversion
            try:
                return float(param_str)
            except ValueError:
                # Return original string if all else fails
                return param_str
    
    def _convert_gate(self, parsed_op: Dict[str, Any]) -> str:
        """
        Convert a parsed PennyLane operation to its OpenQASM 3.0 equivalent.
        
        Args:
            parsed_op (Dict[str, Any]): Parsed operation containing gate, params, and wires
            
        Returns:
            str: OpenQASM 3.0 gate instruction string
        """
        gate_name = parsed_op['gate']
        params = parsed_op['params']
        wires = parsed_op['wires']
        
        # Check if gate is supported
        if gate_name not in self.gate_mapping:
            return f"// Unsupported gate: {gate_name}"
        
        qasm_gate = self.gate_mapping[gate_name]
        
        # Handle parameterized gates
        if params:
            evaluated_params = []
            for param in params:
                if isinstance(param, str):
                    evaluated_params.append(self._evaluate_parameter(param))
                else:
                    evaluated_params.append(param)
            
            param_str = ', '.join(str(p) for p in evaluated_params)
            param_str = f"({param_str})"
        else:
            param_str = ""
        
        # Format wire specifications
        wire_str = ', '.join(f"q[{w}]" for w in wires)
        
        return f"{qasm_gate}{param_str} {wire_str};"
    
    def convert(self, pennylane_code: str) -> ConversionResult:
        """
        Convert PennyLane quantum circuit code to OpenQASM 3.0 format with statistics.
        
        Args:
            pennylane_code (str): Complete PennyLane circuit code as a string
            
        Returns:
            ConversionResult: Object containing QASM code and conversion statistics
            
        Raises:
            ValueError: If the input code cannot be parsed or contains unsupported operations
        """
        try:
            # Extract circuit information from PennyLane code
            circuit_info = self._extract_circuit_info(pennylane_code)
            num_qubits = circuit_info['num_qubits']
            operations = circuit_info['operations']
            
            # Build OpenQASM 3.0 header
            qasm_lines = [
                "OPENQASM 3.0;",
                "include \"stdgates.inc\";",
                "",
                f"qubit[{num_qubits}] q;",
                ""
            ]
            
            # Initialize statistics
            gate_counts = {}
            has_measurements = False
            depth = 0
            
            # Convert each PennyLane operation to OpenQASM 3.0 and collect stats
            for op_line in operations:
                parsed_op = self._parse_operation(op_line)
                qasm_gate = self._convert_gate(parsed_op)
                qasm_lines.append(qasm_gate)
                
                # Update gate counts
                gate_name = parsed_op['gate']
                gate_counts[gate_name] = gate_counts.get(gate_name, 0) + 1
                
                # Check for measurements
                if 'measure' in gate_name.lower():
                    has_measurements = True
                
                # Simple depth calculation (assuming each operation is a new moment)
                depth += 1
            
            # Create stats object
            stats = ConversionStats(
                n_qubits=num_qubits,
                depth=depth,
                n_moments=depth,  # In this simple model, depth = number of moments
                gate_counts=gate_counts,
                has_measurements=has_measurements
            )
            
            # Create and return the result object
            return ConversionResult(
                qasm_code='\n'.join(qasm_lines),
                stats=stats
            )
            
        except Exception as e:
            raise ValueError(f"Failed to convert PennyLane code to OpenQASM 3.0: {str(e)}")


# Public API function for easy module usage
def convert_pennylane_to_qasm3(pennylane_code: str) -> ConversionResult:
    """
    Convert PennyLane quantum circuit code to OpenQASM 3.0 format with statistics.
    
    Args:
        pennylane_code (str): Complete PennyLane circuit code as a string
        
    Returns:
        ConversionResult: Object containing QASM code and conversion statistics
        
    Raises:
        ValueError: If the input code cannot be parsed or contains unsupported operations
    """
    converter = PennyLaneToQASM3Converter()
    return converter.convert(pennylane_code)