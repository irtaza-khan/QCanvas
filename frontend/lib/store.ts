import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { File, EditorState, SupportedLanguage, FILE_TEMPLATES, CompileOptions } from '@/types'
import { generateId, getLanguageFromFilename } from './utils'
import { projectsApi, Project, authApi } from './api'
import { useAuthStore } from './authStore'
import toast from 'react-hot-toast'

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

// QSim simulation results interface
interface SimulationResult {
  counts: { [state: string]: number }
  metadata: {
    n_qubits: number
    visitor?: string
    backend: string
    shots: number
    success?: boolean
    // Performance metrics (populated by backend)
    execution_time?: string
    simulation_time?: string
    postprocessing_time?: string
    memory_usage?: string
    cpu_usage?: string
    fidelity?: number
    successful_shots?: number
    [key: string]: any
  }
  probs?: { [state: string]: number } | null
  circuit?: any
}

// Hybrid execution result interface
interface HybridResult {
  success: boolean
  stdout: string
  stderr: string
  qasm_generated?: string | null
  simulation_results: Array<{
    counts: { [state: string]: number }
    probabilities: { [state: string]: number }
    shots: number
    backend: string
    execution_time: string
    n_qubits: number
    metadata: { [key: string]: any }
  }>
  execution_time: string
  error?: string | null
  error_line?: number | null
  error_type?: string | null
}

// Execution mode type
type ExecutionMode = 'compile' | 'execute' | 'hybrid'

interface FileStore extends EditorState {
  // Additional state for conversion stats and simulation results
  conversionStats: ConversionStats | null
  simulationResults: SimulationResult | null

  // Project state
  projects: Project[]
  activeProjectId: number | null
  loading: boolean

  // Hybrid execution state
  hybridResult: HybridResult | null
  executionMode: ExecutionMode

  // Actions
  setActiveFile: (fileId: string | null) => void
  updateFileContent: (fileId: string, content: string) => void
  addFile: (name: string, content?: string) => File
  addFileWithoutActivating: (name: string, content?: string) => File
  deleteFile: (fileId: string) => Promise<void>

  setTheme: (theme: 'light' | 'dark') => void
  toggleTheme: () => void
  toggleSidebar: () => void
  toggleResults: () => void
  setFiles: (files: File[]) => void
  getActiveFile: () => File | undefined
  setCompileOptions: (options: Partial<CompileOptions>) => void
  setCompiledQasm: (qasm: string | null) => void
  setConversionStats: (stats: ConversionStats | null) => void
  setSimulationResults: (results: SimulationResult | null) => void
  setHybridResult: (result: HybridResult | null) => void
  setExecutionMode: (mode: ExecutionMode) => void
  compileActiveToQasm: () => string | null

  // Async Actions
  fetchProjects: (token: string) => Promise<void>
  fetchProjectFiles: (projectId: number | null, token: string) => Promise<void>
  createProject: (name: string, isPublic: boolean, token: string) => Promise<void>
  saveActiveFile: () => Promise<void>
  createFile: (name: string, content?: string, projectId?: number, isShared?: boolean) => Promise<void>
  renameFile: (fileId: string, newName: string) => Promise<void>
}

