export interface File {
  id: string;
  name: string;
  content: string;
  language: string;
  createdAt: string;
  updatedAt: string;
  size: number;
  projectId?: string;
  isShared?: boolean;
  userId?: string;
}

export interface Project {
  id: string;
  name: string;
  description?: string;
  files: File[];
  createdAt: string;
  updatedAt: string;
}

// Quantum Execution Types
export interface Run {
  id: string;
  fileId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime: string;
  endTime?: string;
  duration?: number;
  output?: string;
  error?: string;
  framework: 'qiskit' | 'cirq' | 'pennylane' | 'qasm';
  backend: string;
  shots: number;
  results?: QuantumResults;
}

export interface QuantumResults {
  counts: Record<string, number>;
  shots: number;
  backend: string;
  execution_time: string;
  success: boolean;
  circuit_info?: {
    depth: number;
    qubits: number;
    gates?: number;
  };
}

// UI State Types
export interface EditorState {
  activeFileId: string | null;
  files: File[];
  theme: 'light' | 'dark';
  sidebarCollapsed: boolean;
  resultsCollapsed: boolean;
  compiledQasm: string | null;
  compileOptions: CompileOptions;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  success: boolean;
}

// File Operations
export interface CreateFileRequest {
  filename: string;
  content: string;
  is_main?: boolean;
  project_id?: number;
  is_shared?: boolean;
}

export interface UpdateFileRequest {
  filename?: string;
  content?: string;
  is_main?: boolean;
  project_id?: number;
  is_shared?: boolean;
}

// Authentication Types (for future use)
export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Supported Languages
export type SupportedLanguage =
  | 'python'
  | 'qasm'
  | 'javascript'
  | 'typescript'
  | 'plaintext'
  | 'json';

// Compile / Simulation Options
export type InputLanguage = 'qiskit' | 'cirq' | 'pennylane' | 'qasm';
export type ResultFormat = 'json' | 'histogram' | 'text';

export interface CompileOptions {
  inputLanguage: InputLanguage;
  resultFormat: ResultFormat;
  qasmVersion: '3.0';
  style?: 'classic' | 'compact';
}

// File Extensions Mapping
export const LANGUAGE_EXTENSIONS: Record<SupportedLanguage, string[]> = {
  python: ['.py', '.pyw'],
  qasm: ['.qasm', '.qc'],
  javascript: ['.js', '.mjs'],
  typescript: ['.ts'],
  plaintext: ['.txt'],
  json: ['.json'],
};

// Default File Templates
export const FILE_TEMPLATES: Record<SupportedLanguage, string> = {
  python: `# Quantum circuit in Python
from qiskit import QuantumCircuit, execute, Aer

# Create quantum circuit
qc = QuantumCircuit(2, 2)
qc.h(0)  # Hadamard gate
qc.cx(0, 1)  # CNOT gate
qc.measure_all()

# Execute circuit
backend = Aer.get_backend('qasm_simulator')
job = execute(qc, backend, shots=1024)
result = job.result()
counts = result.get_counts(qc)
print(counts)
`,
  qasm: `// Quantum circuit in OpenQASM
OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] c;

h q[0];
cx q[0], q[1];
c = measure q;
`,
  javascript: `// Quantum circuit simulation
console.log("Quantum JavaScript simulation");
`,
  typescript: `// Quantum circuit simulation
interface QuantumState {
  qubits: number;
  amplitude: number[];
}

console.log("Quantum TypeScript simulation");
`,
  plaintext: `// Write your quantum code here
`,
  json: `{
  "quantum_circuit": {
    "qubits": 2,
    "gates": [],
    "measurements": []
  }
}
`,
};
