import React from "react";
import { cn } from "@/lib/utils";
import { Framework } from "./CodeEditor";

export interface QuantumExample {
  id: string;
  title: string;
  icon: string;
  description: string;
  codes: {
    qiskit: string;
    cirq: string;
    braket: string;
  };
}

interface ExamplesPanelProps {
  onSelectExample: (example: QuantumExample, framework: Framework) => void;
  currentFramework: Framework;
  className?: string;
}

const QUANTUM_EXAMPLES: QuantumExample[] = [
  {
    id: "bell-state",
    title: "Bell State Creation",
    icon: "🔗",
    description: "Create and measure quantum entanglement between two qubits",
    codes: {
      qiskit: `# Bell State Creation (Qiskit)
from qiskit import QuantumCircuit, execute, Aer

# Create a quantum circuit with 2 qubits
qc = QuantumCircuit(2, 2)

# Create Bell state |00⟩ + |11⟩
qc.h(0)      # Hadamard on qubit 0
qc.cx(0, 1)  # CNOT gate

# Measure both qubits
qc.measure_all()

# Execute
backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend, shots=1024)
result = job.result()
counts = result.get_counts(qc)

print("Bell state measurement results:")
print(counts)`,
      cirq: `# Bell State Creation (Cirq)
import cirq

# Create qubits
q0, q1 = cirq.LineQubit.range(2)

# Create circuit
circuit = cirq.Circuit()

# Add gates to create Bell state
circuit.append(cirq.H(q0))
circuit.append(cirq.CNOT(q0, q1))

# Add measurements
circuit.append(cirq.measure(q0, q1, key='result'))

print("Circuit:")
print(circuit)

# Simulate
simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=1024)
print("\\nBell state measurement results:")
print(result.histogram(key='result'))`,
      braket: `# Bell State Creation (AWS Braket)
from braket.circuits import Circuit
from braket.devices import LocalSimulator

# Create circuit
circuit = Circuit()

# Create Bell state
circuit.h(0)
circuit.cnot(0, 1)

# Add measurements
circuit.measure([0, 1])

print("Circuit:")
print(circuit)

# Execute on local simulator
device = LocalSimulator()
task = device.run(circuit, shots=1024)
result = task.result()

print("\\nBell state measurement results:")
print(result.measurement_counts)`,
    },
  },
  {
    id: "grover",
    title: "Grover's Algorithm",
    icon: "🔍",
    description:
      "Quantum search algorithm for finding items in unsorted databases",
    codes: {
      qiskit: `# Grover's Algorithm (2-qubit example)
from qiskit import QuantumCircuit, execute, Aer
import numpy as np

# Create circuit for 2-qubit Grover search
qc = QuantumCircuit(2, 2)

# Initialize in superposition
qc.h([0, 1])

# Oracle (marking |11⟩)
qc.cz(0, 1)

# Diffusion operator
qc.h([0, 1])
qc.z([0, 1])
qc.cz(0, 1)
qc.h([0, 1])

# Measure
qc.measure_all()

# Execute
backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend, shots=1024)
result = job.result()
counts = result.get_counts(qc)

print("Grover's algorithm results:")
print(counts)`,
      cirq: `# Grover's Algorithm (Cirq)
import cirq
import numpy as np

# Create qubits
qubits = cirq.LineQubit.range(2)

# Create circuit
circuit = cirq.Circuit()

# Initialize in superposition
circuit.append(cirq.H.on_each(*qubits))

# Oracle (marking |11⟩)
circuit.append(cirq.CZ(qubits[0], qubits[1]))

# Diffusion operator
circuit.append(cirq.H.on_each(*qubits))
circuit.append(cirq.Z.on_each(*qubits))
circuit.append(cirq.CZ(qubits[0], qubits[1]))
circuit.append(cirq.H.on_each(*qubits))

# Measure
circuit.append(cirq.measure(*qubits, key='result'))

print("Circuit:")
print(circuit)

# Simulate
simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=1024)
print("\\nGrover's algorithm results:")
print(result.histogram(key='result'))`,
      braket: `# Grover's Algorithm (AWS Braket)
from braket.circuits import Circuit
from braket.devices import LocalSimulator

# Create circuit
circuit = Circuit()

# Initialize in superposition
circuit.h(0).h(1)

# Oracle (marking |11⟩)
circuit.cz(0, 1)

# Diffusion operator
circuit.h(0).h(1)
circuit.z(0).z(1)
circuit.cz(0, 1)
circuit.h(0).h(1)

# Measure
circuit.measure([0, 1])

print("Circuit:")
print(circuit)

# Execute on local simulator
device = LocalSimulator()
task = device.run(circuit, shots=1024)
result = task.result()

print("\\nGrover's algorithm results:")
print(result.measurement_counts)`,
    },
  },
  {
    id: "qft",
    title: "Quantum Fourier Transform",
    icon: "🌊",
    description: "Fundamental quantum algorithm for frequency analysis",
    codes: {
      qiskit: `# Quantum Fourier Transform (Qiskit)
from qiskit import QuantumCircuit, execute, Aer
import numpy as np

def qft_rotations(circuit, n):
    """Performs qft on the first n qubits in circuit"""
    if n == 0:
        return circuit
    n -= 1
    circuit.h(n)
    for qubit in range(n):
        circuit.cp(np.pi/2**(n-qubit), qubit, n)
    qft_rotations(circuit, n)

def swap_registers(circuit, n):
    for qubit in range(n//2):
        circuit.swap(qubit, n-qubit-1)
    return circuit

def qft(circuit, n):
    """QFT on the first n qubits in circuit"""
    qft_rotations(circuit, n)
    swap_registers(circuit, n)
    return circuit

# Create circuit
qc = QuantumCircuit(3, 3)

# Apply QFT
qft(qc, 3)

# Measure
qc.measure_all()

print("Quantum Fourier Transform circuit created")
print("Circuit depth:", qc.depth())`,
      cirq: `# Quantum Fourier Transform (Cirq)
import cirq
import numpy as np

def qft_circuit(qubits):
    """Creates a QFT circuit for the given qubits"""
    circuit = cirq.Circuit()
    
    for i, qubit in enumerate(qubits):
        circuit.append(cirq.H(qubit))
        for j, other_qubit in enumerate(qubits[i+1:], i+1):
            circuit.append(cirq.CZ(qubit, other_qubit) ** (1 / 2**(j-i)))
    
    # Reverse the order
    for i in range(len(qubits) // 2):
        circuit.append(cirq.SWAP(qubits[i], qubits[len(qubits)-1-i]))
    
    return circuit

# Create qubits
qubits = cirq.LineQubit.range(3)

# Create QFT circuit
circuit = qft_circuit(qubits)

# Add measurements
circuit.append(cirq.measure(*qubits, key='result'))

print("Quantum Fourier Transform circuit:")
print(circuit)`,
      braket: `# Quantum Fourier Transform (AWS Braket)
from braket.circuits import Circuit
from braket.devices import LocalSimulator
import numpy as np

def qft_circuit(n_qubits):
    """Creates a QFT circuit for n qubits"""
    circuit = Circuit()
    
    for i in range(n_qubits):
        circuit.h(i)
        for j in range(i + 1, n_qubits):
            circuit.cphaseshift(i, j, np.pi / (2 ** (j - i)))
    
    # Reverse the order
    for i in range(n_qubits // 2):
        circuit.swap(i, n_qubits - 1 - i)
    
    return circuit

# Create QFT circuit
circuit = qft_circuit(3)

# Add measurements
circuit.measure(range(3))

print("Quantum Fourier Transform circuit:")
print(circuit)

# Execute on local simulator
device = LocalSimulator()
task = device.run(circuit, shots=100)
result = task.result()

print("\\nQFT results:")
print(result.measurement_counts)`,
    },
  },
  {
    id: "teleportation",
    title: "Quantum Teleportation",
    icon: "📡",
    description:
      "Transfer quantum information using entanglement and classical communication",
    codes: {
      qiskit: `# Quantum Teleportation (Qiskit)
from qiskit import QuantumCircuit, execute, Aer

# Create circuit with 3 qubits and 3 classical bits
qc = QuantumCircuit(3, 3)

# Prepare the state to teleport (qubit 0)
qc.h(0)  # Create superposition state

# Create Bell pair between qubits 1 and 2
qc.h(1)
qc.cx(1, 2)

# Bell measurement on qubits 0 and 1
qc.cx(0, 1)
qc.h(0)
qc.measure([0, 1], [0, 1])

# Apply corrections based on measurement
qc.cx(1, 2)  # Conditional X gate
qc.cz(0, 2)  # Conditional Z gate

# Measure the teleported state
qc.measure(2, 2)

print("Quantum teleportation circuit created")
print("The state of qubit 0 is teleported to qubit 2")

# Execute
backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend, shots=1024)
result = job.result()
counts = result.get_counts(qc)

print("\\nTeleportation results:")
print(counts)`,
      cirq: `# Quantum Teleportation (Cirq)
import cirq

# Create qubits
alice_qubit = cirq.NamedQubit("alice")
bob_qubit = cirq.NamedQubit("bob")
msg_qubit = cirq.NamedQubit("message")

# Create circuit
circuit = cirq.Circuit()

# Prepare message state (arbitrary state)
circuit.append(cirq.H(msg_qubit))

# Create Bell pair
circuit.append(cirq.H(alice_qubit))
circuit.append(cirq.CNOT(alice_qubit, bob_qubit))

# Bell measurement
circuit.append(cirq.CNOT(msg_qubit, alice_qubit))
circuit.append(cirq.H(msg_qubit))

# Measure Alice's qubits
circuit.append(cirq.measure(msg_qubit, alice_qubit, key='alice_measurement'))

# Apply corrections to Bob's qubit based on measurement
# This would normally be done with classical control
# For simulation, we apply all possible corrections

print("Quantum teleportation circuit:")
print(circuit)

# Simulate
simulator = cirq.Simulator()
result = simulator.run(circuit, repetitions=1024)
print("\\nTeleportation measurements:")
print(result.histogram(key='alice_measurement'))`,
      braket: `# Quantum Teleportation (AWS Braket)
from braket.circuits import Circuit
from braket.devices import LocalSimulator

# Create circuit
circuit = Circuit()

# Prepare message state (qubit 0)
circuit.h(0)

# Create Bell pair (qubits 1 and 2)
circuit.h(1)
circuit.cnot(1, 2)

# Bell measurement on qubits 0 and 1
circuit.cnot(0, 1)
circuit.h(0)

# In a real implementation, we would use the measurement
# results to conditionally apply gates to qubit 2
# For this example, we'll show the circuit structure

print("Quantum teleportation circuit structure:")
print(circuit)

# Add measurements
circuit.measure([0, 1, 2])

# Execute on local simulator
device = LocalSimulator()
task = device.run(circuit, shots=1024)
result = task.result()

print("\\nTeleportation circuit results:")
print(result.measurement_counts)`,
    },
  },
  {
    id: "deutsch",
    title: "Deutsch-Jozsa Algorithm",
    icon: "⚡",
    description:
      "Determine if a function is constant or balanced with quantum advantage",
    codes: {
      qiskit: `# Deutsch-Jozsa Algorithm (Qiskit)
from qiskit import QuantumCircuit, execute, Aer

def deutsch_jozsa_constant():
    """Deutsch-Jozsa for a constant function"""
    # 3 qubits: 2 for input, 1 ancilla
    qc = QuantumCircuit(3, 2)
    
    # Initialize ancilla in |->
    qc.x(2)
    qc.h(2)
    
    # Initialize input qubits in superposition
    qc.h([0, 1])
    
    # Oracle for constant function (identity - does nothing)
    # For f(x) = 0 (constant), no gates needed
    
    # Apply Hadamard to input qubits
    qc.h([0, 1])
    
    # Measure input qubits
    qc.measure([0, 1], [0, 1])
    
    return qc

def deutsch_jozsa_balanced():
    """Deutsch-Jozsa for a balanced function"""
    # 3 qubits: 2 for input, 1 ancilla
    qc = QuantumCircuit(3, 2)
    
    # Initialize ancilla in |->
    qc.x(2)
    qc.h(2)
    
    # Initialize input qubits in superposition
    qc.h([0, 1])
    
    # Oracle for balanced function f(x) = x0 XOR x1
    qc.cx(0, 2)
    qc.cx(1, 2)
    
    # Apply Hadamard to input qubits
    qc.h([0, 1])
    
    # Measure input qubits
    qc.measure([0, 1], [0, 1])
    
    return qc

# Test constant function
qc_constant = deutsch_jozsa_constant()
print("Testing constant function...")

backend = Aer.get_backend('qasm_simulator')
job = execute(qc_constant, backend, shots=1024)
result = job.result()
counts = result.get_counts(qc_constant)

print("Constant function results:", counts)
print("All measurements should be 00 for constant function")`,
      cirq: `# Deutsch-Jozsa Algorithm (Cirq)
import cirq

def deutsch_jozsa_circuit(oracle_type='constant'):
    """Creates Deutsch-Jozsa circuit"""
    # Create qubits
    input_qubits = cirq.LineQubit.range(2)
    ancilla = cirq.LineQubit(2)
    
    circuit = cirq.Circuit()
    
    # Initialize ancilla in |->
    circuit.append(cirq.X(ancilla))
    circuit.append(cirq.H(ancilla))
    
    # Initialize input qubits in superposition
    circuit.append(cirq.H.on_each(*input_qubits))
    
    # Oracle
    if oracle_type == 'balanced':
        # Balanced function: f(x) = x0 XOR x1
        circuit.append(cirq.CNOT(input_qubits[0], ancilla))
        circuit.append(cirq.CNOT(input_qubits[1], ancilla))
    # For constant function, oracle does nothing
    
    # Apply Hadamard to input qubits
    circuit.append(cirq.H.on_each(*input_qubits))
    
    # Measure input qubits
    circuit.append(cirq.measure(*input_qubits, key='result'))
    
    return circuit

# Test both types
constant_circuit = deutsch_jozsa_circuit('constant')
balanced_circuit = deutsch_jozsa_circuit('balanced')

print("Deutsch-Jozsa for constant function:")
print(constant_circuit)

print("\\nDeutsch-Jozsa for balanced function:")
print(balanced_circuit)

# Simulate
simulator = cirq.Simulator()

print("\\nConstant function results:")
result_constant = simulator.run(constant_circuit, repetitions=100)
print(result_constant.histogram(key='result'))

print("\\nBalanced function results:")
result_balanced = simulator.run(balanced_circuit, repetitions=100)
print(result_balanced.histogram(key='result'))`,
      braket: `# Deutsch-Jozsa Algorithm (AWS Braket)
from braket.circuits import Circuit
from braket.devices import LocalSimulator

def deutsch_jozsa_circuit(oracle_type='constant'):
    """Creates Deutsch-Jozsa circuit"""
    circuit = Circuit()
    
    # Initialize ancilla qubit (qubit 2) in |->
    circuit.x(2)
    circuit.h(2)
    
    # Initialize input qubits in superposition
    circuit.h(0)
    circuit.h(1)
    
    # Oracle
    if oracle_type == 'balanced':
        # Balanced function: f(x) = x0 XOR x1
        circuit.cnot(0, 2)
        circuit.cnot(1, 2)
    # For constant function, oracle does nothing
    
    # Apply Hadamard to input qubits
    circuit.h(0)
    circuit.h(1)
    
    # Measure input qubits only
    circuit.measure([0, 1])
    
    return circuit

# Create circuits
constant_circuit = deutsch_jozsa_circuit('constant')
balanced_circuit = deutsch_jozsa_circuit('balanced')

print("Deutsch-Jozsa Algorithm")
print("Constant function circuit:")
print(constant_circuit)

print("\\nBalanced function circuit:")
print(balanced_circuit)

# Execute on local simulator
device = LocalSimulator()

print("\\nTesting constant function:")
task_constant = device.run(constant_circuit, shots=100)
result_constant = task_constant.result()
print("Results:", result_constant.measurement_counts)
print("Should measure 00 for constant function")

print("\\nTesting balanced function:")
task_balanced = device.run(balanced_circuit, shots=100)
result_balanced = task_balanced.result()
print("Results:", result_balanced.measurement_counts)
print("Should NOT measure 00 for balanced function")`,
    },
  },
];

export function ExamplesPanel({
  onSelectExample,
  currentFramework,
  className,
}: ExamplesPanelProps) {
  const handleExampleClick = (example: QuantumExample) => {
    onSelectExample(example, currentFramework);
  };

  return (
    <div
      className={cn(
        "quantum-glass rounded-2xl overflow-hidden shadow-[0_10px_30px_rgba(0,0,0,0.1)]",
        className,
      )}
    >
      <div className="quantum-pink-gradient text-white p-4 md:px-6 font-semibold">
        📚 Quick Examples
      </div>
      <div className="p-6">
        <ul className="space-y-3 list-none">
          {QUANTUM_EXAMPLES.map((example) => (
            <li
              key={example.id}
              onClick={() => handleExampleClick(example)}
              className="quantum-example-item p-3 bg-gray-50 rounded-lg cursor-pointer font-medium"
              title={example.description}
            >
              <span className="mr-2">{example.icon}</span>
              {example.title}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
