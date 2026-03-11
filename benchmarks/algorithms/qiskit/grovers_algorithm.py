"""
Qiskit Implementation: Grover's Algorithm (variable: 2–6 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Grover's Search Algorithm
Category: Search
Qubit Range: 2–6 (n search qubits)
Framework: Qiskit (idiomatic style)

Grover's algorithm provides a quadratic speedup for unstructured search.
For an n-qubit search space of N = 2^n states, it finds the marked state
with high probability using O(√N) oracle queries.

This is the PRIMARY CASE STUDY algorithm for Paper 5 (Case Study 2).
It is expected to show the HIGHEST gate-count divergence across frameworks
because both the oracle AND the diffusion operator can be decomposed
in multiple ways.

Marked states used (fixed for reproducibility):
  n=2 → marked state |11⟩
  n=3 → marked state |101⟩
  n=4 → marked state |1011⟩
  n=5 → marked state |10110⟩
  n=6 → marked state |101101⟩

Number of Grover iterations used:
  floor(π/4 × √(2^n))  — optimal number for single marked state

Circuit structure:
  1. H⊗n (equal superposition)
  2. Repeat k times:
     a. Phase oracle (marks the target state with a phase flip)
     b. Diffusion operator (2|s⟩⟨s| - I)
  3. Measure all qubits

Idiomatic Qiskit conventions:
  - Phase oracle: X gates on zero-bits, multi-controlled Z (mcz), X again
  - Diffusion: H⊗n → X⊗n → multi-controlled Z → X⊗n → H⊗n
  - Qiskit's QuantumCircuit.compose() for building sub-circuits

Key structural differences vs other frameworks:
  - Qiskit decomposes multi-controlled Z into CX + ancilla chains
  - Cirq may use a custom gate or native CCZ
  - PennyLane provides qml.GroverOperator as a built-in template
    which may have a different gate count than a hand-built version

This file is called by:
  - benchmarks/scripts/compile_all.py  (for n ∈ 2..6)
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
  - benchmarks/notebooks/nb04_case_studies.ipynb  (Case Study 2)
  - benchmarks/notebooks/nb03_statistical_analysis.ipynb (scaling analysis)
"""

# ──────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────

# TODO: import QuantumCircuit from qiskit
# TODO: import numpy as np  (for computing number of iterations)


# ──────────────────────────────────────────────────────────
# Constants — fixed marked states per qubit count
# ──────────────────────────────────────────────────────────

# TODO: Define MARKED_STATES dict mapping n → bitstring of the marked state
#   e.g., MARKED_STATES = {2: "11", 3: "101", 4: "1011", 5: "10110", 6: "101101"}
#   IMPORTANT: Use the same marked states in the Cirq and PennyLane files.


# ──────────────────────────────────────────────────────────
# Helper: Phase Oracle sub-circuit
# ──────────────────────────────────────────────────────────

def build_phase_oracle(n: int, marked_state: str):
    """
    Build the phase oracle sub-circuit that flips the phase of the marked state.

    Strategy:
      1. Apply X gate to qubits where marked_state[i] == '0' (flip 0-bits to 1)
      2. Apply multi-controlled-Z (or equivalent) — flips phase only when all qubits are |1⟩
      3. Apply X gate again to the same qubits (undo the flip)

    Args:
        n (int): Number of qubits.
        marked_state (str): Bitstring of the target state (length n).

    Returns:
        QuantumCircuit: Oracle sub-circuit (n qubits, no measurements).

    Notes:
        - Multi-controlled-Z (MCZ) on n qubits decomposes to a sequence of
          Toffoli gates in Qiskit. This is the primary source of gate-count
          variation between frameworks.
        - Qiskit's .mcp(pi, controls, target) or custom MCZ decomposition
          can be used here.
    """

    # TODO: Create QuantumCircuit with n qubits
    # TODO: Apply X to qubits where marked_state[qubit_index] == '0'
    # TODO: Apply multi-controlled Z: mcp(pi, list(range(n-1)), n-1) or equivalent
    # TODO: Apply X again to same qubits
    # TODO: return oracle circuit
    pass


# ──────────────────────────────────────────────────────────
# Helper: Diffusion Operator sub-circuit
# ──────────────────────────────────────────────────────────

def build_diffusion_operator(n: int):
    """
    Build the Grover diffusion operator: 2|s⟩⟨s| - I

    Standard decomposition:
      H⊗n → X⊗n → multi-controlled-Z → X⊗n → H⊗n

    Args:
        n (int): Number of qubits.

    Returns:
        QuantumCircuit: Diffusion sub-circuit (n qubits, no measurements).

    Notes:
        - This is also called the 'inversion about the mean' operator.
        - It is composed with the oracle to form a single Grover iteration.
        - The multi-controlled-Z here is structurally identical to the one
          in the oracle, so gate count scales the same way.
    """

    # TODO: Create QuantumCircuit with n qubits
    # TODO: Apply H to all qubits
    # TODO: Apply X to all qubits
    # TODO: Apply multi-controlled Z
    # TODO: Apply X to all qubits
    # TODO: Apply H to all qubits
    # TODO: return diffusion circuit
    pass


# ──────────────────────────────────────────────────────────
# Main Circuit
# ──────────────────────────────────────────────────────────

def get_circuit(n: int = 2):
    """
    Build and return the full Grover's algorithm circuit for n qubits.

    Args:
        n (int): Number of search qubits (2–6). Default 2.

    Returns:
        QuantumCircuit: Complete Grover circuit with optimal number of
        iterations. Measuring all qubits should yield the marked state
        with high probability (>80% for optimal iterations).

    Notes:
        - Number of iterations k = floor(π/4 × √(2^n))
        - For n=2: k=1, for n=3: k=2, for n=4: k=3, etc.
        - Each iteration = build_phase_oracle + build_diffusion_operator
        - The circuits are composed with QuantumCircuit.compose()
    """

    # TODO: Validate n is in range 2..6
    # TODO: Get marked_state from MARKED_STATES[n]
    # TODO: Compute num_iterations = int(np.floor(np.pi / 4 * np.sqrt(2**n)))

    # TODO: Create main QuantumCircuit with n qubits and n classical bits
    # TODO: Apply H⊗n (initial superposition)

    # TODO: Loop num_iterations times:
    #   - Compose in the phase oracle
    #   - Compose in the diffusion operator

    # TODO: Measure all qubits
    # TODO: return circuit
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: Add if __name__ == "__main__" that:
#   - Runs get_circuit(n) for n = 2, 3, 4 and prints circuit diagram
#   - Prints the marked state and number of Grover iterations for each n
#   - Prints the total gate count for each n
