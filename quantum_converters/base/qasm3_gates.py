"""
OpenQASM 3.0 Gate Library - Complete Implementation

Comprehensive gate definitions and modifiers for OpenQASM 3.0 Iteration I.

Features:
- All standard gates from stdgates.inc
- Gate modifiers (ctrl@, inv@)
- Hierarchical gate definitions
- Gate broadcasting support

Author: QCanvas Team
Date: 2025-09-30
Version: 1.0.0
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class GateModifier:
    """Represents gate modifiers in OpenQASM 3.0"""
    inverse: bool = False
    ctrl_qubits: Optional[int] = None  # Number of control qubits
    power: Optional[float] = None  # Power modifier
    
    def to_string(self) -> str:
        """Convert modifiers to QASM string."""
        parts = []
        
        if self.inverse:
            parts.append("inv")
            
        if self.ctrl_qubits is not None:
            if self.ctrl_qubits == 1:
                parts.append("ctrl")
            else:
                parts.append(f"ctrl({self.ctrl_qubits})")
                
        if self.power is not None:
            parts.append(f"pow({self.power})")
            
        if parts:
            return " @ ".join(parts) + " @ "
        return ""


class QASM3GateLibrary:
    """
    Complete gate library for OpenQASM 3.0 with Iteration I features.
    
    Provides:
    - Standard gate definitions
    - Gate parameter formatting
    - Gate modifier application
    - Custom gate management
    """
    
    # Standard single-qubit gates (no parameters)
    STANDARD_SINGLE_GATES = {
        'h': 'Hadamard',
        'x': 'Pauli-X (NOT)',
        'y': 'Pauli-Y',
        'z': 'Pauli-Z',
        's': 'S gate (sqrt(Z))',
        'sdg': 'S dagger (inverse S)',
        't': 'T gate (sqrt(S))',
        'tdg': 'T dagger (inverse T)',
        'sx': 'sqrt(X)',
        'sxdg': 'inverse sqrt(X)',
        'id': 'Identity',
    }
    
    # Standard parameterized single-qubit gates
    STANDARD_PARAM_SINGLE_GATES = {
        'rx': ('theta',),  # Rotation about X-axis
        'ry': ('theta',),  # Rotation about Y-axis
        'rz': ('lambda',),  # Rotation about Z-axis
        'p': ('lambda',),  # Phase gate
        'u': ('theta', 'phi', 'lambda'),  # Generic single-qubit unitary
        'u1': ('lambda',),  # U1 gate
        'u2': ('phi', 'lambda'),  # U2 gate
        'u3': ('theta', 'phi', 'lambda'),  # U3 gate
    }
    
    # Standard two-qubit gates
    STANDARD_TWO_QUBIT_GATES = {
        'cx': 'Controlled-X (CNOT)',
        'cy': 'Controlled-Y',
        'cz': 'Controlled-Z',
        'ch': 'Controlled-Hadamard',
        'swap': 'SWAP',
    }
    
    # Standard parameterized two-qubit gates
    STANDARD_PARAM_TWO_QUBIT_GATES = {
        'crx': ('theta',),
        'cry': ('theta',),
        'crz': ('lambda',),
        'cp': ('lambda',),  # Controlled-phase
        'cu': ('theta', 'phi', 'lambda', 'gamma'),
    }
    
    # Standard three-qubit gates
    STANDARD_THREE_QUBIT_GATES = {
        'ccx': 'Toffoli (Controlled-Controlled-X)',
        'cswap': 'Fredkin (Controlled-SWAP)',
        'ccz': 'Controlled-Controlled-Z',
    }
    
    # Special gates
    SPECIAL_GATES = {
        'gphase': ('gamma',),  # Global phase
    }
    
    def __init__(self):
        """Initialize the gate library."""
        self.custom_gates: Dict[str, Dict[str, Any]] = {}
        
    def add_custom_gate(self, name: str, parameters: List[str], 
                       qubits: List[str], body: List[str]):
        """
        Add a custom gate definition.
        
        Args:
            name: Gate name
            parameters: List of parameter names
            qubits: List of qubit parameters
            body: Gate definition body
        """
        self.custom_gates[name] = {
            'parameters': parameters,
            'qubits': qubits,
            'body': body
        }
        
    def format_gate_application(self, gate_name: str, qubits: List[str],
                               parameters: Optional[List[Any]] = None,
                               modifiers: Optional[GateModifier] = None) -> str:
        """
        Format a complete gate application statement.
        
        Args:
            gate_name: Name of the gate
            qubits: List of qubit arguments
            parameters: Optional parameters
            modifiers: Optional gate modifiers
            
        Returns:
            Complete QASM gate application string
        """
        # Build modifier string
        mod_str = ""
        if modifiers:
            mod_str = modifiers.to_string()
            
        # Build parameter string
        param_str = ""
        if parameters:
            formatted_params = [self.format_parameter(p) for p in parameters]
            param_str = f"({', '.join(formatted_params)})"
            
        # Build qubit string
        qubit_str = ', '.join(qubits)
        
        # Complete statement
        return f"{mod_str}{gate_name}{param_str} {qubit_str};"
        
    def format_parameter(self, param: Any) -> str:
        """
        Format a gate parameter value.
        
        Args:
            param: Parameter value
            
        Returns:
            Formatted parameter string
        """
        if isinstance(param, str):
            return param
            
        if isinstance(param, (int, float)):
            # Handle numpy types
            if hasattr(param, 'item'):
                param = param.item()
                
            if isinstance(param, float):
                # Check for common constants
                if abs(param - np.pi) < 1e-10:
                    return "PI"
                elif abs(param - np.pi/2) < 1e-10:
                    return "PI_2"
                elif abs(param - np.pi/4) < 1e-10:
                    return "PI_4"
                elif abs(param - 2*np.pi) < 1e-10:
                    return "TAU"
                elif abs(param - np.e) < 1e-10:
                    return "E"
                elif abs(param - 3*np.pi/4) < 1e-10:
                    return "3*PI_4"
                elif abs(param - np.pi/3) < 1e-10:
                    return "PI/3"
                elif abs(param - np.pi/6) < 1e-10:
                    return "PI/6"
                elif abs(param) < 1e-10:
                    return "0"
                else:
                    return f"{param:.10g}"
            else:
                return str(param)
        
        return str(param)
        
    def is_standard_gate(self, gate_name: str) -> bool:
        """Check if a gate is a standard gate."""
        return (gate_name in self.STANDARD_SINGLE_GATES or
                gate_name in self.STANDARD_PARAM_SINGLE_GATES or
                gate_name in self.STANDARD_TWO_QUBIT_GATES or
                gate_name in self.STANDARD_PARAM_TWO_QUBIT_GATES or
                gate_name in self.STANDARD_THREE_QUBIT_GATES or
                gate_name in self.SPECIAL_GATES)
                
    def is_custom_gate(self, gate_name: str) -> bool:
        """Check if a gate is a custom-defined gate."""
        return gate_name in self.custom_gates
        
    def get_gate_qubit_count(self, gate_name: str) -> Optional[int]:
        """
        Get the number of qubits a gate operates on.
        
        Args:
            gate_name: Name of the gate
            
        Returns:
            Number of qubits, or None if unknown
        """
        if gate_name in self.STANDARD_SINGLE_GATES or gate_name in self.STANDARD_PARAM_SINGLE_GATES:
            return 1
        elif gate_name in self.STANDARD_TWO_QUBIT_GATES or gate_name in self.STANDARD_PARAM_TWO_QUBIT_GATES:
            return 2
        elif gate_name in self.STANDARD_THREE_QUBIT_GATES:
            return 3
        elif gate_name in self.custom_gates:
            return len(self.custom_gates[gate_name]['qubits'])
        elif gate_name == 'gphase':
            return 0  # Global phase operates on no specific qubits
        return None
        
    def get_gate_param_count(self, gate_name: str) -> Optional[int]:
        """
        Get the number of parameters a gate requires.
        
        Args:
            gate_name: Name of the gate
            
        Returns:
            Number of parameters, or None if unknown
        """
        if gate_name in self.STANDARD_PARAM_SINGLE_GATES:
            return len(self.STANDARD_PARAM_SINGLE_GATES[gate_name])
        elif gate_name in self.STANDARD_PARAM_TWO_QUBIT_GATES:
            return len(self.STANDARD_PARAM_TWO_QUBIT_GATES[gate_name])
        elif gate_name in self.SPECIAL_GATES:
            return len(self.SPECIAL_GATES[gate_name])
        elif gate_name in self.STANDARD_SINGLE_GATES or gate_name in self.STANDARD_TWO_QUBIT_GATES or gate_name in self.STANDARD_THREE_QUBIT_GATES:
            return 0
        elif gate_name in self.custom_gates:
            return len(self.custom_gates[gate_name]['parameters'])
        return None
        
    def validate_gate_application(self, gate_name: str, num_qubits: int,
                                  num_params: int) -> Tuple[bool, Optional[str]]:
        """
        Validate a gate application.
        
        Args:
            gate_name: Name of the gate
            num_qubits: Number of qubits provided
            num_params: Number of parameters provided
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        expected_qubits = self.get_gate_qubit_count(gate_name)
        expected_params = self.get_gate_param_count(gate_name)
        
        if expected_qubits is not None and num_qubits != expected_qubits:
            return False, f"Gate '{gate_name}' expects {expected_qubits} qubits, got {num_qubits}"
            
        if expected_params is not None and num_params != expected_params:
            return False, f"Gate '{gate_name}' expects {expected_params} parameters, got {num_params}"
            
        return True, None
        
    def generate_gate_definition(self, name: str, parameters: List[str],
                                qubits: List[str], body: List[str]) -> str:
        """
        Generate a gate definition block.
        
        Args:
            name: Gate name
            parameters: Parameter list
            qubits: Qubit parameter list
            body: Gate body statements
            
        Returns:
            Complete gate definition string
        """
        lines = []
        
        # Gate header
        param_str = f"({', '.join(parameters)})" if parameters else ""
        qubit_str = ', '.join(qubits)
        lines.append(f"gate {name}{param_str} {qubit_str} {{")
        
        # Gate body
        for stmt in body:
            lines.append(f"    {stmt}")
            
        lines.append("}")
        
        return '\n'.join(lines)
        
    def create_controlled_gate(self, base_gate: str, num_controls: int = 1) -> str:
        """
        Create a controlled version of a gate name.
        
        Args:
            base_gate: Base gate name
            num_controls: Number of control qubits
            
        Returns:
            Controlled gate name
        """
        if num_controls == 1:
            return f"c{base_gate}"
        else:
            prefix = "c" * num_controls
            return f"{prefix}{base_gate}"
            
    def create_inverse_gate(self, base_gate: str) -> str:
        """
        Create an inverse version of a gate name.
        
        Args:
            base_gate: Base gate name
            
        Returns:
            Inverse gate name (or modifier string)
        """
        # Some gates have standard inverse names
        if base_gate == 's':
            return 'sdg'
        elif base_gate == 't':
            return 'tdg'
        elif base_gate == 'sx':
            return 'sxdg'
        else:
            # Use modifier
            return base_gate  # Modifier will be added separately
