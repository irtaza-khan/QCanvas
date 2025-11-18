"""
Qiskit Complete Gate Demonstration
---------------------------------
This example instantiates a `QuantumCircuit` that exercises every gate supported
by the QCanvas Qiskit → OpenQASM 3.0 converter (Iteration I feature set plus
global phase).
"""

from qiskit import QuantumCircuit, Parameter
import numpy as np


def qiskit_complete_gates() -> QuantumCircuit:
    """
    Build a `QuantumCircuit` that touches all supported gate families.

    Gate coverage:
    - Single-qubit: h, x, y, z, s, t, sx, id
    - Parameterized single-qubit: rx, ry, rz, p, u
    - Two-qubit: cx, cz, swap
    - Parameterized two-qubit: crx, cry, crz, cp, cu
    - Three-qubit: ccx
    - Special: gphase
    """

    # Symbolic parameters for showcasing parameterized gates
    theta = Parameter("theta")
    phi = Parameter("phi")
    lam = Parameter("lambda")
    gamma = Parameter("gamma")

    qc = QuantumCircuit(6, 6)

    # === SINGLE-QUBIT GATES ===
    qc.x(0)
    qc.y(1)
    qc.z(2)
    qc.h(0)
    qc.s(1)
    qc.t(2)
    qc.sx(3)
    qc.id(4)

    # === PARAMETERIZED SINGLE-QUBIT GATES ===
    qc.rx(np.pi / 2, 0)
    qc.ry(np.pi / 4, 1)
    qc.rz(np.pi / 3, 2)
    qc.p(np.pi / 6, 3)
    qc.u(np.pi / 2, np.pi / 4, np.pi / 8, 4)
    qc.rx(theta, 0)
    qc.ry(phi, 1)
    qc.rz(lam, 2)

    # === TWO-QUBIT GATES ===
    qc.cx(0, 1)
    qc.cz(1, 2)
    qc.swap(2, 3)

    # === PARAMETERIZED TWO-QUBIT GATES ===
    qc.crx(np.pi / 2, 0, 1)
    qc.cry(np.pi / 3, 1, 2)
    qc.crz(np.pi / 4, 2, 3)
    qc.cp(np.pi / 8, 3, 4)
    qc.cu(np.pi / 2, np.pi / 4, np.pi / 8, np.pi / 16, 0, 5)

    # === THREE-QUBIT & SPECIAL GATES ===
    qc.ccx(0, 1, 2)
    qc.gphase(gamma)

    qc.measure(0, 0)
    qc.measure(1, 1)
    qc.measure(2, 2)
    qc.measure(3, 3)
    qc.measure(4, 4)
    qc.measure(5, 5)

    return qc


if __name__ == "__main__":
    circuit = qiskit_complete_gates()
    bound = circuit.bind_parameters(
        {"theta": np.pi / 5, "phi": np.pi / 7, "lambda": np.pi / 9, "gamma": np.pi / 11}
    )
    print(bound)

