'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { Copy, Play, Code, Moon, Sun, Menu, X } from 'lucide-react'
import toast from 'react-hot-toast'
import { useFileStore } from '@/lib/store'

interface Example {
  id: string
  title: string
  description: string
  framework: 'qiskit' | 'cirq' | 'pennylane'
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  category: string
  code: string
  tags: string[]
}

const examples: Example[] = [
  {
    id: 'bell-state-qiskit',
    title: 'Bell State (Qiskit)',
    description: 'Create a Bell state using Qiskit - a fundamental quantum entangled state.',
    framework: 'qiskit',
    difficulty: 'beginner',
    category: 'Basic Circuits',
    code: `from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

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
print(qc)`,
    tags: ['entanglement', 'bell-state', 'hadamard', 'cnot']
  },
  {
    id: 'grover-qiskit',
    title: "Grover's Search (Qiskit)",
    description: 'A minimal Grover iteration on 2 qubits using a hard-coded oracle.',
    framework: 'qiskit',
    difficulty: 'advanced',
    category: 'Quantum Algorithms',
    code: `from qiskit import QuantumCircuit

def grover_oracle(qc: QuantumCircuit):
    # Mark state |11>
    qc.cz(0, 1)

def diffusion(qc: QuantumCircuit):
    qc.h([0,1])
    qc.x([0,1])
    qc.h(1)
    qc.cx(0,1)
    qc.h(1)
    qc.x([0,1])
    qc.h([0,1])

def create_grover():
    qc = QuantumCircuit(2, 2)
    qc.h([0,1])
    grover_oracle(qc)
    diffusion(qc)
    qc.measure([0,1],[0,1])
    return qc

qc = create_grover()
print(qc)`,
    tags: ['grover', 'oracle', 'diffusion']
  },
  {
    id: 'qft-cirq',
    title: 'QFT (Cirq)',
    description: 'Quantum Fourier Transform implemented with Cirq.',
    framework: 'cirq',
    difficulty: 'advanced',
    category: 'Quantum Algorithms',
    code: `import cirq, numpy as np

def qft(qubits):
    circuit = cirq.Circuit()
    n = len(qubits)
    for i in range(n):
        circuit.append(cirq.H(qubits[i]))
        for j in range(i+1, n):
            angle = np.pi / (2 ** (j - i))
            circuit.append(cirq.CZ(qubits[j], qubits[i]) ** (angle/np.pi))
    # swap
    for i in range(n//2):
        circuit.append(cirq.SWAP(qubits[i], qubits[n-1-i]))
    return circuit

q0, q1, q2 = cirq.LineQubit.range(3)
circuit = qft([q0,q1,q2])
print(circuit)`,
    tags: ['qft', 'fourier']
  },
  {
    id: 'vqe-pennylane-simple',
    title: 'VQE Simple (PennyLane)',
    description: 'A two-qubit ansatz with ZZ and XX expectation.',
    framework: 'pennylane',
    difficulty: 'intermediate',
    category: 'Variational Algorithms',
    code: `import pennylane as qml, numpy as np

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def ansatz(theta):
    qml.RY(theta, wires=0)
    qml.CNOT(wires=[0,1])
    return qml.expval(qml.PauliZ(0) @ qml.PauliZ(1)) + qml.expval(qml.PauliX(0) @ qml.PauliX(1))

val = ansatz(np.pi/4)
print(val)`,
    tags: ['vqe', 'variational']
  },
  {
    id: 'random-circuit-qiskit',
    title: 'Random Param Circuit (Qiskit)',
    description: 'A small random parameterized circuit for testing converters.',
    framework: 'qiskit',
    difficulty: 'intermediate',
    category: 'Basic Circuits',
    code: `from qiskit import QuantumCircuit
import numpy as np

qc = QuantumCircuit(3,3)
qc.ry(np.pi/3, 0)
qc.rz(0.7, 1)
qc.rx(1.2, 2)
qc.cx(0,1)
qc.cz(1,2)
qc.swap(0,2)
qc.measure([0,1,2],[0,1,2])
print(qc)`,
    tags: ['random', 'param']
  },
  {
    id: 'bell-state-cirq',
    title: 'Bell State (Cirq)',
    description: 'Create a Bell state using Cirq - demonstrating quantum entanglement.',
    framework: 'cirq',
    difficulty: 'beginner',
    category: 'Basic Circuits',
    code: `import cirq

# Create qubits
q0, q1 = cirq.LineQubit.range(2)

# Create Bell state circuit
circuit = cirq.Circuit(
    cirq.H(q0),           # Hadamard on first qubit
    cirq.CNOT(q0, q1),    # CNOT with q0 as control
    cirq.measure(q0, q1)  # Measure both qubits
)

print("Bell State Circuit (Cirq):")
print(circuit)`,
    tags: ['entanglement', 'bell-state', 'hadamard', 'cnot']
  },
  {
    id: 'bell-state-pennylane',
    title: 'Bell State (PennyLane)',
    description: 'Create a Bell state using PennyLane with expectation value measurements.',
    framework: 'pennylane',
    difficulty: 'beginner',
    category: 'Basic Circuits',
    code: `import pennylane as qml

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def bell_state_circuit():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(0)), qml.expval(qml.PauliZ(1))

# Execute circuit
result = bell_state_circuit()
print("Bell State Circuit (PennyLane):")
print(f"Expectation values: {result}")`,
    tags: ['entanglement', 'bell-state', 'hadamard', 'cnot']
  },
  {
    id: 'ghz-state-qiskit',
    title: 'GHZ State (Qiskit)',
    description: 'Create a GHZ (Greenberger-Horne-Zeilinger) state with multiple qubits.',
    framework: 'qiskit',
    difficulty: 'intermediate',
    category: 'Basic Circuits',
    code: `from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

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
print(ghz_circuit)`,
    tags: ['entanglement', 'ghz-state', 'multi-qubit', 'hadamard', 'cnot']
  },
  {
    id: 'quantum-fourier-transform',
    title: 'Quantum Fourier Transform',
    description: 'Implement the Quantum Fourier Transform (QFT) - a key component in many quantum algorithms.',
    framework: 'qiskit',
    difficulty: 'advanced',
    category: 'Quantum Algorithms',
    code: `from qiskit import QuantumCircuit
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
print(qft_circuit)`,
    tags: ['qft', 'fourier-transform', 'quantum-algorithm', 'phase-gates']
  },
  {
    id: 'quantum-teleportation',
    title: 'Quantum Teleportation',
    description: 'Implement quantum teleportation protocol to transfer quantum information.',
    framework: 'cirq',
    difficulty: 'advanced',
    category: 'Quantum Algorithms',
    code: `import cirq

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
print(teleport_circuit)`,
    tags: ['teleportation', 'bell-measurement', 'quantum-protocol', 'entanglement']
  },
  {
    id: 'variational-quantum-eigensolver',
    title: 'Variational Quantum Eigensolver (VQE)',
    description: 'Implement VQE to find the ground state energy of quantum systems.',
    framework: 'pennylane',
    difficulty: 'advanced',
    category: 'Variational Algorithms',
    code: `import pennylane as qml
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

# Test with specific parameter
theta_val = np.pi/4
result = vqe_circuit(theta_val)
print("VQE Circuit:")
print(f"Parameter: theta={theta_val}")
print(f"Energy: {result}")`,
    tags: ['vqe', 'variational', 'optimization', 'energy', 'hamiltonian']
  },
  {
    id: 'quantum-approximate-optimization',
    title: 'Quantum Approximate Optimization Algorithm (QAOA)',
    description: 'Implement QAOA for combinatorial optimization problems.',
    framework: 'pennylane',
    difficulty: 'advanced',
    category: 'Variational Algorithms',
    code: `import pennylane as qml
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
print(f"Expectation values: {result}")`,
    tags: ['qaoa', 'optimization', 'maxcut', 'variational', 'combinatorial']
  },
  {
    id: 'error-correction',
    title: '3-Qubit Bit-Flip Error Correction',
    description: 'Implement a simple quantum error correction code that can detect and correct bit-flip errors.',
    framework: 'qiskit',
    difficulty: 'intermediate',
    category: 'Error Correction',
    code: `from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

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
print(error_correction_circuit)`,
    tags: ['error-correction', 'syndrome', 'ancilla', 'encoding', 'detection']
  },
  {
    id: 'quantum-neural-network',
    title: 'Quantum Neural Network',
    description: 'A simple quantum neural network for classification tasks.',
    framework: 'pennylane',
    difficulty: 'intermediate',
    category: 'Quantum Machine Learning',
    code: `import pennylane as qml
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
print(f"Output: {result}")`,
    tags: ['quantum-ml', 'neural-network', 'classification', 'variational', 'layers']
  },
  {
    id: 'deutsch-jozsa-algorithm',
    title: 'Deutsch-Jozsa Algorithm',
    description: 'Demonstrates quantum advantage over classical algorithms for function evaluation.',
    framework: 'qiskit',
    difficulty: 'advanced',
    category: 'Quantum Algorithms',
    code: `from qiskit import QuantumCircuit, Aer, execute
from qiskit.visualization import plot_histogram
import numpy as np

def create_deutsch_jozsa_circuit(n_qubits, oracle_type='constant'):
    """
    Create Deutsch-Jozsa circuit for n-qubit function evaluation
    oracle_type: 'constant' or 'balanced'
    """
    qc = QuantumCircuit(n_qubits + 1, n_qubits)
    
    # Initialize ancilla qubit to |1⟩
    qc.x(n_qubits)
    
    # Apply Hadamard gates to all qubits
    for i in range(n_qubits + 1):
        qc.h(i)
    
    # Apply oracle (function evaluation)
    if oracle_type == 'balanced':
        # Balanced function: f(x) = x_0 ⊕ x_1 ⊕ ... ⊕ x_{n-1}
        for i in range(n_qubits):
            qc.cx(i, n_qubits)
    # For constant function, no additional gates needed
    
    # Apply Hadamard gates to first n qubits
    for i in range(n_qubits):
        qc.h(i)
    
    # Measure first n qubits
    qc.measure(range(n_qubits), range(n_qubits))
    
    return qc

# Create and run Deutsch-Jozsa circuit
n = 3  # Number of input qubits
qc_balanced = create_deutsch_jozsa_circuit(n, 'balanced')
qc_constant = create_deutsch_jozsa_circuit(n, 'constant')

print("Deutsch-Jozsa Algorithm:")
print("Balanced function circuit:")
print(qc_balanced)
print("\nConstant function circuit:")
print(qc_constant)`,
    tags: ['deutsch-jozsa', 'quantum-advantage', 'oracle', 'algorithm']
  },
  {
    id: 'quantum-key-distribution',
    title: 'BB84 Quantum Key Distribution',
    description: 'Implement the BB84 protocol for secure quantum key distribution.',
    framework: 'cirq',
    difficulty: 'advanced',
    category: 'Quantum Algorithms',
    code: `import cirq
import numpy as np

def bb84_protocol(n_bits=10):
    """
    Simulate BB84 quantum key distribution protocol
    """
    # Alice's random bits and bases
    alice_bits = np.random.randint(2, size=n_bits)
    alice_bases = np.random.randint(2, size=n_bits)
    
    # Bob's random bases
    bob_bases = np.random.randint(2, size=n_bits)
    
    # Create qubits
    qubits = [cirq.LineQubit(i) for i in range(n_bits)]
    
    # Alice prepares qubits
    circuit = cirq.Circuit()
    for i in range(n_bits):
        if alice_bits[i] == 1:
            circuit.append(cirq.X(qubits[i]))
        if alice_bases[i] == 1:
            circuit.append(cirq.H(qubits[i]))
    
    # Bob measures qubits
    for i in range(n_bits):
        if bob_bases[i] == 1:
            circuit.append(cirq.H(qubits[i]))
        circuit.append(cirq.measure(qubits[i], key=f'bob_{i}'))
    
    # Simulate the circuit
    simulator = cirq.Simulator()
    result = simulator.run(circuit, repetitions=1)
    
    # Extract Bob's results
    bob_results = []
    for i in range(n_bits):
        bob_results.append(result.measurements[f'bob_{i}'][0][0])
    
    # Sifted key (where bases match)
    sifted_key = []
    for i in range(n_bits):
        if alice_bases[i] == bob_bases[i]:
            sifted_key.append(bob_results[i])
    
    return {
        'alice_bits': alice_bits,
        'alice_bases': alice_bases,
        'bob_bases': bob_bases,
        'bob_results': bob_results,
        'sifted_key': sifted_key
    }

# Run BB84 protocol
bb84_result = bb84_protocol(10)
print("BB84 Quantum Key Distribution:")
print(f"Alice's bits: {bb84_result['alice_bits']}")
print(f"Alice's bases: {bb84_result['alice_bases']}")
print(f"Bob's bases: {bb84_result['bob_bases']}")
print(f"Bob's results: {bb84_result['bob_results']}")
print(f"Sifted key: {bb84_result['sifted_key']}")`,
    tags: ['bb84', 'quantum-cryptography', 'key-distribution', 'security']
  },
  {
    id: 'quantum-phase-estimation',
    title: 'Quantum Phase Estimation',
    description: 'Estimate the phase of an eigenvalue using quantum phase estimation algorithm.',
    framework: 'qiskit',
    difficulty: 'advanced',
    category: 'Quantum Algorithms',
    code: `from qiskit import QuantumCircuit, Aer, execute
from qiskit.circuit.library import QFT
import numpy as np

def create_phase_estimation_circuit(n_counting_qubits, phase_angle):
    """
    Create quantum phase estimation circuit
    """
    n = n_counting_qubits
    qc = QuantumCircuit(n + 1, n)
    
    # Initialize counting qubits
    for i in range(n):
        qc.h(i)
    
    # Apply controlled-U operations
    # For this example, U = |1⟩⟨1| + e^(iφ)|0⟩⟨0|
    for i in range(n):
        angle = phase_angle * (2 ** (n - i - 1))
        qc.cp(angle, i, n)
    
    # Apply inverse QFT
    qc.append(QFT(n).inverse(), range(n))
    
    # Measure counting qubits
    qc.measure(range(n), range(n))
    
    return qc

# Create phase estimation circuit
n_counting = 3
phase = np.pi / 4  # Target phase to estimate
qc = create_phase_estimation_circuit(n_counting, phase)

print("Quantum Phase Estimation:")
print(f"Target phase: {phase / np.pi}π")
print("Circuit:")
print(qc)`,
    tags: ['phase-estimation', 'qft', 'eigenvalue', 'shor']
  }
]

