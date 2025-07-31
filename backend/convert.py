from qiskit import QuantumCircuit
import qiskit
import cirq

def detect_framework(code: str):
    if "QuantumCircuit" in code:
        return "qiskit"
    elif "cirq." in code:
        return "cirq"
    return None
from qiskit.qasm3 import dumps

def parse_qiskit(code: str):
    local_vars = {}
    exec(code, {}, local_vars)
    qc = local_vars.get("qc", None)
    if not isinstance(qc, QuantumCircuit):
        raise ValueError("Qiskit code must define 'qc = QuantumCircuit(...)'")
    return dumps(qc)  # QASM 3 format
def parse_cirq(code: str):
    # Extract Cirq circuit and convert to Qiskit
    local_vars = {}
    exec(code, {}, local_vars)
    cirq_circuit = None
    for val in local_vars.values():
        if isinstance(val, cirq.Circuit):
            cirq_circuit = val
            break
    if not cirq_circuit:
        raise ValueError("Cirq code must define a cirq.Circuit")

    # Translate basic Cirq gates to Qiskit
    qreg = QuantumCircuit(cirq_circuit.num_qubits)
    qubit_map = {}

    for op in cirq_circuit.all_operations():
        for q in op.qubits:
            if q not in qubit_map:
                qubit_map[q] = q.x  # maintain order

        gate = op.gate
        qubits = [q.x for q in op.qubits]
        if isinstance(gate, cirq.HPowGate):
            qreg.h(qubits[0])
        elif isinstance(gate, cirq.XPowGate):
            qreg.x(qubits[0])
        elif isinstance(gate, cirq.CNOT):
            qreg.cx(qubits[0], qubits[1])
        elif isinstance(gate, cirq.measure.MeasurementGate):
            qreg.measure(qubits[0])
        else:
            raise ValueError(f"Unsupported Cirq gate: {gate}")

    return qreg.qasm()
