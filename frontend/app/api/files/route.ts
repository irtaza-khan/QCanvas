import { NextRequest, NextResponse } from 'next/server'
import { File, CreateFileRequest } from '@/types'
import { generateId, getLanguageFromFilename } from '@/lib/utils'

// Mock files database
const mockFiles: File[] = [
  {
    id: 'file-1',
    name: 'main.qasm',
    content: `// Bell State Creation
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] c;

h q[0];
cx q[0], q[1];
c = measure q;`,
    language: 'qasm',
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-15T10:00:00Z',
    size: 150,
  },
  {
    id: 'file-2',
    name: 'demo_qiskit.py',
    content: `# Grover's Algorithm Implementation
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, execute, Aer
import numpy as np

def grovers_algorithm(target_state):
    n = 2
    qc = QuantumCircuit(n, n)
    
    # Initialize superposition
    qc.h(range(n))
    
    # Oracle for target state
    if target_state == '11':
        qc.cz(0, 1)
    elif target_state == '10':
        qc.x(1)
        qc.cz(0, 1)
        qc.x(1)
    elif target_state == '01':
        qc.x(0)
        qc.cz(0, 1)
        qc.x(0)
    
    # Diffusion operator
    qc.h(range(n))
    qc.x(range(n))
    qc.cz(0, 1)
    qc.x(range(n))
    qc.h(range(n))
    
    qc.measure_all()
    return qc

circuit = grovers_algorithm('11')
backend = Aer.get_backend('qasm_simulator')
job = execute(circuit, backend, shots=1024)
result = job.result()
counts = result.get_counts(circuit)
print("Results:", counts)`,
    language: 'python',
    createdAt: '2024-01-15T11:00:00Z',
    updatedAt: '2024-01-15T11:30:00Z',
    size: 1250,
  },
  {
    id: 'file-3',
    name: 'sample_pennylane.py',
    content: `# Quantum Teleportation with PennyLane
import pennylane as qml
import numpy as np

dev = qml.device('default.qubit', wires=3)

@qml.qnode(dev)
def quantum_teleportation(state_prep_angle):
    # Prepare state to teleport
    qml.RY(state_prep_angle, wires=0)
    
    # Create Bell pair
    qml.Hadamard(wires=1)
    qml.CNOT(wires=[1, 2])
    
    # Bell measurement
    qml.CNOT(wires=[0, 1])
    qml.Hadamard(wires=0)
    
    return qml.state()

angle = np.pi / 4
final_state = quantum_teleportation(angle)
print("Teleportation completed:", final_state)`,
    language: 'python',
    createdAt: '2024-01-15T12:00:00Z',
    updatedAt: '2024-01-15T12:15:00Z',
    size: 980,
  },
]

// GET /api/files - Get all files
export async function GET() {
  try {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100))
    
    return NextResponse.json({
      files: mockFiles,
      count: mockFiles.length,
      branding: 'QCanvas'
    })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch files' },
      { status: 500 }
    )
  }
}

// POST /api/files - Create new file
export async function POST(request: NextRequest) {
  try {
    const body: CreateFileRequest = await request.json()
    
    // Validate request
    if (!body.name || body.name.trim() === '') {
      return NextResponse.json(
        { error: 'File name is required' },
        { status: 400 }
      )
    }
    
    // Check if file with same name exists
    const existingFile = mockFiles.find(f => f.name === body.name)
    if (existingFile) {
      return NextResponse.json(
        { error: 'File with this name already exists' },
        { status: 409 }
      )
    }
    
    // Create new file
    const newFile: File = {
      id: generateId(),
      name: body.name,
      content: body.content || '',
      language: body.language || getLanguageFromFilename(body.name),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      size: (body.content || '').length,
    }
    
    // Add to mock database
    mockFiles.push(newFile)
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 200))
    
    return NextResponse.json(newFile, { status: 201 })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to create file' },
      { status: 500 }
    )
  }
}
