from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from quantum_converters.converters.qiskit_to_qasm import QiskitToQASM3Converter

def get_circuit():
    qr = QuantumRegister(2, 'q')
    cr = ClassicalRegister(2, 'c')
    qc = QuantumCircuit(qr, cr)
    qc.h(qr[0])
    qc.cx(qr[0], qr[1])
    qc.measure(qr, cr)
    return qc

source = """
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
def get_circuit():
    qr = QuantumRegister(2, 'q')
    cr = ClassicalRegister(2, 'c')
    qc = QuantumCircuit(qr, cr)
    qc.h(qr[0])
    qc.cx(qr[0], qr[1])
    qc.measure(qr, cr)
    return qc
"""

converter = QiskitToQASM3Converter()
result = converter.convert(source)
print(result.qasm_code)
