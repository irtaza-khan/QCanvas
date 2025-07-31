from qiskit import QuantumCircuit
from qiskit.qasm3 import dumps  # QASM 3 exporter
import cirq

# Framework detection based on code string
def detect_framework(code: str):
    if "QuantumCircuit" in code:
        return "qiskit"
    elif "cirq." in code:
        return "cirq"
    return None

# Qiskit parser + QASM 3 exporter
def parse_qiskit(code: str):
    local_vars = {}
    exec(code, {}, local_vars)
    qc = local_vars.get("qc", None)
    if not isinstance(qc, QuantumCircuit):
        raise ValueError("Qiskit code must define 'qc = QuantumCircuit(...)'")
    return dumps(qc)

# Cirq parser + converter to Qiskit + QASM 3 exporter
def parse_cirq(code: str):
    import cirq
    from qiskit import QuantumCircuit, ClassicalRegister
    from qiskit.qasm3 import dumps

    local_vars = {}
    exec(code, {}, local_vars)

    cirq_circuit = None
    for val in local_vars.values():
        if isinstance(val, cirq.Circuit):
            cirq_circuit = val
            break
    if not cirq_circuit:
        raise ValueError("Cirq code must define a cirq.Circuit")

    qubits = sorted({q for op in cirq_circuit.all_operations() for q in op.qubits}, key=lambda q: q.x)
    qubit_map = {q: i for i, q in enumerate(qubits)}
    qreg = QuantumCircuit(len(qubits))
    qreg.add_register(ClassicalRegister(len(qubits)))

    for op in cirq_circuit.all_operations():
        gate = op.gate
        qubit_indices = [qubit_map[q] for q in op.qubits]

        if isinstance(gate, cirq.HPowGate):
            qreg.h(qubit_indices[0])
        elif isinstance(gate, cirq.XPowGate):
            qreg.x(qubit_indices[0])
        elif isinstance(gate, cirq.CNotPowGate):
            qreg.cx(qubit_indices[0], qubit_indices[1])
        elif isinstance(gate, cirq.MeasurementGate):
            for q in qubit_indices:
                qreg.measure(q, q)  # map qubit i to classical bit i
        else:
            raise ValueError(f"Unsupported Cirq gate: {gate}")

    return dumps(qreg)

