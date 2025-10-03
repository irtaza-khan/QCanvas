import sys
import os
import re
from typing import Dict, Any, Optional

# Add the project root directory to Python path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
sys.path.insert(0, project_root)

# Import the user's own quantum converters (independently per framework)
convert_qiskit_to_qasm3 = None
convert_cirq_to_qasm3 = None
convert_pennylane_to_qasm3 = None
ConversionResult = None

try:
    from quantum_converters.base.ConversionResult import ConversionResult
except ImportError as e:
    print(f"Import error: ConversionResult unavailable: {e}")

try:
    from quantum_converters.converters.qiskit_to_qasm_new import convert_qiskit_to_qasm3 as _qiskit_convert
    convert_qiskit_to_qasm3 = _qiskit_convert
    print("✓ Qiskit converter available")
except ImportError as e:
    print(f"Qiskit converter import error: {e}")

# Removed exec-based cirq_to_qasm import to disable fallback
try:
    from quantum_converters.converters.cirq_to_qasm_new import convert_cirq_to_qasm3 as _cirq_convert
    convert_cirq_to_qasm3 = _cirq_convert
    print("✓ Cirq converter available (AST-based only)")
except ImportError as e:
    print(f"Cirq converter import error: {e}")

try:
    from quantum_converters.converters.pennylane_to_qasm import convert_pennylane_to_qasm3 as _pl_convert
    convert_pennylane_to_qasm3 = _pl_convert
    print("✓ PennyLane converter available")
