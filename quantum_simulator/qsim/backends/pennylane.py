import pennylane as qml
import numpy as np
from typing import Any, Dict
from .base import BaseBackend # Assuming this is correct


class PennylaneBackend(BaseBackend):
    """
    PennyLane-based concrete backend for executing quantum tapes.
    
    This uses PennyLane's 'default.qubit' or 'lightning.qubit' simulator
    to execute the compiled circuit (qml.QuantumTape).
    """

    def _get_dev_name(self) -> str:
        """Helper to check for faster simulator availability."""
        try:
            # Prefer lightning for speed if available
            qml.device("lightning.qubit", wires=1)
            return "lightning.qubit"
        except qml.QuantumDeviceError:
            # Fallback to default if lightning is not installed
            return "default.qubit"


    def run(self, tape: qml.tape.QuantumTape, shots: int = 1024) -> Dict[str, Any]:
        """
        Run simulation on PennyLane tape.

        Args:
            tape: The quantum program as a qml.QuantumTape object.
            shots: Number of shots for sampling. Use 0 for exact probabilities.

        Returns:
            A dictionary containing counts and probabilities.
        """
        num_qubits = len(tape.wires)

        if num_qubits == 0:
            return {'counts': {}, 'probs': {}, 'metadata': {'shots': shots, 'device': 'None'}}
        
        dev_name = self._get_dev_name()
        
                
        def tape_operations_wrapper():
            """Applies all operations from the input tape within the QNode context."""
            for op in tape.operations:
                qml.apply(op)
        
        if shots > 0:
            dev = qml.device(dev_name, wires=num_qubits, shots=shots)
            
            def qnode_wrapper_sampling():
                """Defines the QNode logic for sampling."""
                tape_operations_wrapper() 
                return qml.counts(wires=tape.wires) 

            qnode = qml.QNode(qnode_wrapper_sampling, dev)
            counts_dict = qnode()
            
            total_shots = shots
            if isinstance(counts_dict, dict):
                counts_dict = {k: v for k, v in counts_dict.items()} # Ensure standard dict
            else:
                total_shots = sum(counts_dict.values()) # Recalculate if needed
            
            probs_dict = {k: v / total_shots for k, v in counts_dict.items()}
            
            return {
                'counts': counts_dict,
                'probs': probs_dict,
                'metadata': {'shots': total_shots, 'device': dev_name, 'result_type': 'sampling'}
            }
        
        else:
            dev = qml.device(dev_name, wires=num_qubits)
            
            def qnode_wrapper_exact():
                tape_operations_wrapper()  # Apply the input tape's operations
                return qml.probs(wires=tape.wires) # Add the required measurement for exact

            # Execute the QNode
            qnode = qml.QNode(qnode_wrapper_exact, dev, diff_method=None)
            probs_vector = qnode()
            
            # Process results
            probs_dict = self._probs_to_dict(probs_vector, num_qubits)
            
            return {
                'counts': {}, # No counts for exact simulation
                'probs': probs_dict,
                'metadata': {'shots': shots, 'device': dev_name, 'result_type': 'exact'}
            }

    def _probs_to_dict(self, probs_vector: np.ndarray, num_qubits: int) -> Dict[str, float]:
        """Converts a probability vector to a dictionary with bitstring keys."""
        probs_dict = {}
        for i, prob in enumerate(probs_vector):
            # Format the index 'i' as a bitstring of length num_qubits
            bitstring = format(i, f'0{num_qubits}b')
            probs_dict[bitstring] = float(prob)
        return probs_dict