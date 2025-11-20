import sys
import os
from typing import Dict, Any, Optional, List

# Add the project root directory to Python path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
sys.path.insert(0, project_root)

# Import QSim for quantum simulation
try:
    from qsim import run_qasm, RunArgs, SimResult
    print("✓ QSim imported successfully")
    QSIM_AVAILABLE = True
except ImportError as e:
    print(f"Import error in simulation service: {e}")
    print("QSim simulation features may not be fully available")
    run_qasm = None
    RunArgs = None
    SimResult = None
    QSIM_AVAILABLE = False

class SimulationService:
    """Service for executing quantum simulations using QSim"""
    
    def __init__(self):
        self.available_backends = ['cirq', 'qiskit', 'pennylane']
        self.legacy_backends = ["statevector", "density_matrix"]
    
    def execute_qasm(self, qasm_code: str, backend: str = "statevector", shots: int = 1024) -> Dict[str, Any]:
        """
        Execute OpenQASM code using the specified backend (legacy method)
        
        Args:
            qasm_code: OpenQASM 3.0 code to execute
            backend: Backend to use for simulation
            shots: Number of measurement shots
            
        Returns:
            Dictionary containing simulation results
        """
        try:
            # Validate backend
            if backend not in self.legacy_backends:
                return {
                    "success": False,
                    "error": f"Unsupported backend: {backend}. Available: {self.legacy_backends}"
                }
            
            # For now, return a basic simulation result
            if backend == "statevector":
                result = self._simulate_statevector(qasm_code, shots)
            elif backend == "density_matrix":
                result = self._simulate_density_matrix(qasm_code, shots)
            else:
                return {
                    "success": False,
                    "error": f"Backend {backend} not implemented yet"
                }
            
            return {
                "success": True,
                "results": result,
                "backend": backend,
                "shots": shots,
                "qasm_code": qasm_code
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Simulation failed: {str(e)}"
            }
    
    def execute_qasm_with_qsim(self, qasm_code: str, backend: str = "cirq", shots: int = 1024) -> Dict[str, Any]:
        """
        Execute OpenQASM code using QSim
        
        Args:
            qasm_code: OpenQASM 3.0 code to execute
            backend: QSim backend to use (cirq, qiskit, or pennylane)
            shots: Number of measurement shots
            
        Returns:
            Dictionary containing simulation results from QSim
        """
        try:
            if not QSIM_AVAILABLE:
                return {
                    "success": False,
                    "error": "QSim is not available. Please ensure it is installed correctly."
                }
            
            # Validate backend
            if backend not in self.available_backends:
                return {
                    "success": False,
                    "error": f"Unsupported QSim backend: {backend}. Available: {self.available_backends}"
                }
            
            # Create RunArgs for QSim
            args = RunArgs(
                qasm_input=qasm_code,
                backend=backend,
                shots=shots
            )
            
            # Execute with QSim
            sim_result: SimResult = run_qasm(args)
            
            # Convert SimResult to dictionary format
            result_dict = {
                "counts": sim_result.counts,
                "metadata": sim_result.metadata,
                "probs": sim_result.probs,
                # Note: circuit object might not be JSON serializable, so we omit it or convert to string
            }
            
            return {
                "success": True,
                "results": result_dict,
                "backend": backend,
                "shots": shots
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"QSim simulation failed: {str(e)}"
            }
    
    def _simulate_statevector(self, qasm_code: str, shots: int) -> Dict[str, Any]:
        """Simulate using statevector backend"""
        # Parse QASM to determine number of qubits
        num_qubits = self._extract_qubit_count(qasm_code)
        
        # Basic Bell state simulation result (placeholder)
        if "h q[0]" in qasm_code and "cx q[0], q[1]" in qasm_code:
            # Bell state preparation
            return {
                "statevector": [0.7071, 0, 0, 0.7071],  # |00⟩ + |11⟩
                "probabilities": {"00": 0.5, "11": 0.5},
                "counts": {"00": shots//2, "11": shots//2},
                "num_qubits": num_qubits
            }
        else:
            # Default to |0...0⟩ state
            statevector = [1.0] + [0.0] * (2**num_qubits - 1)
            counts = {"0" * num_qubits: shots}
            return {
                "statevector": statevector,
                "counts": counts,
                "num_qubits": num_qubits
            }
    
    def _simulate_density_matrix(self, qasm_code: str, shots: int) -> Dict[str, Any]:
        """Simulate using density matrix backend"""
        num_qubits = self._extract_qubit_count(qasm_code)
        
        # Basic simulation result (placeholder)
        return {
            "density_matrix": "Complex density matrix representation",
            "counts": {"0" * num_qubits: shots},
            "num_qubits": num_qubits
        }
    
    def _extract_qubit_count(self, qasm_code: str) -> int:
        """Extract number of qubits from QASM code"""
        lines = qasm_code.split('\n')
        for line in lines:
            if 'qubit[' in line:
                # Extract number from qubit[n]
                import re
                match = re.search(r'qubit\[(\d+)\]', line)
                if match:
                    return int(match.group(1))
        return 2  # Default fallback
    
    def get_available_backends(self) -> List[str]:
        """Get list of available simulation backends (QSim backends)"""
        return self.available_backends
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of simulation service"""
        try:
            # Test basic functionality
            backends = self.get_available_backends()
            return {
                "status": "healthy",
                "available_backends": backends,
                "qsim_available": QSIM_AVAILABLE
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }
