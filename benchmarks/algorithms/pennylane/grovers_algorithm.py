"""
PennyLane Implementation: Grover's Algorithm (variable: 2–6 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Grover's Search Algorithm
Category: Search
Qubit Range: 2–6
Framework: PennyLane (idiomatic style)

Key comparison point (Case Study 2):
  PennyLane provides qml.GroverOperator as a BUILT-IN TEMPLATE.
  This is the primary structural difference vs Qiskit and Cirq which
  require manual construction of the oracle + diffusion operator.

Two implementation options:
  Option A (idiomatic): Use qml.GroverOperator → may produce fewer or more
            gates than the manual construction, depending on PennyLane version.
  Option B (manual): Build oracle + diffusion from primitives (same as Qiskit/Cirq).

For this benchmark, we use OPTION A (qml.GroverOperator) because:
  - It IS the idiomatic PennyLane approach
  - It reveals template overhead vs. manual construction
  - The QASM generated from templates is the most interesting comparison

The manual oracle for the phase flip is still needed to mark the specific
target state; qml.GroverOperator handles only the diffusion (reflection) operator.

MARKED_STATES (MUST match other framework files):
  n=2 → "11", n=3 → "101", n=4 → "1011", n=5 → "10110", n=6 → "101101"
"""

# TODO: import pennylane as qml
# TODO: import numpy as np

# TODO: MARKED_STATES = {2: "11", 3: "101", 4: "1011", 5: "10110", 6: "101101"}

def get_circuit(n: int = 2):
    """
    Build and return the PennyLane Grover QNode.

    Args:
        n (int): Number of search qubits (2–6). Default 2.

    Returns:
        function: QNode.

    Notes:
        - Uses qml.GroverOperator for the diffusion step (idiomatic).
        - Phase oracle is built manually: X on 0-bits → multi-controlled-Z → X.
        - Optimal iterations = int(np.floor(np.pi / 4 * np.sqrt(2**n))).
        - return qml.probs(wires=list(range(n)))
    """

    # TODO: dev = qml.device('default.qubit', wires=n)
    # TODO: marked_state = MARKED_STATES[n]
    # TODO: num_iterations = int(np.floor(np.pi / 4 * np.sqrt(2**n)))

    # TODO: @qml.qnode(dev)
    #   def grover_circuit():
    #       # Equal superposition
    #       for i in range(n): qml.Hadamard(wires=i)
    #       # Grover iterations
    #       for _ in range(num_iterations):
    #           # Phase oracle: mark the target state
    #           for i in range(n):
    #               if marked_state[i] == '0': qml.PauliX(wires=i)
    #           qml.ctrl(qml.PauliZ, control=list(range(n-1)))(wires=n-1)  # multi-controlled Z
    #           for i in range(n):
    #               if marked_state[i] == '0': qml.PauliX(wires=i)
    #           # Diffusion step (GroverOperator)
    #           qml.GroverOperator(wires=list(range(n)))
    #       return qml.probs(wires=list(range(n)))

    # TODO: return grover_circuit
    pass


# TODO: if __name__ == "__main__": run for n=2,3,4; print marked state probabilities
