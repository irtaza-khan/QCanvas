"""
Cirq Implementation: Bernstein–Vazirani Algorithm (variable: 3–8 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Bernstein–Vazirani
Category: Oracle-Based
Qubit Range: 3–8
Framework: Cirq (idiomatic style)

Same algorithm as bernstein_vazirani.py in qiskit/, implemented in Cirq.
Uses the SAME fixed secret strings (imported from the Qiskit version or
re-declared as a shared constant) for reproducibility.

Idiomatic Cirq conventions:
  - cirq.LineQubit.range(n+1)
  - Explicit moment grouping for H layers and oracle CNOTs

Fixed secrets (MUST match qiskit/bernstein_vazirani.py and pennylane/bernstein_vazirani.py):
  n=3 → "101", n=4 → "1011", n=5 → "10110", n=6 → "101101", ...

This file is called by:
  - benchmarks/scripts/compile_all.py
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
"""

# ──────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────

# TODO: import cirq


# ──────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────

# TODO: SECRET_STRINGS = {3: "101", 4: "1011", 5: "10110", 6: "101101", 7: "1011010", 8: "10110100"}
# NOTE: Must be identical to the Qiskit and PennyLane versions


# ──────────────────────────────────────────────────────────
# Circuit Definition
# ──────────────────────────────────────────────────────────

def get_circuit(n: int = 3):
    """
    Build and return the Cirq Bernstein–Vazirani circuit.

    Args:
        n (int): Number of input qubits (3–8).

    Returns:
        cirq.Circuit
    """

    # TODO: Validate n in SECRET_STRINGS
    # TODO: qubits = cirq.LineQubit.range(n+1); ancilla = qubits[n]
    # TODO: secret = SECRET_STRINGS[n]

    # ── Ancilla prep ──────────────────────────────────
    # TODO: cirq.X(ancilla), cirq.H(ancilla)

    # ── Input H layer ─────────────────────────────────
    # TODO: [cirq.H(qubits[i]) for i in range(n)]

    # ── Oracle ────────────────────────────────────────
    # TODO: [cirq.CNOT(qubits[i], ancilla) for i where secret[i]=='1']

    # ── Second H layer ────────────────────────────────
    # TODO: [cirq.H(qubits[i]) for i in range(n)]

    # ── Measurement ───────────────────────────────────
    # TODO: cirq.measure(*qubits[:n], key='result')

    # TODO: return cirq.Circuit([...])
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: if __name__ == "__main__": print circuits for n=3 and n=6, print oracle CNOT counts
