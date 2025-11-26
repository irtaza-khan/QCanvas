import { File, ApiResponse, CreateFileRequest, UpdateFileRequest } from '@/types'

// =============================================================================
// API BASE CONFIGURATION
// =============================================================================
// Backend counterpart: config/config.py -> DISABLE_REMOTE_API_FALLBACK
// Keep these in sync manually.
//
// When DISABLE_REMOTE_FALLBACK is true:
//   - Only use the local backend (http://127.0.0.1:8000)
//   - Do NOT fall back to Railway/production URL
// When false:
//   - Fall back to NEXT_PUBLIC_API_BASE/Railway when local is unavailable

const DISABLE_REMOTE_FALLBACK =
  process.env.NEXT_PUBLIC_DISABLE_REMOTE_FALLBACK === 'true' || true

let cachedApiBase: string | null = null

async function getApiBase(): Promise<string> {
  if (cachedApiBase) return cachedApiBase

  const localUrl = 'http://127.0.0.1:8000'
  const railwayUrl = process.env.NEXT_PUBLIC_API_BASE || 'https://qcanvas-nextjs-production.up.railway.app'

  // Always prefer local when available
  try {
    const response = await fetch(`${localUrl}/api/health`, { method: 'GET' })
    if (response.ok) {
      cachedApiBase = localUrl
      console.log('[API] Using local backend:', localUrl)
      return localUrl
    }
  } catch (error) {
    console.log('[API] Local backend not reachable')
  }

  // If remote fallback is disabled, always return local URL
  if (DISABLE_REMOTE_FALLBACK) {
    cachedApiBase = localUrl
    console.warn('[API] Remote fallback disabled, forcing local backend even if unreachable')
    return localUrl
  }

  // Remote fallback enabled: use Railway/production URL
  cachedApiBase = railwayUrl
  console.log('[API] Falling back to remote backend:', railwayUrl)
  return railwayUrl
}

// Generic API helper
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const API_BASE = await getApiBase()
    const url = `${API_BASE}${endpoint}`
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    // Try to parse response body even if status is not ok
    let data: any
    try {
      data = await response.json()
    } catch (e) {
      // If response is not JSON, use status text
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status} ${response.statusText}`)
      }
      throw new Error('Invalid JSON response')
    }

    // If response is not ok, check if we have error details in the body
    if (!response.ok) {
      // Check if the response body has error information
      const errorMsg = data?.error || data?.detail || data?.message || `HTTP error! status: ${response.status}`
      return {
        error: errorMsg,
        success: false,
        data: data, // Include the full response data in case it has useful info
      }
    }

    return { data, success: true }
  } catch (error) {
    console.error('API request failed:', error)
    return {
      error: error instanceof Error ? error.message : 'Unknown error',
      success: false,
    }
  }
}

// File API functions
export const fileApi = {
  // Get all files
  async getFiles(): Promise<ApiResponse<File[]>> {
    return apiRequest<File[]>('/api/files')
  },

  // Get specific file
  async getFile(id: string): Promise<ApiResponse<File>> {
    return apiRequest<File>(`/api/files/${id}`)
  },

  // Create new file
  async createFile(data: CreateFileRequest): Promise<ApiResponse<File>> {
    return apiRequest<File>('/api/files', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },

  // Update file
  async updateFile(id: string, data: UpdateFileRequest): Promise<ApiResponse<File>> {
    return apiRequest<File>(`/api/files/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },

  // Delete file
  async deleteFile(id: string): Promise<ApiResponse<{ success: boolean }>> {
    return apiRequest<{ success: boolean }>(`/api/files/${id}`, {
      method: 'DELETE',
    })
  },
}

// Health check
export async function healthCheck(): Promise<ApiResponse<{ ok: boolean }>> {
  return apiRequest<{ ok: boolean }>('/api/health')
}

