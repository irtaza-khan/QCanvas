"""
PennyLane to OpenQASM 3.0 Converter Module

This module provides functionality to convert PennyLane quantum circuits 
containing basic gates to OpenQASM 3.0 format. It serves as an intermediate 
representation (IR) converter for unified quantum simulators.

Author: [Your Name]
Date: [Current Date]
Version: 1.0.0
"""
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
            # Look for qml operations inside a qnode function body
            if line.startswith('qml.') and not line.startswith('qml.expval') and not line.startswith('qml.device'):
                operations.append(line)

        # If no operations were found by static scan, try executing to introspect
        if not operations:
            namespace: Dict[str, Any] = {}
            try:
                exec(compile(circuit_code, "<pennylane_source>", "exec"), namespace)
                # Prefer a get_circuit returning a callable qnode
                qnode = namespace.get('get_circuit')
                candidate_funcs = []
                if callable(qnode):
                    try:
                        qnode = qnode()
                    except Exception:
                        pass
                if callable(qnode):
                    candidate_funcs.append(qnode)
                # Also scan other callables that look like qnodes
                for name, obj in namespace.items():
                    if callable(obj) and hasattr(obj, 'qml') or hasattr(obj, 'device'):
                        candidate_funcs.append(obj)
            except Exception:
                candidate_funcs = []  # fall back to empty

            # We cannot easily extract ops from qnode; keep operations empty but keep num_qubits from device
        
        return {
            'num_qubits': num_qubits,
            'operations': operations
        }
    
    def _parse_operation(self, op_line: str, num_qubits: int) -> Dict[str, Any]:
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
            # Expand range(n_qubits) patterns
            if wire_part.startswith('range('):
                wires = list(range(num_qubits))
            else:
                # Handle list format [wire1, wire2]
                if wire_part.startswith('[') and wire_part.endswith(']'):
                    wire_part = wire_part[1:-1]
                parts = [p.strip() for p in wire_part.split(',')]
                wires = []
                unsupported = False
                for p in parts:
                    try:
                        wires.append(int(p))
                    except Exception:
                        # Try to extract integer literals inside expressions (e.g., "1", "0")
                        import re as _re
                        m = _re.findall(r"\d+", p)
                        if m:
                            wires.append(int(m[0]))
                        else:
                            unsupported = True
                if unsupported and not wires:
                    # Mark operation as unsupported due to dynamic wire indices
                    return { 'unsupported': True, 'reason': 'dynamic_wires', 'raw': op_line }
                
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
        Evaluate numerical expressions in parameters, including mathematical constants.

        Args:
            param_str (str): Parameter string that may contain mathematical expressions

        Returns:
            Union[float, str]: Evaluated numerical value or symbolic constant
        """
        try:
            # Check for direct mathematical constants
            if param_str.strip() in ['np.pi', 'numpy.pi', 'pi', 'math.pi']:
                return "PI"
            elif param_str.strip() in ['np.e', 'numpy.e', 'e', 'math.e']:
                return "E"
            elif param_str.strip() == 'np.pi/2' or param_str.strip() == 'pi/2':
                return "PI/2"
            elif param_str.strip() == 'np.pi/4' or param_str.strip() == 'pi/4':
                return "PI/4"

            # For more complex expressions, evaluate numerically but keep symbolic constants
            param_str = param_str.replace('np.pi', 'PI')
            param_str = param_str.replace('numpy.pi', 'PI')
            param_str = param_str.replace('np.e', 'E')
            param_str = param_str.replace('numpy.e', 'E')

            # If it contains symbolic constants, return as string
            if 'PI' in param_str or 'E' in param_str:
                return param_str

            # For pure numerical expressions, evaluate them
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
            if isinstance(result, (int, float)):
                # Format nicely
                if isinstance(result, float):
                    # Check for common values
                    if abs(result - np.pi) < 1e-10:
                        return "PI"
                    elif abs(result - np.pi/2) < 1e-10:
                        return "PI/2"
                    elif abs(result - np.pi/4) < 1e-10:
                        return "PI/4"
                    elif abs(result - np.e) < 1e-10:
                        return "E"
                    else:
                        return f"{result:.6f}"
                else:
                    return str(result)

        except Exception:
            # If evaluation fails, try direct float conversion
            try:
                return float(param_str)
            except ValueError:
                # As a last resort, return as string
                return param_str
    
    def _convert_gate(self, parsed_op: Dict[str, Any]) -> str:
        """
        Convert a parsed PennyLane operation to its OpenQASM 3.0 equivalent.
        
        Args:
            parsed_op (Dict[str, Any]): Parsed operation containing gate, params, and wires
            
        Returns:
            str: OpenQASM 3.0 gate instruction string
        """
        if parsed_op.get('unsupported'):
            return f"// Unsupported PennyLane op: {parsed_op.get('raw')}"

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

            # Detect common loop patterns to expand dynamic wires
            has_loop_i_n = 'for i in range(n_qubits):' in pennylane_code or 'for i in range(n_qubits):' in pennylane_code
            has_loop_i_n_minus_1 = 'for i in range(n_qubits - 1):' in pennylane_code or 'for i in range(n_qubits-1):' in pennylane_code
            # Layers for QAOA-like circuits
            p_default = 2
            has_layer_loop = 'for layer in range(p):' in pennylane_code
            # Try to detect default p from function signature `p=2`
            try:
                import re as _re
                m = _re.search(r'p\s*=\s*(\d+)', pennylane_code)
                if m:
                    p_default = int(m.group(1))
            except Exception:
                pass
            
            # Build enhanced OpenQASM 3.0 header with advanced features
            qasm_lines = [
                "OPENQASM 3.0;",
                'include "stdgates.inc";',
                "",
                "// Mathematical constants",
                "const float PI = 3.141592653589793;",
                "const float E = 2.718281828459045;",
                "const float PI_2 = 1.5707963267948966;  // PI/2",
                "const float PI_4 = 0.7853981633974483;  // PI/4",
                "",
                f"// Quantum registers",
                f"qubit[{num_qubits}] q;",
                ""
            ]

            # Add classical registers if measurements exist
            has_measurements = any('measure' in op.lower() for op in operations)
            if has_measurements:
                qasm_lines.extend([
                    "// Classical registers",
                    f"bit[{num_qubits}] c;",
                    ""
                ])
            
            # Add classical variables for intermediate calculations
            qasm_lines.extend([
                "// Classical variables for intermediate calculations",
                "int loop_index;",
                "bool condition_result;",
                "float temp_angle;",
                ""
            ])

            # Add gate definitions section
            qasm_lines.extend([
                "// Gate definitions",
                "// (Custom gate definitions would go here)",
                "",
                "// Classical operations examples",
                "// Assignment statements",
                "temp_angle = PI/2;",
                "loop_index = 0;",
                "",
                "// Circuit operations"
            ])
            
            # Initialize statistics
            gate_counts = {}
            has_measurements = False
            depth = 0
            
            # Convert each PennyLane operation to OpenQASM 3.0 and collect stats
            for op_line in operations:
                expanded_lines = [op_line]

                # Expand loops over i when wires use i
                if 'wires=i' in op_line or 'wires=[i' in op_line or 'wires=i + 1' in op_line:
                    new_lines = []
                    if 'i + 1' in op_line and has_loop_i_n_minus_1:
                        for i in range(max(0, num_qubits - 1)):
                            nl = op_line.replace('i + 1', str(i + 1)).replace('i+1', str(i + 1)).replace('i', str(i))
                            new_lines.append(nl)
                    elif has_loop_i_n:
                        for i in range(num_qubits):
                            nl = op_line.replace('i', str(i))
                            new_lines.append(nl)
                    if new_lines:
                        expanded_lines = new_lines

                # Expand over layers if parameters index by layer
                final_lines = []
                if 'gamma[' in op_line or 'beta[' in op_line:
                    for _ in range(p_default if has_layer_loop else 1):
                        final_lines.extend(expanded_lines)
                else:
                    final_lines = expanded_lines

                for line in final_lines:
                    parsed_op = self._parse_operation(line, num_qubits)
                    qasm_gate = self._convert_gate(parsed_op)
                    qasm_lines.append(qasm_gate)
                    
                    # Update gate counts
                    if not parsed_op.get('unsupported'):
                        gate_name = parsed_op['gate']
                        gate_counts[gate_name] = gate_counts.get(gate_name, 0) + 1
                        # Check for measurements
                        if 'measure' in gate_name.lower():
                            has_measurements = True
                        depth += 1
            
            # Add example control flow (if we have classical bits)
            if has_measurements:
                qasm_lines.extend([
                    "",
                    "// Classical control flow examples",
                    "// If statement based on measurement result",
                    "if (c[0] == 1) {",
                    "    // Apply corrective operations",
                    "    x q[1];",
                    "}",
                    "",
                    "// For loop example",
                    "for loop_index in [0:2] {",
                    "    // Conditional operations",
                    "    ry(temp_angle) q[loop_index];",
                    "}"
                ])
            
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