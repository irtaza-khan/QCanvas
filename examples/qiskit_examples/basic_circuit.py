"""
Basic Qiskit Circuit Example - Bell State Preparation

This example demonstrates how to create a Bell state using Qiskit.
The circuit applies a Hadamard gate to the first qubit, then a CNOT gate
to create an entangled state.
"""

from qiskit import QuantumCircuit

def get_circuit():
    """
    Create a Bell state quantum circuit.
    
    Returns:
        QuantumCircuit: A 2-qubit circuit that prepares the Bell state |00⟩ + |11⟩
    """
    # Create a quantum circuit with 2 qubits
    qc = QuantumCircuit(2)
    
    # Apply Hadamard gate to qubit 0
    qc.h(0)
    
    # Apply CNOT gate with control=0, target=1
    qc.cx(0, 1)
    
    return qc

if __name__ == "__main__":
    # Create the circuit
    circuit = get_circuit()
    
    # Print the circuit
    print("Bell State Circuit:")
    print(circuit)
    
    # Print circuit information
    print(f"\nCircuit Info:")
    print(f"Number of qubits: {circuit.num_qubits}")
    print(f"Circuit depth: {circuit.depth()}")
    print(f"Gate counts: {circuit.count_ops()}")
