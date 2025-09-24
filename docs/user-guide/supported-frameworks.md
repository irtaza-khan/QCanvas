# Supported Quantum Computing Frameworks

## Overview

QCanvas supports three major quantum computing frameworks, each with its own strengths and specializations. This guide provides detailed information about each framework, their capabilities, and how to use them effectively in QCanvas.

## Framework Comparison

| Framework | Developer | Focus | Max Qubits | Key Features |
|-----------|-----------|-------|------------|--------------|
| **Cirq** | Google | Near-term devices | 53+ | Device-specific, noise models |
| **Qiskit** | IBM | Comprehensive | 100+ | IBM devices, quantum ML |
| **PennyLane** | Xanadu | Quantum ML | 50+ | Gradients, hybrid algorithms |

## Cirq (Google)

### Overview
Cirq is Google's quantum computing framework, designed specifically for near-term quantum devices (NISQ era). It focuses on practical quantum computing with realistic noise models and device-specific optimizations.

### Key Features

#### Device-Specific Design
- **Grid Qubits**: Support for 2D grid layouts (like Google's Sycamore)
- **Device Constraints**: Built-in support for device connectivity constraints
- **Calibration**: Integration with device calibration data
- **Noise Models**: Realistic noise models based on actual device characteristics

#### Advanced Circuit Features
- **Parameterized Circuits**: Support for parameterized quantum circuits
- **Circuit Optimization**: Built-in circuit optimization tools
- **Measurement**: Flexible measurement strategies
- **Classical Control**: Classical control flow in quantum circuits

#### Research Tools
- **Quantum Algorithms**: Implementation of major quantum algorithms
- **Error Correction**: Tools for quantum error correction
- **Quantum Chemistry**: Integration with quantum chemistry applications
- **Quantum Machine Learning**: Support for quantum ML workflows

### Supported Gates

#### Single-Qubit Gates
```python
# Basic gates
cirq.H(qubit)      # Hadamard gate
cirq.X(qubit)      # Pauli-X gate
cirq.Y(qubit)      # Pauli-Y gate
cirq.Z(qubit)      # Pauli-Z gate
cirq.S(qubit)      # S gate
cirq.T(qubit)      # T gate

# Parameterized gates
cirq.Rx(angle, qubit)  # Rotation around X-axis
cirq.Ry(angle, qubit)  # Rotation around Y-axis
cirq.Rz(angle, qubit)  # Rotation around Z-axis
cirq.PhasedXPowGate(phase_exponent=0.25, exponent=0.5)(qubit)
```

#### Two-Qubit Gates
```python
# Entangling gates
cirq.CNOT(control, target)     # Controlled-NOT
cirq.CZ(control, target)       # Controlled-Z
cirq.SWAP(qubit1, qubit2)      # SWAP gate
cirq.ISWAP(qubit1, qubit2)     # iSWAP gate

# Parameterized two-qubit gates
cirq.CZPowGate(exponent=0.5)(control, target)
cirq.ISWAPPowGate(exponent=0.5)(qubit1, qubit2)
```

#### Multi-Qubit Gates
```python
# Multi-qubit operations
cirq.CCX(control1, control2, target)  # Toffoli gate
cirq.CSWAP(control, qubit1, qubit2)   # Controlled-SWAP
```

### Example Circuits

#### Bell State Circuit
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

print(circuit)
```

#### Quantum Fourier Transform
```python
import cirq
import numpy as np

def create_qft_circuit(qubits):
    circuit = cirq.Circuit()
    
    for i, qubit in enumerate(qubits):
        circuit.append(cirq.H(qubit))
        
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
```

#### Parameterized Circuit
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
    cirq.Rx(theta)(q0),
    cirq.Ry(phi)(q1),
    cirq.CNOT(q0, q1),
    cirq.measure(q0, q1)
)

print(circuit)
```

### Best Practices

#### Circuit Design
1. **Use Device-Aware Qubits**: Use `GridQubit` for device-specific layouts
2. **Consider Connectivity**: Design circuits with device connectivity in mind
3. **Optimize for Noise**: Use noise-aware circuit design techniques
4. **Parameterize Circuits**: Use symbolic parameters for variational algorithms

#### Performance Optimization
1. **Use Built-in Optimizers**: Leverage Cirq's circuit optimization tools
2. **Minimize Circuit Depth**: Reduce circuit depth to minimize decoherence
3. **Use Appropriate Gates**: Choose gates that are native to target devices
4. **Batch Operations**: Use batch operations when possible

## Qiskit (IBM)

### Overview
Qiskit is IBM's comprehensive quantum computing framework, designed for both research and practical applications. It provides access to IBM's quantum devices and simulators, along with extensive tools for quantum machine learning and algorithm development.

### Key Features

#### Comprehensive Ecosystem
- **Multiple Backends**: Access to IBM quantum devices and simulators
- **Quantum Machine Learning**: Qiskit Machine Learning library
- **Optimization**: Qiskit Optimization for quantum optimization problems
- **Finance**: Qiskit Finance for quantum finance applications
- **Nature**: Qiskit Nature for quantum chemistry and physics

#### Advanced Simulation
- **Aer Simulator**: High-performance quantum circuit simulator
- **Noise Models**: Realistic noise models for quantum devices
- **Pulse Control**: Low-level pulse control for quantum devices
- **Error Mitigation**: Advanced error mitigation techniques

#### Educational Resources
- **Textbook**: Comprehensive quantum computing textbook
- **Tutorials**: Extensive tutorial library
- **Community**: Large and active community
- **Documentation**: Excellent documentation and examples

### Supported Gates

#### Single-Qubit Gates
```python
from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)

# Basic gates
qc.h(0)      # Hadamard gate
qc.x(0)      # Pauli-X gate
qc.y(0)      # Pauli-Y gate
qc.z(0)      # Pauli-Z gate
qc.s(0)      # S gate
qc.t(0)      # T gate

# Parameterized gates
qc.rx(theta, 0)  # Rotation around X-axis
qc.ry(theta, 0)  # Rotation around Y-axis
qc.rz(theta, 0)  # Rotation around Z-axis
qc.u(theta, phi, lam, 0)  # U gate
```

#### Two-Qubit Gates
```python
# Entangling gates
qc.cx(0, 1)      # Controlled-NOT
qc.cz(0, 1)      # Controlled-Z
qc.swap(0, 1)    # SWAP gate
qc.cswap(0, 1, 2)  # Controlled-SWAP

# Parameterized two-qubit gates
qc.crx(theta, 0, 1)  # Controlled-RX
qc.cry(theta, 0, 1)  # Controlled-RY
qc.crz(theta, 0, 1)  # Controlled-RZ
```

#### Multi-Qubit Gates
```python
# Multi-qubit operations
qc.ccx(0, 1, 2)  # Toffoli gate
qc.mcx([0, 1], 2)  # Multi-controlled X
qc.mct([0, 1], 2)  # Multi-controlled T
```

### Example Circuits

#### Bell State Circuit
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

print(qc)
```

#### Quantum Fourier Transform
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
```

#### Parameterized Circuit
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

print(qc)
```

### Best Practices

#### Circuit Design
1. **Use Quantum Registers**: Organize qubits into logical registers
2. **Optimize for IBM Devices**: Design circuits for IBM's device topology
3. **Use Qiskit Optimizers**: Leverage Qiskit's optimization passes
4. **Error Mitigation**: Use error mitigation techniques for better results

#### Performance Optimization
1. **Transpile Efficiently**: Use appropriate transpilation settings
2. **Choose Right Backend**: Select the best backend for your needs
3. **Use Noise Models**: Simulate with realistic noise models
4. **Batch Jobs**: Submit multiple jobs efficiently

## PennyLane (Xanadu)

### Overview
PennyLane is Xanadu's quantum machine learning framework, specializing in variational quantum circuits and hybrid classical-quantum algorithms. It's designed for quantum machine learning, optimization, and quantum chemistry applications.

### Key Features

#### Quantum Machine Learning
- **Automatic Differentiation**: Compute gradients of quantum circuits
- **Hybrid Algorithms**: Seamless integration of classical and quantum computing
- **Optimization**: Built-in optimizers for variational quantum algorithms
- **Quantum Neural Networks**: Tools for building quantum neural networks

#### Advanced Features
- **Multiple Devices**: Support for various quantum devices and simulators
- **Plugin System**: Extensible plugin architecture
- **Quantum Chemistry**: Integration with quantum chemistry packages
- **Quantum Generative Models**: Support for quantum generative adversarial networks

#### Research Tools
- **Variational Quantum Eigensolver (VQE)**: Implementation of VQE algorithm
- **Quantum Approximate Optimization Algorithm (QAOA)**: QAOA implementation
- **Quantum Natural Gradient**: Advanced optimization techniques
- **Quantum Fisher Information**: Quantum information theoretic tools

### Supported Gates

#### Single-Qubit Gates
```python
import pennylane as qml

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def circuit():
    # Basic gates
    qml.Hadamard(wires=0)  # Hadamard gate
    qml.PauliX(wires=0)    # Pauli-X gate
    qml.PauliY(wires=0)    # Pauli-Y gate
    qml.PauliZ(wires=0)    # Pauli-Z gate
    qml.S(wires=0)         # S gate
    qml.T(wires=0)         # T gate
    
    # Parameterized gates
    qml.RX(theta, wires=0)  # Rotation around X-axis
    qml.RY(theta, wires=0)  # Rotation around Y-axis
    qml.RZ(theta, wires=0)  # Rotation around Z-axis
    qml.Rot(phi, theta, omega, wires=0)  # General rotation
    
    return qml.expval(qml.PauliZ(0))
```

#### Two-Qubit Gates
```python
@qml.qnode(dev)
def circuit():
    # Entangling gates
    qml.CNOT(wires=[0, 1])      # Controlled-NOT
    qml.CZ(wires=[0, 1])        # Controlled-Z
    qml.SWAP(wires=[0, 1])      # SWAP gate
    qml.ISWAP(wires=[0, 1])     # iSWAP gate
    
    # Parameterized two-qubit gates
    qml.CRX(theta, wires=[0, 1])  # Controlled-RX
    qml.CRY(theta, wires=[0, 1])  # Controlled-RY
    qml.CRZ(theta, wires=[0, 1])  # Controlled-RZ
    
    return qml.expval(qml.PauliZ(0))
```

#### Multi-Qubit Gates
```python
@qml.qnode(dev)
def circuit():
    # Multi-qubit operations
    qml.Toffoli(wires=[0, 1, 2])  # Toffoli gate
    qml.CSWAP(wires=[0, 1, 2])    # Controlled-SWAP
    qml.MultiRZ(theta, wires=[0, 1, 2])  # Multi-qubit RZ
    
    return qml.expval(qml.PauliZ(0))
```

### Example Circuits

#### Variational Quantum Circuit
```python
import pennylane as qml
import numpy as np

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def variational_circuit(weights, bias):
    # Initial layer
    for i in range(2):
        qml.RX(bias[i], wires=i)
        qml.RY(bias[i + 2], wires=i)
    
    # Entangling layer
    qml.CNOT(wires=[0, 1])
    
    # Variational layer
    for i in range(2):
        qml.RX(weights[0, i], wires=i)
        qml.RY(weights[1, i], wires=i)
    
    return [qml.expval(qml.PauliZ(i)) for i in range(2)]

# Initialize parameters
weights = np.random.randn(2, 2)
bias = np.random.randn(4)

# Execute circuit
result = variational_circuit(weights, bias)
print(result)
```

#### Quantum Neural Network
```python
import pennylane as qml
import numpy as np

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def quantum_neural_network(inputs, weights):
    # Encode input data
    for i in range(2):
        qml.RX(inputs[i], wires=i)
        qml.RY(inputs[i], wires=i)
    
    # Process through layers
    for layer in range(2):
        # Entangling layer
        qml.CNOT(wires=[0, 1])
        
        # Rotation layer
        for i in range(2):
            qml.RX(weights[layer, i, 0], wires=i)
            qml.RY(weights[layer, i, 1], wires=i)
            qml.RZ(weights[layer, i, 2], wires=i)
    
    return [qml.expval(qml.PauliZ(i)) for i in range(2)]

# Initialize parameters
inputs = np.random.randn(2)
weights = np.random.randn(2, 2, 3)

# Execute circuit
result = quantum_neural_network(inputs, weights)
print(result)
```

#### VQE for H2 Molecule
```python
import pennylane as qml
import numpy as np

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

# Optimize parameters
from pennylane import numpy as pnp

def cost_function(theta):
    return vqe_circuit(theta)

# Use gradient descent
opt = qml.GradientDescentOptimizer(stepsize=0.4)
theta = pnp.array(0.0, requires_grad=True)

for iteration in range(100):
    theta, energy = opt.step_and_cost(cost_function, theta)
    if iteration % 10 == 0:
        print(f"Iteration {iteration}: Energy = {energy:.4f}")
```

### Best Practices

#### Circuit Design
1. **Use QNodes**: Wrap circuits in QNode decorators for automatic differentiation
2. **Parameterize Circuits**: Use parameterized gates for variational algorithms
3. **Optimize for Gradients**: Design circuits that are efficient for gradient computation
4. **Use Appropriate Devices**: Choose devices that support your required operations

#### Performance Optimization
1. **Use Gradient Descent**: Leverage automatic differentiation for optimization
2. **Choose Right Optimizer**: Select appropriate optimizers for your problem
3. **Use Hybrid Algorithms**: Combine classical and quantum computing effectively
4. **Batch Operations**: Use batch processing for multiple parameter sets

## Framework Conversion Guidelines

### General Principles

#### Conversion Process
1. **Parse Source Code**: Extract circuit structure from source framework
2. **Convert to OpenQASM 3.0**: Use OpenQASM as intermediate representation
3. **Generate Target Code**: Convert OpenQASM to target framework
4. **Validate Conversion**: Ensure converted circuit produces same results

#### Optimization Levels
- **Level 0**: Direct conversion without optimization
- **Level 1**: Basic gate fusion and simplification
- **Level 2**: Advanced optimizations including circuit restructuring
- **Level 3**: Maximum optimization, may change circuit structure

### Framework-Specific Considerations

#### Cirq to Qiskit
- **Qubit Mapping**: Convert Cirq qubits to Qiskit quantum registers
- **Gate Translation**: Map Cirq gates to equivalent Qiskit gates
- **Measurement**: Convert Cirq measurement operations to Qiskit format
- **Optimization**: Use Qiskit's transpilation for device-specific optimization

#### Qiskit to PennyLane
- **QNode Wrapping**: Wrap Qiskit circuits in PennyLane QNodes
- **Parameter Handling**: Convert Qiskit parameters to PennyLane format
- **Gradient Computation**: Enable automatic differentiation for PennyLane
- **Device Selection**: Choose appropriate PennyLane device

#### PennyLane to Cirq
- **Circuit Extraction**: Extract circuit structure from PennyLane QNode
- **Gate Conversion**: Convert PennyLane gates to Cirq equivalents
- **Parameter Binding**: Bind PennyLane parameters to concrete values
- **Device Optimization**: Optimize for Cirq's device-specific features

### Validation and Testing

#### Conversion Validation
1. **Circuit Equivalence**: Verify circuits produce same results
2. **Gate Count**: Compare gate counts before and after conversion
3. **Circuit Depth**: Check circuit depth optimization
4. **Parameter Handling**: Ensure parameters are correctly converted

#### Testing Strategies
1. **Unit Tests**: Test individual gate conversions
2. **Integration Tests**: Test complete circuit conversions
3. **Performance Tests**: Compare execution times
4. **Regression Tests**: Ensure conversions remain correct over time

## Advanced Features

### Noise Models
All frameworks support noise modeling, but with different approaches:

#### Cirq Noise Models
```python
import cirq
from cirq.devices import GridQubit
from cirq.ops import common_gates
from cirq.contrib.noise_models import DepolarizingNoiseModel

# Create noise model
noise_model = DepolarizingNoiseModel(depol_prob=0.01)

# Apply noise to circuit
noisy_circuit = noise_model.noisy_circuit(circuit)
```

#### Qiskit Noise Models
```python
from qiskit.providers.aer.noise import NoiseModel
from qiskit.providers.aer.noise.errors import depolarizing_error

# Create noise model
noise_model = NoiseModel()
noise_model.add_all_qubit_quantum_error(depolarizing_error(0.01, 1), ['u1', 'u2', 'u3'])

# Use noise model in simulation
backend = Aer.get_backend('qasm_simulator')
job = execute(circuit, backend, noise_model=noise_model)
```

#### PennyLane Noise Models
```python
import pennylane as qml

# Use noisy device
dev = qml.device("default.mixed", wires=2)

@qml.qnode(dev)
def noisy_circuit():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(0))
```

### Error Mitigation
Each framework provides different error mitigation techniques:

#### Cirq Error Mitigation
- **Zero-Noise Extrapolation**: Extrapolate to zero noise
- **Measurement Error Mitigation**: Correct measurement errors
- **Circuit Optimization**: Optimize circuits for noise resilience

#### Qiskit Error Mitigation
- **Measurement Error Mitigation**: Built-in measurement error correction
- **Zero-Noise Extrapolation**: Extrapolate results to zero noise
- **Probabilistic Error Cancellation**: Cancel errors probabilistically

#### PennyLane Error Mitigation
- **Gradient Descent**: Use gradients for error mitigation
- **Variational Error Mitigation**: Optimize error mitigation parameters
- **Hybrid Algorithms**: Combine classical and quantum error mitigation

## Conclusion

Each framework has its own strengths and is optimized for different use cases:

- **Cirq**: Best for near-term quantum devices and research
- **Qiskit**: Best for comprehensive quantum computing and IBM devices
- **PennyLane**: Best for quantum machine learning and variational algorithms

QCanvas provides seamless conversion between these frameworks, allowing you to leverage the strengths of each while maintaining code portability and interoperability.

Choose the framework that best fits your specific use case, and use QCanvas to convert between frameworks as needed for different applications and devices.
