"""
Qiskit Implementation: Bernstein–Vazirani Algorithm (variable: 3–8 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Bernstein–Vazirani
Category: Oracle-Based
Qubit Range: 3–8 (n input qubits + 1 ancilla)
Framework: Qiskit (idiomatic style)

The Bernstein–Vazirani algorithm recovers a hidden secret string s ∈ {0,1}^n
using a single quantum query to the oracle f(x) = s·x mod 2.

The oracle encodes the secret string by applying CNOT gates from each qubit
where s[i] == 1 to the ancilla qubit. The resulting measurement of the input
register directly reveals s.

Reproducibility:
  The secret string is fixed as a module-level constant so all frameworks
  use the IDENTICAL oracle. This ensures structural differences in the
  generated QASM come solely from framework conventions, not from different
  oracle encodings.

Fixed secrets used in the benchmark:
  n=3 → s = "101"
  n=4 → s = "1011"
  n=5 → s = "10110"
  n=6 → s = "101101"
  n=7 → s = "1011010"
  n=8 → s = "10110100"

Key metric for paper:
  Simpler oracle than Deutsch–Jozsa, so the gate count difference between
  frameworks is more clearly attributable to framework overhead rather than
  oracle complexity. Serves as a clean baseline for cross-framework comparison.

This file is called by:
  - benchmarks/scripts/compile_all.py
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
"""

# ──────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────

# TODO: import QuantumCircuit from qiskit


# ──────────────────────────────────────────────────────────
# Constants — fixed secret strings for reproducibility
# ──────────────────────────────────────────────────────────

# TODO: Define SECRET_STRINGS dict mapping n → secret string
#   e.g., SECRET_STRINGS = {3: "101", 4: "1011", 5: "10110", ...}
#   Keeping this identical across all three framework files is critical
#   for a fair cross-framework comparison.


# ──────────────────────────────────────────────────────────
# Circuit Definition
# ──────────────────────────────────────────────────────────

def get_circuit(n: int = 3):
    """
    Build and return the Qiskit Bernstein–Vazirani circuit.

    Args:
        n (int): Number of input qubits. Total qubits = n+1. Default 3.

    Returns:
        QuantumCircuit: The BV circuit. Measuring input qubits should
        yield exactly the secret string SECRET_STRINGS[n].

    Circuit structure:
        1. ancilla = |−⟩  (X then H)
        2. H⊗n on input qubits
        3. Oracle: cx(i, ancilla) for each i where s[i] == '1'
        4. H⊗n on input qubits again
        5. Measure input qubits

    Notes:
        - The number of CNOT gates in the oracle = Hamming weight of s.
        - Circuit depth is dominated by the parallel H layers (depth 1 each)
          and the sequential oracle CNOTs (depth = Hamming weight of s,
          assuming no parallelism between them).
    """

    # TODO: Validate n is in SECRET_STRINGS, raise ValueError if not
    # TODO: Retrieve secret = SECRET_STRINGS[n]

    # TODO: Create QuantumCircuit with n+1 qubits and n classical bits

    # ── Ancilla preparation ────────────────────────────
    # TODO: Apply X then H to ancilla qubit (index n)

    # ── Input Hadamard layer ───────────────────────────
    # TODO: Apply H to all n input qubits

    # ── Oracle ─────────────────────────────────────────
    # TODO: barrier
    # TODO: For each index i where secret[i] == '1', apply cx(i, n)
    # TODO: barrier

    # ── Second Hadamard layer ──────────────────────────
    # TODO: Apply H to all n input qubits

    # ── Measurement ───────────────────────────────────
    # TODO: Measure input qubits 0..n-1 into classical bits

    # TODO: return circuit
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: Add if __name__ == "__main__" that:
#   - Iterates over n = 3..6 and prints each circuit diagram
#   - Prints the secret string used and the total number of oracle CNOTs
