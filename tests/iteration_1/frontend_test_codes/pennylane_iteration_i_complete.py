"""
PennyLane Complete Iteration I Feature Test

This circuit demonstrates ALL Iteration I features that should be
converted to OpenQASM 3.0 by the QCanvas platform.

Paste this code into the QCanvas frontend to test conversion.

Expected Output: OpenQASM 3.0 code with all Iteration I features
"""

import pennylane as qml
import numpy as np

# Define number of qubits
n_qubits = 5

# Create device
dev = qml.device('default.qubit', wires=n_qubits)

@qml.qnode(dev)
def get_circuit():
    # === ITERATION I FEATURE 1: Basic Single-Qubit Gates ===
    qml.Hadamard(wires=0)
    qml.PauliX(wires=1)
    qml.PauliY(wires=2)
    qml.PauliZ(wires=3)
    qml.S(wires=0)
    qml.T(wires=1)
    qml.Identity(wires=4)
    
    # === ITERATION I FEATURE 2: Parameterized Gates ===
    qml.RX(np.pi/2, wires=0)  # RX rotation
    qml.RY(np.pi/4, wires=1)  # RY rotation
    qml.RZ(np.pi, wires=2)    # RZ rotation
    qml.PhaseShift(np.pi/3, wires=3)  # Phase gate
    
    # === ITERATION I FEATURE 3: Two-Qubit Gates ===
    qml.CNOT(wires=[0, 1])  # Controlled-X
    qml.CZ(wires=[1, 2])    # Controlled-Z
    qml.SWAP(wires=[0, 2])  # SWAP
    
    # === ITERATION I FEATURE 4: Three-Qubit Gates ===
    qml.Toffoli(wires=[0, 1, 2])  # Toffoli (CCX)
    
    # === ITERATION I FEATURE 5: Controlled Gates (Gate Modifiers) ===
    qml.ctrl(qml.Hadamard(wires=1), control=0)  # Controlled-Hadamard
    qml.CRX(np.pi/3, wires=[0, 1])  # Controlled-RX
    qml.CRY(np.pi/6, wires=[1, 2])  # Controlled-RY
    qml.CRZ(np.pi/2, wires=[2, 3])  # Controlled-RZ
    
    # === ITERATION I FEATURE 6: Inverse Gates (Gate Modifiers) ===
    qml.adjoint(qml.S(wires=0))  # Inverse S (S dagger)
    qml.adjoint(qml.T(wires=1))  # Inverse T (T dagger)
    
    # === ITERATION I FEATURE 7: Global Phase ===
    qml.GlobalPhase(np.pi/4, wires=0)
    
    # === ITERATION I FEATURE 8: Barrier (implicit in PennyLane) ===
    # PennyLane doesn't have explicit barriers
    # The converter should handle operation ordering
    
    # === ITERATION I FEATURE 9: Advanced Rotations ===
    qml.Rot(np.pi/2, np.pi/4, np.pi/6, wires=0)  # General rotation
    qml.U3(np.pi/2, 0, np.pi, wires=1)  # U3 gate
    qml.U2(0, np.pi, wires=2)  # U2 gate
    
    # === ITERATION I FEATURE 10: Multi-Qubit Operations ===
    qml.MultiRZ(np.pi/4, wires=[0, 1, 2])  # Multi-qubit RZ
    
    # === ITERATION I FEATURE 11: Measurements ===
    # PennyLane measurements return values
    return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]

# Alternative circuit without @qnode decorator for direct execution
def get_circuit_ops():
    """
    Alternative version that returns operations without execution.
    Use this if the @qnode version doesn't work with the converter.
    """
    ops = []
    
    # Basic gates
    ops.append(qml.Hadamard(wires=0))
    ops.append(qml.PauliX(wires=1))
    ops.append(qml.CNOT(wires=[0, 1]))
    
    # Parameterized gates
    ops.append(qml.RX(np.pi/2, wires=0))
    ops.append(qml.RY(np.pi/4, wires=1))
    ops.append(qml.RZ(np.pi, wires=2))
    
    # Multi-qubit gates
    ops.append(qml.Toffoli(wires=[0, 1, 2]))
    ops.append(qml.SWAP(wires=[1, 3]))
    
    # Controlled operations
    ops.append(qml.CRX(np.pi/3, wires=[0, 1]))
    ops.append(qml.CRZ(np.pi/2, wires=[2, 3]))
    
    # Measurements
    ops.extend([qml.expval(qml.PauliZ(i)) for i in range(n_qubits)])
    
    return ops

# Expected OpenQASM 3.0 features in output:
# ✓ OPENQASM 3.0;
# ✓ include "stdgates.inc";
# ✓ Mathematical constants (PI, E, PI_2, PI_4)
# ✓ qubit[5] q;
# ✓ bit[5] c;
# ✓ Classical variables declarations
# ✓ All standard gates (h, x, y, z, s, t)
# ✓ Parameterized gates (rx, ry, rz, p)
# ✓ Two-qubit gates (cx, cz, swap)
# ✓ Three-qubit gates (ccx)
# ✓ Controlled gates showing ctrl@ modifier
# ✓ Inverse gates showing inv@ modifier
# ✓ Global phase gate (gphase)
# ✓ Measurement operations
# ✓ Classical control structures (if/else, for loops)