// Quantum conversion API - connects to FastAPI backend
export const quantumApi = {
  // Convert quantum code to OpenQASM
  async convertToQasm(code: string, framework: string, style: 'classic' | 'compact' = 'classic'): Promise<ApiResponse<any>> {
    return apiRequest('/api/converter/convert', {
      method: 'POST',
      body: JSON.stringify({
        code,
        framework,
        qasm_version: '3.0',
        style,
      }),
    })
  },

  // Validate quantum code syntax
  async validateCode(code: string, framework: string): Promise<ApiResponse<any>> {
    return apiRequest('/api/converter/validate', {
      method: 'POST',
      body: JSON.stringify({
        code,
        framework,
      }),
    })
  },

  // Get supported frameworks
  async getSupportedFrameworks(): Promise<ApiResponse<string[]>> {
    return apiRequest('/api/converter/frameworks')
  },

  // Execute quantum code (legacy - for frontend server)
  async executeCode(code: string, framework: string, shots = 1024): Promise<ApiResponse<any>> {
    return apiRequest('/api/quantum/execute', {
      method: 'POST',
      body: JSON.stringify({
        code,
        framework,
        shots,
        backend: 'qasm_simulator',
      }),
    })
  },

  // Execute OpenQASM code via FastAPI backend (legacy)
  async executeQasm(qasm_code: string, backend = 'statevector', shots = 1024): Promise<ApiResponse<any>> {
    return apiRequest('/api/simulator/execute', {
      method: 'POST',
      body: JSON.stringify({
        qasm_code,
        backend,
        shots,
      }),
    })
  },

  // Execute OpenQASM code with QSim backend
  async executeQasmWithQSim(qasm_code: string, backend: 'cirq' | 'qiskit' | 'pennylane' = 'cirq', shots = 1024): Promise<ApiResponse<any>> {
    return apiRequest('/api/simulator/execute-qsim', {
      method: 'POST',
      body: JSON.stringify({
        qasm_input: qasm_code,
        backend,
        shots,
      }),
    })
  },

  // Get available backends
  async getAvailableBackends(): Promise<ApiResponse<any>> {
    return apiRequest('/api/simulator/backends')
  },

  // Execute hybrid Python code with qcanvas/qsim
  async executeHybrid(
    code: string, 
    framework?: string,
    timeout?: number
  ): Promise<ApiResponse<HybridExecuteResult>> {
    return apiRequest('/api/hybrid/execute', {
      method: 'POST',
      body: JSON.stringify({
        code,
        framework,
        timeout: timeout ?? 30,
      }),
    })
  },

  // Validate hybrid code without executing
  async validateHybrid(code: string): Promise<ApiResponse<HybridValidateResult>> {
    return apiRequest('/api/hybrid/validate', {
      method: 'POST',
      body: JSON.stringify({ code }),
    })
  },

  // Get hybrid execution status/configuration
  async getHybridStatus(): Promise<ApiResponse<HybridStatusResult>> {
    return apiRequest('/api/hybrid/status')
  },
}

// Hybrid execution result types
export interface HybridExecuteResult {
  success: boolean
  stdout: string
  stderr: string
  qasm_generated?: string | null
  simulation_results: HybridSimulationResult[]
  execution_time: string
  error?: string | null
  error_line?: number | null
  error_type?: string | null
}

export interface HybridSimulationResult {
  counts: { [state: string]: number }
  probabilities: { [state: string]: number }
  shots: number
  backend: string
  execution_time: string
  n_qubits: number
  metadata: { [key: string]: any }
}

export interface HybridValidateResult {
  valid: boolean
  errors?: string[] | null
  warnings?: string[] | null
}

export interface HybridStatusResult {
  enabled: boolean
  sandbox_available: boolean
  security_settings: {
    block_dangerous_imports: boolean
    block_file_access: boolean
    block_network: boolean
    block_shell: boolean
    restrict_builtins: boolean
    block_code_execution: boolean
  }
  limits: {
    max_execution_time: number
    max_memory_mb: number
    max_simulation_runs: number
  }
  allowed_modules: string[]
}

// Auth API (for future use)
export const authApi = {
  async login(email: string, password: string): Promise<ApiResponse<{ token: string }>> {
    return apiRequest('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
  },

  async logout(): Promise<ApiResponse<{ success: boolean }>> {
    return apiRequest('/api/auth/logout', {
      method: 'POST',
    })
  },

  async me(): Promise<ApiResponse<any>> {
    return apiRequest('/api/auth/me')
  },
}
