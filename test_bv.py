from qiskit import QuantumCircuit
from quantum_converters.converters.qiskit_to_qasm import QiskitToQASM3Converter

SECRET_STRINGS = {
    3: "101",
    4: "1011",
    5: "10110",
    6: "101101",
    7: "1011010",
    8: "10110101",
}

def get_circuit(n: int = 6):
    s = SECRET_STRINGS[n]
    total = n + 1
    qc = QuantumCircuit(total, n)
    qc.x(n)
    qc.h(range(total))
    for i, bit in enumerate(s):
        if bit == '1':
            qc.cx(i, n)
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc

source = """
from qiskit import QuantumCircuit
SECRET_STRINGS = {3: "101", 4: "1011", 5: "10110", 6: "101101", 7: "1011010", 8: "10110101"}
def get_circuit(n: int = 6):
    s = SECRET_STRINGS[n]
    total = n + 1
    qc = QuantumCircuit(total, n)
    qc.x(n)
    qc.h(range(total))
    for i, bit in enumerate(s):
        if bit == '1':
            qc.cx(i, n)
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc
"""

converter = QiskitToQASM3Converter()
result = converter.convert(source)
print(result.qasm_code)
