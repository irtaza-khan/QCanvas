import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { File, EditorState, SupportedLanguage, FILE_TEMPLATES, CompileOptions } from '@/types'
import { generateId, getLanguageFromFilename } from './utils'

interface FileStore extends EditorState {
  // Actions
  setActiveFile: (fileId: string | null) => void
  updateFileContent: (fileId: string, content: string) => void
  addFile: (name: string, content?: string) => File
  deleteFile: (fileId: string) => void
  renameFile: (fileId: string, newName: string) => void
  setTheme: (theme: 'light' | 'dark') => void
  toggleTheme: () => void
  toggleSidebar: () => void
  toggleResults: () => void
  setFiles: (files: File[]) => void
  getActiveFile: () => File | undefined
  setCompileOptions: (options: Partial<CompileOptions>) => void
  setCompiledQasm: (qasm: string | null) => void
  compileActiveToQasm: () => string | null
}

// Mock initial files
const initialFiles: File[] = [
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
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    size: 150,
  },
  {
    id: 'file-2',
    name: 'demo_qiskit.py',
    content: `# Grover's Algorithm Implementation
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, execute, Aer
import numpy as np

# Create quantum circuit for Grover's algorithm
def grovers_algorithm(target_state):
    # Number of qubits
    n = 2
    
    # Create quantum circuit
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
    # '00' requires no oracle
    
    # Diffusion operator
    qc.h(range(n))
    qc.x(range(n))
    qc.cz(0, 1)
    qc.x(range(n))
    qc.h(range(n))
    
    # Measure
    qc.measure_all()
    
    return qc

# Execute circuit
circuit = grovers_algorithm('11')
backend = Aer.get_backend('qasm_simulator')
job = execute(circuit, backend, shots=1024)
result = job.result()
counts = result.get_counts(circuit)
print("Grover's Algorithm Results:", counts)`,
    language: 'python',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    size: 1250,
  },
  {
    id: 'file-3',
    name: 'sample_pennylane.py',
    content: `# Quantum Teleportation with PennyLane
import pennylane as qml
import numpy as np

# Create device
dev = qml.device('default.qubit', wires=3)

@qml.qnode(dev)
def quantum_teleportation(state_prep_angle):
    # Prepare the state to be teleported on qubit 0
    qml.RY(state_prep_angle, wires=0)
    
    # Create Bell pair between qubits 1 and 2
    qml.Hadamard(wires=1)
    qml.CNOT(wires=[1, 2])
    
    # Bell measurement on qubits 0 and 1
    qml.CNOT(wires=[0, 1])
    qml.Hadamard(wires=0)
    
    # Conditional operations based on measurement results
    # (In real quantum computing, these would be conditional)
    # For simulation, we apply all possible corrections
    
    return qml.state()

# Execute teleportation
angle = np.pi / 4  # Prepare |+⟩ state
final_state = quantum_teleportation(angle)
print("Quantum Teleportation completed")
print("Final state:", final_state)`,
    language: 'python',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    size: 980,
  },
]

