"""
PennyLane Implementation: QAOA (variable: 2–6 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: QAOA MaxCut
Category: Variational
Qubit Range: 2–6
Framework: PennyLane (idiomatic style)

Idiomatic PennyLane uses qml.qaoa.maxcut() to generate the cost Hamiltonian
and qml.qaoa.cost_layer() / qml.qaoa.mixer_layer() for the QAOA layers.
This is a significantly higher-level API than Qiskit/Cirq manual construction.

Key comparison question:
  Does PennyLane's qaoa template produce MORE or FEWER gates than the
  manual Rzz decomposition (CNOT → Rz → CNOT) used in Qiskit and Cirq?

Same graph as other frameworks (triangle for n=3, path graph for n>3).
Same parameters: gamma=π/4, beta=π/4, p=1 layer.
"""

# TODO: import pennylane as qml
# TODO: from pennylane import qaoa
# TODO: import numpy as np
# TODO: import networkx as nx  (PennyLane's qaoa module requires networkx for graph input)

def get_circuit(n: int = 3, p: int = 1, gamma: float = None, beta: float = None):
    """
    Build and return the PennyLane QAOA QNode.

    Args:
        n (int): Number of qubits / nodes (2–6). Default 3.
        p (int): QAOA layers. Default 1.
        gamma (float): Cost layer parameter. Default π/4.
        beta (float): Mixer parameter. Default π/4.

    Returns:
        function: QNode.

    Notes:
        - Use networkx.Graph to define the MaxCut graph.
        - qml.qaoa.maxcut(graph) returns (cost_h, mixer_h) Hamiltonians.
        - qml.qaoa.cost_layer(gamma, cost_h) and qml.qaoa.mixer_layer(beta, mixer_h)
          are the PennyLane idiom for QAOA circuit layers.
        - the PennyLane QAOA layers internally use PauliRot gates which may produce
          different QASM than the explicit CNOT+Rz decomposition.
    """

    # TODO: Set defaults: gamma = np.pi/4, beta = np.pi/4
    # TODO: Build graph G using networkx (same edge structure as Qiskit version)
    # TODO: cost_h, mixer_h = qml.qaoa.maxcut(G)
    # TODO: dev = qml.device('default.qubit', wires=n)

    # TODO: @qml.qnode(dev)
    #   def qaoa_circuit():
    #       # Equal superposition
    #       for i in range(n): qml.Hadamard(wires=i)
    #       # p QAOA layers
    #       for _ in range(p):
    #           qml.qaoa.cost_layer(gamma, cost_h)
    #           qml.qaoa.mixer_layer(beta, mixer_h)
    #       return qml.probs(wires=list(range(n)))

    # TODO: return qaoa_circuit
    pass


# TODO: if __name__ == "__main__": run for n=3 and n=5, print gate specs
