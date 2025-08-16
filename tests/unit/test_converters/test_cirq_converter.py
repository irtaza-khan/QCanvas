# TODO: Implement tests
import cirq
def get_circuit():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.H(q0),
        cirq.CNOT(q0, q1),
        cirq.measure(q0, key="m0"),
        cirq.measure(q1, key="m1")
    )
    return circuit