try:
    from CirqToQASM import convert_cirq_to_qasm3
    from PennyLanetoQASM import convert_pennylane_to_qasm3
    from QiskitToQASM import convert_qiskit_to_qasm3
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all converter modules (CirqToQASM, PennyLanetoQASM, QiskitToQASM) are available.")
    exit(1)

# Define equivalent circuits in all three languages that perform:
# 1. Hadamard on qubit 0
# 2. RX(π/4) on qubit 0
# 3. RY(π/2) on qubit 1
# 4. CNOT between qubits 0 and 1
# 5. RZ(π/3) on qubit 2
# 6. CZ between qubits 1 and 2

# PennyLane circuit
pennylane_code = '''
import pennylane as qml
import numpy as np

dev = qml.device('default.qubit', wires=3)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.RX(np.pi/4, wires=0)
    qml.RY(np.pi/2, wires=1)
    qml.CNOT(wires=[0, 1])
    qml.RZ(np.pi/3, wires=2)
    qml.CZ(wires=[1, 2])
    return qml.expval(qml.PauliZ(0))
'''

# Cirq circuit (wrapped in get_circuit function)
cirq_code = '''
import cirq
import numpy as np

def get_circuit():
    # Create 3 qubits
    q0, q1, q2 = cirq.LineQubit.range(3)
    
    # Build the circuit
    circuit = cirq.Circuit(
        cirq.H(q0),
        cirq.rx(np.pi/4).on(q0),
        cirq.ry(np.pi/2).on(q1),
        cirq.CNOT(q0, q1),
        cirq.rz(np.pi/3).on(q2),
        cirq.CZ(q1, q2)
    )
    
    return circuit
'''

# Qiskit circuit (wrapped in get_circuit function)
qiskit_code = '''
from qiskit import QuantumCircuit
import numpy as np

def get_circuit():
    # Create a quantum circuit with 3 qubits
    qc = QuantumCircuit(3)
    
    # Add gates
    qc.h(0)
    qc.rx(np.pi/4, 0)
    qc.ry(np.pi/2, 1)
    qc.cx(0, 1)
    qc.rz(np.pi/3, 2)
    qc.cz(1, 2)
    
    return qc
'''

def print_conversion(title, code, converter_func):
    print(f"\n{'='*50}")
    print(f"{title} Conversion")
    print(f"{'='*50}")
    try:
        qasm_output = converter_func(code)
        print("\nOpenQASM 3.0 Output:")
        print(qasm_output)
    except Exception as e:
        print(f"\nConversion failed: {str(e)}")

# Perform and print all conversions
print_conversion("PennyLane", pennylane_code, convert_pennylane_to_qasm3)
print_conversion("Cirq", cirq_code, convert_cirq_to_qasm3)
print_conversion("Qiskit", qiskit_code, convert_qiskit_to_qasm3)