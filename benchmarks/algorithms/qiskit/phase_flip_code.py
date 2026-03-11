"""
Qiskit Implementation: Phase-Flip Error Correcting Code (3 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: 3-Qubit Phase-Flip Error Correction Code
Category: Error Correction
Qubit Range: 3 (fixed: 1 logical qubit + 2 ancilla)
Framework: Qiskit (idiomatic style)

The phase-flip code is the Hadamard-conjugate of the bit-flip code.
It protects against single-qubit phase-flip (Z) errors by working in the
X-basis (Hadamard basis).

Circuit structure:
  1. Encode: Apply H to all qubits, then copy as in bit-flip code
     - Logical |ψ⟩ = α|+⟩+β|−⟩ encoded across all three qubits
     - H on data qubit, cx(data,anc0), cx(data,anc1), H on all 3
  2. (Optional) Error injection: Z gate on one qubit
  3. Syndrome measurement: detect which qubit had a phase flip
     - Apply H to all 3 qubits, then do bit-flip syndrome measurement
  4. Correction: apply Z to the identified qubit

Structural difference from bit-flip code:
  The phase-flip code has an additional layer of H gates wrapping the
  encoding/decoding stages. This doubles the H-gate count compared to
  the bit-flip code. The extra Hadamard layer may or may not be merged
  by each framework's QASM emitter — providing a second comparison point.

This file is called by:
  - benchmarks/scripts/compile_all.py
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
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
    Build and return the full phase-flip error correction circuit.

    Returns:
        QuantumCircuit: A 3-qubit phase-flip code circuit.

    Notes:
        - The phase-flip code is structurally identical to the bit-flip code
          except wrapped in Hadamard gates before and after the CNOT network.
        - Gate count = (H × 3) + (CNOT × 2) + (H × 3) = 8 gates for encoding alone,
          plus syndrome measurement overhead.
    """

    # TODO: Create QuantumRegisters and ClassicalRegisters (same layout as bit_flip_code.py)

    # ── Initialise data qubit ─────────────────────────
    # TODO: Apply H to data qubit → puts it in |+⟩

    # ── Encoding (phase-flip basis) ───────────────────
    # TODO: cx(data[0], ancilla[0])
    # TODO: cx(data[0], ancilla[1])
    # TODO: Apply H to data[0], ancilla[0], ancilla[1]  (rotate to X-basis)

    # ── (Optional) Error injection ────────────────────
    # TODO: Comment marker for where a Z error would be injected
    #   e.g., # qc.z(data[0])  — uncomment to test phase-flip on the data qubit

    # ── Syndrome measurement ──────────────────────────
    # TODO: Apply H to all 3 qubits  (rotate back to Z-basis for measurement)
    # TODO: Parity checks: cx(data[0], anc[0]), measure anc[0] → syndrome[0]
    # TODO:                 cx(data[0], anc[1]), measure anc[1] → syndrome[1]

    # ── Error correction ──────────────────────────────
    # TODO: Apply Z corrections based on syndrome (using c_if)
    #   Z on data[0] if syndrome[0]==1 and syndrome[1]==0
    #   Z on anc[0]  if syndrome[0]==1 and syndrome[1]==1
    #   Z on anc[1]  if syndrome[0]==0 and syndrome[1]==1

    # ── Final measurement ─────────────────────────────
    # TODO: Apply H to data[0] again (decode from X-basis)
    # TODO: Measure data[0] → output[0]

    # TODO: return circuit
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: if __name__ == "__main__":
#   Draw the circuit, print gate count, compare total H count vs. bit_flip_code
