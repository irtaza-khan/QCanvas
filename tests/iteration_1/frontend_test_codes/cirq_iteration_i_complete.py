"""
Cirq Complete Iteration I Feature Test

This circuit demonstrates ALL Iteration I features that should be
converted to OpenQASM 3.0 by the QCanvas platform.

Paste this code into the QCanvas frontend to test conversion.

Expected Output: OpenQASM 3.0 code with all Iteration I features
"""

import cirq
import numpy as np

def get_circuit():
    # Create qubits
    q0, q1, q2, q3, q4 = cirq.LineQubit.range(5)
    
    # Create circuit
    circuit = cirq.Circuit()
    
    # === ITERATION I FEATURE 1: Basic Single-Qubit Gates ===
    circuit.append(cirq.H(q0))  # Hadamard
    circuit.append(cirq.X(q1))  # Pauli-X
    circuit.append(cirq.Y(q2))  # Pauli-Y
    circuit.append(cirq.Z(q3))  # Pauli-Z
    circuit.append(cirq.S(q0))  # S gate
    circuit.append(cirq.T(q1))  # T gate
    circuit.append(cirq.S(q2)**-1)  # S dagger (inverse)
    circuit.append(cirq.T(q3)**-1)  # T dagger (inverse)
    
    # === ITERATION I FEATURE 2: Parameterized Gates ===
    circuit.append(cirq.rx(np.pi/2)(q0))  # RX rotation
    circuit.append(cirq.ry(np.pi/4)(q1))  # RY rotation
    circuit.append(cirq.rz(np.pi)(q2))    # RZ rotation
    circuit.append(cirq.ZPowGate(exponent=0.5)(q3))  # Phase-like gate
    
    # === ITERATION I FEATURE 3: Two-Qubit Gates ===
    circuit.append(cirq.CNOT(q0, q1))  # Controlled-X
    circuit.append(cirq.CZ(q1, q2))    # Controlled-Z
    circuit.append(cirq.SWAP(q0, q2))  # SWAP
    
    # === ITERATION I FEATURE 4: Three-Qubit Gates ===
    circuit.append(cirq.TOFFOLI(q0, q1, q2))  # Toffoli (CCX)
    circuit.append(cirq.FREDKIN(q0, q1, q2))  # Fredkin (CSWAP)
    
    # === ITERATION I FEATURE 5: Special Gates ===
    circuit.append(cirq.I(q0))  # Identity
    circuit.append(cirq.GlobalPhaseGate(np.pi/4))  # Global phase
    
    # === ITERATION I FEATURE 6: Gate Modifiers - Inverse ===
    # Inverse modifier: inv@
    circuit.append(cirq.H(q0)**-1)  # Inverse Hadamard
    circuit.append(cirq.S(q1)**-1)  # Inverse S (sdg)
    
    # === ITERATION I FEATURE 7: Gate Modifiers - Control ===
    # Control modifier: ctrl@
    circuit.append(cirq.ControlledGate(cirq.H)(q0, q1))  # Controlled-H
    
    # === ITERATION I FEATURE 8: Barrier ===
    # Cirq doesn't have built-in barrier, but we can add a comment
    # The converter should recognize this pattern
    circuit.append(cirq.WaitGate(duration=cirq.Duration())(q0, q1, q2) if hasattr(cirq, 'WaitGate') else cirq.I(q0))
    
    # === ITERATION I FEATURE 9: Reset ===
    circuit.append(cirq.reset(q4))
    
    # === ITERATION I FEATURE 10: Measurements ===
    circuit.append(cirq.measure(q0, key='m0'))
    circuit.append(cirq.measure(q1, key='m1'))
    circuit.append(cirq.measure(q2, key='m2'))
    circuit.append(cirq.measure(q3, key='m3'))
    circuit.append(cirq.measure(q4, key='m4'))
    
    # === ITERATION I FEATURE 11: Gate Broadcasting ===
    # Apply same gate to multiple qubits
    circuit.append([cirq.H(q) for q in [q0, q1, q2]])
    
    return circuit

# Expected OpenQASM 3.0 features in output:
# ✓ OPENQASM 3.0;
# ✓ include "stdgates.inc";
# ✓ Mathematical constants (PI, E, PI_2, PI_4)
# ✓ qubit[5] q;
# ✓ bit[5] c;
# ✓ Classical variables (int, uint, float, angle, bool)
# ✓ All standard gates
# ✓ Parameterized gates with proper angle formatting
# ✓ Two-qubit and three-qubit gates
# ✓ Global phase gate (gphase)
# ✓ Gate modifiers (inv@, ctrl@)
# ✓ Reset instruction
# ✓ Measurement instruction
# ✓ Classical control flow (if/else, for loops)
