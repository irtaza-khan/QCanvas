from qiskit import QuantumCircuit
from quantum_converters.converters.qiskit_to_qasm import QiskitToQASM3Converter

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
# Simulate fallback by forcing Exception in AST path
try:
    # circuit = converter._execute_qiskit_source(source)
    # qasm = converter._convert_to_qasm3(circuit)
    # print(qasm)
    
    # Actually just call the conversion, it should fail AST now if I add the check
    pass
except:
    pass

# For now, let's just see what _execute_qiskit_source + _convert_to_qasm3 produces
circuit = get_circuit(6)
qasm = converter._convert_to_qasm3(circuit)
print(qasm)
