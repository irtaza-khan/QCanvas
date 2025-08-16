"""
Basic Cirq Circuit Example - Bell State Preparation

This example demonstrates how to create a Bell state using Cirq.
"""

import cirq

def get_circuit():
    """
    Create a Bell state quantum circuit using Cirq.
    
    Returns:
        cirq.Circuit: A 2-qubit circuit that prepares the Bell state |00⟩ + |11⟩
    """
    # Create qubits
    q0, q1 = cirq.LineQubit.range(2)
    
    # Create the circuit
    circuit = cirq.Circuit(
        cirq.H(q0),  # Hadamard gate on qubit 0
        cirq.CNOT(q0, q1)  # CNOT gate between qubits 0 and 1
    )
    
    return circuit

if __name__ == "__main__":
    # Create the circuit
    circuit = get_circuit()
    
    # Print the circuit
    print("Bell State Circuit (Cirq):")
    print(circuit)
    
    # Print circuit information
    print(f"\nCircuit Info:")
    print(f"Number of qubits: {len(circuit.all_qubits())}")
    print(f"Number of moments: {len(circuit)}")
