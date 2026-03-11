"""
PennyLane Implementation: GHZ State (variable: 3–8 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: GHZ State
Category: Foundational
Qubit Range: 3–8
Framework: PennyLane (idiomatic style)

PennyLane does not have a built-in GHZ template, so this is implemented
manually — same logical structure as the Qiskit and Cirq versions.

Idiomatic PennyLane conventions:
  - Dynamic device creation inside get_circuit(n) since the number of wires is n
  - Inner @qml.qnode function defined within get_circuit() to bind device
  - qml.Hadamard(wires=0) + [qml.CNOT(wires=[i, i+1]) for i in range(n-1)]
  - return qml.probs(wires=list(range(n)))
"""

# TODO: import pennylane as qml
# TODO: import numpy as np

def get_circuit(n: int = 3):
    """
    Build and return the PennyLane GHZ QNode for n qubits.

    Args:
        n (int): Number of qubits (3–8). Default 3.

    Returns:
        function: A QNode that when called returns the probability distribution
                  over all 2^n basis states.

    Notes:
        - Device is created inside this function for the correct wire count.
        - The QNode is created with @qml.qnode inside the function body.
        - Returns the QNode function object (not the result of calling it).
    """

    # TODO: dev = qml.device('default.qubit', wires=n)

    # TODO: @qml.qnode(dev)
    #   def ghz_circuit():
    #       qml.Hadamard(wires=0)
    #       for i in range(n - 1):
    #           qml.CNOT(wires=[i, i + 1])
    #       return qml.probs(wires=list(range(n)))

    # TODO: return ghz_circuit
    pass


def get_scaling_circuits():
    """Return (n, qnode_fn) pairs for scaling sweep (n=3..8)."""
    # TODO: return [(n, get_circuit(n)) for n in range(3, 9)]
    pass


# TODO: if __name__ == "__main__": call and print for n=3, n=5, n=8
