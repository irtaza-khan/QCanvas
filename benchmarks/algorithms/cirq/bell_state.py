"""
Cirq Implementation: Bell State (2 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Bell State
Category: Foundational
Qubit Range: 2
Framework: Cirq (idiomatic style)

This file implements the Bell state preparation circuit idiomatically in Cirq,
following Google's Cirq library conventions and moment-based circuit construction.
It is Part of the benchmark suite for Paper 5.

Idiomatic Cirq conventions used:
  - cirq.LineQubit for qubit allocation
  - cirq.Circuit with a list of gate operations (not method-chained)
  - cirq.CNOT (not cirq.CX — Cirq uses the full name)
  - cirq.measure() with a string key parameter
  - Natural (big-endian) bitstring ordering (opposite of Qiskit)

Key QASM structural difference vs Qiskit:
  - Cirq may emit the CNOT as 'ctrl @ x q[1];' using QASM 3.0 modifier syntax
    rather than the traditional 'cx q[0], q[1];' form
  - The qubit register declaration may differ (named vs unnamed)
  - Measurement key names appear in the generated QASM as comments

Expected output distribution:
  |00⟩ → ~50%
  |11⟩ → ~50%
  (Cirq uses natural/big-endian ordering; no reversal needed unlike Qiskit)

This file is called by:
  - benchmarks/scripts/compile_all.py
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
  - benchmarks/notebooks/nb04_case_studies.ipynb (Case Study 1)
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
    Build and return the Cirq Bell state circuit.

    Returns:
        cirq.Circuit: A 2-qubit circuit with:
          - H gate on q0
          - CNOT gate (control=q0, target=q1)
          - Measurement of both qubits with key 'result'

    Notes:
        - cirq.LineQubit.range(2) creates qubits at positions 0 and 1.
        - All operations are passed as a list to cirq.Circuit([...]).
        - The 'result' key in cirq.measure() identifies the measurement in outputs.
        - Cirq's simulator returns bitstrings in row-major order (q0 leftmost).
    """

    # TODO: Create q0, q1 = cirq.LineQubit.range(2)

    # TODO: Build circuit with:
    #   - cirq.H(q0)
    #   - cirq.CNOT(q0, q1)
    #   - cirq.measure(q0, q1, key='result')

    # TODO: return circuit
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: if __name__ == "__main__":
#   - Call get_circuit() and print the circuit
#   - Print the number of qubits, moments, and operations
