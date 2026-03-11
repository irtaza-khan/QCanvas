"""
Qiskit Implementation: GHZ State (variable: 3–8 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Greenberger–Horne–Zeilinger (GHZ) State
Category: Foundational
Qubit Range: 3–8 (parameterised on n)
Framework: Qiskit (idiomatic style)

This file implements the n-qubit GHZ state idiomatically in Qiskit.
The GHZ state is the primary algorithm used for SCALING ANALYSIS (RQ4):
  we compile and simulate it for n = 3, 4, 5, 6, 7, 8 and plot how
  gate count, circuit depth, compilation time, and Quantum Volume
  estimate change with n, for each framework.

Idiomatic Qiskit conventions used:
  - Parameterised function that accepts n (number of qubits)
  - QuantumCircuit directly (no named registers needed for simplicity)
  - measure_all() shorthand

Expected output distribution:
  |00...0⟩ → ~50%
  |11...1⟩ → ~50%

This file is called by:
  - benchmarks/scripts/compile_all.py   (for each n in 3..8)
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
  - benchmarks/notebooks/nb03_statistical_analysis.ipynb (scaling fit)
  - benchmarks/notebooks/nb05_figures.ipynb  (Fig. 5 – gate count scaling)
"""

# ──────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────

# TODO: import QuantumCircuit from qiskit


# ──────────────────────────────────────────────────────────
# Circuit Definition
# ──────────────────────────────────────────────────────────

def get_circuit(n: int = 3):
    """
    Build and return the Qiskit GHZ state circuit for n qubits.

    Args:
        n (int): Number of qubits. Must be >= 2. Default 3.
                 For scaling analysis, called with n ∈ {3,4,5,6,7,8}.

    Returns:
        QuantumCircuit: An n-qubit circuit with:
          - H gate on qubit 0
          - CNOT chain: cx(i, i+1) for i in 0..n-2
          - measure_all() at the end

    Notes:
        - Gate count grows linearly as n-1 CNOT gates + 1 H = n gates total.
        - Circuit depth = n (sequential CNOT chain, non-parallelisable).
        - This linear growth is the theoretical baseline; differences across
          frameworks reveal constant overhead from different decomposition
          strategies.
    """

    # TODO: Validate that n >= 2, raise ValueError if not

    # TODO: Create QuantumCircuit with n qubits and n classical bits

    # TODO: Apply H gate to qubit 0
    # TODO: Apply CNOT chain: cx(i, i+1) for i in range(n-1)

    # TODO: measure_all()

    # TODO: return circuit
    pass


# ──────────────────────────────────────────────────────────
# Scaling helper (used by notebooks for the sweep)
# ──────────────────────────────────────────────────────────

def get_scaling_circuits():
    """
    Return a list of (n, circuit) tuples for the full scaling sweep.

    Returns:
        list[tuple[int, QuantumCircuit]]: Circuits for n = 3, 4, 5, 6, 7, 8.

    This is the primary data source for:
      - benchmarks/notebooks/nb01 (static analysis across qubit sizes)
      - benchmarks/notebooks/nb03 (scaling regression)
      - benchmarks/notebooks/nb05 (Fig. 5 line plots)
    """

    # TODO: Return [(n, get_circuit(n)) for n in range(3, 9)]
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: Add if __name__ == "__main__" that:
#   - Prints the GHZ circuit diagram for n=3, n=5, and n=8
#   - Prints gate count and depth for each
