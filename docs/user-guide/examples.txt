# QCanvas Examples and Tutorials

## Overview

This guide provides comprehensive examples and tutorials for using QCanvas. Each example demonstrates different aspects of quantum computing and shows how to use QCanvas effectively for various applications.

## Table of Contents

1. [Basic Circuits](#basic-circuits)
2. [Quantum Algorithms](#quantum-algorithms)
3. [Variational Quantum Circuits](#variational-quantum-circuits)
4. [Error Correction](#error-correction)
5. [Quantum Machine Learning](#quantum-machine-learning)
6. [Advanced Examples](#advanced-examples)

## Basic Circuits

### Bell State Circuit

The Bell state is a fundamental quantum state that demonstrates quantum entanglement.

#### Cirq Implementation
```python
import cirq

# Create qubits
q0, q1 = cirq.LineQubit.range(2)

# Create Bell state circuit
circuit = cirq.Circuit(
    cirq.H(q0),           # Hadamard on first qubit
    cirq.CNOT(q0, q1),    # CNOT with q0 as control
    cirq.measure(q0, q1)  # Measure both qubits
)

print("Bell State Circuit (Cirq):")
print(circuit)
```

#### Qiskit Implementation
```python
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

# Create quantum and classical registers
qr = QuantumRegister(2, 'q')
cr = ClassicalRegister(2, 'c')

# Create quantum circuit
qc = QuantumCircuit(qr, cr)

# Apply Hadamard gate to first qubit
qc.h(qr[0])

# Apply CNOT gate between qubits 0 and 1
qc.cx(qr[0], qr[1])

# Measure both qubits
qc.measure(qr, cr)

print("Bell State Circuit (Qiskit):")
print(qc)
```

#### PennyLane Implementation
```python
import pennylane as qml

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def bell_state_circuit():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(0)), qml.expval(qml.PauliZ(1))

# Execute circuit
result = bell_state_circuit()
print("Bell State Circuit (PennyLane):")
print(f"Expectation values: {result}")
```

#### Expected Results
When simulated, the Bell state circuit should produce:
- **Measurement counts**: Approximately 50% `00` and 50% `11`
- **State vector**: `(|00⟩ + |11⟩)/√2`
- **Entanglement**: Maximum entanglement between the two qubits

### GHZ State Circuit

The GHZ (Greenberger-Horne-Zeilinger) state is a maximally entangled state of multiple qubits.

#### Cirq Implementation
```python
import cirq

def create_ghz_circuit(n_qubits):
    qubits = cirq.LineQubit.range(n_qubits)
    circuit = cirq.Circuit()
    
    # Apply Hadamard to first qubit
    circuit.append(cirq.H(qubits[0]))
    
    # Apply CNOT gates to create entanglement
    for i in range(1, n_qubits):
        circuit.append(cirq.CNOT(qubits[0], qubits[i]))
    
    # Measure all qubits
    circuit.append(cirq.measure(*qubits))
    
    return circuit

# Create 4-qubit GHZ state
ghz_circuit = create_ghz_circuit(4)
print("GHZ State Circuit (4 qubits):")
print(ghz_circuit)
```

#### Qiskit Implementation
```python
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def create_ghz_circuit(n_qubits):
    qr = QuantumRegister(n_qubits, 'q')
    cr = ClassicalRegister(n_qubits, 'c')
    qc = QuantumCircuit(qr, cr)
    
    # Apply Hadamard to first qubit
    qc.h(qr[0])
    
    # Apply CNOT gates to create entanglement
    for i in range(1, n_qubits):
        qc.cx(qr[0], qr[i])
    
    # Measure all qubits
    qc.measure(qr, cr)
    
    return qc

# Create 4-qubit GHZ state
ghz_circuit = create_ghz_circuit(4)
print("GHZ State Circuit (4 qubits):")
print(ghz_circuit)
```

#### Expected Results
For an n-qubit GHZ state:
- **Measurement counts**: Approximately 50% `0...0` and 50% `1...1`
- **State vector**: `(|0...0⟩ + |1...1⟩)/√2`
- **Entanglement**: Maximum entanglement across all qubits

### Parameterized Circuit

Parameterized circuits are essential for variational quantum algorithms.

#### Cirq Implementation
```python
import cirq
import sympy

# Create symbolic parameters
theta = sympy.Symbol('theta')
phi = sympy.Symbol('phi')

# Create qubits
q0, q1 = cirq.LineQubit.range(2)

# Create parameterized circuit
circuit = cirq.Circuit(
    cirq.Rx(theta)(q0),    # Parameterized X rotation
    cirq.Ry(phi)(q1),      # Parameterized Y rotation
    cirq.CNOT(q0, q1),     # Entangling gate
    cirq.measure(q0, q1)   # Measurement
)

print("Parameterized Circuit (Cirq):")
print(circuit)
```

#### Qiskit Implementation
```python
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

# Create parameters
theta = Parameter('θ')
phi = Parameter('φ')

# Create quantum circuit
qc = QuantumCircuit(2, 2)

# Apply parameterized gates
qc.rx(theta, 0)
qc.ry(phi, 1)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

print("Parameterized Circuit (Qiskit):")
print(qc)
```

#### PennyLane Implementation
```python
import pennylane as qml
import numpy as np

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def parameterized_circuit(theta, phi):
    qml.RX(theta, wires=0)
    qml.RY(phi, wires=1)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(0)), qml.expval(qml.PauliZ(1))

# Test with specific parameters
theta_val = np.pi/4
phi_val = np.pi/3

result = parameterized_circuit(theta_val, phi_val)
print("Parameterized Circuit (PennyLane):")
print(f"Parameters: theta={theta_val}, phi={phi_val}")
print(f"Expectation values: {result}")
```

## Quantum Algorithms

### Quantum Fourier Transform (QFT)

The QFT is a key component in many quantum algorithms, including Shor's algorithm.

#### Cirq Implementation
```python
import cirq
import numpy as np

def create_qft_circuit(qubits):
    circuit = cirq.Circuit()
    
    for i, qubit in enumerate(qubits):
        # Apply Hadamard gate
        circuit.append(cirq.H(qubit))
        
        # Apply controlled phase rotations
        for j in range(i + 1, len(qubits)):
            angle = 2 * np.pi / (2 ** (j - i + 1))
            circuit.append(cirq.CZPowGate(exponent=angle/np.pi)(qubits[j], qubit))
    
    # Swap qubits to get correct order
    for i in range(len(qubits) // 2):
        circuit.append(cirq.SWAP(qubits[i], qubits[len(qubits) - 1 - i]))
    
    return circuit

# Create 4-qubit QFT
qubits = cirq.LineQubit.range(4)
qft_circuit = create_qft_circuit(qubits)
print("Quantum Fourier Transform (4 qubits):")
print(qft_circuit)
```

#### Qiskit Implementation
```python
from qiskit import QuantumCircuit
import numpy as np

def create_qft_circuit(n_qubits):
    qc = QuantumCircuit(n_qubits)
    
    for i in range(n_qubits):
        qc.h(i)
        
        for j in range(i + 1, n_qubits):
            angle = 2 * np.pi / (2 ** (j - i + 1))
            qc.cp(angle, j, i)
    
    # Swap qubits to get correct order
    for i in range(n_qubits // 2):
        qc.swap(i, n_qubits - 1 - i)
    
    return qc

# Create 4-qubit QFT
qft_circuit = create_qft_circuit(4)
print("Quantum Fourier Transform (4 qubits):")
print(qft_circuit)
```

#### PennyLane Implementation
```python
import pennylane as qml
import numpy as np

def create_qft_circuit(n_qubits):
    dev = qml.device("default.qubit", wires=n_qubits)
    
    @qml.qnode(dev)
    def qft_circuit():
        for i in range(n_qubits):
            qml.Hadamard(wires=i)
            
            for j in range(i + 1, n_qubits):
                angle = 2 * np.pi / (2 ** (j - i + 1))
                qml.CRZ(angle, wires=[j, i])
        
        # Swap qubits to get correct order
        for i in range(n_qubits // 2):
            qml.SWAP(wires=[i, n_qubits - 1 - i])
        
        return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
    
    return qft_circuit

# Create 4-qubit QFT
qft_circuit = create_qft_circuit(4)
result = qft_circuit()
print("Quantum Fourier Transform (4 qubits):")
print(f"Expectation values: {result}")
```

### Quantum Phase Estimation (QPE)

QPE is used to estimate the phase of an eigenvector of a unitary operator.

#### Cirq Implementation
```python
import cirq
import numpy as np

def create_qpe_circuit(precision_qubits, target_qubit=1):
    # Create qubits
    precision = cirq.LineQubit.range(precision_qubits)
    target = cirq.LineQubit(precision_qubits)
    
    circuit = cirq.Circuit()
    
    # Initialize precision qubits in superposition
    for qubit in precision:
        circuit.append(cirq.H(qubit))
    
    # Apply controlled unitary operations
    for i, qubit in enumerate(precision):
        # Apply controlled-U^(2^i) operation
        # For demonstration, we use a simple controlled rotation
        angle = 2 * np.pi * 0.125 * (2 ** i)  # Example phase
        circuit.append(cirq.CZPowGate(exponent=angle/np.pi)(qubit, target))
    
    # Apply inverse QFT to precision qubits
    circuit.append(cirq.inverse(cirq.QuantumFourierTransformGate(precision_qubits))(*precision))
    
    # Measure precision qubits
    circuit.append(cirq.measure(*precision))
    
    return circuit

# Create 4-qubit QPE
qpe_circuit = create_qpe_circuit(4)
print("Quantum Phase Estimation (4 precision qubits):")
print(qpe_circuit)
```

### Quantum Teleportation

Quantum teleportation demonstrates quantum entanglement and information transfer.

#### Cirq Implementation
```python
import cirq

def create_teleportation_circuit():
    # Create qubits: Alice's qubit, Bell pair, and Bob's qubit
    alice = cirq.LineQubit(0)
    bell_1 = cirq.LineQubit(1)
    bell_2 = cirq.LineQubit(2)
    bob = cirq.LineQubit(3)
    
    circuit = cirq.Circuit()
    
    # Prepare Bell pair between Bell_1 and Bell_2
    circuit.append(cirq.H(bell_1))
    circuit.append(cirq.CNOT(bell_1, bell_2))
    
    # Prepare Alice's qubit in some state (e.g., |1⟩)
    circuit.append(cirq.X(alice))
    
    # Alice performs Bell measurement
    circuit.append(cirq.CNOT(alice, bell_1))
    circuit.append(cirq.H(alice))
    
    # Measure Alice's qubit and Bell_1
    circuit.append(cirq.measure(alice, bell_1))
    
    # Bob applies corrections based on measurement results
    circuit.append(cirq.CNOT(bell_1, bell_2))
    circuit.append(cirq.CZ(alice, bell_2))
    
    # Measure Bob's qubit
    circuit.append(cirq.measure(bell_2))
    
    return circuit

teleport_circuit = create_teleportation_circuit()
print("Quantum Teleportation Circuit:")
print(teleport_circuit)
```

## Variational Quantum Circuits

### Variational Quantum Eigensolver (VQE)

VQE is used to find the ground state energy of quantum systems.

#### PennyLane Implementation
```python
import pennylane as qml
import numpy as np

def create_vqe_circuit():
    dev = qml.device("default.qubit", wires=2)
    
    @qml.qnode(dev)
    def vqe_circuit(theta):
        # Prepare variational state
        qml.RY(theta, wires=0)
        qml.CNOT(wires=[0, 1])
        
        # Measure Hamiltonian terms
        # H = Z⊗Z + X⊗X
        zz = qml.expval(qml.PauliZ(0) @ qml.PauliZ(1))
        xx = qml.expval(qml.PauliX(0) @ qml.PauliX(1))
        
        return zz + xx
    
    return vqe_circuit

# Create VQE circuit
vqe_circuit = create_vqe_circuit()

# Optimize parameters
from pennylane import numpy as pnp

def cost_function(theta):
    return vqe_circuit(theta)

# Use gradient descent
opt = qml.GradientDescentOptimizer(stepsize=0.4)
theta = pnp.array(0.0, requires_grad=True)

print("VQE Optimization:")
for iteration in range(100):
    theta, energy = opt.step_and_cost(cost_function, theta)
    if iteration % 10 == 0:
        print(f"Iteration {iteration}: Energy = {energy:.4f}")

print(f"Final energy: {energy:.4f}")
print(f"Optimal parameter: {theta:.4f}")
```

### Quantum Approximate Optimization Algorithm (QAOA)

QAOA is used for combinatorial optimization problems.

#### PennyLane Implementation
```python
import pennylane as qml
import numpy as np

def create_qaoa_circuit(n_qubits=4, p=2):
    dev = qml.device("default.qubit", wires=n_qubits)
    
    @qml.qnode(dev)
    def qaoa_circuit(gamma, beta):
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
    
    return qaoa_circuit

# Create QAOA circuit
qaoa_circuit = create_qaoa_circuit(4, 2)

# Initialize parameters
gamma = np.random.randn(2)
beta = np.random.randn(2)

# Execute circuit
result = qaoa_circuit(gamma, beta)
print("QAOA Circuit (4 qubits, 2 layers):")
print(f"Parameters: gamma={gamma}, beta={beta}")
print(f"Expectation values: {result}")
```

## Error Correction

### 3-Qubit Bit-Flip Code

This is a simple quantum error correction code that can detect and correct bit-flip errors.

#### Cirq Implementation
```python
import cirq

def create_error_correction_circuit():
    # Create qubits: 3 data qubits + 2 ancilla qubits
    data_qubits = cirq.LineQubit.range(3)
    ancilla_qubits = cirq.LineQubit.range(3, 5)
    
    circuit = cirq.Circuit()
    
    # Encoding: Prepare logical |1⟩ state
    circuit.append(cirq.X(data_qubits[0]))  # Flip first qubit to |1⟩
    
    # Apply CNOT gates to create encoded state
    circuit.append(cirq.CNOT(data_qubits[0], data_qubits[1]))
    circuit.append(cirq.CNOT(data_qubits[0], data_qubits[2]))
    
    # Error detection: Apply syndrome measurement
    circuit.append(cirq.CNOT(data_qubits[0], ancilla_qubits[0]))
    circuit.append(cirq.CNOT(data_qubits[1], ancilla_qubits[0]))
    circuit.append(cirq.CNOT(data_qubits[1], ancilla_qubits[1]))
    circuit.append(cirq.CNOT(data_qubits[2], ancilla_qubits[1]))
    
    # Measure ancilla qubits (syndrome)
    circuit.append(cirq.measure(*ancilla_qubits))
    
    # Measure data qubits
    circuit.append(cirq.measure(*data_qubits))
    
    return circuit

error_correction_circuit = create_error_correction_circuit()
print("3-Qubit Bit-Flip Error Correction Circuit:")
print(error_correction_circuit)
```

#### Qiskit Implementation
```python
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def create_error_correction_circuit():
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

error_correction_circuit = create_error_correction_circuit()
print("3-Qubit Bit-Flip Error Correction Circuit:")
print(error_correction_circuit)
```

## Quantum Machine Learning

### Quantum Neural Network

A simple quantum neural network for classification tasks.

#### PennyLane Implementation
```python
import pennylane as qml
import numpy as np

def create_quantum_neural_network(n_qubits=2, n_layers=2):
    dev = qml.device("default.qubit", wires=n_qubits)
    
    @qml.qnode(dev)
    def quantum_neural_network(inputs, weights):
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
    
    return quantum_neural_network

# Create quantum neural network
qnn = create_quantum_neural_network(2, 2)

# Initialize parameters
inputs = np.random.randn(2)
weights = np.random.randn(2, 2, 3)

# Execute circuit
result = qnn(inputs, weights)
print("Quantum Neural Network:")
print(f"Input: {inputs}")
print(f"Weights shape: {weights.shape}")
print(f"Output: {result}")
```

### Variational Quantum Classifier

A variational quantum classifier for binary classification.

#### PennyLane Implementation
```python
import pennylane as qml
import numpy as np

def create_variational_classifier(n_qubits=2, n_layers=2):
    dev = qml.device("default.qubit", wires=n_qubits)
    
    @qml.qnode(dev)
    def variational_classifier(inputs, weights):
        # Encode input data
        for i in range(n_qubits):
            qml.RX(inputs[i], wires=i)
            qml.RY(inputs[i], wires=i)
        
        # Variational layers
        for layer in range(n_layers):
            # Entangling layer
            for i in range(n_qubits - 1):
                qml.CNOT(wires=[i, i + 1])
            
            # Rotation layer
            for i in range(n_qubits):
                qml.RX(weights[layer, i, 0], wires=i)
                qml.RY(weights[layer, i, 1], wires=i)
                qml.RZ(weights[layer, i, 2], wires=i)
        
        # Measure first qubit for classification
        return qml.expval(qml.PauliZ(0))
    
    return variational_classifier

# Create variational classifier
classifier = create_variational_classifier(2, 2)

# Initialize parameters
inputs = np.random.randn(2)
weights = np.random.randn(2, 2, 3)

# Execute circuit
result = classifier(inputs, weights)
print("Variational Quantum Classifier:")
print(f"Input: {inputs}")
print(f"Classification output: {result}")
print(f"Predicted class: {'Class 1' if result > 0 else 'Class 0'}")
```

## Advanced Examples

### Quantum Chemistry (H2 Molecule)

A simple quantum chemistry example using VQE for the H2 molecule.

#### PennyLane Implementation
```python
import pennylane as qml
import numpy as np

def create_h2_vqe():
    dev = qml.device("default.qubit", wires=2)
    
    @qml.qnode(dev)
    def h2_circuit(theta):
        # Prepare Hartree-Fock state (|01⟩)
        qml.PauliX(wires=1)
        
        # Apply variational ansatz
        # Single-qubit rotations
        qml.RY(theta, wires=0)
        qml.RY(theta, wires=1)
        
        # Entangling gate
        qml.CNOT(wires=[0, 1])
        
        # More single-qubit rotations
        qml.RZ(theta, wires=0)
        qml.RZ(theta, wires=1)
        
        # Measure in computational basis
        return qml.expval(qml.PauliZ(0)), qml.expval(qml.PauliZ(1))
    
    return h2_circuit

# Create H2 VQE circuit
h2_circuit = create_h2_vqe()

# Test with different parameters
thetas = np.linspace(0, 2*np.pi, 10)
results = []

for theta in thetas:
    result = h2_circuit(theta)
    results.append(result)

print("H2 Molecule VQE:")
for i, (theta, result) in enumerate(zip(thetas, results)):
    print(f"θ = {theta:.2f}: Expectation values = {result}")
```

### Quantum Walk

A quantum walk implementation demonstrating quantum dynamics.

#### Cirq Implementation
```python
import cirq
import numpy as np

def create_quantum_walk_circuit(steps=4):
    # Create qubits: coin qubit + position qubits
    coin = cirq.LineQubit(0)
    position_qubits = cirq.LineQubit.range(1, 2 * steps + 2)
    
    circuit = cirq.Circuit()
    
    # Initialize coin in superposition
    circuit.append(cirq.H(coin))
    
    # Initialize position qubits (start at center)
    center = len(position_qubits) // 2
    circuit.append(cirq.X(position_qubits[center]))
    
    # Perform quantum walk steps
    for step in range(steps):
        # Apply coin flip
        circuit.append(cirq.H(coin))
        
        # Apply controlled shift based on coin state
        for i in range(len(position_qubits) - 1):
            # If coin is |0⟩, move left; if |1⟩, move right
            circuit.append(cirq.CSWAP(coin, position_qubits[i], position_qubits[i + 1]))
    
    # Measure all qubits
    circuit.append(cirq.measure(coin))
    circuit.append(cirq.measure(*position_qubits))
    
    return circuit

quantum_walk_circuit = create_quantum_walk_circuit(4)
print("Quantum Walk Circuit (4 steps):")
print(quantum_walk_circuit)
```

## Using QCanvas with Examples

### Converting Between Frameworks

To convert any of these examples between frameworks using QCanvas:

1. **Copy the source code** from one framework
2. **Paste it into the QCanvas converter**
3. **Select the target framework**
4. **Choose optimization level** (0-3)
5. **Click convert** to get the equivalent code

### Example Conversion Workflow

```python
# Step 1: Start with Cirq Bell state
import cirq

q0, q1 = cirq.LineQubit.range(2)
circuit = cirq.Circuit(
    cirq.H(q0),
    cirq.CNOT(q0, q1),
    cirq.measure(q0, q1)
)

# Step 2: Convert to Qiskit using QCanvas API
import requests

conversion_request = {
    "source_framework": "cirq",
    "target_framework": "qiskit",
    "source_code": """
import cirq

q0, q1 = cirq.LineQubit.range(2)
circuit = cirq.Circuit(
    cirq.H(q0),
    cirq.CNOT(q0, q1),
    cirq.measure(q0, q1)
)
""",
    "optimization_level": 1
}

response = requests.post("http://localhost:8000/api/convert", json=conversion_request)
result = response.json()

print("Converted Qiskit code:")
print(result["converted_code"])
```

### Simulating Circuits

To simulate any of these circuits using QCanvas:

1. **Convert to OpenQASM 3.0** using the converter
2. **Use the simulator** with the QASM code
3. **Choose appropriate backend** (statevector, density_matrix, stabilizer)
4. **Set simulation parameters** (shots, noise model, etc.)
5. **Run simulation** and analyze results

### Example Simulation Workflow

```python
# Step 1: Get QASM code from conversion
qasm_code = result["qasm_code"]

# Step 2: Simulate using QCanvas API
simulation_request = {
    "qasm_code": qasm_code,
    "backend": "statevector",
    "shots": 1000,
    "noise_model": None,
    "optimization_level": 1
}

response = requests.post("http://localhost:8000/api/simulate", json=simulation_request)
result = response.json()

print("Simulation results:")
print(f"Measurement counts: {result['results']['counts']}")
print(f"Execution time: {result['execution_time']:.3f} seconds")
```

## Best Practices for Examples

### Code Organization
1. **Modular Design**: Break complex circuits into functions
2. **Clear Naming**: Use descriptive variable and function names
3. **Documentation**: Add comments explaining quantum operations
4. **Parameterization**: Use parameters for flexible circuit design

### Testing and Validation
1. **Unit Tests**: Test individual circuit components
2. **Integration Tests**: Test complete circuit functionality
3. **Cross-Framework Validation**: Verify conversions produce same results
4. **Performance Testing**: Compare execution times across frameworks

### Optimization
1. **Circuit Depth**: Minimize circuit depth for better performance
2. **Gate Count**: Reduce number of gates when possible
3. **Backend Selection**: Choose appropriate backend for your circuit
4. **Parameter Optimization**: Use optimization techniques for variational circuits

## Conclusion

These examples demonstrate the power and flexibility of QCanvas for quantum computing applications. From basic circuits to advanced algorithms, QCanvas provides the tools you need to work effectively across different quantum computing frameworks.

Start with simple examples and gradually build complexity as you become more comfortable with quantum computing concepts. Use the conversion and simulation features to explore different approaches and optimize your quantum circuits.

Remember to experiment with different parameters, optimization levels, and frameworks to find the best approach for your specific use case.
