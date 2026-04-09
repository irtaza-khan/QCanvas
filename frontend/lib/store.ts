import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { File, Folder, ExplorerTree, EditorState, FILE_TEMPLATES, CompileOptions } from '@/types'
import { generateId, getLanguageFromFilename } from './utils'
import { projectsApi, foldersApi, Project, authApi } from './api'
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
type ExecutionMode = 'basic' | 'expert'

interface FileStore extends EditorState {
  // Additional state for conversion stats and simulation results
  conversionStats: ConversionStats | null
  simulationResults: SimulationResult | null

  // Project state
  projects: Project[]
  activeProjectId: number | null
  loading: boolean

  // Explorer tree state (folders + files)
  folders: Folder[]
  selectedFolderId: string | null

  // Editor tabs state
  openFileIds: string[]

  // Hybrid execution state
  hybridResult: HybridResult | null
  executionMode: ExecutionMode

  // Actions
  setActiveFile: (fileId: string | null) => void
  openFile: (fileId: string) => void
  closeFile: (fileId: string) => void
  closeOtherFiles: (fileId: string) => void
  updateFileContent: (fileId: string, content: string) => void
  addFile: (name: string, content?: string) => File
  addFileWithoutActivating: (name: string, content?: string) => File
  deleteFile: (fileId: string) => Promise<void>
  fetchFiles: (projectId?: number) => Promise<void>

  setTheme: (theme: 'light' | 'dark') => void
  toggleTheme: () => void
  setExplainItMode: (enabled: boolean) => void
  toggleExplainItMode: () => void
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
  fetchExplorerTree: (projectId: number | null, token: string) => Promise<void>
  createFolder: (name: string, projectId?: number, parentFolderId?: string) => Promise<void>
  renameFolder: (folderId: string, newName: string) => Promise<void>
  deleteFolder: (folderId: string) => Promise<void>
  createProject: (name: string, isPublic: boolean, token: string) => Promise<void>
  saveActiveFile: () => Promise<void>
  createFile: (name: string, content?: string, projectId?: number, isShared?: boolean, folderId?: string) => Promise<void>
  renameFile: (fileId: string, newName: string) => Promise<void>
  moveFileToFolder: (fileId: string, folderId: string | null) => Promise<void>
}

// =============================================================================
// DEVELOPER TOGGLE: Set to true to show built-in template files in the sidebar
// =============================================================================
const SHOW_TEMPLATE_FILES = false

const BASIC_QISKIT_BELL_TEMPLATE = `from qiskit import QuantumCircuit

# Bell state circuit
qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

print(qc)
`

const getDefaultNewFileContent = (name: string, content?: string) => {
  if (content !== undefined) return content
  const language = getLanguageFromFilename(name)
  if (language === 'python') return BASIC_QISKIT_BELL_TEMPLATE
  return FILE_TEMPLATES[language] ?? ''
}

const splitFilename = (name: string) => {
  const trimmed = name.trim()
  const dot = trimmed.lastIndexOf('.')
  if (dot <= 0 || dot === trimmed.length - 1) {
    return { base: trimmed, ext: '' }
  }
  return { base: trimmed.slice(0, dot), ext: trimmed.slice(dot) }
}

const makeUniqueFilename = (desiredName: string, existingNames: string[]) => {
  const existing = new Set(existingNames.map((n) => n.trim().toLowerCase()))
  const desiredTrimmed = desiredName.trim()
  if (!desiredTrimmed) return desiredName

  if (!existing.has(desiredTrimmed.toLowerCase())) return desiredTrimmed

  const { base, ext } = splitFilename(desiredTrimmed)
  let i = 1
  // eslint-disable-next-line no-constant-condition
  while (true) {
    const candidate = `${base} (${i})${ext}`
    if (!existing.has(candidate.toLowerCase())) return candidate
    i += 1
  }
}

const makeUniqueFolderName = (desiredName: string, existingNames: string[]) => {
  const existing = new Set(existingNames.map((n) => n.trim().toLowerCase()))
  const desiredTrimmed = desiredName.trim()
  if (!desiredTrimmed) return desiredName

  if (!existing.has(desiredTrimmed.toLowerCase())) return desiredTrimmed

  let i = 1
  // eslint-disable-next-line no-constant-condition
  while (true) {
    const candidate = `${desiredTrimmed} (${i})`
    if (!existing.has(candidate.toLowerCase())) return candidate
    i += 1
  }
}

