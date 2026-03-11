"""
Cirq Implementation: Grover's Algorithm (variable: 2–6 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Grover's Search Algorithm
Category: Search
Qubit Range: 2–6
Framework: Cirq (idiomatic style)

Primary case study (Case Study 2). Uses the SAME marked states as the
Qiskit version for reproducibility.

Idiomatic Cirq conventions:
  - Custom gate classes can be defined as cirq.Gate subclasses for the oracle
    and diffusion operator, or constructed inline from primitive gates
  - cirq.X, cirq.H, cirq.CNOT, cirq.CZ, cirq.CCX (Toffoli gate: cirq.CCX)
  - cirq.ControlledGate for multi-controlled gates of arbitrary size

Key structural difference from Qiskit:
  - Cirq may represent multi-controlled Z (MCZ) as a native gate (e.g., cirq.CCZ
    for 3-qubit or cirq.ControlledGate(cirq.Z, num_controls=n-1))
  - Qiskit decomposes MCZ via mcp(pi, controls, target)
  - PennyLane provides qml.GroverOperator as template (may have fewest gates)
  This three-way comparison is central to Case Study 2.

Marked states (MUST match qiskit/grovers_algorithm.py):
  n=2 → "11", n=3 → "101", n=4 → "1011", n=5 → "10110", n=6 → "101101"

This file is called by:
  - benchmarks/scripts/compile_all.py  (for n ∈ 2..6)
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
  - benchmarks/notebooks/nb04_case_studies.ipynb  (Case Study 2)
"""

# ──────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────

# TODO: import cirq
# TODO: import numpy as np


# ──────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────

# TODO: MARKED_STATES = {2: "11", 3: "101", 4: "1011", 5: "10110", 6: "101101"}


# ──────────────────────────────────────────────────────────
# Helper: Phase Oracle
# ──────────────────────────────────────────────────────────

def build_phase_oracle(qubits, marked_state: str):
    """
    Return a list of Cirq operations implementing the phase oracle.

    Strategy:
      - X on qubits where marked_state bit == '0'
      - Multi-controlled-Z (using cirq.ControlledGate or cirq.CCZ for small n)
      - X again on same qubits

    Returns:
        list[cirq.Operation]: Oracle operations to append to a circuit.
    """

    # TODO: ops = []
    # TODO: For each i where marked_state[i] == '0': ops.append(cirq.X(qubits[i]))
    # TODO: Build MCZ: for n<=3 use cirq.CCZ(*qubits) or cirq.CZ(q0, q1);
    #        for n>3 use cirq.ControlledGate(cirq.Z, num_controls=n-1)(*qubits)
    # TODO: For each i where marked_state[i] == '0': ops.append(cirq.X(qubits[i]))
    # TODO: return ops
    pass


# ──────────────────────────────────────────────────────────
# Helper: Diffusion Operator
# ──────────────────────────────────────────────────────────

def build_diffusion_operator(qubits):
    """
    Return Cirq operations for the Grover diffusion operator (2|s⟩⟨s|-I).

    H⊗n → X⊗n → MCZ → X⊗n → H⊗n

    Returns:
        list[cirq.Operation]
    """

    # TODO: ops = []
    # TODO: H on all qubits
    # TODO: X on all qubits
    # TODO: MCZ (same construction as oracle)
    # TODO: X on all qubits
    # TODO: H on all qubits
    # TODO: return ops
    pass


# ──────────────────────────────────────────────────────────
# Main Circuit
# ──────────────────────────────────────────────────────────

def get_circuit(n: int = 2):
    """
    Build and return the full Cirq Grover's algorithm circuit.

    Args:
        n (int): Number of search qubits (2–6). Default 2.

    Returns:
        cirq.Circuit
    """

    # TODO: qubits = cirq.LineQubit.range(n)
    # TODO: marked_state = MARKED_STATES[n]
    # TODO: num_iterations = int(np.floor(np.pi / 4 * np.sqrt(2**n)))

    # TODO: Build circuit:
    #   - H on all qubits
    #   - Repeat num_iterations: build_phase_oracle + build_diffusion_operator
    #   - cirq.measure(*qubits, key='result')

    # TODO: return cirq.Circuit([...])
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: if __name__ == "__main__": print circuits for n=2, n=3, n=4; print gate counts
