"""
Qiskit Implementation: Quantum Teleportation (3 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Quantum Teleportation Protocol
Category: Quantum Communication
Qubit Range: 3 (fixed)
Framework: Qiskit (idiomatic style)

This file implements the standard Alice-Bob quantum teleportation protocol
idiomatically in Qiskit. This algorithm is notable because it requires
mid-circuit measurements and classically-controlled gates, which each
framework handles differently — making it an interesting structural
divergence test case.

Qubit layout:
  q[0] = Alice's qubit to teleport (initialised in some state |ψ⟩)
  q[1] = Alice's half of the Bell pair (ancilla)
  q[2] = Bob's qubit (output)

Protocol steps:
  1. Prepare Bell pair between q[1] and q[2]
  2. Alice entangles q[0] with q[1] (CNOT + H)
  3. Alice measures q[0] and q[1] → classical bits c[0], c[1]
  4. Bob applies X gate conditionally on c[0]
  5. Bob applies Z gate conditionally on c[1]
  6. Bob's qubit q[2] is now in state |ψ⟩

Idiomatic Qiskit convention:
  - c_if() for classically-controlled operations (Qiskit-specific)
  - measure() into named classical bits before conditional gates

Key structural difference vs Cirq / PennyLane:
  - Qiskit uses c_if() on gate objects
  - Cirq uses ClassicallyControlledOperation  
  - PennyLane uses qml.cond() with qml.measure() (newer API)
  This difference may produce different QASM 3.0 control-flow syntax.

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
    Build and return the Qiskit quantum teleportation circuit.

    Returns:
        QuantumCircuit: A 3-qubit circuit implementing the teleportation
        protocol with mid-circuit measurement and classically-controlled
        correction gates.

    Notes:
        - The initial state of q[0] can be |+⟩ (H applied) or any single-qubit
          rotation. Use |+⟩ as the state to teleport for this benchmark.
        - The classically-controlled X and Z gates use Qiskit's c_if() method,
          which generates QASM 3.0 'if' statements in the output.
        - Verify correctness: after teleportation, q[2] should be in state |+⟩,
          giving a uniform measurement distribution (50/50 on |0⟩ / |1⟩).
    """

    # TODO: Create 3 QuantumRegisters and 3 ClassicalRegisters (or use 2+1 layout)

    # ── State preparation ──────────────────────────────
    # TODO: Apply H to q[0] to set it in state |+⟩ (the state to teleport)

    # ── Bell pair creation ─────────────────────────────
    # TODO: Apply H to q[1]
    # TODO: Apply CNOT (cx) with control=q[1], target=q[2]

    # ── Alice's operations ─────────────────────────────
    # TODO: Apply CNOT with control=q[0], target=q[1]
    # TODO: Apply H to q[0]

    # ── Alice's measurements ───────────────────────────
    # TODO: Measure q[0] → c[0]
    # TODO: Measure q[1] → c[1]

    # ── Bob's corrections (classically controlled) ─────
    # TODO: Apply X to q[2] conditioned on c[0] == 1  (use c_if)
    # TODO: Apply Z to q[2] conditioned on c[1] == 1  (use c_if)

    # ── Final measurement ─────────────────────────────
    # TODO: Measure q[2] → c[2]

    # TODO: return circuit
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: Add if __name__ == "__main__" that:
#   - Calls get_circuit() and prints the circuit diagram
#   - Notes the total gate count and classical control flow structure
