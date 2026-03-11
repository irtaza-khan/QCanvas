"""
Qiskit Implementation: VQE – Variational Quantum Eigensolver (variable: 2–6 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Variational Quantum Eigensolver (VQE)
Category: Variational
Qubit Range: 2–6 (n qubits, one variational layer)
Framework: Qiskit (idiomatic style)

VQE is a hybrid quantum-classical algorithm for finding the ground-state
energy of a Hamiltonian. The quantum circuit prepares a parameterised
ansatz state; a classical optimiser adjusts the parameters.

For this benchmark, we fix the parameters at zero (all parameters = 0)
to produce a deterministic, comparable QASM circuit. We use ONE ansatz
layer for simplicity. The goal is to compare the STRUCTURE of the ansatz,
not optimisation performance.

Hamiltonian used (fixed for reproducibility):
  H = Z⊗Z + X⊗I  (2-qubit case)
  For n qubits: nearest-neighbour ZZ interactions + single-qubit X terms

Ansatz: EfficientSU2 (Qiskit's canonical variational ansatz)
  - Ry + Rz gates on each qubit
  - CNOT entanglement layer (linear connectivity)
  - One repetition (reps=1) for benchmark comparability

Key structural difference vs Cirq / PennyLane:
  - Qiskit provides EfficientSU2 from qiskit.circuit.library (built-in template)
  - Cirq requires manual Rz + CNOT layer construction
  - PennyLane provides qml.StronglyEntanglingLayers (different gate count)
  This is the PRIMARY INTEREST of Case Study 3.

Parameter handling in QASM:
  - Qiskit's Parameter objects become 'input float theta[i];' declarations
    in OPENQASM 3.0, creating named parameters rather than literal values.
  - This is an important structural feature to compare.

This file is called by:
  - benchmarks/scripts/compile_all.py  (for n ∈ 2..6)
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
  - benchmarks/notebooks/nb04_case_studies.ipynb  (Case Study 3)
"""

# ──────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────

# TODO: import QuantumCircuit, ParameterVector from qiskit
# TODO: from qiskit.circuit.library import EfficientSU2
# TODO: import numpy as np


# ──────────────────────────────────────────────────────────
# Circuit Definition
# ──────────────────────────────────────────────────────────

def get_circuit(n: int = 2, reps: int = 1, bind_zero: bool = True):
    """
    Build and return the Qiskit VQE ansatz circuit.

    Args:
        n (int): Number of qubits (2–6). Default 2.
        reps (int): Number of ansatz repetitions. Default 1 (for benchmark).
        bind_zero (bool): If True, bind all parameters to 0.0 for
                          deterministic QASM output. Default True.

    Returns:
        QuantumCircuit: The VQE ansatz circuit with or without bound parameters.
                        If bind_zero=True, produces a concrete circuit (no free
                        parameters). If False, parameters remain symbolic.

    Notes:
        - EfficientSU2 uses Ry + Rz gates followed by a linear CNOT layer.
        - Gate count per layer = n*Ry + n*Rz + (n-1)*CNOT, scaling linearly.
        - With bind_zero=True: all Ry(0) and Rz(0) become identity gates
          in simulation, but the QASM structure is still full (no gate folding).
        - With bind_zero=False: QASM contains symbolic parameter references
          — useful for testing QCanvas's parameter handling in QASM generation.
    """

    # TODO: Create EfficientSU2 ansatz with n qubits, reps=reps, entanglement='linear'

    # TODO: If bind_zero is True:
    #   - Create ParameterVector with the correct number of parameters
    #   - Bind all to 0.0 using circuit.assign_parameters({})
    #   - Also add measurement gates at the end (EfficientSU2 does not include them)

    # TODO: If bind_zero is False:
    #   - Add measurement gates without binding (symbolic QASM output)

    # TODO: return circuit
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: Add if __name__ == "__main__" that:
#   - Prints EfficientSU2 circuit for n=2 and n=4
#   - Prints the number of parameters, gate count, and depth
#   - Shows the difference between bind_zero=True vs False circuit diagrams
