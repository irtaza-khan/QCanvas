"""
Cirq Complete Gate Demonstration
--------------------------------
Builds a `cirq.Circuit` that covers every gate handled by the QCanvas
Cirq → OpenQASM 3.0 converter.
"""

import cirq
import numpy as np


def cirq_complete_gates() -> cirq.Circuit:
    """
    Create a circuit that highlights the supported gate surface.

    Gate coverage:
    - Single-qubit: H, X, Y, Z, S, T, I
    - Parameterized single-qubit: Rx, Ry, Rz
    - Two-qubit: CNOT, CZ, SWAP
    - Three-qubit: CCX
    - Special: GlobalPhase
    """

    qubits = cirq.LineQubit.range(6)
    q0, q1, q2, q3, q4, q5 = qubits

    circuit = cirq.Circuit()

    # === SINGLE-QUBIT GATES ===
    circuit.append(cirq.X(q0))
    circuit.append(cirq.Y(q1))
    circuit.append(cirq.Z(q2))
    circuit.append(cirq.H(q0))
    circuit.append(cirq.S(q1))
    circuit.append(cirq.T(q2))
    circuit.append(cirq.I(q4))

    # === PARAMETERIZED SINGLE-QUBIT GATES ===
    circuit.append(cirq.rx(np.pi / 2)(q0))
    circuit.append(cirq.ry(np.pi / 4)(q1))
    circuit.append(cirq.rz(np.pi / 3)(q2))
    circuit.append(cirq.rx(np.pi)(q3))
    circuit.append(cirq.ry(np.pi / 6)(q4))
    circuit.append(cirq.rz(2 * np.pi / 3)(q5))

    # === TWO-QUBIT GATES ===
    circuit.append(cirq.CNOT(q0, q1))
    circuit.append(cirq.CZ(q1, q2))
    circuit.append(cirq.SWAP(q2, q3))
    circuit.append(cirq.CNOT(q3, q4))
    circuit.append(cirq.CZ(q4, q5))

    # === THREE-QUBIT & SPECIAL GATES ===
    circuit.append(cirq.CCX(q0, q1, q2))
    circuit.append(cirq.CCX(q3, q4, q5))
    circuit.append(cirq.GlobalPhaseGate(np.pi / 7))

    # Measurements
    circuit.append(cirq.measure(q0, key="m0"))
    circuit.append(cirq.measure(q1, key="m1"))
    circuit.append(cirq.measure(q2, key="m2"))
    circuit.append(cirq.measure(q3, key="m3"))
    circuit.append(cirq.measure(q4, key="m4"))
    circuit.append(cirq.measure(q5, key="m5"))

    return circuit


if __name__ == "__main__":
    print(cirq_complete_gates())