const collectDescendantFolderIds = (folders: Folder[], rootFolderId: string) => {
  const childrenByParent = new Map<string, string[]>()
  for (const f of folders) {
    const parent = f.parentId
    if (!parent) continue
    const list = childrenByParent.get(parent) ?? []
    list.push(f.id)
    childrenByParent.set(parent, list)
  }

  const result = new Set<string>()
  const stack = [rootFolderId]
  while (stack.length > 0) {
    const cur = stack.pop() as string
    if (result.has(cur)) continue
    result.add(cur)
    const kids = childrenByParent.get(cur) ?? []
    for (const k of kids) stack.push(k)
  }
  return result
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
      folders: [],
      selectedFolderId: null,
      openFileIds: [],
      theme: 'dark', // Always default to dark
      explainItMode: true,
      sidebarCollapsed: false,
      resultsCollapsed: false,
      compiledQasm: null,
      conversionStats: null,
      simulationResults: null,
      hybridResult: null,
      executionMode: 'basic' as ExecutionMode,
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

      openFile: (fileId: string) => {
        set(
          (state) => {
            const openFileIds = state.openFileIds.includes(fileId)
              ? state.openFileIds
              : [...state.openFileIds, fileId]
            return { openFileIds, activeFileId: fileId }
          },
          false,
          'openFile'
        )
      },

      closeFile: (fileId: string) => {
        set(
          (state) => {
            const openFileIds = state.openFileIds.filter((id) => id !== fileId)
            let activeFileId = state.activeFileId
            if (state.activeFileId === fileId) {
              activeFileId = openFileIds.at(-1) ?? null
            }
            return { openFileIds, activeFileId }
          },
          false,
          'closeFile'
        )
      },

      closeOtherFiles: (fileId: string) => {
        set(
          (state) => {
            const openFileIds = state.openFileIds.includes(fileId) ? [fileId] : state.openFileIds
            const activeFileId = state.openFileIds.includes(fileId) ? fileId : state.activeFileId
            return { openFileIds, activeFileId }
          },
          false,
          'closeOtherFiles'
        )
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
        const uniqueName = makeUniqueFilename(name, get().files.map((f) => f.name))
        const language = getLanguageFromFilename(uniqueName)
        const defaultContent = getDefaultNewFileContent(uniqueName, content)

        const newFile: File = {
          id: generateId(),
          name: uniqueName,
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
        const uniqueName = makeUniqueFilename(name, get().files.map((f) => f.name))
        const language = getLanguageFromFilename(uniqueName)
        const defaultContent = getDefaultNewFileContent(uniqueName, content)

        const newFile: File = {
          id: generateId(),
          name: uniqueName,
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
            await api.deleteFile(Number.parseInt(fileId, 10), token)
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
        const existingOtherNames = state.files
          .filter((f) => f.id !== fileId)
          .map((f) => f.name)
        const uniqueName = makeUniqueFilename(newName, existingOtherNames)

        // Optimistic update
        set(
          (state) => ({
            files: state.files.map((file) =>
              file.id === fileId
                ? {
                  ...file,
                  name: uniqueName,
                  language: getLanguageFromFilename(uniqueName),
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
            await api.updateFile(Number.parseInt(fileId, 10), { filename: uniqueName }, token)
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

      setExplainItMode: (enabled) => {
        set(
          () => {
            try {
              if (globalThis.window !== undefined) {
                localStorage.setItem('qcanvas-explain-it', enabled ? '1' : '0')
              }
            } catch { }
            return { explainItMode: enabled }
          },
          false,
          'setExplainItMode'
        )
      },

      toggleExplainItMode: () => {
        set(
          (state) => {
            const next = !state.explainItMode
            try {
              if (globalThis.window !== undefined) {
                localStorage.setItem('qcanvas-explain-it', next ? '1' : '0')
              }
            } catch { }
            return { explainItMode: next }
          },
          false,
          'toggleExplainItMode'
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
          const api = await import('./api').then(m => m.projectsApi)
          const res = await api.getProjects(token)
          if (res.success && res.data) {
            // Map files within projects to frontend format
            const mappedProjects = res.data.map((project: any) => ({
              ...project,
              id: project.id.toString(),
              files: (project.files || []).map((f: any) => ({
                id: f.id.toString(),
                name: f.filename,
                content: f.content,
                language: getLanguageFromFilename(f.filename),
                createdAt: f.created_at || new Date().toISOString(),
                updatedAt: f.updated_at || new Date().toISOString(),
                size: f.content?.length || 0,
                projectId: project.id.toString(),
                isShared: f.is_shared,
                userId: f.user_id,
              }))
            }))
            set({ projects: mappedProjects }, false, 'fetchProjects')
          }
        } catch (error) {
          console.error("Failed to fetch projects", error)
        } finally {
          set({ loading: false })
        }
      },

      fetchFiles: async (projectId?: number) => {
        const token = useAuthStore.getState().token
        if (!token) return

        set({ loading: true })
        try {
          const api = await import('./api').then(m => m.fileApi)
          const res = await api.getFiles(projectId)
          if (res.success && res.data) {
            const mappedFiles = (res.data as any[]).map((f: any) => ({
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
              // If we are showing root files (projectId is undefined), 
              // we might want to keep template files if SHOW_TEMPLATE_FILES is true
              const templates = SHOW_TEMPLATE_FILES ? initialFiles : []
              const filesToShow = projectId ? mappedFiles : [...templates, ...mappedFiles]
              
              return { 
                files: filesToShow,
                loading: false
              }
            }, false, 'fetchFiles')
          }
        } catch (error) {
          console.error('Failed to fetch files:', error)
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
            // Refresh explorer scope for the created project so folders/files stay in sync.
            get().fetchExplorerTree(newProject.id, token)
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

              const templates = SHOW_TEMPLATE_FILES ? initialFiles : []
              const filesToShow = projectId
                ? fetchedFiles
                : [...templates, ...fetchedFiles]

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

      fetchExplorerTree: async (projectId: number | null, token: string) => {
        set({ loading: true })
        try {
          const res = await foldersApi.getExplorerTree(projectId || undefined, token)
          if (res.success && res.data) {
            const tree = res.data

            const folders: Folder[] = (tree.folders || []).map((f: any) => ({
              id: f.id.toString(),
              name: f.name,
              projectId: f.project_id == null ? undefined : f.project_id.toString(),
              parentId: f.parent_id == null ? undefined : f.parent_id.toString(),
              createdAt: f.created_at || new Date().toISOString(),
              updatedAt: f.updated_at || new Date().toISOString(),
            }))

            const fetchedFiles: File[] = (tree.files || []).map((f: any) => ({
              id: f.id.toString(),
              name: f.filename,
              content: f.content,
              language: getLanguageFromFilename(f.filename),
              createdAt: f.created_at || new Date().toISOString(),
              updatedAt: f.updated_at || new Date().toISOString(),
              size: f.content?.length || 0,
              projectId: f.project_id == null ? undefined : f.project_id.toString(),
              folderId: f.folder_id == null ? undefined : f.folder_id.toString(),
              isShared: f.is_shared,
              userId: f.user_id?.toString?.() ?? undefined,
            }))

            set((state) => {
              const templates = SHOW_TEMPLATE_FILES ? initialFiles : []
              const filesToShow = projectId ? fetchedFiles : [...templates, ...fetchedFiles]
              return {
                folders,
                files: filesToShow,
                activeProjectId: projectId,
              }
            }, false, 'fetchExplorerTree')
          }
        } catch (error) {
          console.error('Failed to fetch explorer tree', error)
        } finally {
          set({ loading: false })
        }
      },

      createFolder: async (name: string, projectId?: number, parentFolderId?: string) => {
        const token = useAuthStore.getState().token
        if (!token) {
          toast.error('Please log in to create a folder')
          return
        }

        const state = get()
        const folderName = name.trim()
        if (!folderName) return

        const siblingFolderNames = state.folders
          .filter((f) => {
            const sameProject =
              (f.projectId ?? undefined) === (projectId?.toString() ?? undefined)
            const sameParent =
              (f.parentId ?? undefined) === (parentFolderId ?? undefined)
            return sameProject && sameParent
          })
          .map((f) => f.name)
        const uniqueFolderName = makeUniqueFolderName(folderName, siblingFolderNames)

        const toastId = toast.loading('Creating folder...')
        try {
          const res = await foldersApi.createFolder({
            name: uniqueFolderName,
            project_id: projectId,
            parent_id: parentFolderId ? Number.parseInt(parentFolderId, 10) : undefined,
          }, token)

          if (res.success && res.data) {
            const f: any = res.data
            const newFolder: Folder = {
              id: f.id.toString(),
              name: f.name,
              projectId: f.project_id == null ? undefined : f.project_id.toString(),
              parentId: f.parent_id == null ? undefined : f.parent_id.toString(),
              createdAt: f.created_at || new Date().toISOString(),
              updatedAt: f.updated_at || new Date().toISOString(),
            }

            set((state) => ({
              folders: [...state.folders, newFolder],
            }), false, 'createFolder')

            toast.success(`Created folder ${uniqueFolderName}`, { id: toastId })
          } else {
            const errorText = typeof res.error === 'object' ? JSON.stringify(res.error) : res.error
            toast.error(`Failed to create folder: ${errorText}`, { id: toastId })
          }
        } catch (error) {
          console.error('Create folder failed', error)
          toast.error('Failed to create folder', { id: toastId })
        }
      },

      renameFolder: async (folderId: string, newName: string) => {
        const token = useAuthStore.getState().token
        if (!token) {
          toast.error('Please log in to rename a folder')
          return
        }

        const state = get()
        const folderName = newName.trim()
        if (!folderName) return

        const current = state.folders.find((f) => f.id === folderId)
        const siblingFolderNames = state.folders
          .filter((f) => {
            if (f.id === folderId) return false
            const sameProject = (f.projectId ?? undefined) === (current?.projectId ?? undefined)
            const sameParent = (f.parentId ?? undefined) === (current?.parentId ?? undefined)
            return sameProject && sameParent
          })
          .map((f) => f.name)
        const uniqueFolderName = makeUniqueFolderName(folderName, siblingFolderNames)

        const toastId = toast.loading('Renaming folder...')
        try {
          const res = await foldersApi.updateFolder(
            Number.parseInt(folderId, 10),
            { name: uniqueFolderName },
            token,
          )
          if (res.success && res.data) {
            set((state) => ({
              folders: state.folders.map((f) =>
                f.id === folderId
                  ? { ...f, name: uniqueFolderName, updatedAt: new Date().toISOString() }
                  : f
              ),
            }), false, 'renameFolder')
            toast.success('Folder renamed', { id: toastId })
          } else {
            const errorText = typeof res.error === 'object' ? JSON.stringify(res.error) : res.error
            toast.error(`Failed to rename folder: ${errorText}`, { id: toastId })
          }
        } catch (error) {
          console.error('Rename folder failed', error)
          toast.error('Failed to rename folder', { id: toastId })
        }
      },

      deleteFolder: async (folderId: string) => {
        const token = useAuthStore.getState().token
        if (!token) {
          toast.error('Please log in to delete a folder')
          return
        }

        const toastId = toast.loading('Deleting folder...')
        try {
          const state = get()
          const folderIdsToRemove = collectDescendantFolderIds(state.folders, folderId)
          const filesInTree = state.files.filter((f) => f.folderId && folderIdsToRemove.has(f.folderId))

          // 1) Delete files first (backend rejects non-empty folder deletes).
          const api = await import('./api').then((m) => m.fileApi)
          for (const f of filesInTree) {
            if (f.id.startsWith('file-')) continue
            const fileIdNum = Number.parseInt(f.id, 10)
            // If parse fails, skip remote delete (keeps UI consistent with local-only files)
            if (Number.isNaN(fileIdNum)) continue
            const delRes = await api.deleteFile(fileIdNum, token)
            if (!delRes.success) {
              const errorText =
                typeof delRes.error === 'object' ? JSON.stringify(delRes.error) : delRes.error
              toast.error(`Failed to delete file "${f.name}": ${errorText}`, { id: toastId })
              return
            }
          }

          // 2) Delete folders deepest-first.
          const depthOf = (id: string) => {
            const byId = new Map(state.folders.map((x) => [x.id, x]))
            let depth = 0
            let cur = byId.get(id)
            while (cur?.parentId) {
              depth += 1
              cur = byId.get(cur.parentId)
            }
            return depth
          }
          const folderIdsSorted = Array.from(folderIdsToRemove).sort((a, b) => depthOf(b) - depthOf(a))

          for (const fid of folderIdsSorted) {
            const delFolderRes = await foldersApi.deleteFolder(Number.parseInt(fid, 10), token)
            if (!delFolderRes.success) {
              const errorText =
                typeof delFolderRes.error === 'object'
                  ? JSON.stringify(delFolderRes.error)
                  : delFolderRes.error
              toast.error(`Failed to delete folder: ${errorText}`, { id: toastId })
              return
            }
          }

          // 3) Update local state after successful remote deletion.
          set((s) => {
            const removedFileIds = new Set(filesInTree.map((f) => f.id))
            const files = s.files.filter((f) => !removedFileIds.has(f.id))
            const folders = s.folders.filter((f) => !folderIdsToRemove.has(f.id))
            const openFileIds = s.openFileIds.filter((id) => !removedFileIds.has(id))
            const activeFileId =
              s.activeFileId && removedFileIds.has(s.activeFileId)
                ? openFileIds.at(-1) ?? null
                : s.activeFileId
            return { folders, files, openFileIds, activeFileId }
          }, false, 'deleteFolder')

          toast.success('Folder deleted', { id: toastId })
        } catch (error) {
          console.error('Delete folder failed', error)
          toast.error('Failed to delete folder', { id: toastId })
        }
      },

      moveFileToFolder: async (fileId: string, folderId: string | null) => {
        const token = useAuthStore.getState().token
        const prev = get().files.find((f) => f.id === fileId)
        if (!prev) return

        // Optimistic UI update
        set(
          (state) => ({
            files: state.files.map((f) =>
              f.id === fileId
                ? { ...f, folderId: folderId ?? undefined, updatedAt: new Date().toISOString() }
                : f,
            ),
          }),
          false,
          'moveFileToFolder',
        )

        // Local-only file or unauthenticated: done.
        if (!token || fileId.startsWith('file-')) return

        try {
          const api = await import('./api').then((m) => m.fileApi)
          await api.updateFile(
            Number.parseInt(fileId, 10),
            {
              folder_id: folderId ? Number.parseInt(folderId, 10) : null,
            },
            token,
          )
        } catch (e) {
          console.error('moveFileToFolder failed', e)
          // Revert on failure
          set(
            (state) => ({
              files: state.files.map((f) =>
                f.id === fileId ? { ...f, folderId: prev.folderId, updatedAt: new Date().toISOString() } : f,
              ),
            }),
            false,
            'moveFileToFolder.revert',
          )
          toast.error('Failed to move file')
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
            res = await api.updateFile(Number.parseInt(activeFile.id, 10), {
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

      createFile: async (name: string, content?: string, projectId?: number, isShared: boolean = false, folderId?: string) => {
        const state = get()
        const token = useAuthStore.getState().token

        // Fallback to local if no token (but user asked for backend sync)
        if (!token) {
          // Toast or memory?
          get().addFile(name, content)
          return
        }

        const uniqueName = makeUniqueFilename(name, state.files.map((f) => f.name))
        const language = getLanguageFromFilename(uniqueName)
        const defaultContent = getDefaultNewFileContent(uniqueName, content)
        const toastId = toast.loading('Creating file...')

        try {
          const api = await import('./api').then(m => m.fileApi)
          const res = await api.createFile({
            filename: uniqueName,
            content: defaultContent,
            is_main: false,
            project_id: projectId,
            folder_id: folderId ? Number.parseInt(folderId, 10) : undefined,
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
              folderId: f.folder_id?.toString(),
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
            toast.success(`Created ${uniqueName}`, { id: toastId })
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
