import { NextRequest, NextResponse } from 'next/server'
import { File, UpdateFileRequest } from '@/types'
import { getLanguageFromFilename } from '@/lib/utils'

// Mock files database (same as in route.ts)
const mockFiles: File[] = [
  {
    id: 'file-1',
    name: 'main.qasm',
    content: `// Bell State Creation
OPENQASM 3;
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

// GET /api/files/[id] - Get specific file
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const fileId = params.id
    
    // Find file in mock database
    const file = mockFiles.find(f => f.id === fileId)
    
    if (!file) {
      return NextResponse.json(
        { error: 'File not found' },
        { status: 404 }
      )
    }
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 50))
    
    return NextResponse.json({ ...file, branding: 'QCanvas' })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch file' },
      { status: 500 }
    )
  }
}

// PUT /api/files/[id] - Update file
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const fileId = params.id
    const body: UpdateFileRequest = await request.json()
    
    // Find file in mock database
    const fileIndex = mockFiles.findIndex(f => f.id === fileId)
    
    if (fileIndex === -1) {
      return NextResponse.json(
        { error: 'File not found' },
        { status: 404 }
      )
    }
    
    // Update file
    const existingFile = mockFiles[fileIndex]
    const updatedFile: File = {
      ...existingFile,
      ...(body.name && { name: body.name }),
      ...(body.content !== undefined && { content: body.content }),
      ...(body.name && { language: getLanguageFromFilename(body.name) }),
      updatedAt: new Date().toISOString(),
      size: (body.content !== undefined ? body.content : existingFile.content).length,
    }
    
    // If name is being changed, check for conflicts
    if (body.name && body.name !== existingFile.name) {
      const nameExists = mockFiles.some(f => f.id !== fileId && f.name === body.name)
      if (nameExists) {
        return NextResponse.json(
          { error: 'File with this name already exists' },
          { status: 409 }
        )
      }
    }
    
    // Update in mock database
    mockFiles[fileIndex] = updatedFile
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100))
    
    return NextResponse.json(updatedFile)
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to update file' },
      { status: 500 }
    )
  }
}

// DELETE /api/files/[id] - Delete file
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const fileId = params.id
    
    // Find file in mock database
    const fileIndex = mockFiles.findIndex(f => f.id === fileId)
    
    if (fileIndex === -1) {
      return NextResponse.json(
        { error: 'File not found' },
        { status: 404 }
      )
    }
    
    // Remove from mock database
    mockFiles.splice(fileIndex, 1)
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100))
    
    return NextResponse.json({ success: true })
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to delete file' },
      { status: 500 }
    )
  }
}
