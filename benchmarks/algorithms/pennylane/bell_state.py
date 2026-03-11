"""
PennyLane Implementation: Bell State (2 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Bell State
Category: Foundational
Qubit Range: 2
Framework: PennyLane (idiomatic style)

This file implements the Bell state idiomatically in PennyLane, following
Xanadu's PennyLane library conventions with the @qml.qnode decorator pattern.

Idiomatic PennyLane conventions:
  - @qml.qnode(dev) decorator on the circuit function
  - qml.device('default.qubit', wires=2) for the backend device
  - qml.Hadamard(wires=0) and qml.CNOT(wires=[0, 1])
  - return qml.probs(wires=[0, 1]) for probability distribution
    (equivalent to measuring in the Z-basis and returning probabilities)

Key QASM structural difference vs Qiskit / Cirq:
  - PennyLane's decorator pattern produces a more complex Python AST than
    Qiskit's method-chain pattern, making CirqASTVisitor and PennyLaneASTVisitor
    structurally different. The QCanvas PennyLaneASTVisitor must handle the
    @qml.qnode decorator and the inner function body.
  - Processing time is expected to be SLIGHTLY LONGER for PennyLane due
    to the more complex AST traversal.

Expected QASM output: Identical to Qiskit and Cirq versions (same 2 gates).
Expected JSD vs other frameworks: < 0.001 (effectively identical distributions).

This file is called by:
  - benchmarks/scripts/compile_all.py
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
  - benchmarks/notebooks/nb04_case_studies.ipynb  (Case Study 1)
"""

# ──────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────

# TODO: import pennylane as qml
# TODO: import numpy as np


# ──────────────────────────────────────────────────────────
# Device
# ──────────────────────────────────────────────────────────

# TODO: dev = qml.device('default.qubit', wires=2)


# ──────────────────────────────────────────────────────────
# Circuit Definition
# ──────────────────────────────────────────────────────────

# TODO: @qml.qnode(dev)
def bell_state_circuit():
    """
    PennyLane Bell state QNode.

    Operations:
      - qml.Hadamard(wires=0)
      - qml.CNOT(wires=[0, 1])

    Returns:
        np.ndarray: Probability distribution over computational basis states.
                    Shape: (4,) for 2 qubits.
                    Expected: [0.5, 0.0, 0.0, 0.5] (|00⟩ and |11⟩ each 50%).

    Notes:
        - qml.probs() returns the FULL probability vector over all basis states.
        - This is different from measurement samples — probs() is deterministic.
        - For sampling-based simulation (to compare with Qiskit/Cirq shot output),
          use qml.sample(qml.PauliZ(0)) or equivalent and post-process.
    """

    # TODO: qml.Hadamard(wires=0)
    # TODO: qml.CNOT(wires=[0, 1])
    # TODO: return qml.probs(wires=[0, 1])
    pass


def get_circuit():
    """
    Return the QNode function for use by compile_all.py.

    Returns:
        function: The bell_state_circuit QNode.

    Notes:
        - The QCanvas PennyLane parser expects to receive the QNode function
          object (not its output). It inspects the function's source code
          via inspect.getsource() or AST parsing.
        - compile_all.py should call converter_fn(get_circuit()) where
          get_circuit() returns the function object, not the result.
    """

    # TODO: return bell_state_circuit
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: if __name__ == "__main__":
#   - Call bell_state_circuit() and print probability output
#   - Print the QNode's device name and wire count
#   - Print the tape (circuit) via print(qml.draw(bell_state_circuit)())
