"""
Qiskit Implementation: QAOA – Quantum Approximate Optimisation Algorithm (variable: 2–6 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Quantum Approximate Optimisation Algorithm (QAOA)
Category: Variational
Qubit Range: 2–6 (n qubits representing graph nodes)
Framework: Qiskit (idiomatic style)

QAOA finds approximate solutions to combinatorial optimisation problems.
We use the MaxCut problem on a fixed graph as the benchmark target.

Problem: MaxCut on a triangle graph (3-node complete graph K3)
  Edges: (0,1), (1,2), (0,2)
  This is the simplest non-trivial MaxCut instance.
  For n > 3 qubits, use the path graph: edges (0,1), (1,2), ..., (n-2, n-1).

Circuit structure (p=1 QAOA layer):
  1. H⊗n  (equal superposition initialisation)
  2. Cost Hamiltonian layer (γ parameter):
     For each edge (i,j): Rzz(2γ) gate = CNOT(i,j) → Rz(2γ, j) → CNOT(i,j)
  3. Mixer Hamiltonian layer (β parameter):
     Rx(2β) on each qubit

Parameters fixed for reproducibility:
  γ = π/4   (standard initialisation choice)
  β = π/4

Key structural difference vs Cirq / PennyLane:
  - Qiskit uses ZZFeatureMap or manual Rzz decomposition
  - Cirq builds cost layers manually with moment-based construction
  - PennyLane provides qml.qaoa.cost_layer and qml.qaoa.mixer_layer

The Rzz decomposition is the main comparison point:
  CNOT → Rz(gamma) → CNOT  (standard decomposition)
  vs. native ZZ gate (if available in framework)

This file is called by:
  - benchmarks/scripts/compile_all.py  (for n ∈ 2..6, p=1)
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
  - benchmarks/notebooks/nb04_case_studies.ipynb  (Case Study 3)
"""

# ──────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────

# TODO: import QuantumCircuit from qiskit
# TODO: import numpy as np


# ──────────────────────────────────────────────────────────
# Graph definitions
# ──────────────────────────────────────────────────────────

# TODO: Define get_graph_edges(n) function that returns:
#   n=2: [(0,1)]
#   n=3: [(0,1), (1,2), (0,2)]  (triangle K3)
#   n>=4: [(i, i+1) for i in range(n-1)]  (path graph)


# ──────────────────────────────────────────────────────────
# Circuit Definition
# ──────────────────────────────────────────────────────────

def get_circuit(n: int = 3, p: int = 1, gamma: float = None, beta: float = None):
    """
    Build and return the Qiskit QAOA circuit.

    Args:
        n (int): Number of qubits / graph nodes (2–6). Default 3.
        p (int): Number of QAOA layers. Default 1 (for benchmark comparison).
        gamma (float): Cost layer parameter. Default π/4.
        beta (float): Mixer parameter. Default π/4.

    Returns:
        QuantumCircuit: QAOA circuit with bound parameters (concrete values).

    Circuit structure per layer:
        1. Cost Hamiltonian: For each edge (i,j), apply Rzz(2γ):
           cx(i,j) → rz(2*gamma, j) → cx(i,j)
        2. Mixer: rx(2*beta) on each qubit

    Notes:
        - p=1 is used for this benchmark to keep the comparison fair.
        - Gamma and beta are fixed so QASM output is deterministic.
        - The number of 2-qubit gates per layer = 2 × |edges|
          (each Rzz needs 2 CNOT gates in the standard decomposition).
    """

    # TODO: Set gamma = np.pi/4 if None, beta = np.pi/4 if None
    # TODO: Get edges from get_graph_edges(n)

    # TODO: Create QuantumCircuit with n qubits and n classical bits

    # ── Initial superposition ─────────────────────────
    # TODO: Apply H to all n qubits

    # ── QAOA layers ───────────────────────────────────
    # TODO: Loop p times:
    #   Cost layer: for each edge (i,j):
    #     cx(i, j), rz(2*gamma, j), cx(i, j)
    #   Mixer layer: for each qubit i:
    #     rx(2*beta, i)

    # ── Measurement ───────────────────────────────────
    # TODO: Measure all qubits

    # TODO: return circuit
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: Add if __name__ == "__main__" that:
#   - Runs get_circuit(n=3) and prints the circuit diagram
#   - Runs get_circuit(n=5) and prints the diagram
#   - Prints edge count and gate count for each
