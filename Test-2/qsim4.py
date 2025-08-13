import qiskit
from qiskit import QuantumCircuit
from qiskit.qasm3 import dumps as qasm3_dumps

import cirq
import pennylane as qml

print("=" * 60)
print("QSIM Compilation Demo: Converting to OpenQASM 3 IR")
print("=" * 60)

# ============================================================
# Qiskit -> QASM3
# ============================================================
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

stats_qiskit = {
    "n_qubits": qc.num_qubits,
    "n_clbits": qc.num_clbits,
    "depth": qc.depth(),
    "has_parameters": qc.num_parameters > 0,
    "basis_gates": qc.count_ops().keys()
}

print("\n=== Qiskit -> QASM3 ===")
print("Stats:", stats_qiskit)
print("Program:")
print(qasm3_dumps(qc))


# ============================================================
# Cirq -> QASM3
# ============================================================
q0, q1 = cirq.LineQubit.range(2)
circuit_cirq = cirq.Circuit(
    cirq.H(q0),
    cirq.CNOT(q0, q1),
    cirq.measure(q0, key='m0'),
    cirq.measure(q1, key='m1')
)

stats_cirq = {
    "n_qubits": len(circuit_cirq.all_qubits()),
    "depth": len(circuit_cirq)  # moment count instead of circuit_cirq.depth()
}

print("\n=== Cirq -> QASM3 ===")
print("Stats:", stats_cirq)
print("Program:")
print(cirq.qasm(circuit_cirq, version=3))


# ============================================================
# PennyLane -> QASM3
# ============================================================
def compile_pennylane_to_qasm3():
    dev = qml.device("default.qubit", wires=2)

    @qml.qnode(dev)
    def bell():
        qml.H(0)
        qml.CNOT([0, 1])
        return qml.measure(0), qml.measure(1)

    qasm3_code = qml.to_openqasm(bell, dialect="qasm3")

    stats = {
        "n_wires": dev.num_wires,
        "ops": len(bell.tape.operations),
        "has_measurements": len(bell.tape.measurements) > 0
    }
    return qasm3_code, stats

res_pl, stats_pl = compile_pennylane_to_qasm3()
print("\n=== PennyLane -> QASM3 ===")
print("Stats:", stats_pl)
print("Program:")
print(res_pl)

print("\n" + "=" * 60)
print("All frameworks successfully converted to OpenQASM 3!")
print("Universal IR (OpenQASM 3) can now be used across different")
print("quantum computing platforms and simulators.")
print("=" * 60)
