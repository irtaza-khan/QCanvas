"""
PennyLane Complete Gate Demonstration
------------------------------------
Exercises every PennyLane gate supported by the QCanvas converter
(Iteration I + Iteration II feature sets).
"""

import pennylane as qml
import numpy as np


def pennylane_complete_gates():
    """
    Build a PennyLane QNode that touches the full gate surface.

    Gate coverage:
    - Pauli + single-qubit: X, Y, Z, Hadamard, S, T, Identity
    - Parameterized single-qubit: RX, RY, RZ, PhaseShift
    - Two-qubit: CNOT, CZ, SWAP
    - Controlled two-qubit (Iteration II): CY, CH, CRX, CRY, CRZ, ControlledPhaseShift
    - Three-qubit: Toffoli, CSWAP, CCZ
    - Special: GlobalPhase
    """

    dev = qml.device("default.qubit", wires=7)

    @qml.qnode(dev)
    def circuit():
        # === SINGLE-QUBIT GATES ===
        qml.PauliX(0)
        qml.PauliY(1)
        qml.PauliZ(2)
        qml.Hadamard(0)
        qml.S(1)
        qml.T(2)
        qml.Identity(3)

        # === PARAMETERIZED SINGLE-QUBIT GATES ===
        qml.RX(np.pi / 2, 0)
        qml.RY(np.pi / 4, 1)
        qml.RZ(np.pi / 3, 2)
        qml.PhaseShift(np.pi / 6, 3)
        qml.RX(np.pi, 4)
        qml.RY(2 * np.pi / 3, 5)
        qml.RZ(np.pi / 8, 6)

        # === TWO-QUBIT GATES (Iteration I) ===
        qml.CNOT([0, 1])
        qml.CZ([1, 2])
        qml.SWAP([2, 3])

        # === CONTROLLED TWO-QUBIT GATES (Iteration II) ===
        qml.CY([0, 1])
        qml.CH([1, 2])
        qml.CRX(np.pi / 2, [2, 3])
        qml.CRY(np.pi / 3, [3, 4])
        qml.CRZ(np.pi / 4, [4, 5])
        qml.ControlledPhaseShift(np.pi / 8, wires=[5, 6])

        # === THREE-QUBIT & SPECIAL GATES ===
        qml.Toffoli([0, 1, 2])
        qml.CSWAP([3, 4, 5])
        qml.CCZ([0, 1, 3])
        qml.GlobalPhase(np.pi / 7)

        return [qml.expval(qml.PauliZ(i)) for i in range(7)]

    return circuit


if __name__ == "__main__":
    circuit = pennylane_complete_gates()
    print(circuit())