// Initial files - quantum algorithm examples from different frameworks
const initialFiles: File[] = [
  (() => {
    const content = `import cirq

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
`;
    return {
      id: 'file-1',
      name: 'bell_state_cirq.py',
      content,
      language: 'python',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      size: content.length,
    };
  })(),
  // Hybrid execution example
  (() => {
    const content = `# Hybrid CPU-QPU Execution Example
# Switch to "Hybrid" mode in the toolbar to run this code!

import cirq
from qcanvas import compile
import qsim

# Create a Bell state circuit
q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(q[0], q[1], key='result')
])

print("Circuit created:")
print(circuit)
print()

# Compile circuit to OpenQASM 3.0
qasm = compile(circuit, framework="cirq")
print("Generated QASM:")
print(qasm)
print()

# Run multiple simulations in a loop
print("Running 3 simulations...")
for i in range(3):
    result = qsim.run(qasm, shots=100, backend="cirq")
    print(f"Run {i+1}: {result.counts}")
    print(f"  Probabilities: {result.probabilities}")

print()
print("Hybrid execution complete!")
`;
    return {
      id: 'file-hybrid',
      name: 'hybrid_example.py',
      content,
      language: 'python',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      size: content.length,
    };
  })(),
  (() => {
    const content = `from qiskit import QuantumCircuit

# 3 qubits, 2 classical bits (only measure input qubits)
qc = QuantumCircuit(3, 2)

# STEP 1: Initialize ancilla to |1⟩
qc.x(2)

# STEP 2: Hadamard on all qubits
for i in range(3):
    qc.h(i)

# STEP 3: Balanced Oracle
qc.cx(0, 2)
qc.cx(1, 2)

# STEP 4: Hadamard on input qubits
qc.h(0)
qc.h(1)

# STEP 5: Measure input qubits
qc.measure(0, 0)
qc.measure(1, 1)
`;
    return {
      id: 'file-2',
      name: 'deutsch_jozsa_qiskit.py',
      content,
      language: 'python',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      size: content.length,
    };
  })(),
  (() => {
    const content = `import pennylane as qml

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def grover_circuit():
    # STEP 1: Initialize superposition
    qml.Hadamard(wires=0)
    qml.Hadamard(wires=1)
    
    # STEP 2: Oracle - mark |11⟩
    qml.CZ(wires=[0, 1])
    
    # STEP 3: Diffusion Operator
    qml.Hadamard(wires=0)
    qml.Hadamard(wires=1)
    qml.PauliX(wires=0)
    qml.PauliX(wires=1)
    qml.CZ(wires=[0, 1])
    qml.PauliX(wires=0)
    qml.PauliX(wires=1)
    qml.Hadamard(wires=0)
    qml.Hadamard(wires=1)
    
    # STEP 4: Measure
    qml.measure(wires=0)
    qml.measure(wires=1)
`;
    return {
      id: 'file-3',
      name: 'grovers_search_pennylane.py',
      content,
      language: 'python',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      size: content.length,
    };
  })(),
  // Quantum Random Number Generator (QRNG) - Hybrid example
  (() => {
    const content = `import cirq

from qcanvas import compile
import qsim

print("=== Quantum Random Number Generator (QRNG) ===\\n")

# Create a simple circuit that generates one random bit
# H gate creates superposition, measurement collapses to 0 or 1
q = cirq.LineQubit(0)
circuit = cirq.Circuit([
    cirq.H(q),
    cirq.measure(q, key='random_bit')
])

# Compile to QASM
qasm = compile(circuit, framework="cirq")
print(f"QRNG Circuit QASM:\\n{qasm}\\n")

# Generate 10 random bits
print("Generating 10 random bits:")
random_bits = []
for i in range(10):
    result = qsim.run(qasm, shots=1, backend="cirq")
    # Extract the bit value (0 or 1)
    bit = list(result.counts.keys())[0]
    random_bits.append(bit)
    print(f"  Bit {i+1}: {bit}")

print(f"\\nRandom bit sequence: {''.join(random_bits)}")
`;
    return {
      id: 'file-4',
      name: 'qrng_hybrid_cirq.py',
      content,
      language: 'python',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      size: content.length,
    };
  })(),
]

