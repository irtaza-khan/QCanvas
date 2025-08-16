"""
Basic PennyLane Circuit Example - Bell State Preparation

This example demonstrates how to create a Bell state using PennyLane.
"""

import pennylane as qml

def get_circuit():
    """
    Create a Bell state quantum circuit using PennyLane.
    
    Returns:
        qml.QNode: A quantum node that prepares the Bell state |00⟩ + |11⟩
    """
    # Create a device with 2 qubits
    dev = qml.device('default.qubit', wires=2)
    
    @qml.qnode(dev)
    def circuit():
        qml.Hadamard(wires=0)  # Hadamard gate on qubit 0
        qml.CNOT(wires=[0, 1])  # CNOT gate between qubits 0 and 1
        return qml.expval(qml.PauliZ(0))
    
    return circuit

if __name__ == "__main__":
    # Create the circuit
    circuit = get_circuit()
    
    # Print circuit information
    print("Bell State Circuit (PennyLane):")
    print(f"Device: {circuit.device}")
    print(f"Number of wires: {circuit.device.num_wires}")
    
    # Execute the circuit
    result = circuit()
    print(f"Expectation value: {result}")
