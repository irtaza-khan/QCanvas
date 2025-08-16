import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { File, EditorState, SupportedLanguage, FILE_TEMPLATES, CompileOptions } from '@/types'
import { generateId, getLanguageFromFilename } from './utils'

// Conversion stats interface based on backend ConversionResult
interface ConversionStats {
  qubits?: number | null
  gates?: { [gateName: string]: number } | null
  depth?: number | null
  conversion_time?: string | null
  framework?: string
  qasm_version?: string
  success?: boolean
  error?: string | null
}

interface FileStore extends EditorState {
  // Additional state for conversion stats
  conversionStats: ConversionStats | null
  
  // Actions
  setActiveFile: (fileId: string | null) => void
  updateFileContent: (fileId: string, content: string) => void
  addFile: (name: string, content?: string) => File
  addFileWithoutActivating: (name: string, content?: string) => File
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
  setConversionStats: (stats: ConversionStats | null) => void
  compileActiveToQasm: () => string | null
}

// Initial files sourced from tests/unit/test_converters
const initialFiles: File[] = [
  {
    id: 'file-1',
    name: 'test_qiskit_converter.py',
    content: `from qiskit import QuantumCircuit
def get_circuit():
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure([0, 1], [0, 1])
    return qc
`,
    language: 'python',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    size: 0,
  },
  {
    id: 'file-2',
    name: 'test_cirq_converter.py',
    content: `import cirq
def get_circuit():
    q0, q1 = cirq.LineQubit.range(2)
    circuit = cirq.Circuit(
        cirq.H(q0),
        cirq.CNOT(q0, q1),
        cirq.measure(q0, key="m0"),
        cirq.measure(q1, key="m1")
    )
    return circuit
`,
    language: 'python',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    size: 0,
  },
  {
    id: 'file-3',
    name: 'test_pennylane_converter.py',
    content: `import pennylane as qml
import numpy as np

dev = qml.device('default.qubit', wires=3)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.RX(np.pi/4, wires=0)
    qml.RY(np.pi/2, wires=1)
    qml.CNOT(wires=[0, 1])
    qml.RZ(np.pi/3, wires=2)
    qml.CZ(wires=[1, 2])
    return qml.expval(qml.PauliZ(0))
`,
    language: 'python',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    size: 0,
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
      conversionStats: null,
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

      // Create a new file but keep the current active file unchanged
      addFileWithoutActivating: (name, content) => {
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
          }),
          false,
          'addFileWithoutActivating'
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

      setConversionStats: (stats) => {
        set({ conversionStats: stats }, false, 'setConversionStats')
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
