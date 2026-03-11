"""
Cirq Implementation: GHZ State (variable: 3–8 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: GHZ State
Category: Foundational
Qubit Range: 3–8
Framework: Cirq (idiomatic style)

Idiomatic Cirq conventions used:
  - cirq.LineQubit.range(n) for n-qubit allocation
  - Moment-based construction: H in one moment, then CNOT chain in subsequent moments
  - cirq.measure_each() for measuring all qubits with individual keys
    (alternative: cirq.measure(*qubits, key='result'))

Structural difference vs Qiskit:
  - Cirq's CNOT chain may be scheduled into a different number of moments
    depending on whether the simulator enforces sequential CNOT ordering.
  - Moment structure can cause circuit depth to differ even for identical logical gates.

This file is called by:
  - benchmarks/scripts/compile_all.py  (for n ∈ 3..8)
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
  - benchmarks/notebooks/nb03_statistical_analysis.ipynb (scaling)
  - benchmarks/notebooks/nb05_figures.ipynb (Fig. 5)
"""

# ──────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────

# TODO: import cirq


# ──────────────────────────────────────────────────────────
# Circuit Definition
# ──────────────────────────────────────────────────────────

def get_circuit(n: int = 3):
    """
    Build and return the Cirq GHZ state circuit for n qubits.

    Args:
        n (int): Number of qubits. Default 3.

    Returns:
        cirq.Circuit: The GHZ state circuit.

    Notes:
        - Use cirq.Circuit() and append operations with explicit moment separation.
        - The CNOT chain should be: cirq.CNOT(qubits[i], qubits[i+1]) for i in range(n-1)
        - Measure all qubits with key='result' using cirq.measure(*qubits, key='result')
    """

    # TODO: qubits = cirq.LineQubit.range(n)
    # TODO: Create cirq.Circuit and append:
    #   - cirq.H(qubits[0])
    #   - [cirq.CNOT(qubits[i], qubits[i+1]) for i in range(n-1)]
    #   - cirq.measure(*qubits, key='result')
    # TODO: return circuit
    pass


# ──────────────────────────────────────────────────────────
# Scaling helper
# ──────────────────────────────────────────────────────────

def get_scaling_circuits():
    """
    Return (n, circuit) pairs for scaling sweep (n=3..8).
    Used by nb01, nb03, and nb05.
    """

    # TODO: return [(n, get_circuit(n)) for n in range(3, 9)]
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: if __name__ == "__main__": print GHZ circuits for n=3, 5, 8
