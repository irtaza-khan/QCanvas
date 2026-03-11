"""
Qiskit Implementation: Deutsch–Jozsa Algorithm (variable: 3–8 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Deutsch–Jozsa
Category: Oracle-Based
Qubit Range: 3–8 (n input qubits + 1 ancilla = n+1 total)
Framework: Qiskit (idiomatic style)

The Deutsch–Jozsa algorithm determines whether an n-bit boolean function
f:{0,1}^n → {0,1} is constant or balanced, using a single query to the
quantum oracle.

This benchmark implements TWO oracle variants:
  - get_circuit_constant()  →  constant oracle (f always returns 0)
  - get_circuit_balanced()  →  balanced oracle (f returns 0 for half inputs, 1 for the other half)

Circuit structure (n input qubits + 1 ancilla):
  1. Prepare ancilla in |−⟩ = H|1⟩
  2. Apply H⊗n to all input qubits
  3. Apply oracle U_f
  4. Apply H⊗n again to input qubits
  5. Measure input qubits
     - All zeros → constant function
     - At least one 1 → balanced function

Key metric for paper:
  Oracle encoding is the PRIMARY source of gate-count variation between
  frameworks. The diffusion + oracle section may decompose CNOT sequences
  very differently across Qiskit, Cirq, and PennyLane.

This file is called by:
  - benchmarks/scripts/compile_all.py  (for n ∈ 3..8, both oracle types)
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
  - benchmarks/notebooks/nb03_statistical_analysis.ipynb (scaling)
"""

# ──────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────

# TODO: import QuantumCircuit from qiskit


# ──────────────────────────────────────────────────────────
# Constants Oracle
# ──────────────────────────────────────────────────────────

def get_circuit_constant(n: int = 3):
    """
    Build the Deutsch–Jozsa circuit with a CONSTANT oracle (f always 0).

    Args:
        n (int): Number of input qubits. Total qubits = n + 1 (ancilla).

    Returns:
        QuantumCircuit: Full Deutsch–Jozsa circuit. Measuring input
        qubits should always yield all-zeros (00...0).

    Oracle implementation:
        Constant-0 oracle: do nothing (identity). Zero gates added.
        This is the trivial baseline — useful for measuring the framework's
        overhead for the non-oracle portions of the circuit.
    """

    # TODO: Create QuantumCircuit with n+1 qubits and n classical bits
    #       (index n is the ancilla qubit)

    # ── Initial state preparation ──────────────────────
    # TODO: Apply X then H to ancilla qubit (index n) → puts ancilla in |−⟩
    # TODO: Apply H to all n input qubits (range(n))

    # ── Constant oracle (identity — no gates needed) ───
    # TODO: Add a barrier to separate oracle from rest of circuit (improves clarity in QASM)

    # ── Second Hadamard layer ──────────────────────────
    # TODO: Apply H to all n input qubits again

    # ── Measurement ───────────────────────────────────
    # TODO: Measure input qubits 0..n-1 into classical bits 0..n-1

    # TODO: return circuit
    pass


# ──────────────────────────────────────────────────────────
# Balanced Oracle
# ──────────────────────────────────────────────────────────

def get_circuit_balanced(n: int = 3):
    """
    Build the Deutsch–Jozsa circuit with a BALANCED oracle.

    Args:
        n (int): Number of input qubits. Total qubits = n + 1 (ancilla).

    Returns:
        QuantumCircuit: Full Deutsch–Jozsa circuit. Measuring input
        qubits should yield a non-zero result (confirming balanced function).

    Oracle implementation:
        The standard balanced oracle applies CNOT gates from each input qubit
        to the ancilla: cx(i, n) for i in range(n).
        This flips the ancilla for exactly half the input combinations,
        making f balanced. The number of CNOT gates scales linearly with n —
        this is the key metric for the scaling analysis.
    """

    # TODO: Create QuantumCircuit with n+1 qubits and n classical bits

    # ── Initial state preparation ──────────────────────
    # TODO: Apply X then H to ancilla
    # TODO: Apply H to all n input qubits

    # ── Balanced oracle ────────────────────────────────
    # TODO: Apply barrier
    # TODO: Apply CNOT from each input qubit i to ancilla (n): cx(i, n)
    # TODO: Apply barrier

    # ── Second Hadamard layer ──────────────────────────
    # TODO: Apply H to all n input qubits

    # ── Measurement ───────────────────────────────────
    # TODO: Measure qubits 0..n-1

    # TODO: return circuit
    pass


# ──────────────────────────────────────────────────────────
# Convenience wrapper
# ──────────────────────────────────────────────────────────

def get_circuit(n: int = 3, oracle_type: str = "balanced"):
    """
    Convenience dispatcher.

    Args:
        n (int): Number of input qubits.
        oracle_type (str): 'constant' or 'balanced'. Default 'balanced'.

    Returns:
        QuantumCircuit

    Used by compile_all.py to iterate over both oracle types and qubit sizes.
    """

    # TODO: if oracle_type == 'constant': return get_circuit_constant(n)
    # TODO: elif oracle_type == 'balanced': return get_circuit_balanced(n)
    # TODO: else raise ValueError(f"Unknown oracle_type: {oracle_type}")
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: Add if __name__ == "__main__" that:
#   - Runs get_circuit(n=3, oracle_type='constant') and prints diagram
#   - Runs get_circuit(n=3, oracle_type='balanced') and prints diagram
#   - Prints gate counts for both
