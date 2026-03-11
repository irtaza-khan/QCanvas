"""
Cirq Implementation: QRNG (variable: 4–8 qubits)
Paper 5 – Cross-Framework Quantum Algorithm Benchmarking

Algorithm: Quantum Random Number Generator (QRNG)
Category: Randomness
Qubit Range: 4–8
Framework: Cirq (idiomatic style)

Same algorithm as qiskit/qrng.py — all H gates, then measure.
Cirq's moment-based scheduling should place all H gates in the SAME moment,
producing circuit depth = 1 (parallel), which is the theoretically optimal depth.

Expected QASM structure:
  H q[0]; H q[1]; H q[2]; ... all in one parallel moment → depth 1

This is used as the FLAT BASELINE in the scaling analysis: since depth
should always = 1 regardless of n, any deviation across frameworks is pure overhead.
"""

# TODO: import cirq

def get_circuit(n: int = 4):
    """
    Build and return the Cirq QRNG circuit for n qubits.

    Args:
        n (int): Number of qubits (4–8). Default 4.

    Returns:
        cirq.Circuit: H on all qubits in one moment, then measure.

    Notes:
        - Use cirq.Moment([cirq.H(q) for q in qubits]) to force parallel H gates.
        - Measure with cirq.measure(*qubits, key='random_bits').
    """

    # TODO: qubits = cirq.LineQubit.range(n)
    # TODO: h_moment = cirq.Moment([cirq.H(q) for q in qubits])
    # TODO: measure_op = cirq.measure(*qubits, key='random_bits')
    # TODO: return cirq.Circuit([h_moment, measure_op])
    pass


def get_scaling_circuits():
    """Return (n, circuit) pairs for n=4..8."""
    # TODO: return [(n, get_circuit(n)) for n in range(4, 9)]
    pass


# TODO: if __name__ == "__main__": print QRNG for n=4 and n=8, verify depth=1