export const useFileStore = create<FileStore>()(
  devtools(
    (set, get) => ({
      // Initial state
      activeFileId: null, // No file active initially until loaded
      files: [], // Start empty, load from DB
      projects: [],
      activeProjectId: null,
      loading: false,
      theme: 'dark', // Always default to dark
      sidebarCollapsed: false,
      resultsCollapsed: false,
      compiledQasm: null,
      conversionStats: null,
      simulationResults: null,
      hybridResult: null,
      executionMode: 'execute' as ExecutionMode,
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

      deleteFile: async (fileId) => {
        const token = useAuthStore.getState().token

        // API call if token exists and not a temp file
        if (token && !fileId.startsWith('file-')) {
          try {
            // Import dynamically to avoid circular dependency if any (though api.ts is already imported)
            const api = await import('./api').then(m => m.fileApi)
            await api.deleteFile(parseInt(fileId), token)
          } catch (error) {
            console.error("Failed to delete remote file", error)
            // Propagate error to caller (Sidebar) so it can show error toast
            throw error
          }
        }

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

      renameFile: async (fileId: string, newName: string) => {
        const state = get()
        const token = useAuthStore.getState().token

        // Optimistic update
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

        // API call if token exists and not a temp file
        if (token && !fileId.startsWith('file-')) {
          try {
            // We need to know if it's a project file or root file?
            // Actually fileApi.updateFile handles root files (via /api/files/{id})
            // But if it's a project file, we might need projectsApi.updateFile??
            // Our refactor made /api/files/{id} universial for updates generally?
            // Let's check api.ts again. fileApi.updateFile uses /api/files/{id} PUT.
            // projectsApi.updateFile uses /api/projects/{pid}/files/{fid} PUT.
            // If the file has a projectId, we should safe check.
            // But our backend /api/files/{id} update should work if user owns it.
            // Let's use fileApi.updateFile as it's cleaner.

            const api = await import('./api').then(m => m.fileApi)
            await api.updateFile(parseInt(fileId), { filename: newName }, token)
          } catch (error) {
            console.error("Failed to rename file remotely", error)
            toast.error("Failed to save rename")
            // Revert? For now, keep optimistic
          }
        }
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
            } catch { }
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
            } catch { }
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

      setSimulationResults: (results) => {
        set({ simulationResults: results }, false, 'setSimulationResults')
      },

      setHybridResult: (result) => {
        set({ hybridResult: result }, false, 'setHybridResult')
      },

      setExecutionMode: (mode) => {
        set({ executionMode: mode }, false, 'setExecutionMode')
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

        // Mock conversion to OpenQASM 3
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

      // Async Actions
      fetchProjects: async (token: string) => {
        set({ loading: true })
        try {
          const res = await projectsApi.getProjects(token)
          if (res.success && res.data) {
            set({ projects: res.data }, false, 'fetchProjects')
            // Don't auto-select project, allow viewing root files
          }
        } catch (error) {
          console.error("Failed to fetch projects", error)
        } finally {
          set({ loading: false })
        }
      },

      createProject: async (name: string, isPublic: boolean, token: string) => {
        set({ loading: true })
        try {
          const res = await projectsApi.createProject({ name, is_public: isPublic }, token)
          if (res.success && res.data) {
            const newProject = res.data
            set(state => ({
              projects: [...state.projects, newProject],
              activeProjectId: newProject.id,
              activeFileId: null
            }), false, 'createProject')
            // After creating project, we might want to fetch its files (empty) + root files?
            // Or just let the UI trigger fetch
            get().fetchProjectFiles(newProject.id, token)
          }
        } catch (error) {
          console.error("Failed to create project", error)
          toast.error("Failed to create project")
        } finally {
          set({ loading: false })
        }
      },

      fetchProjectFiles: async (projectId: number | null, token: string) => {
        // If projectId is null, we fetch root files.
        // If projectId is set, we fetch project files.
        // BUT we likely want to see root files ALWAYS?
        // For now, let's implement fetching specific scope.
        // The Sidebar might call this twice or we merge results?
        // Let's assume this action REPLACES files list with the scope's files
        // OR we can rely on `files` containing everything and Sidebar filtering.
        // Let's try to fetch BOTH if a project is active?
        // Simplest: Fetch based on argument.

        set({ loading: true })
        try {
          // Using fileApi now
          const res = await import('./api').then(m => m.fileApi.getFiles(projectId || undefined, token))

          if (res.success && res.data) {
            const fetchedFiles = (res.data as any[]).map((f: any) => ({
              id: f.id.toString(),
              name: f.filename,
              content: f.content,
              language: getLanguageFromFilename(f.filename),
              createdAt: f.created_at || new Date().toISOString(),
              updatedAt: f.updated_at || new Date().toISOString(),
              size: f.content?.length || 0,
              projectId: f.project_id ? f.project_id.toString() : undefined,
              isShared: f.is_shared,
              userId: f.user_id,
            }))

            set(state => {
              // If fetching a project, filter out old files of THAT project?
              // Or just replace all files?
              // If we want to show Root files + Project files, we need to manage them.
              // Let's assume we replace `files` entirely for the view scope?
              // User said "In memory files are always visible".
              // Let's merge with initialFiles.

              // If we are switching projects, we probably want to clear other project files.
              // But keep root files if we fetched them?

              // Strategy: Just set files to (Initial + Fetched).
              // If we want root + project, caller needs to handle it or we fetch both here.
              // Let's fetch root files if projectId is provided too?

              const filesToShow = projectId
                ? fetchedFiles
                : [...initialFiles, ...fetchedFiles]

              return {
                files: filesToShow,
                activeProjectId: projectId
              }
            }, false, 'fetchProjectFiles')

            if (fetchedFiles.length > 0) {
              // Optional: set active, or handle in UI
            }
          }
        } catch (error) {
          console.error("Failed to fetch files", error)
        } finally {
          set({ loading: false })
        }
      },

      saveActiveFile: async () => {
        const state = get()
        const activeFile = state.getActiveFile()
        const token = useAuthStore.getState().token

        if (!activeFile || !token) {
          if (!token) toast.error("Please log in to save")
          return
        }

        // If it's an initial in-memory file without DB ID (starts with 'file-'), we create it?
        // Or if it has a real ID (numeric usually from DB, but we verify)
        // Actually our DB IDs are Ints, converted to string. 
        // Initial files have 'file-X' which is not int-like.
        // If we save a 'file-X', we should create it.

        const isNew = activeFile.id.startsWith('file-')
        const endpoint = import('./api').then(m => isNew ? m.fileApi.createFile : m.fileApi.updateFile)

        const toastId = toast.loading('Saving...')
        try {
          const api = await import('./api').then(m => m.fileApi)
          let res;
          if (isNew) {
            // Create
            res = await api.createFile({
              filename: activeFile.name,
              content: activeFile.content,
              is_main: false, // Default?
              project_id: state.activeProjectId || undefined,
              is_shared: activeFile.isShared
            }, token)
          } else {
            // Update
            res = await api.updateFile(parseInt(activeFile.id), {
              content: activeFile.content
            }, token)
          }

          if (res.success && res.data) {
            toast.success('Saved', { id: toastId })
            // Update local file with new data (ID might change if new)
            const backendFile = res.data as any
            const updatedFile: File = {
              ...activeFile,
              id: backendFile.id.toString(),
              name: backendFile.filename,
              content: backendFile.content,
              updatedAt: backendFile.updated_at || new Date().toISOString(),
              projectId: backendFile.project_id?.toString(),
              isShared: backendFile.is_shared
            }

            set(state => ({
              files: state.files.map(f => f.id === activeFile.id ? updatedFile : f),
              activeFileId: updatedFile.id
            }))
          } else {
            const errorText = typeof res.error === 'object' ? JSON.stringify(res.error) : res.error
            toast.error(`Failed to save: ${errorText}`, { id: toastId })
          }
        } catch (error) {
          console.error('Save failed', error)
          toast.error('Save failed', { id: toastId })
        }
      },

      createFile: async (name: string, content?: string, projectId?: number, isShared: boolean = false) => {
        const state = get()
        const token = useAuthStore.getState().token

        // Fallback to local if no token (but user asked for backend sync)
        if (!token) {
          // Toast or memory?
          get().addFile(name, content)
          return
        }

        const language = getLanguageFromFilename(name)
        const defaultContent = content ?? FILE_TEMPLATES[language] ?? ''
        const toastId = toast.loading('Creating file...')

        try {
          const api = await import('./api').then(m => m.fileApi)
          const res = await api.createFile({
            filename: name,
            content: defaultContent,
            is_main: false,
            project_id: projectId,
            is_shared: isShared
          }, token)

          if (res.success && res.data) {
            const f = res.data as any
            const newFile: File = {
              id: f.id.toString(),
              name: f.filename,
              content: f.content,
              language: language,
              createdAt: f.created_at || new Date().toISOString(),
              updatedAt: f.updated_at || new Date().toISOString(),
              size: f.content.length,
              projectId: f.project_id?.toString(),
              isShared: f.is_shared,
              userId: f.user_id?.toString()
            }
            set(
              (state) => ({
                files: [...state.files, newFile],
                activeFileId: newFile.id,
              }),
              false,
              'createFile'
            )
            toast.success(`Created ${name}`, { id: toastId })
          } else {
            const errorText = typeof res.error === 'object' ? JSON.stringify(res.error) : res.error
            toast.error(`Failed to create file: ${errorText}`, { id: toastId })
          }
        } catch (error) {
          console.error("Create file failed", error)
          toast.error("Failed to create file", { id: toastId })
        }
      },
    }),
    {
      name: 'file-store',
    }
  )
)