except ImportError as e:
    print(f"PennyLane converter import error: {e}")

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
            converter_func = self.converters.get(framework)
            qasm_code = None
            stats = None
            
            if converter_func is None:
                # No fallback conversion, return error directly
                return {
                    "success": False,
                    "error": f"No converter available for framework: {framework}",
                    "framework": framework,
                    "qasm_code": None,
                    "conversion_stats": None
                }
            else:
                # Use user's actual converter
                print(f"Using user's {framework} converter")
                try:
                    result = converter_func(code)
                    print(f"Converter returned result type: {type(result)}")
                    
                    # Handle ConversionResult objects from user's converters
                    if ConversionResult is not None and isinstance(result, ConversionResult):
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
                    # No fallback conversion, return error
                    return {
                        "success": False,
                        "error": f"Conversion error: {str(converter_error)}",
                        "framework": framework,
                        "qasm_code": None,
                        "conversion_stats": None
                    }
            
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
        """Fallback conversion removed for Cirq as per user request"""
        if framework == "qiskit":
            return self._basic_qiskit_conversion(code)
        elif framework == "pennylane":
            return self._basic_pennylane_conversion(code)
        else:
            raise ValueError(f"Unsupported framework or fallback removed: {framework}")
    
    def _basic_qiskit_conversion(self, code: str) -> str:
        """Heuristic Qiskit-to-QASM conversion without importing qiskit."""
        import re
        import math

        def eval_param(expr: str) -> str:
            try:
                expr = expr.replace('np.pi', str(math.pi)).replace('numpy.pi', str(math.pi)).replace('pi', str(math.pi))
                return str(float(eval(expr, {"__builtins__": {}}, {})))
            except Exception:
                return expr

        # Determine qubit count
        num_qubits = 2
        m = re.search(r"QuantumRegister\((\d+)", code)
        if m:
            num_qubits = int(m.group(1))
        else:
            m2 = re.search(r"QuantumCircuit\((\d+)", code)
            if m2:
                num_qubits = int(m2.group(1))
            else:
                m3 = re.search(r"create_\w+\((\d+)\)", code)
                if m3:
                    num_qubits = int(m3.group(1))

        qasm_lines = [
            "OPENQASM 3.0;",
            "include \"stdgates.inc\";",
            "",
            f"qubit[{num_qubits}] q;",
            ""
        ]

        # Map simple one- and two-qubit gates
        for line in code.splitlines():
            s = line.strip().replace(' ', '')
            if s.startswith('qc.h('):
                m = re.search(r"qc\.h\((\d+)\)", s)
                if m: qasm_lines.append(f"h q[{int(m.group(1))}];")
            elif s.startswith('qc.x('):
                m = re.search(r"qc\.x\((\d+)\)", s)
                if m: qasm_lines.append(f"x q[{int(m.group(1))}];")
            elif s.startswith('qc.y('):
                m = re.search(r"qc\.y\((\d+)\)", s)
                if m: qasm_lines.append(f"y q[{int(m.group(1))}];")
            elif s.startswith('qc.z('):
                m = re.search(r"qc\.z\((\d+)\)", s)
                if m: qasm_lines.append(f"z q[{int(m.group(1))}];")
            elif s.startswith('qc.s('):
                m = re.search(r"qc\.s\((\d+)\)", s)
                if m: qasm_lines.append(f"s q[{int(m.group(1))}];")
            elif s.startswith('qc.t('):
                m = re.search(r"qc\.t\((\d+)\)", s)
                if m: qasm_lines.append(f"t q[{int(m.group(1))}];")
            elif s.startswith('qc.rx('):
                m = re.search(r"qc\.rx\(([^,]+),(\d+)\)", s)
                if m: qasm_lines.append(f"rx({eval_param(m.group(1))}) q[{int(m.group(2))}];")
            elif s.startswith('qc.ry('):
                m = re.search(r"qc\.ry\(([^,]+),(\d+)\)", s)
                if m: qasm_lines.append(f"ry({eval_param(m.group(1))}) q[{int(m.group(2))}];")
            elif s.startswith('qc.rz('):
                m = re.search(r"qc\.rz\(([^,]+),(\d+)\)", s)
                if m: qasm_lines.append(f"rz({eval_param(m.group(1))}) q[{int(m.group(2))}];")
            elif s.startswith('qc.p(') or s.startswith('qc.u1('):
                m = re.search(r"qc\.(?:p|u1)\(([^,]+),(\d+)\)", s)
                if m: qasm_lines.append(f"p({eval_param(m.group(1))}) q[{int(m.group(2))}];")
            elif s.startswith('qc.cx('):
                m = re.search(r"qc\.cx\((\d+),(\d+)\)", s)
                if m: qasm_lines.append(f"cx q[{int(m.group(1))}], q[{int(m.group(2))}];")
            elif s.startswith('qc.cz('):
                m = re.search(r"qc\.cz\((\d+),(\d+)\)", s)
                if m: qasm_lines.append(f"cz q[{int(m.group(1))}], q[{int(m.group(2))}];")
            elif s.startswith('qc.swap('):
                m = re.search(r"qc\.swap\((\d+),(\d+)\)", s)
                if m: qasm_lines.append(f"swap q[{int(m.group(1))}], q[{int(m.group(2))}];")
            elif s.startswith('qc.cp('):
                m = re.search(r"qc\.cp\(([^,]+),(\d+),(\d+)\)", s)
                if m: qasm_lines.append(f"cp({eval_param(m.group(1))}) q[{int(m.group(2))}], q[{int(m.group(3))}];")
            elif s.startswith('qc.measure'):
                # Skip explicit measurement for heuristic QASM
                continue
        return '\n'.join(qasm_lines)
    
    def _basic_cirq_conversion(self, code: str) -> str:
        """Heuristic Cirq-to-QASM conversion without importing cirq."""
        import re
        # Detect qubit mapping from `q0, q1, ... = cirq.LineQubit.range(N)`
        num_qubits = 2
        name_to_idx = {}
        m = re.search(r"([a-zA-Z_]\w*(?:\s*,\s*[a-zA-Z_]\w*)+)\s*=\s*cirq\.LineQubit\.range\((\d+)\)", code)
        if m:
            names = [n.strip() for n in m.group(1).split(',')]
            num_qubits = int(m.group(2))
            for i, nm in enumerate(names):
                name_to_idx[nm] = i
        else:
            m2 = re.search(r"LineQubit\.range\((\d+)\)", code)
            if m2:
                num_qubits = int(m2.group(1))

        qasm_lines = [
            "OPENQASM 3.0;",
            "include \"stdgates.inc\";",
            "",
            f"qubit[{num_qubits}] q;",
            ""
        ]

        def qidx(token: str) -> int:
            token = token.strip()
            if token in name_to_idx:
                return name_to_idx[token]
            m = re.search(r"\[(\d+)\]", token)
            if m:
                return int(m.group(1))
            # Fallback, try qN naming like q0
            m2 = re.search(r"(\d+)$", token)
            return int(m2.group(1)) if m2 else 0

        for raw in code.splitlines():
            s = raw.strip().replace(' ', '')
            # One-qubit gates
            m = re.search(r"cirq\.H\(([^\)]+)\)" , s)
            if m:
                qasm_lines.append(f"h q[{qidx(m.group(1))}];"); continue
            m = re.search(r"cirq\.X\(([^\)]+)\)" , s)
            if m:
                qasm_lines.append(f"x q[{qidx(m.group(1))}];"); continue
            m = re.search(r"cirq\.Y\(([^\)]+)\)" , s)
            if m:
                qasm_lines.append(f"y q[{qidx(m.group(1))}];"); continue
            m = re.search(r"cirq\.Z\(([^\)]+)\)" , s)
            if m:
                qasm_lines.append(f"z q[{qidx(m.group(1))}];"); continue
            # Two-qubit gates
            m = re.search(r"cirq\.CNOT\(([^,]+),([^\)]+)\)" , s)
            if m:
                qasm_lines.append(f"cx q[{qidx(m.group(1))}], q[{qidx(m.group(2))}];"); continue
            m = re.search(r"cirq\.CZ\(([^,]+),([^\)]+)\)" , s)
            if m:
                qasm_lines.append(f"cz q[{qidx(m.group(1))}], q[{qidx(m.group(2))}];"); continue
            m = re.search(r"cirq\.SWAP\(([^,]+),([^\)]+)\)" , s)
            if m:
                qasm_lines.append(f"swap q[{qidx(m.group(1))}], q[{qidx(m.group(2))}];"); continue
            # Ignore measurements and others in heuristic mode
        return '\n'.join(qasm_lines)
    
    def _basic_pennylane_conversion(self, code: str) -> str:
        """Basic PennyLane to QASM conversion"""
        return """OPENQASM 3.0;
include "stdgates.inc";

// Converted from PennyLane (basic fallback)
qubit[2] q;

h q[0];
cx q[0], q[1];
"""
    
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
            # Heuristic validation: accept common patterns for each framework
            fw = framework.lower()
            is_valid = False
            if fw == "qiskit":
                is_valid = ("from qiskit" in code) or ("import qiskit" in code) or ("QuantumCircuit(" in code)
            elif fw == "cirq":
                is_valid = ("import cirq" in code) or ("cirq.Circuit(" in code)
            elif fw == "pennylane":
                is_valid = ("import pennylane" in code) or ("qml.device(" in code) or ("qml." in code)

            if not is_valid:
                return {
                    "valid": False,
                    "error": f"Provided code does not look like {framework} code. Include the proper imports or circuit creation."
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
