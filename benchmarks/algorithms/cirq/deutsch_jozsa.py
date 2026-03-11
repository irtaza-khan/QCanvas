"""
Cirq Implementation: Deutsch–Jozsa Algorithm (variable: 3–8 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Deutsch–Jozsa
Category: Oracle-Based
Qubit Range: 3–8
Framework: Cirq (idiomatic style)

Same algorithm as deutsch_jozsa.py in qiskit/, implemented idiomatically in Cirq.

Idiomatic Cirq conventions:
  - cirq.LineQubit.range(n+1) for n input qubits + 1 ancilla
  - Operations assembled with cirq.Circuit([*ops1, cirq.Moment([...]), *ops2])
    to explicitly control moment structure (parallelism)
  - cirq.X(ancilla) then cirq.H(ancilla) to prepare |−⟩
  - cirq.CNOT(qubits[i], ancilla) for oracle CNOT gates

Oracle implementations:
  - CONSTANT oracle: no additional gates (empty moment between H layers)
  - BALANCED oracle: CNOT from each input qubit to ancilla

Structural comparison note:
  Cirq's moment-based construction may cause H gates on multiple qubits
  to be emitted in a single parallel moment in QASM, whereas Qiskit may
  emit them sequentially. This can cause circuit DEPTH to differ even
  when gate COUNT is identical.

This file is called by:
  - benchmarks/scripts/compile_all.py  (for n ∈ 3..8, both oracle types)
  - benchmarks/notebooks/nb01_compile_and_static_analysis.ipynb
"""

# ──────────────────────────────────────────────────────────
# Imports
# ──────────────────────────────────────────────────────────

# TODO: import cirq


# ──────────────────────────────────────────────────────────
# Constants Oracle
# ──────────────────────────────────────────────────────────

def get_circuit_constant(n: int = 3):
    """
    Cirq Deutsch–Jozsa with constant oracle (f ≡ 0).

    Args:
        n (int): Number of input qubits. Total = n+1.

    Returns:
        cirq.Circuit
    """

    # TODO: qubits = cirq.LineQubit.range(n+1); ancilla = qubits[n]
    # TODO: Prepare ancilla: X(ancilla), H(ancilla)
    # TODO: H on all input qubits in same moment
    # TODO: Constant oracle: no-op (add empty moment or just barrier comment)
    # TODO: H on all input qubits again (second layer)
    # TODO: cirq.measure(*qubits[:n], key='result')
    # TODO: return cirq.Circuit([...])
    pass


# ──────────────────────────────────────────────────────────
# Balanced Oracle
# ──────────────────────────────────────────────────────────

def get_circuit_balanced(n: int = 3):
    """
    Cirq Deutsch–Jozsa with balanced oracle (CNOT from each input to ancilla).

    Args:
        n (int): Number of input qubits. Total = n+1.

    Returns:
        cirq.Circuit
    """

    # TODO: qubits = cirq.LineQubit.range(n+1); ancilla = qubits[n]
    # TODO: Prepare ancilla: X(ancilla), H(ancilla)
    # TODO: H on all input qubits
    # TODO: Balanced oracle: [cirq.CNOT(qubits[i], ancilla) for i in range(n)]
    # TODO: H on all input qubits again
    # TODO: cirq.measure(*qubits[:n], key='result')
    # TODO: return cirq.Circuit([...])
    pass


# ──────────────────────────────────────────────────────────
# Convenience dispatcher
# ──────────────────────────────────────────────────────────

def get_circuit(n: int = 3, oracle_type: str = "balanced"):
    """
    Dispatch to constant or balanced circuit. See Qiskit version for full docs.
    """

    # TODO: dispatch to get_circuit_constant or get_circuit_balanced
    pass


# ──────────────────────────────────────────────────────────
# Module entry-point
# ──────────────────────────────────────────────────────────

# TODO: if __name__ == "__main__": print both oracle variants for n=3
