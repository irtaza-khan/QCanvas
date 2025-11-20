import numpy as np
from typing import Any, Dict
from .base import BaseBackend

class CirqBackend(BaseBackend):
    """Backend for Cirq circuits."""
    
    def __init__(self, simulator: str = "simulator"):
        """
        Args:
            simulator: 'simulator' for standard or 'density_matrix_simulator'
        """
        import cirq
        self.cirq = cirq
        if simulator == "density_matrix_simulator":
            self.simulator = cirq.DensityMatrixSimulator()
        else:
            self.simulator = cirq.Simulator()
    
    def run(self, circuit: Any, shots: int = 1024) -> Dict[str, Any]:
        """
        Run Cirq circuit simulation.
        Args:
            circuit: cirq.Circuit from visitor
            shots: Number of shots (0 for exact statevector)
        """
        # Get qubits in order
        qubits = sorted(circuit.all_qubits())
        n_qubits = len(qubits)
        
        if shots > 0:
            # Sampling mode
            result = self.simulator.run(circuit, repetitions=shots)
            
            # Extract measurements
            counts = {}
            if result.measurements:
                # Get all measurement keys
                measurement_keys = list(result.measurements.keys())
                
                # Combine all measurements into bitstrings
                for i in range(shots):
                    # Collect bits from all measurement keys
                    bits = []
                    for key in measurement_keys:
                        measurement = result.measurements[key][i]
                        # Handle both single bit and multi-bit measurements
                        if isinstance(measurement, (list, np.ndarray)):
                            bits.extend([int(b) for b in measurement])
                        else:
                            bits.append(int(measurement))
                    
                    bitstring = ''.join(str(b) for b in bits)
                    counts[bitstring] = counts.get(bitstring, 0) + 1
            else:
                # No measurements in circuit, sample final state
                final_state = self.simulator.simulate(circuit)
                state_vector = final_state.final_state_vector
                
                # Sample from statevector
                probs_array = np.abs(state_vector) ** 2
                indices = np.random.choice(len(probs_array), size=shots, p=probs_array)
                
                for idx in indices:
                    bitstring = format(idx, f'0{n_qubits}b')
                    counts[bitstring] = counts.get(bitstring, 0) + 1
            
            probs = {k: v / shots for k, v in counts.items()}
            
            return {
                'counts': counts,
                'probs': probs,
                'metadata': {'backend': 'cirq', 'shots': shots}
            }
        else:
            # Exact statevector mode
            result = self.simulator.simulate(circuit)
            state_vector = result.final_state_vector
            
            # Calculate probabilities
            probs_array = np.abs(state_vector) ** 2
            probs = {}
            for idx, prob in enumerate(probs_array):
                if prob > 1e-10:
                    bitstring = format(idx, f'0{n_qubits}b')
                    probs[bitstring] = float(prob)
            
            return {
                'counts': {},
                'probs': probs,
                'statevector': state_vector,
                'metadata': {'backend': 'cirq', 'shots': 0}
            }