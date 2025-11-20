from typing import Any, Dict
import numpy as np
from .base import BaseBackend
from qiskit_aer import Aer


class QiskitBackend(BaseBackend):
    """Backend for Qiskit circuits."""
    
    def __init__(self, backend_name: str = "aer_simulator"):
        """
        Args:
            backend_name: Qiskit backend (e.g., 'aer_simulator', 'statevector_simulator')
        """
        self.backend_name = backend_name
        self.Aer = Aer
    
    def run(self, circuit: Any, shots: int = 1024) -> Dict[str, Any]:
        """
        Run Qiskit circuit simulation.
        Args:
            circuit: qiskit.QuantumCircuit from visitor
            shots: Number of shots (0 for statevector)
        """
        from qiskit import transpile
        
        if shots > 0:
            # Sampling mode
            backend = self.Aer.get_backend('aer_simulator')
            
            # Add measurements if not present
            qc = circuit.copy()
            if not any(instr.operation.name == 'measure' for instr in qc.data):
                qc.measure_all()
            
            # Transpile and run
            qc_transpiled = transpile(qc, backend)
            job = backend.run(qc_transpiled, shots=shots)
            result = job.result()
            counts_raw = result.get_counts()
            
            # Normalize counts format (Qiskit returns reversed bitstrings)
            counts = {k[::-1]: v for k, v in counts_raw.items()}
            probs = {k: v / shots for k, v in counts.items()}
            
            return {
                'counts': counts,
                'probs': probs,
                'metadata': {'backend': 'qiskit', 'simulator': self.backend_name, 'shots': shots}
            }
        else:
            # Exact statevector mode
            backend = self.Aer.get_backend('statevector_simulator')
            
            qc = circuit.copy()
            qc.save_statevector()
            
            qc_transpiled = transpile(qc, backend)
            job = backend.run(qc_transpiled)
            result = job.result()
            statevector = result.get_statevector()
            
            # Calculate probabilities
            n_qubits = circuit.num_qubits
            probs_array = np.abs(statevector.data) ** 2
            probs = {}
            for idx, prob in enumerate(probs_array):
                if prob > 1e-10:
                    bitstring = format(idx, f'0{n_qubits}b')[::-1]  # Reverse for Qiskit convention
                    probs[bitstring] = float(prob)
            
            return {
                'counts': {},
                'probs': probs,
                'statevector': statevector.data,
                'metadata': {'backend': 'qiskit', 'simulator': 'statevector', 'shots': 0}
            }