const categories = ['Basic Circuits', 'Quantum Algorithms', 'Variational Algorithms', 'Error Correction', 'Quantum Machine Learning']
const frameworks = ['qiskit', 'cirq', 'pennylane']
const difficulties = ['beginner', 'intermediate', 'advanced']

export default function ExamplesPage() {
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedFramework, setSelectedFramework] = useState<string>('all')
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const { theme, toggleTheme, addFile } = useFileStore()
  const router = useRouter()
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [scrollY, setScrollY] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const openInEditor = (example: Example) => {
    const filename = `${example.title.replace(/\s+/g, '_')}.py`

    // Try to send message to existing app tab
    const channel = new BroadcastChannel('qcanvas-examples')
    channel.postMessage({
      type: 'add-example-file',
      filename,
      code: example.code
    })

    // Fallback: navigate to app if no response after timeout
    const timeout = setTimeout(() => {
      channel.close()
      // If app tab is not open, navigate to it
      router.push('/app')
    }, 500)

    // Listen for confirmation (optional, for now just close after sending)
    channel.onmessage = (event) => {
      if (event.data.type === 'file-added') {
        clearTimeout(timeout)
        channel.close()
        toast.success(`Example loaded in editor: ${filename}`)
      }
    }
  }

  const filteredExamples = examples.filter(example => {
    const matchesCategory = selectedCategory === 'all' || example.category === selectedCategory
    const matchesFramework = selectedFramework === 'all' || example.framework === selectedFramework
    const matchesDifficulty = selectedDifficulty === 'all' || example.difficulty === selectedDifficulty
    const matchesSearch = example.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         example.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         example.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))

    return matchesCategory && matchesFramework && matchesDifficulty && matchesSearch
  })

  const copyToClipboard = (code: string) => {
    navigator.clipboard.writeText(code)
    toast.success('Code copied to clipboard!')
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-500'
      case 'intermediate': return 'bg-yellow-500'
      case 'advanced': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getFrameworkColor = (framework: string) => {
    switch (framework) {
      case 'qiskit': return 'bg-blue-500'
      case 'cirq': return 'bg-purple-500'
      case 'pennylane': return 'bg-green-500'
      default: return 'bg-gray-500'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-editor-bg via-gray-900 to-editor-bg relative overflow-x-hidden">
      {/* Navigation */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrollY > 50 ? 'bg-black/80 backdrop-blur-lg border-b border-white/10' : 'bg-transparent'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <Link href="/" className="flex items-center space-x-2 group">
              <div className="relative">
                <Image
                  src="/QCanvas-logo-Black.svg"
                  alt="QCanvas Logo"
                  width={48}
                  height={48}
                  className="object-contain block dark:hidden transition-all duration-300 hover:scale-110 animate-pulse"
                  priority
                />
                <Image
                  src="/QCanvas-logo-White.svg"
                  alt="QCanvas Logo"
                  width={48}
                  height={48}
                  className="object-contain hidden dark:block transition-all duration-300 hover:scale-110 animate-pulse"
                  priority
                />
              </div>
              <span className="text-2xl font-bold quantum-gradient bg-clip-text text-transparent transition-all duration-200">
                QCanvas
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <Link href="/" className="text-editor-text hover:text-white transition-colors duration-200">
                Home
              </Link>
              <Link href="/examples" className="text-white font-medium underline decoration-quantum-blue-light decoration-2 underline-offset-4">
                Examples
              </Link>
              <Link href="/docs" className="text-editor-text hover:text-white transition-colors duration-200">
                Documentation
              </Link>
              <Link href="/about" className="text-editor-text hover:text-white transition-colors duration-200">
                About
              </Link>

              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg bg-editor-bg/50 border border-editor-border hover:border-quantum-blue-light transition-colors duration-200"
                title="Toggle theme"
              >
                {theme === 'dark' ? <Sun className="w-5 h-5 text-editor-text" /> : <Moon className="w-5 h-5 text-editor-text" />}
              </button>

              {/* Auth Buttons */}
              <div className="flex items-center space-x-3">
                <Link
                  href="/login"
                  className="text-editor-text hover:text-white transition-colors duration-200 font-medium"
                >
                  Sign In
                </Link>
                <Link
                  href="/login"
                  className="btn-quantum text-sm px-4 py-2"
                >
                  Get Started
                </Link>
              </div>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 rounded-lg bg-editor-bg/50 border border-editor-border"
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>

          {/* Mobile Menu */}
          {isMenuOpen && (
            <div className="md:hidden bg-black/95 backdrop-blur-lg border-t border-white/10">
              <div className="px-4 py-4 space-y-4">
                <Link href="/" className="block text-editor-text hover:text-white transition-colors duration-200">
                  Home
                </Link>
                <Link href="/examples" className="block text-white font-medium transition-colors duration-200">
                  Examples
                </Link>
                <Link href="/docs" className="block text-editor-text hover:text-white transition-colors duration-200">
                  Documentation
                </Link>
                <Link href="/about" className="block text-editor-text hover:text-white transition-colors duration-200">
                  About
                </Link>

                <div className="flex items-center justify-between pt-4 border-t border-white/10">
                  <button
                    onClick={toggleTheme}
                    className="flex items-center space-x-2 text-editor-text hover:text-white transition-colors duration-200"
                  >
                    {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                    <span>Theme</span>
                  </button>
                  <div className="flex space-x-3">
                    <Link href="/login" className="text-editor-text hover:text-white transition-colors duration-200">
                      Sign In
                    </Link>
                    <Link href="/login" className="btn-quantum text-sm px-3 py-1">
                      Get Started
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-4 pt-20">
        {/* Animated Background */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-quantum-blue-light opacity-10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-500 opacity-10 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-teal-500 opacity-5 rounded-full blur-3xl animate-pulse delay-500"></div>
        </div>

        <div className="text-center max-w-6xl mx-auto relative z-10">
          <div className="inline-flex items-center justify-center w-24 h-24 rounded-full quantum-gradient mb-6 shadow-2xl">
            <Code className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            Quantum <span className="quantum-gradient bg-clip-text text-transparent">Examples</span>
          </h1>
          <p className="text-xl md:text-2xl text-editor-text mb-8 max-w-3xl mx-auto leading-relaxed">
            Explore quantum computing examples across different frameworks. Copy, modify, and run these circuits in QCanvas.
          </p>
        </div>
      </section>

      {/* Filters */}
      <main className="px-4 py-8 flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto">
          <div className="quantum-glass-dark rounded-2xl p-6 backdrop-blur-xl border border-white/10">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Search */}
              <div>
                <label htmlFor="search-input" className="block text-sm font-medium text-editor-text mb-2">Search</label>
                <input
                  id="search-input"
                  type="text"
                  placeholder="Search examples..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 bg-editor-bg border border-editor-border rounded-lg focus-quantum text-white placeholder-gray-400"
                />
              </div>

              {/* Category Filter */}
              <div>
                <label htmlFor="category-select" className="block text-sm font-medium text-editor-text mb-2">Category</label>
                <select
                  id="category-select"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2 bg-editor-bg border border-editor-border rounded-lg focus-quantum text-white"
                >
                  <option value="all">All Categories</option>
                  {categories.map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>

              {/* Framework Filter */}
              <div>
                <label htmlFor="framework-select" className="block text-sm font-medium text-editor-text mb-2">Framework</label>
                <select
                  id="framework-select"
                  value={selectedFramework}
                  onChange={(e) => setSelectedFramework(e.target.value)}
                  className="w-full px-3 py-2 bg-editor-bg border border-editor-border rounded-lg focus-quantum text-white"
                >
                  <option value="all">All Frameworks</option>
                  {frameworks.map(framework => (
                    <option key={framework} value={framework}>{framework.charAt(0).toUpperCase() + framework.slice(1)}</option>
                  ))}
                </select>
              </div>

              {/* Difficulty Filter */}
              <div>
                <label htmlFor="difficulty-select" className="block text-sm font-medium text-editor-text mb-2">Difficulty</label>
                <select
                  id="difficulty-select"
                  value={selectedDifficulty}
                  onChange={(e) => setSelectedDifficulty(e.target.value)}
                  className="w-full px-3 py-2 bg-editor-bg border border-editor-border rounded-lg focus-quantum text-white"
                >
                  <option value="all">All Levels</option>
                  {difficulties.map(difficulty => (
                    <option key={difficulty} value={difficulty}>{difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>
      {/* Examples Grid (inside main) */}
      <div className="px-4 py-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {filteredExamples.map(example => (
              <div key={example.id} className="quantum-glass-dark rounded-2xl backdrop-blur-xl border border-white/10 hover:border-quantum-blue-light transition-all duration-300 overflow-hidden">
                <div className="p-6">
                  {/* Header */}
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold text-white mb-2">{example.title}</h3>
                      <p className="text-editor-text text-sm mb-3">{example.description}</p>
                    </div>
                  </div>

                  {/* Tags */}
                  <div className="flex flex-wrap gap-2 mb-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium text-white ${getFrameworkColor(example.framework)}`}>
                      {example.framework}
                    </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium text-white ${getDifficultyColor(example.difficulty)}`}>
                      {example.difficulty}
                    </span>
                    {example.tags.slice(0, 2).map(tag => (
                      <span key={tag} className="px-2 py-1 rounded-full text-xs font-medium text-gray-300 bg-gray-700">
                        {tag}
                      </span>
                    ))}
                  </div>

                  {/* Actions */}
                  <div className="flex space-x-2">
                    <button
                      onClick={() => copyToClipboard(example.code)}
                      className="flex-1 btn-quantum flex items-center justify-center py-2 text-sm"
                    >
                      <Copy className="w-4 h-4 mr-2" />
                      Copy Code
                    </button>
                    <button
                      onClick={() => openInEditor(example)}
                      className="flex-1 btn-ghost flex items-center justify-center py-2 text-sm"
                    >
                      <Play className="w-4 h-4 mr-2" />
                      Try in QCanvas
                    </button>
                  </div>
                </div>

                {/* Code Preview */}
                <div className="bg-editor-bg p-4 border-t border-editor-border">
                  <pre className="text-xs text-editor-text overflow-x-auto max-w-full">
                    <code className="whitespace-pre-wrap break-words">{example.code.split('\n').slice(0, 8).join('\n')}...</code>
                  </pre>
                </div>
              </div>
            ))}
          </div>

          {filteredExamples.length === 0 && (
            <div className="text-center py-16">
              <Code className="w-16 h-16 text-editor-text mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No examples found</h3>
              <p className="text-editor-text">Try adjusting your filters or search terms.</p>
            </div>
          )}
        </div>
      </div>
      </main>

      {/* Footer */}
      <footer className="px-4 py-8 border-t border-editor-border">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-editor-text">
            Ready to explore quantum computing? Copy any example and try it in QCanvas!
          </p>
          <div className="flex justify-center space-x-6 mt-4">
            <Link href="/about" className="text-editor-text hover:text-white transition-colors">
              About QCanvas
            </Link>
            <Link href="/docs" className="text-editor-text hover:text-white transition-colors">
              Documentation
            </Link>
            <a href="https://github.com" className="text-editor-text hover:text-white transition-colors">
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
