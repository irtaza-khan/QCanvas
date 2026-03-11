"""
PennyLane Implementation: Deutsch–Jozsa (variable: 3–8 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Deutsch–Jozsa
Category: Oracle-Based
Qubit Range: 3–8
Framework: PennyLane (idiomatic style)

PennyLane does not have a DJ template; oracle is built manually.
Uses same oracle strategy as Qiskit version (CNOT from each input to ancilla).
"""

# TODO: import pennylane as qml

def get_circuit(n: int = 3, oracle_type: str = "balanced"):
    """
    Build and return the PennyLane Deutsch–Jozsa QNode.

    Args:
        n (int): Number of input qubits. Total wires = n+1 (ancilla at wire n).
        oracle_type (str): 'constant' or 'balanced'.

    Returns:
        function: QNode.

    Notes:
        - Ancilla wire = n, input wires = 0..n-1
        - return qml.probs(wires=list(range(n)))
    """

    # TODO: dev = qml.device('default.qubit', wires=n+1)

    # TODO: @qml.qnode(dev)
    #   def dj_circuit():
    #       # Ancilla prep: X then H
    #       qml.PauliX(wires=n)
    #       qml.Hadamard(wires=n)
    #       # H on input qubits
    #       for i in range(n): qml.Hadamard(wires=i)
    #       # Oracle
    #       if oracle_type == 'balanced':
    #           for i in range(n): qml.CNOT(wires=[i, n])
    #       # Second H layer
    #       for i in range(n): qml.Hadamard(wires=i)
    #       return qml.probs(wires=list(range(n)))

    # TODO: return dj_circuit
    pass


# TODO: if __name__ == "__main__": run both oracle types for n=3
