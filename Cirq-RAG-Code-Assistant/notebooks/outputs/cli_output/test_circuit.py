import cirq
q = cirq.LineQubit.range(2)
c = cirq.Circuit(cirq.H(q[0]), cirq.CNOT(q[0], q[1]))
print(c)