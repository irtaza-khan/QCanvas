"""
PennyLane Implementation: VQE (variable: 2–6 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: VQE
Category: Variational
Qubit Range: 2–6
Framework: PennyLane (idiomatic style)

Idiomatic PennyLane uses qml.StronglyEntanglingLayers as the ansatz template.
This is the KEY STRUCTURAL DIFFERENCE from Case Study 3:
  Qiskit → EfficientSU2 (Ry + Rz + linear CNOT)
  Cirq   → Manual Ry + Rz + CNOT
  PennyLane → StronglyEntanglingLayers (all 3 rotation angles + cyclic CNOT)

StronglyEntanglingLayers uses:
  - Rot(phi, theta, omega) gates on each qubit (= Rz Ry Rz decomposition under the hood)
  - Cyclic (circular) entanglement: CNOT(i, (i+1) % n)
This gives MORE GATES per layer than EfficientSU2 (3 rotation angles vs 2).

Parameters fixed to 0.0 (same as Qiskit and Cirq versions).
"""

# TODO: import pennylane as qml
# TODO: import numpy as np

def get_circuit(n: int = 2, reps: int = 1, param_value: float = 0.0):
    """
    Build and return the PennyLane VQE QNode using StronglyEntanglingLayers.

    Args:
        n (int): Number of qubits (2–6). Default 2.
        reps (int): Number of StronglyEntangling layers. Default 1.
        param_value (float): Fixed value for all parameters. Default 0.0.

    Returns:
        function: QNode.

    Notes:
        - StronglyEntanglingLayers requires weights of shape (reps, n, 3).
        - All weights are set to param_value (0.0 for benchmark).
        - Cyclic entanglement means CNOT connects qubit n-1 back to qubit 0,
          adding one extra CNOT vs linear entanglement — be aware when counting.
        - return qml.probs(wires=list(range(n)))
    """

    # TODO: dev = qml.device('default.qubit', wires=n)
    # TODO: weights = np.full((reps, n, 3), param_value)

    # TODO: @qml.qnode(dev)
    #   def vqe_circuit():
    #       qml.StronglyEntanglingLayers(weights=weights, wires=list(range(n)))
    #       return qml.probs(wires=list(range(n)))

    # TODO: return vqe_circuit
    pass


# TODO: if __name__ == "__main__":
#   - Run for n=2 and n=4, print gate count via qml.specs(vqe_circuit)()
#   - Compare Rot gate count vs Qiskit's EfficientSU2 (Ry+Rz)
