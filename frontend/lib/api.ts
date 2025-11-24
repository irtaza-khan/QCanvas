import { File, ApiResponse, CreateFileRequest, UpdateFileRequest } from '@/types'

// const API_BASE = "http://127.0.0.1:8000"
const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'https://qcanvas-nextjs-production.up.railway.app'

let cachedApiBase: string | null = null

async function getApiBase(): Promise<string> {
  if (cachedApiBase) return cachedApiBase

  const localUrl = 'http://127.0.0.1:8000'
  const railwayUrl = process.env.NEXT_PUBLIC_API_BASE || 'https://qcanvas-nextjs-production.up.railway.app'

  try {
    const response = await fetch(`${localUrl}/api/health`, { method: 'GET' })
    if (response.ok) {
      cachedApiBase = localUrl
      return localUrl
    }
  } catch (error) {
    // Local backend not available
  }

  cachedApiBase = railwayUrl
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
