# Gate Syntax Reference

This document provides the syntax for supported quantum gates in **Cirq**, **Qiskit**, and **PennyLane**, based on the `QCanvas` system's capabilities.

## Single Qubit Gates

| Gate | Description | Cirq Syntax | Qiskit Syntax | PennyLane Syntax |
| :--- | :--- | :--- | :--- | :--- |
| **Hadamard** | Creates superposition. | `cirq.H(q)` | `qc.h(q)` | `qml.Hadamard(wires=q)` |
| **Pauli-X** | Bit flip (NOT gate). | `cirq.X(q)` | `qc.x(q)` | `qml.PauliX(wires=q)` |
| **Pauli-Y** | Bit and phase flip. | `cirq.Y(q)` | `qc.y(q)` | `qml.PauliY(wires=q)` |
| **Pauli-Z** | Phase flip. | `cirq.Z(q)` | `qc.z(q)` | `qml.PauliZ(wires=q)` |
| **S** | $\sqrt{Z}$ phase gate. | `cirq.S(q)` | `qc.s(q)` | `qml.S(wires=q)` |
| **T** | $\sqrt{S}$ phase gate. | `cirq.T(q)` | `qc.t(q)` | `qml.T(wires=q)` |
| **SX** | $\sqrt{X}$ gate. | `cirq.SX(q)` | `qc.sx(q)` | `qml.SX(wires=q)` |
| **Identity** | No operation. | `cirq.I(q)` | `qc.id(q)` or `qc.i(q)` | `qml.Identity(wires=q)` |

## Parameterized Single Qubit Gates

| Gate | Description | Cirq Syntax | Qiskit Syntax | PennyLane Syntax |
| :--- | :--- | :--- | :--- | :--- |
| **RX** | Rotation around X-axis. | `cirq.rx(theta)(q)` | `qc.rx(theta, q)` | `qml.RX(theta, wires=q)` |
| **RY** | Rotation around Y-axis. | `cirq.ry(theta)(q)` | `qc.ry(theta, q)` | `qml.RY(theta, wires=q)` |
| **RZ** | Rotation around Z-axis. | `cirq.rz(theta)(q)` | `qc.rz(theta, q)` | `qml.RZ(theta, wires=q)` |
| **PhaseShift / P** | Phase shift by angle $\lambda$. | `cirq.Z(q)**(lambda/pi)` *or* `cirq.ZPowGate(exponent=lambda/pi)(q)` | `qc.p(lambda, q)` | `qml.PhaseShift(lambda, wires=q)` |
| **U** | Universal single-qubit gate. | *Not directly standard, usually decomposed* | `qc.u(theta, phi, lam, q)` | `qml.U3(theta, phi, lam, wires=q)` |

> **Note:** Cirq's `ZPowGate` exponent is normalized by $\pi$ (i.e., `exponent=1` means $Z$ or $180^\circ$ phase). Qiskit and PennyLane typically use radians.

## Two Qubit Gates

| Gate | Description | Cirq Syntax | Qiskit Syntax | PennyLane Syntax |
| :--- | :--- | :--- | :--- | :--- |
| **CNOT / CX** | Controlled-NOT. | `cirq.CNOT(c, t)` or `cirq.CX(c, t)` | `qc.cx(c, t)` or `qc.cnot(c, t)` | `qml.CNOT(wires=[c, t])` |
| **CZ** | Controlled-Z. | `cirq.CZ(c, t)` | `qc.cz(c, t)` | `qml.CZ(wires=[c, t])` |
| **CY** | Controlled-Y. | `cirq.CY(c, t)` | `qc.cy(c, t)` | `qml.CY(wires=[c, t])` |
| **CH** | Controlled-Hadamard. | `cirq.ControlledGate(cirq.H)(c, t)` *or* `cirq.H(t).controlled_by(c)` | `qc.ch(c, t)` | `qml.CH(wires=[c, t])` *or* `qml.ctrl(qml.Hadamard, control=c)(wires=t)` |
| **SWAP** | Swaps two qubits. | `cirq.SWAP(q1, q2)` | `qc.swap(q1, q2)` | `qml.SWAP(wires=[q1, q2])` |

## Three Qubit Gates

| Gate | Description | Cirq Syntax | Qiskit Syntax | PennyLane Syntax |
| :--- | :--- | :--- | :--- | :--- |
| **Toffoli / CCX** | Controlled-Controlled-NOT. | `cirq.CCX(c1, c2, t)` or `cirq.TOFFOLI(c1, c2, t)` | `qc.ccx(c1, c2, t)` | `qml.Toffoli(wires=[c1, c2, t])` |
| **CCZ** | Controlled-Controlled-Z. | `cirq.CCZ(c1, c2, t)` | `qc.ccz(c1, c2, t)` | `qml.CCZ(wires=[c1, c2, t])` |
| **Fredkin / CSWAP** | Controlled-SWAP. | `cirq.CSWAP(c, t1, t2)` or `cirq.FREDKIN(c, t1, t2)` | `qc.cswap(c, t1, t2)` | `qml.CSWAP(wires=[c, t1, t2])` |

## Controlled Parameterized Gates

| Gate | Description | Cirq Syntax | Qiskit Syntax | PennyLane Syntax |
| :--- | :--- | :--- | :--- | :--- |
| **CP / CPhase** | Controlled-Phase. | `cirq.CZ(c, t)**(theta/pi)` | `qc.cp(theta, c, t)` | `qml.ControlledPhaseShift(theta, wires=[c, t])` |
| **CRX** | Controlled-RX. | `cirq.rx(theta)(t).controlled_by(c)` | `qc.crx(theta, c, t)` | `qml.CRX(theta, wires=[c, t])` |
| **CRY** | Controlled-RY. | `cirq.ry(theta)(t).controlled_by(c)` | `qc.cry(theta, c, t)` | `qml.CRY(theta, wires=[c, t])` |
| **CRZ** | Controlled-RZ. | `cirq.rz(theta)(t).controlled_by(c)` | `qc.crz(theta, c, t)` | `qml.CRZ(theta, wires=[c, t])` |
| **CU** | Controlled-U. | *Complex decomposition* | `qc.cu(theta, phi, lam, gamma, c, t)` | *Via `qml.ctrl` on `qml.U3`* |

## Other Operations

| Operation | Description | Cirq Syntax | Qiskit Syntax | PennyLane Syntax |
| :--- | :--- | :--- | :--- | :--- |
| **Measure** | Measurement. | `cirq.measure(q, key='c')` | `qc.measure(q, c)` | `qml.measure(wires=q)` |
| **Reset** | Reset to \|0>. | `cirq.reset(q)` | `qc.reset(q)` | *Not standard in all devices* |
| **Barrier** | Visual/Compiler barrier. | *Not directly supported in standard syntax* | `qc.barrier(q)` | `qml.Barrier(wires=q)` |
| **Global Phase** | Global phase shift. | `cirq.GlobalPhaseOperation(coeff)` | `qc.global_phase += angle` | `qml.GlobalPhase(angle, wires=...)` |

## Summary Table

| Gate Category | Gates Included |
| :--- | :--- |
| **Single Qubit** | H, X, Y, Z, S, T, SX, I |
| **Parameterized** | RX, RY, RZ, P, U |
| **Two Qubit** | CX (CNOT), CZ, CY, CH, SWAP |
| **Three Qubit** | CCX (Toffoli), CCZ, CSWAP (Fredkin) |
| **Controlled Param** | CP, CRX, CRY, CRZ, CU |
| **Non-Unitary** | Measure, Reset, Barrier |

---
*Generated by QCanvas Assistant*
