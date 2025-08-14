"""
PennyLane Variational Circuit Example

This example demonstrates variational quantum circuits using PennyLane,
including parameterized gates, cost functions, and optimization.
The circuit implements a simple variational quantum eigensolver (VQE)
for finding the ground state energy of a simple Hamiltonian.

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

import pennylane as qml
import numpy as np
from pennylane import numpy as pnp


def create_variational_circuit(n_qubits=2, n_layers=2):
    """
    Create a variational quantum circuit using PennyLane.
    
    This circuit implements a hardware-efficient ansatz with
    alternating layers of single-qubit rotations and entangling gates.
    
    Args:
        n_qubits (int): Number of qubits in the circuit
        n_layers (int): Number of variational layers
        
    Returns:
        qml.QNode: PennyLane quantum node
    """
    # Create a quantum device
    dev = qml.device("default.qubit", wires=n_qubits)
    
    @qml.qnode(dev)
    def circuit(weights, bias):
        """
        Variational quantum circuit.
        
        Args:
            weights (array): Variational parameters for rotation gates
            bias (array): Bias parameters for single-qubit rotations
            
        Returns:
            array: Expectation values of Pauli Z operators
        """
        # Initial layer of single-qubit rotations
        for i in range(n_qubits):
            qml.RX(bias[i], wires=i)
            qml.RY(bias[i + n_qubits], wires=i)
            qml.RZ(bias[i + 2 * n_qubits], wires=i)
        
        # Variational layers
        for layer in range(n_layers):
            # Entangling layer with CNOT gates
            for i in range(n_qubits - 1):
                qml.CNOT(wires=[i, i + 1])
            qml.CNOT(wires=[n_qubits - 1, 0])  # Periodic boundary
            
            # Single-qubit rotation layer
            for i in range(n_qubits):
                qml.RX(weights[layer, i, 0], wires=i)
                qml.RY(weights[layer, i, 1], wires=i)
                qml.RZ(weights[layer, i, 2], wires=i)
        
        # Measure all qubits in Z basis
        return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
    
    return circuit


def create_quantum_neural_network(n_qubits=2, n_layers=2):
    """
    Create a quantum neural network using PennyLane.
    
    This circuit implements a quantum neural network that can be
    used for classification or regression tasks.
    
    Args:
        n_qubits (int): Number of qubits in the circuit
        n_layers (int): Number of layers in the network
        
    Returns:
        qml.QNode: PennyLane quantum node
    """
    dev = qml.device("default.qubit", wires=n_qubits)
    
    @qml.qnode(dev)
    def circuit(inputs, weights):
        """
        Quantum neural network circuit.
        
        Args:
            inputs (array): Input data
            weights (array): Network weights
            
        Returns:
            array: Output of the quantum neural network
        """
        # Encode input data
        for i in range(n_qubits):
            qml.RX(inputs[i], wires=i)
            qml.RY(inputs[i], wires=i)
        
        # Process through layers
        for layer in range(n_layers):
            # Entangling layer
            for i in range(n_qubits - 1):
                qml.CNOT(wires=[i, i + 1])
            
            # Rotation layer
            for i in range(n_qubits):
                qml.RX(weights[layer, i, 0], wires=i)
                qml.RY(weights[layer, i, 1], wires=i)
                qml.RZ(weights[layer, i, 2], wires=i)
        
        # Measure in computational basis
        return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
    
    return circuit


def create_vqe_circuit():
    """
    Create a Variational Quantum Eigensolver (VQE) circuit.
    
    This circuit implements VQE to find the ground state energy
    of a simple 2-qubit Hamiltonian: H = Z⊗Z + X⊗X
    
    Returns:
        qml.QNode: PennyLane quantum node for VQE
    """
    dev = qml.device("default.qubit", wires=2)
    
    @qml.qnode(dev)
    def circuit(theta):
        """
        VQE circuit for 2-qubit Hamiltonian.
        
        Args:
            theta (float): Variational parameter
            
        Returns:
            float: Expectation value of the Hamiltonian
        """
        # Prepare variational state
        qml.RY(theta, wires=0)
        qml.CNOT(wires=[0, 1])
        
        # Measure Hamiltonian terms
        # H = Z⊗Z + X⊗X
        zz = qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))
        xx = qml.expval(qml.PauliX(0) @ qml.PauliX(1))
        
        return zz + xx
    
    return circuit


def create_quantum_approximate_optimization_algorithm(n_qubits=4, p=2):
    """
    Create a Quantum Approximate Optimization Algorithm (QAOA) circuit.
    
    This circuit implements QAOA for solving combinatorial optimization
    problems, specifically the MaxCut problem on a simple graph.
    
    Args:
        n_qubits (int): Number of qubits (vertices in the graph)
        p (int): Number of QAOA layers
        
    Returns:
        qml.QNode: PennyLane quantum node for QAOA
    """
    dev = qml.device("default.qubit", wires=n_qubits)
    
    @qml.qnode(dev)
    def circuit(gamma, beta):
        """
        QAOA circuit for MaxCut problem.
        
        Args:
            gamma (array): Phase separation parameters
            beta (array): Mixing parameters
            
        Returns:
            float: Cost function value
        """
        # Initial state: equal superposition
        for i in range(n_qubits):
            qml.Hadamard(wires=i)
        
        # QAOA layers
        for layer in range(p):
            # Phase separation operator (problem Hamiltonian)
            # For MaxCut: apply ZZ gates between connected vertices
            for i in range(n_qubits - 1):
                qml.CNOT(wires=[i, i + 1])
                qml.RZ(gamma[layer], wires=i + 1)
                qml.CNOT(wires=[i, i + 1])
            
            # Mixing operator
            for i in range(n_qubits):
                qml.RX(beta[layer], wires=i)
        
        # Measure in computational basis
        return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
    
    return circuit


def create_quantum_generative_model(n_qubits=3):
    """
    Create a quantum generative model using PennyLane.
    
    This circuit implements a quantum generative adversarial network
    (QGAN) generator circuit that can learn to generate quantum states.
    
    Args:
        n_qubits (int): Number of qubits in the circuit
        
    Returns:
        qml.QNode: PennyLane quantum node
    """
    dev = qml.device("default.qubit", wires=n_qubits)
    
    @qml.qnode(dev)
    def circuit(noise, weights):
        """
        Quantum generative model circuit.
        
        Args:
            noise (array): Random noise input
            weights (array): Generator weights
            
        Returns:
            array: Generated quantum state
        """
        # Encode noise
        for i in range(n_qubits):
            qml.RX(noise[i], wires=i)
            qml.RY(noise[i + n_qubits], wires=i)
        
        # Generator layers
        for layer in range(len(weights) // (3 * n_qubits)):
            # Entangling layer
            for i in range(n_qubits - 1):
                qml.CNOT(wires=[i, i + 1])
            
            # Rotation layer
            for i in range(n_qubits):
                idx = layer * 3 * n_qubits + 3 * i
                qml.RX(weights[idx], wires=i)
                qml.RY(weights[idx + 1], wires=i)
                qml.RZ(weights[idx + 2], wires=i)
        
        # Measure in computational basis
        return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
    
    return circuit


def get_circuit():
    """
    Main function to return a quantum circuit for conversion.
    
    This function returns a variational circuit as the default example.
    You can modify this function to return any of the other circuits
    defined above for testing different circuit types.
    
    Returns:
        qml.QNode: PennyLane quantum node
    """
    return create_variational_circuit(2, 2)


# Example usage and testing
if __name__ == "__main__":
    print("PennyLane Variational Circuit Examples")
    print("=" * 50)
    
    # Test variational circuit
    print("\n1. Variational Circuit (2 qubits, 2 layers):")
    var_circuit = create_variational_circuit(2, 2)
    
    # Initialize random parameters
    weights = np.random.randn(2, 2, 3)  # 2 layers, 2 qubits, 3 rotations each
    bias = np.random.randn(6)  # 2 qubits * 3 rotations
    
    result = var_circuit(weights, bias)
    print(f"Circuit output: {result}")
    
    # Test quantum neural network
    print("\n2. Quantum Neural Network:")
    qnn_circuit = create_quantum_neural_network(2, 2)
    
    inputs = np.random.randn(2)
    weights = np.random.randn(2, 2, 3)
    
    result = qnn_circuit(inputs, weights)
    print(f"QNN output: {result}")
    
    # Test VQE circuit
    print("\n3. VQE Circuit:")
    vqe_circuit = create_vqe_circuit()
    
    theta = np.random.randn()
    energy = vqe_circuit(theta)
    print(f"VQE energy: {energy}")
    
    # Test QAOA circuit
    print("\n4. QAOA Circuit (4 qubits, 2 layers):")
    qaoa_circuit = create_quantum_approximate_optimization_algorithm(4, 2)
    
    gamma = np.random.randn(2)
    beta = np.random.randn(2)
    
    result = qaoa_circuit(gamma, beta)
    print(f"QAOA output: {result}")
    
    # Test quantum generative model
    print("\n5. Quantum Generative Model:")
    gen_circuit = create_quantum_generative_model(3)
    
    noise = np.random.randn(6)
    weights = np.random.randn(18)  # 2 layers * 3 qubits * 3 rotations
    
    result = gen_circuit(noise, weights)
    print(f"Generator output: {result}")
    
    print("\n" + "=" * 50)
    print("All PennyLane circuits created successfully!")
