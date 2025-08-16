import { File, ApiResponse, CreateFileRequest, UpdateFileRequest } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || ''

// Generic API helper
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const url = `${API_BASE}${endpoint}`
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
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

// Quantum execution API (for future use)
export const quantumApi = {
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
