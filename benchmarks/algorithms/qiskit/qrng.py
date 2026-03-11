"""
Qiskit Implementation: QRNG – Quantum Random Number Generator (variable: 4–8 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Quantum Random Number Generator (QRNG)
Category: Randomness
Qubit Range: 4–8
Framework: Qiskit (idiomatic style)

The QRNG circuit applies a Hadamard gate to every qubit, placing them all
in equal superposition, then measures. The output is a uniformly random
bitstring of length n.

This is the SIMPLEST possible algorithm in the benchmark suite (after Bell).
Its purpose is to isolate pure Hadamard-translation overhead. Since there are
no multi-qubit gates, any gate-count difference across frameworks is entirely
due to how each framework translates the H gate and measurement to QASM 3.0.

Expected output: uniform distribution over all 2^n bitstrings.
  Each bitstring should appear with probability 1/2^n.

Scaling behaviour:
  Gate count = n (exactly n Hadamard gates)
  Circuit depth = 1 (all gates are parallelisable)
  This gives a theoretical lower bound on circuit depth for n qubits.
  Frameworks that add any overhead (e.g., extra barrier gates) will show
  depth > 1, which is measurable.

This file is called by:
  - benchmarks/scripts/compile_all.py  (for n ∈ 4..8)
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
  - benchmarks/notebooks/nb03_statistical_analysis.ipynb (scaling baseline)
"""

# ──────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────

# TODO: import QuantumCircuit from qiskit


# ──────────────────────────────────────────────────────────
# Circuit Definition
# ──────────────────────────────────────────────────────────

def get_circuit(n: int = 4):
    """
    Build and return the Qiskit QRNG circuit for n qubits.

    Args:
        n (int): Number of qubits (4–8). Default 4.

    Returns:
        QuantumCircuit: An n-qubit circuit with:
          - H gate on every qubit (applied in a single loop)
          - Measurement of all qubits

    Notes:
        - Expected circuit depth = 1 (parallel Hadamards) + 1 (measurement).
        - Gate count = n Hadamards + n measurements = 2n gates total.
        - Any deviation from depth=1 in the generated QASM reveals framework
          overhead or sequential emission strategies.
    """

    # TODO: Create QuantumCircuit with n qubits and n classical bits

    # TODO: Apply H gate to every qubit in range(n)

    # TODO: Measure all qubits (use measure_all() or explicit loop)

    # TODO: return circuit
    pass


# ──────────────────────────────────────────────────────────
# Scaling helper
# ──────────────────────────────────────────────────────────

def get_scaling_circuits():
    """
    Return (n, circuit) pairs for the full QRNG scaling sweep (n=4..8).

    Used by:
      - nb01 for static analysis
      - nb03 for scaling regression (depth should remain constant at 1)
      - nb05 for Fig. 5 line plots (QRNG is the flat baseline)
    """

    # TODO: return [(n, get_circuit(n)) for n in range(4, 9)]
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: Add if __name__ == "__main__" that:
#   - Prints the QRNG circuit for n=4 and n=8
#   - Verifies depth == 1 (or notes if > 1 and why)
