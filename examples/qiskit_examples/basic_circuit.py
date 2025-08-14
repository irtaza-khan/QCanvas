"""
Basic Qiskit Circuit Example

This example demonstrates a simple quantum circuit using Qiskit,
including common gates like Hadamard, CNOT, and measurements.
The circuit creates a Bell state and measures both qubits.

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import numpy as np


def create_bell_state_circuit():
    """
    Create a Bell state circuit using Qiskit.
    
    This circuit creates the Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2
    by applying a Hadamard gate to the first qubit followed by
    a CNOT gate between the first and second qubits.
    
    Returns:
        QuantumCircuit: Qiskit quantum circuit
    """
    # Create quantum and classical registers
    qr = QuantumRegister(2, 'q')
    cr = ClassicalRegister(2, 'c')
    
    # Create quantum circuit
    qc = QuantumCircuit(qr, cr)
    
    # Apply Hadamard gate to first qubit (creates superposition)
    qc.h(qr[0])
    
    # Apply CNOT gate between qubits 0 and 1 (creates entanglement)
    qc.cx(qr[0], qr[1])
    
    # Measure both qubits
    qc.measure(qr, cr)
    
    return qc


def create_ghz_state_circuit(n_qubits=3):
    """
    Create a GHZ (Greenberger-Horne-Zeilinger) state circuit.
    
    The GHZ state is a maximally entangled state of n qubits:
    |GHZ⟩ = (|0...0⟩ + |1...1⟩)/√2
    
    Args:
        n_qubits (int): Number of qubits in the circuit
        
    Returns:
        QuantumCircuit: Qiskit quantum circuit
    """
    # Create quantum and classical registers
    qr = QuantumRegister(n_qubits, 'q')
    cr = ClassicalRegister(n_qubits, 'c')
    
    # Create quantum circuit
    qc = QuantumCircuit(qr, cr)
    
    # Apply Hadamard gate to first qubit
    qc.h(qr[0])
    
    # Apply CNOT gates to create entanglement
    for i in range(1, n_qubits):
        qc.cx(qr[0], qr[i])
    
    # Measure all qubits
    qc.measure(qr, cr)
    
    return qc


def create_parameterized_circuit():
    """
    Create a parameterized quantum circuit with rotation gates.
    
    This circuit demonstrates the use of parameterized gates
    that can be optimized for quantum machine learning applications.
    
    Returns:
        QuantumCircuit: Qiskit quantum circuit with parameters
    """
    from qiskit.circuit import Parameter
    
    # Create parameters
    theta = Parameter('θ')
    phi = Parameter('φ')
    
    # Create quantum and classical registers
    qr = QuantumRegister(2, 'q')
    cr = ClassicalRegister(2, 'c')
    
    # Create quantum circuit
    qc = QuantumCircuit(qr, cr)
    
    # Apply parameterized rotation gates
    qc.rx(theta, qr[0])
    qc.ry(phi, qr[1])
    
    # Apply CNOT gate
    qc.cx(qr[0], qr[1])
    
    # Apply more parameterized gates
    qc.rz(theta + phi, qr[0])
    
    # Measure qubits
    qc.measure(qr, cr)
    
    return qc


def create_quantum_fourier_transform(n_qubits=3):
    """
    Create a Quantum Fourier Transform (QFT) circuit.
    
    The QFT is a key component in many quantum algorithms,
    including Shor's algorithm for factoring.
    
    Args:
        n_qubits (int): Number of qubits in the circuit
        
    Returns:
        QuantumCircuit: Qiskit quantum circuit implementing QFT
    """
    # Create quantum and classical registers
    qr = QuantumRegister(n_qubits, 'q')
    cr = ClassicalRegister(n_qubits, 'c')
    
    # Create quantum circuit
    qc = QuantumCircuit(qr, cr)
    
    # Apply QFT
    for i in range(n_qubits):
        # Apply Hadamard gate
        qc.h(qr[i])
        
        # Apply controlled phase rotations
        for j in range(i + 1, n_qubits):
            angle = 2 * np.pi / (2 ** (j - i + 1))
            qc.cp(angle, qr[j], qr[i])
    
    # Swap qubits to get correct order
    for i in range(n_qubits // 2):
        qc.swap(qr[i], qr[n_qubits - 1 - i])
    
    # Measure all qubits
    qc.measure(qr, cr)
    
    return qc


def create_error_correction_circuit():
    """
    Create a simple error correction circuit (3-qubit bit-flip code).
    
    This circuit demonstrates basic quantum error correction
    by encoding one logical qubit into three physical qubits.
    
    Returns:
        QuantumCircuit: Qiskit quantum circuit for error correction
    """
    # Create quantum and classical registers
    qr = QuantumRegister(5, 'q')  # 3 data qubits + 2 ancilla qubits
    cr = ClassicalRegister(3, 'c')  # Measure only data qubits
    
    # Create quantum circuit
    qc = QuantumCircuit(qr, cr)
    
    # Encoding: Prepare logical |1⟩ state
    qc.x(qr[0])  # Flip first qubit to |1⟩
    
    # Apply CNOT gates to create encoded state
    qc.cx(qr[0], qr[1])
    qc.cx(qr[0], qr[2])
    
    # Error detection: Apply syndrome measurement
    qc.cx(qr[0], qr[3])
    qc.cx(qr[1], qr[3])
    qc.cx(qr[1], qr[4])
    qc.cx(qr[2], qr[4])
    
    # Measure ancilla qubits (syndrome)
    qc.measure(qr[3], cr[0])
    qc.measure(qr[4], cr[1])
    
    # Measure data qubits
    qc.measure(qr[0], cr[2])
    
    return qc


def get_circuit():
    """
    Main function to return a quantum circuit for conversion.
    
    This function returns a Bell state circuit as the default example.
    You can modify this function to return any of the other circuits
    defined above for testing different circuit types.
    
    Returns:
        QuantumCircuit: Qiskit quantum circuit
    """
    return create_bell_state_circuit()


# Example usage and testing
if __name__ == "__main__":
    print("Qiskit Basic Circuit Examples")
    print("=" * 40)
    
    # Test Bell state circuit
    print("\n1. Bell State Circuit:")
    bell_circuit = create_bell_state_circuit()
    print(bell_circuit)
    
    # Test GHZ state circuit
    print("\n2. GHZ State Circuit (3 qubits):")
    ghz_circuit = create_ghz_state_circuit(3)
    print(ghz_circuit)
    
    # Test parameterized circuit
    print("\n3. Parameterized Circuit:")
    param_circuit = create_parameterized_circuit()
    print(param_circuit)
    
    # Test QFT circuit
    print("\n4. Quantum Fourier Transform (3 qubits):")
    qft_circuit = create_quantum_fourier_transform(3)
    print(qft_circuit)
    
    # Test error correction circuit
    print("\n5. Error Correction Circuit:")
    error_circuit = create_error_correction_circuit()
    print(error_circuit)
    
    print("\n" + "=" * 40)
    print("All circuits created successfully!")
