"""
PennyLane Implementation: Bernstein–Vazirani (variable: 3–8 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Bernstein–Vazirani
Category: Oracle-Based
Qubit Range: 3–8
Framework: PennyLane (idiomatic style)

Same algorithm as qiskit/bernstein_vazirani.py using PennyLane.
MUST use the same SECRET_STRINGS as Qiskit and Cirq versions.
"""

# TODO: import pennylane as qml

# TODO: SECRET_STRINGS = {3: "101", 4: "1011", 5: "10110", 6: "101101", 7: "1011010", 8: "10110100"}

def get_circuit(n: int = 3):
    """
    Build and return the PennyLane BV QNode.

    Args:
        n (int): Number of input qubits (3–8).

    Returns:
        function: QNode.
    """

    # TODO: Validate n in SECRET_STRINGS
    # TODO: dev = qml.device('default.qubit', wires=n+1)

    # TODO: @qml.qnode(dev)
    #   def bv_circuit():
    #       secret = SECRET_STRINGS[n]
    #       # Ancilla prep
    #       qml.PauliX(wires=n); qml.Hadamard(wires=n)
    #       # Input H layer
    #       for i in range(n): qml.Hadamard(wires=i)
    #       # Oracle: CNOT where secret[i]=='1'
    #       for i in range(n):
    #           if secret[i] == '1': qml.CNOT(wires=[i, n])
    #       # Second H layer
    #       for i in range(n): qml.Hadamard(wires=i)
    #       return qml.probs(wires=list(range(n)))

    # TODO: return bv_circuit
    pass


# TODO: if __name__ == "__main__": run for n=3..6, print probabilities
