"""
Qiskit Implementation: Bell State (2 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Bell State
Category: Foundational
Qubit Range: 2
Framework: Qiskit (idiomatic style)

This file implements the Bell state preparation circuit idiomatically
in Qiskit, following Qiskit's QuantumCircuit API conventions.
It is part of the benchmark suite for Paper 5.

Idiomatic Qiskit conventions used:
  - QuantumRegister / ClassicalRegister for named registers
  - Method chaining on a QuantumCircuit object (.h(), .cx(), .measure())
  - Little-endian bitstring ordering in measurement output

Expected output distribution:
  |00⟩ → ~50%
  |11⟩ → ~50%
  (after bit-reversal correction for Qiskit's little-endian convention)

This file is called by:
  - benchmarks/scripts/compile_all.py   (to generate QASM 3.0)
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
  - benchmarks/notebooks/nb04_case_studies.ipynb (Case Study 1)
"""

# ──────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────

# TODO: import QuantumCircuit, QuantumRegister, ClassicalRegister from qiskit


# ──────────────────────────────────────────────────────────
# Circuit Definition
# ──────────────────────────────────────────────────────────

def get_circuit():
    """
    Build and return the Qiskit Bell state circuit.

    Returns:
        QuantumCircuit: A 2-qubit circuit with:
          - H gate on qubit 0
          - CNOT gate with control=0, target=1
          - Measurement of both qubits

    Notes:
        - Named registers (qr, cr) are used for clarity in generated QASM.
        - Qiskit outputs bitstrings in little-endian order (qubit 0 is
          the rightmost character). The compile_all.py runner accounts
          for this with the normalize_bitstring() utility.
    """

    # TODO: Create QuantumRegister with 2 qubits named 'q'
    # TODO: Create ClassicalRegister with 2 bits named 'c'
    # TODO: Create QuantumCircuit from both registers

    # TODO: Apply H gate to qubit 0
    # TODO: Apply CNOT (cx) with control=0, target=1
    # TODO: Measure both qubits into the classical register

    # TODO: return the circuit
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point (for quick visual check)
# ──────────────────────────────────────────────────────────

# TODO: Add an if __name__ == "__main__" block that:
#   - calls get_circuit()
#   - prints the circuit diagram (qc.draw('text'))
#   - prints the number of qubits and classical bits
