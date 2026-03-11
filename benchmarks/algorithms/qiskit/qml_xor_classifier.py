"""
Qiskit Implementation: QML XOR Classifier (2–4 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Quantum Machine Learning XOR Classifier
Category: Quantum ML
Qubit Range: 2–4
Framework: Qiskit (idiomatic style)

This circuit implements a simple quantum classifier for the XOR function.
It consists of two stages:
  1. Data encoding: classical input bits are angle-encoded into qubit rotations
  2. Variational layer: parametric rotation + entanglement gates

XOR truth table (2-qubit case):
  Input [0,0] → Label 0
  Input [0,1] → Label 1
  Input [1,0] → Label 1
  Input [1,1] → Label 0

Data encoding strategy: Angle encoding
  Input x = [x0, x1] → RX(π*x0) on qubit 0, RX(π*x1) on qubit 1

Variational layer (one layer):
  RY(θ0) on each qubit, then CNOT entanglement, then RY(θ1)

For this benchmark:
  - Input is fixed at x = [0.5, 0.5] (mid-point, arbitrary but consistent)
  - Variational parameters are bound to 0.0 for deterministic QASM output
  - All three frameworks use the SAME input values and parameter values

Key comparison interest (Case Study 4):
  PennyLane provides qml.AngleEmbedding as a built-in template, while Qiskit
  and Cirq require manual RX/RY implementation. This may result in a different
  gate count or structure for the encoding stage.

This file is called by:
  - benchmarks/scripts/compile_all.py
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
  - benchmarks/notebooks/nb04_case_studies.ipynb  (Case Study 4)
"""

# ──────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────

# TODO: import QuantumCircuit, ParameterVector from qiskit
# TODO: import numpy as np


# ──────────────────────────────────────────────────────────
# Constants — fixed benchmark inputs
# ──────────────────────────────────────────────────────────

# TODO: Define BENCHMARK_INPUT = [0.5, 0.5]  (angle-encoded classical input)
# TODO: Define BENCHMARK_PARAMS = [0.0, 0.0]  (variational layer parameters at zero)


# ──────────────────────────────────────────────────────────
# Circuit Definition
# ──────────────────────────────────────────────────────────

def get_circuit(n: int = 2, x: list = None, params: list = None):
    """
    Build and return the Qiskit QML XOR classifier circuit.

    Args:
        n (int): Number of qubits (2–4). Default 2.
        x (list): Classical input values for angle encoding. Length = n.
                  Default BENCHMARK_INPUT (all 0.5).
        params (list): Variational layer parameters. Length = 2*n.
                       Default BENCHMARK_PARAMS (all 0.0).

    Returns:
        QuantumCircuit: Classifier circuit with:
          - Angle encoding layer (RX gates)
          - Variational layer (RY + CNOT + RY)
          - Measurement of all qubits

    Notes:
        - With all parameters = 0.0, the variational layer produces no rotation.
        - The circuit depth is dominated by the CNOT entanglement pattern.
        - For n > 2, extend the CNOT pattern as a chain: CNOT(i, i+1) for i in range(n-1).
    """

    # TODO: Set defaults for x and params from BENCHMARK_INPUT / BENCHMARK_PARAMS
    # TODO: Validate len(x) == n and len(params) == 2*n

    # TODO: Create QuantumCircuit with n qubits and n classical bits

    # ── Angle encoding layer ──────────────────────────
    # TODO: Apply RX(np.pi * x[i]) to qubit i for all i

    # ── Variational layer ─────────────────────────────
    # TODO: Apply RY(params[i]) to qubit i  (first RY layer)
    # TODO: Apply CNOT chain: cx(i, i+1) for i in range(n-1)
    # TODO: Apply RY(params[n+i]) to qubit i  (second RY layer)

    # ── Measurement ───────────────────────────────────
    # TODO: Measure all qubits

    # TODO: return circuit
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: Add if __name__ == "__main__" that:
#   - Draws the QML circuit for n=2 and n=4
#   - Prints gate count and depth
#   - Notes which gates come from encoding vs. variational layers
