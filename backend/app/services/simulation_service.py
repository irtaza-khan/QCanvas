import sys
import os
import time
import psutil
from typing import Dict, Any, Optional, List
import numpy as np

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


def convert_numpy_types(obj: Any) -> Any:
    """
    Recursively convert NumPy types to native Python types for JSON serialization.
    
    Args:
        obj: Object that may contain NumPy types
        
    Returns:
        Object with NumPy types converted to native Python types
    """
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_numpy_types(item) for item in obj]
    else:
        return obj

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
            
            # Capture initial memory and CPU stats
            process = psutil.Process()
            initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
            initial_cpu = psutil.cpu_percent(interval=None)
            
            # Create RunArgs for QSim
            args = RunArgs(
                qasm_input=qasm_code,
                backend=backend,
                shots=shots
            )
            
            # Execute with QSim and measure time
            start_time = time.perf_counter()
            sim_result: SimResult = run_qasm(args)
            simulation_time = time.perf_counter() - start_time
            
            # Post-processing time measurement
            post_start = time.perf_counter()
            
            # Convert SimResult to dictionary format
            result_dict = {
                "counts": sim_result.counts,
                "metadata": sim_result.metadata,
                "probs": sim_result.probs,
                # Note: circuit object might not be JSON serializable, so we omit it or convert to string
            }
            
            # Convert NumPy types to native Python types for JSON serialization
            result_dict = convert_numpy_types(result_dict)
            
            post_processing_time = time.perf_counter() - post_start
            total_time = simulation_time + post_processing_time
            
            # Capture final memory stats
            final_memory = process.memory_info().rss / (1024 * 1024)  # MB
            memory_used = final_memory - initial_memory
            final_cpu = psutil.cpu_percent(interval=None)
            
            # Calculate successful shots from counts
            successful_shots = sum(result_dict["counts"].values()) if result_dict["counts"] else 0
            
            # Add performance metrics to metadata
            result_dict["metadata"]["execution_time"] = f"{total_time*1000:.2f}ms"
            result_dict["metadata"]["simulation_time"] = f"{simulation_time*1000:.2f}ms"
            result_dict["metadata"]["postprocessing_time"] = f"{post_processing_time*1000:.2f}ms"
            result_dict["metadata"]["memory_usage"] = f"{max(memory_used, 0.1):.2f}MB"
            result_dict["metadata"]["cpu_usage"] = f"{max(final_cpu, initial_cpu):.1f}%"
            result_dict["metadata"]["successful_shots"] = successful_shots
            result_dict["metadata"]["visitor"] = backend  # The visitor used is the backend name
            
            # Calculate fidelity estimate (for simulation, fidelity is 100% unless there are errors)
            # In a real quantum device, this would be calculated differently
            if successful_shots > 0 and shots > 0:
                result_dict["metadata"]["fidelity"] = (successful_shots / shots) * 100.0
            else:
                result_dict["metadata"]["fidelity"] = 100.0 if shots == 0 else 0.0
            
            return {
                "success": True,
                "results": result_dict,
                "backend": backend,
                "shots": shots
            }
            
        except Exception as e:
            # Log the full error for debugging
            import traceback
            error_trace = traceback.format_exc()
            print(f"QSim execution error for backend '{backend}': {e}")
            print(error_trace)
            
            # Return a user-friendly error message
            error_msg = str(e)
            # Extract more specific error if available
            if hasattr(e, '__cause__') and e.__cause__:
                error_msg = str(e.__cause__)
            
            return {
                "success": False,
                "error": f"QSim simulation failed: {error_msg}"
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
