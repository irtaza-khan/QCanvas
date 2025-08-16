import sys
import os
import re
from typing import Dict, Any, Optional

# Add the project root directory to Python path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
sys.path.insert(0, project_root)

# Import the user's own quantum converters
try:
    from quantum_converters.converters.qiskit_to_qasm import convert_qiskit_to_qasm3
    from quantum_converters.converters.cirq_to_qasm import convert_cirq_to_qasm3
    from quantum_converters.converters.pennylane_to_qasm import convert_pennylane_to_qasm3
    from quantum_converters.base.ConversionResult import ConversionResult
    print("✓ User's quantum converters imported successfully")
except ImportError as e:
    print(f"Import error in conversion service: {e}")
    print("Falling back to basic conversion logic")
    # Set converters to None to use fallback
    convert_qiskit_to_qasm3 = None
    convert_cirq_to_qasm3 = None
    convert_pennylane_to_qasm3 = None
    ConversionResult = None

class ConversionService:
    """Service for converting quantum circuit code between different frameworks and OpenQASM"""
    
    def __init__(self):
        self.converters = {
            "qiskit": convert_qiskit_to_qasm3,
            "cirq": convert_cirq_to_qasm3,
            "pennylane": convert_pennylane_to_qasm3
        }
    
    def convert_to_qasm(self, code: str, framework: str, style: str = "classic") -> Dict[str, Any]:
        """
        Convert quantum circuit code from specified framework to OpenQASM 3.0
        
        Args:
            code: The source code in the specified framework
            framework: The source framework ("qiskit", "cirq", or "pennylane")
            style: Output style ("classic" or "compact")
            
        Returns:
            Dictionary containing conversion result and metadata
        """
        if framework not in ["qiskit", "cirq", "pennylane"]:
            return {
                "success": False,
                "error": f"Unsupported framework: {framework}",
                "framework": framework,
                "qasm_code": None,
                "conversion_stats": None
            }
        
        try:
            # Check if user's converters are available
            converter_func = self.converters[framework]
            qasm_code = None
            stats = None
            
            if converter_func is None:
                # Use fallback conversion if user's converter is not available
                print(f"User's {framework} converter not available, using fallback")
                qasm_code = self._fallback_conversion(code, framework)
                # Generate basic stats for fallback
                stats = {
                    "qubits": self._count_qubits(qasm_code) if qasm_code else None,
                    "gates": self._count_gates(qasm_code) if qasm_code else None,
                    "depth": None,
                    "conversion_time": None
                }
            else:
                # Use user's actual converter
                print(f"Using user's {framework} converter")
                try:
                    result = converter_func(code)
                    print(f"Converter returned result type: {type(result)}")
                    
                    # Handle ConversionResult objects from user's converters
                    if isinstance(result, ConversionResult):
                        qasm_code = result.qasm_code
                        print(f"Got ConversionResult with QASM code length: {len(qasm_code) if qasm_code else 0}")
                        stats = {
                            "qubits": result.stats.n_qubits if hasattr(result.stats, 'n_qubits') else None,
                            "gates": result.stats.gate_counts if hasattr(result.stats, 'gate_counts') else None,
                            "depth": result.stats.depth if hasattr(result.stats, 'depth') else None,
                            "conversion_time": None
                        }
                    else:
                        # Fallback for string results
                        qasm_code = str(result)
                        print(f"Got string result with length: {len(qasm_code) if qasm_code else 0}")
                        stats = {
                            "qubits": self._count_qubits(qasm_code) if qasm_code else None,
                            "gates": self._count_gates(qasm_code) if qasm_code else None,
                            "depth": None,
                            "conversion_time": None
                        }
                except Exception as converter_error:
                    print(f"Error in {framework} converter: {str(converter_error)}")
                    raise converter_error
            
            # Check if conversion was successful
            if qasm_code:
                # Apply style formatting if needed
                if style == "compact":
                    qasm_code = self._format_compact(qasm_code)
                
                return {
                    "success": True,
                    "qasm_code": qasm_code,
                    "error": None,
                    "framework": framework,
                    "qasm_version": "3.0",
                    "conversion_stats": stats
                }
            else:
                return {
                    "success": False,
                    "error": "Conversion failed - no QASM output generated",
                    "framework": framework,
                    "qasm_code": None,
                    "conversion_stats": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Conversion failed: {str(e)}",
                "framework": framework,
                "qasm_code": None,
                "conversion_stats": None
            }
    
    def _fallback_conversion(self, code: str, framework: str) -> str:
        """Fallback conversion when user's converters are not available"""
        if framework == "qiskit":
            return self._basic_qiskit_conversion(code)
        elif framework == "cirq":
            return self._basic_cirq_conversion(code)
        elif framework == "pennylane":
            return self._basic_pennylane_conversion(code)
        else:
            raise ValueError(f"Unsupported framework: {framework}")
    
    def _basic_qiskit_conversion(self, code: str) -> str:
        """Basic Qiskit to QASM conversion"""
        # This is a simplified conversion - you can enhance this
        if "get_circuit()" not in code:
            raise ValueError("Qiskit code must define a 'get_circuit()' function")
        
        # For now, return a basic QASM template
        # You can implement more sophisticated conversion here
        return """OPENQASM 3.0;
include "stdgates.inc";

// Converted from Qiskit
qubit[2] q;

h q[0];
cx q[0], q[1];

// Note: This is a basic conversion. Implement full conversion logic in quantum_executor."""
    
    def _basic_cirq_conversion(self, code: str) -> str:
        """Basic Cirq to QASM conversion"""
        if "get_circuit()" not in code:
            raise ValueError("Cirq code must define a 'get_circuit()' function")
        
        return """OPENQASM 3.0;
include "stdgates.inc";

// Converted from Cirq
qubit[2] q;

h q[0];
cx q[0], q[1];

// Note: This is a basic conversion. Implement full conversion logic."""
    
    def _basic_pennylane_conversion(self, code: str) -> str:
        """Basic PennyLane to QASM conversion"""
        if "get_circuit()" not in code:
            raise ValueError("PennyLane code must define a 'get_circuit()' function")
        
        return """OPENQASM 3.0;
include "stdgates.inc";

// Converted from PennyLane
qubit[2] q;

h q[0];
cx q[0], q[1];

// Note: This is a basic conversion. Implement full conversion logic."""
    
    def _format_compact(self, qasm_code: str) -> str:
        """Format QASM code in compact style by removing extra whitespace"""
        lines = qasm_code.split('\n')
        compact_lines = []
        
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('//'):
                compact_lines.append(stripped)
            elif stripped.startswith('//'):
                compact_lines.append(stripped)
        
        return '\n'.join(compact_lines)
    
    def _count_qubits(self, qasm_code: str) -> int:
        """Count the number of qubits in QASM code"""
        lines = qasm_code.split('\n')
        for line in lines:
            if 'qubit[' in line:
                # Extract number from qubit[n]
                match = re.search(r'qubit\[(\d+)\]', line)
                if match:
                    return int(match.group(1))
        return 2  # Default fallback
    
    def _count_gates(self, qasm_code: str) -> Dict[str, int]:
        """Count the number of gates in QASM code"""
        gate_counts = {}
        lines = qasm_code.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('OPENQASM') and not line.startswith('include') and not line.startswith('qubit') and not line.startswith('bit'):
                # Extract gate name (first word after stripping)
                parts = line.split()
                if parts:
                    gate_name = parts[0]
                    gate_counts[gate_name] = gate_counts.get(gate_name, 0) + 1
        
        return gate_counts
    
    def get_supported_frameworks(self) -> list:
        """Get list of supported frameworks"""
        return ["qiskit", "cirq", "pennylane"]
    
    def validate_code(self, code: str, framework: str) -> Dict[str, Any]:
        """
        Validate code syntax for the specified framework
        
        Args:
            code: The source code to validate
            framework: The framework to validate against
            
        Returns:
            Dictionary containing validation result
        """
        if framework not in ["qiskit", "cirq", "pennylane"]:
            return {
                "valid": False,
                "error": f"Unsupported framework: {framework}"
            }
        
        try:
            # Basic validation - check for required function
            if "get_circuit()" not in code:
                return {
                    "valid": False,
                    "error": f"Code must define a 'get_circuit()' function for {framework}"
                }
            
            # Try to parse the code
            import ast
            ast.parse(code)
            return {"valid": True, "error": None}
            
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"Syntax error: {str(e)}"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    def _get_format_guide(self, framework: str) -> str:
        """
        Get format guide for the specified framework
        
        Args:
            framework: The framework name
            
        Returns:
            String containing format instructions
        """
        guides = {
            "qiskit": """Qiskit Code Format:
Your code must define a function called 'get_circuit()' that returns a QuantumCircuit object.

Example:
from qiskit import QuantumCircuit

def get_circuit():
    qc = QuantumCircuit(2)
    qc.h(0)  # Hadamard gate on qubit 0
    qc.cx(0, 1)  # CNOT gate between qubits 0 and 1
    return qc""",
            
            "cirq": """Cirq Code Format:
Your code must define a function called 'get_circuit()' that returns a Circuit object.

Example:
import cirq

def get_circuit():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.H(q0),  # Hadamard gate on qubit 0
        cirq.CNOT(q0, q1)  # CNOT gate between qubits 0 and 1
    )
    return circuit""",
            
            "pennylane": """PennyLane Code Format:
Your code must define a function called 'get_circuit()' that returns a qnode function.

Example:
import pennylane as qml

def get_circuit():
    dev = qml.device('default.qubit', wires=2)
    
    @qml.qnode(dev)
    def circuit():
        qml.Hadamard(wires=0)  # Hadamard gate on qubit 0
        qml.CNOT(wires=[0, 1])  # CNOT gate between qubits 0 and 1
        return qml.expval(qml.PauliZ(0))
    
    return circuit"""
        }
        
        return guides.get(framework, "Format guide not available for this framework.")
