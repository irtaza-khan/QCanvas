'use client'

import { useState } from 'react'
import { ArrowLeft, Copy, Play, Code, Zap, BookOpen, Cpu, BarChart3, Moon, Sun } from 'lucide-react'
import Link from 'next/link'
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
  const { theme, toggleTheme } = useFileStore()

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
    <div className="min-h-screen bg-gradient-to-br from-editor-bg via-gray-900 to-editor-bg flex flex-col overflow-x-hidden">
      {/* Header */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-quantum-blue-light opacity-10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500 opacity-10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>
        
        <div className="relative z-10 px-4 py-8">
          <Link 
            href="/login" 
            className="inline-flex items-center text-editor-text hover:text-white transition-colors mb-8"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Login
          </Link>
          
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-24 h-24 rounded-full quantum-gradient mb-6 shadow-2xl">
              <Code className="w-12 h-12 text-white" />
            </div>
            <h1 className="text-5xl font-bold text-white mb-4">
              Quantum <span className="quantum-gradient bg-clip-text text-transparent">Examples</span>
            </h1>
            <div className="flex justify-center mb-4">
              <button onClick={toggleTheme} className="btn-ghost p-2 hover:bg-quantum-blue-light/20 rounded-lg" title="Toggle theme">
                {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>
            </div>
            <p className="text-xl text-editor-text max-w-3xl mx-auto">
              Explore quantum computing examples across different frameworks. Copy, modify, and run these circuits in QCanvas.
            </p>
          </div>
        </div>
      </div>

      {/* Filters */}
      <main className="px-4 py-8 flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto">
          <div className="quantum-glass-dark rounded-2xl p-6 backdrop-blur-xl border border-white/10">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Search */}
              <div>
                <label className="block text-sm font-medium text-editor-text mb-2">Search</label>
                <input
                  type="text"
                  placeholder="Search examples..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full px-3 py-2 bg-editor-bg border border-editor-border rounded-lg focus-quantum text-white placeholder-gray-400"
                />
              </div>

              {/* Category Filter */}
              <div>
                <label className="block text-sm font-medium text-editor-text mb-2">Category</label>
                <select
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
                <label className="block text-sm font-medium text-editor-text mb-2">Framework</label>
                <select
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
                <label className="block text-sm font-medium text-editor-text mb-2">Difficulty</label>
                <select
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
                      onClick={() => {
                        copyToClipboard(example.code)
                        // In a real app, this would open the editor with the code
                        toast.success('Code copied! Open QCanvas to use it.')
                      }}
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
