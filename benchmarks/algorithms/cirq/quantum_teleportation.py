"""
Cirq Implementation: Quantum Teleportation (3 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Quantum Teleportation Protocol
Category: Quantum Communication
Qubit Range: 3 (fixed)
Framework: Cirq (idiomatic style)

Same protocol as quantum_teleportation.py in qiskit/, but expressed in Cirq.

Idiomatic Cirq conventions:
  - cirq.ClassicallyControlledOperation for mid-circuit conditioned gates
  - cirq.measure(qubit, key='m0') with named keys for classical bits
  - Operations appended moment-by-moment to preserve causal ordering

Key QASM structural difference:
  Qiskit uses c_if() which generates 'if (c == 1) { x q[2]; }' in QASM 3.0.
  Cirq uses ClassicallyControlledOperation which may generate different QASM
  control-flow syntax. This difference is a primary comparison point.

The qubit layout and protocol steps are IDENTICAL to the Qiskit version
to ensure the oracle (protocol) is semantically equivalent:
  q[0] = Alice's qubit (initialised in |+⟩)
  q[1] = Alice's ancilla (part of Bell pair)
  q[2] = Bob's qubit (will receive |+⟩ after teleportation)

This file is called by:
  - benchmarks/scripts/compile_all.py
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
"""

# ──────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────

# TODO: import cirq


# ──────────────────────────────────────────────────────────
# Circuit Definition
# ──────────────────────────────────────────────────────────

def get_circuit():
    """
    Build and return the Cirq quantum teleportation circuit.

    Returns:
        cirq.Circuit: 3-qubit teleportation circuit with mid-circuit
        measurement and ClassicallyControlledOperation corrections.

    Notes:
        - cirq.measure(q, key='m_alice_0') for each of Alice's measurements
        - cirq.X(q2).on_each() is NOT used here — use cirq.X(q2) directly
        - Classically-controlled operations: use
            cirq.X(q2).with_classical_controls('m_alice_0')
          to apply X on Bob's qubit when measurement 'm_alice_0' == 1.
        - The key name used in measure() must match the key in with_classical_controls().
    """

    # TODO: q0, q1, q2 = cirq.LineQubit.range(3)

    # ── State preparation ──────────────────────────────
    # TODO: cirq.H(q0)  — prepare |+⟩ to teleport

    # ── Bell pair ──────────────────────────────────────
    # TODO: cirq.H(q1), cirq.CNOT(q1, q2)

    # ── Alice's entanglement ───────────────────────────
    # TODO: cirq.CNOT(q0, q1), cirq.H(q0)

    # ── Alice's measurements ───────────────────────────
    # TODO: cirq.measure(q0, key='m0'), cirq.measure(q1, key='m1')

    # ── Bob's corrections ─────────────────────────────
    # TODO: cirq.X(q2).with_classical_controls('m0')
    # TODO: cirq.Z(q2).with_classical_controls('m1')

    # ── Bob's measurement ─────────────────────────────
    # TODO: cirq.measure(q2, key='output')

    # TODO: Assemble all operations into cirq.Circuit([...]) and return
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: if __name__ == "__main__": print circuit, number of operations, moment count