export const useFileStore = create<FileStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      activeFileId: 'file-1',
      files: initialFiles,
      theme: 'dark', // Always default to dark
      sidebarCollapsed: false,
      resultsCollapsed: false,
      compiledQasm: null,
      compileOptions: {
        inputLanguage: 'qasm',
        resultFormat: 'json',
        qasmVersion: '3.0',
        style: 'classic',
      },

      // Actions
      setActiveFile: (fileId) => {
        set({ activeFileId: fileId }, false, 'setActiveFile')
      },

      updateFileContent: (fileId, content) => {
        set(
          (state) => ({
            files: state.files.map((file) =>
              file.id === fileId
                ? {
                    ...file,
                    content,
                    updatedAt: new Date().toISOString(),
                    size: content.length,
                  }
                : file
            ),
          }),
          false,
          'updateFileContent'
        )
      },

      addFile: (name, content) => {
        const language = getLanguageFromFilename(name)
        const defaultContent = content ?? FILE_TEMPLATES[language] ?? ''
        
        const newFile: File = {
          id: generateId(),
          name,
          content: defaultContent,
          language,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          size: defaultContent.length,
        }

        set(
          (state) => ({
            files: [...state.files, newFile],
            activeFileId: newFile.id,
          }),
          false,
          'addFile'
        )

        return newFile
      },

      deleteFile: (fileId) => {
        set(
          (state) => {
            const newFiles = state.files.filter((file) => file.id !== fileId)
            const newActiveFileId =
              state.activeFileId === fileId
                ? newFiles.length > 0
                  ? newFiles[0].id
                  : null
                : state.activeFileId

            return {
              files: newFiles,
              activeFileId: newActiveFileId,
            }
          },
          false,
          'deleteFile'
        )
      },

      renameFile: (fileId, newName) => {
        set(
          (state) => ({
            files: state.files.map((file) =>
              file.id === fileId
                ? {
                    ...file,
                    name: newName,
                    language: getLanguageFromFilename(newName),
                    updatedAt: new Date().toISOString(),
                  }
                : file
            ),
          }),
          false,
          'renameFile'
        )
      },

      setTheme: (theme) => {
        set(
          () => {
            try {
              if (typeof window !== 'undefined') {
                localStorage.setItem('qcanvas-theme', theme)
                // Apply theme immediately to document
                document.documentElement.classList.toggle('dark', theme === 'dark')
                document.documentElement.classList.toggle('light', theme === 'light')
              }
            } catch {}
            return { theme }
          },
          false,
          'setTheme'
        )
      },

      toggleTheme: () => {
        set(
          (state) => {
            const next = state.theme === 'light' ? 'dark' : 'light'
            try {
              if (typeof window !== 'undefined') {
                localStorage.setItem('qcanvas-theme', next)
                // Apply theme immediately to document
                document.documentElement.classList.toggle('dark', next === 'dark')
                document.documentElement.classList.toggle('light', next === 'light')
              }
            } catch {}
            return { theme: next }
          },
          false,
          'toggleTheme'
        )
      },

      toggleSidebar: () => {
        set(
          (state) => ({
            sidebarCollapsed: !state.sidebarCollapsed,
          }),
          false,
          'toggleSidebar'
        )
      },

      toggleResults: () => {
        set(
          (state) => ({
            resultsCollapsed: !state.resultsCollapsed,
          }),
          false,
          'toggleResults'
        )
      },

      setFiles: (files) => {
        set({ files }, false, 'setFiles')
      },

      getActiveFile: () => {
        const state = get()
        return state.files.find((file) => file.id === state.activeFileId)
      },

      setCompileOptions: (options) => {
        set(
          (state) => ({
            compileOptions: { ...state.compileOptions, ...options },
          }),
          false,
          'setCompileOptions'
        )
      },

      setCompiledQasm: (qasm) => {
        set({ compiledQasm: qasm }, false, 'setCompiledQasm')
      },

      compileActiveToQasm: () => {
        const state = get()
        const active = state.files.find((f) => f.id === state.activeFileId)
        if (!active) return null

        // If already QASM, trust content
        if (active.language === 'qasm') {
          set({ compiledQasm: active.content }, false, 'compileActiveToQasm.qasm')
          return active.content
        }

        // Mock conversion to OpenQASM 3.0
        const header = `OPENQASM 3.0;\ninclude "stdgates.inc";\n\n// Converted from ${active.language.toUpperCase()} by QCanvas`;
        // Provide a minimal Bell-like placeholder when converting
        const body = [
          'qubit[2] q;',
          'bit[2] c;',
          '',
          'h q[0];',
          'cx q[0], q[1];',
          'c = measure q;',
          '',
          '// Original source:',
          ...active.content.split('\n').map((l) => `// ${l}`),
        ].join('\n')

        const qasm = `${header}\n\n${body}`
        set({ compiledQasm: qasm }, false, 'compileActiveToQasm.mock')
        return qasm
      },
    }),
    {
      name: 'file-store',
    }
  )
)
