"""
Qiskit Implementation: Bit-Flip Error Correcting Code (3 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: 3-Qubit Bit-Flip Error Correction Code
Category: Error Correction
Qubit Range: 3 (fixed: 1 logical qubit + 2 ancilla)
Framework: Qiskit (idiomatic style)

The bit-flip code encodes one logical qubit into three physical qubits to
protect against single-qubit bit-flip (X) errors. This benchmark tests
whether each framework and QCanvas's parsers correctly handle:
  - Ancilla qubit initialisation
  - Syndrome measurement circuits
  - Classical feedback (correction operations)

Circuit structure:
  1. Encode: Map logical |ψ⟩ = α|0⟩+β|1⟩ to α|000⟩+β|111⟩
     - cx(0,1), cx(0,2)  (copy logical qubit 0 to ancilla qubits 1 and 2)
  2. Error injection (for simulation): optionally flip one qubit with X gate
     - For this benchmark: no error injected (ideal encoding/decoding)
  3. Syndrome measurement:
     - p1 = measure(cx(0,1)) → detects if qubits 0 and 1 differ
     - p2 = measure(cx(0,2)) → detects if qubits 0 and 2 differ
  4. Correction: apply X to the qubit identified as flipped by syndrome
     - Implemented as classically-controlled operations

This is primarily of interest for testing QASM 3.0 classical control flow
(if/else statements in the generated QASM) and multi-register handling.

Key structural comparison:
  Qiskit's classical control uses c_if() → generates 'if' blocks in QASM 3.0
  Cirq uses ClassicallyControlledOperation
  PennyLane uses qml.cond() — may have different QASM structure

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
    Build and return the full bit-flip error correction circuit.

    Returns:
        QuantumCircuit: A 3-qubit circuit implementing:
          - Encoding stage
          - Syndrome measurement
          - Classical error correction

    Notes:
        - Qubit 0 is the data qubit (initialised in |+⟩ for this benchmark)
        - Qubits 1 and 2 are ancilla (initialised in |0⟩)
        - Two classical bits for syndrome measurement (s0, s1)
        - One classical bit for the final readout of the corrected logical qubit
    """

    # TODO: Create 3 QuantumRegisters: data (1 qubit), ancilla (2 qubits)
    # TODO: Create 3 ClassicalRegisters: syndrome (2 bits), output (1 bit)

    # ── Initialise data qubit ─────────────────────────
    # TODO: Apply H to data qubit to put it in |+⟩ (arbitrary state to protect)

    # ── Encoding ──────────────────────────────────────
    # TODO: cx(data[0], ancilla[0])  — copy data to ancilla 0
    # TODO: cx(data[0], ancilla[1])  — copy data to ancilla 1

    # ── (Optional) Error injection ────────────────────
    # TODO: Add a commented barrier here to indicate where an error could be injected
    #   e.g., # qc.x(ancilla[0])  — uncomment to inject a bit-flip error on ancilla[0]

    # ── Syndrome measurement ──────────────────────────
    # TODO: cx(data[0], ancilla[0]), then measure ancilla[0] → syndrome[0]
    # TODO: cx(data[0], ancilla[1]), then measure ancilla[1] → syndrome[1]

    # ── Error correction ──────────────────────────────
    # TODO: Apply X to data[0] conditioned on syndrome[0]==1 and syndrome[1]==0   (c_if)
    # TODO: Apply X to ancilla[0] conditioned on syndrome[0]==1 and syndrome[1]==1 (c_if)
    # TODO: Apply X to ancilla[1] conditioned on syndrome[0]==0 and syndrome[1]==1 (c_if)

    # ── Final measurement ─────────────────────────────
    # TODO: Measure data[0] → output[0]

    # TODO: return circuit
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: Add if __name__ == "__main__" that:
#   - Draws the full circuit
#   - Prints the total gate count including classical control
#   - Prints the number of classical bits used
