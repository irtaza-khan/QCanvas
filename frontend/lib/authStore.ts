import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
    id: string
    email: string
    username: string
    full_name: string
    role: 'user' | 'admin' | 'demo'
    is_active: boolean
    is_verified: boolean
    created_at: string
    last_login_at: string | null
}

interface AuthState {
    user: User | null
    token: string | null
    isAuthenticated: boolean
    isLoading: boolean

    // Actions
    setAuth: (user: User, token: string) => void
    clearAuth: () => void
    setLoading: (loading: boolean) => void
    updateUser: (user: Partial<User>) => void
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set, get) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,

            setAuth: (user, token) => {
                set({
                    user,
                    token,
                    isAuthenticated: true,
                    isLoading: false
                })
            },

            clearAuth: () => {
                const currentUser = get().user

                // If demo user, clear all localStorage
                if (currentUser?.role === 'demo') {
                    if (typeof window !== 'undefined') {
                        // Clear all QCanvas data
                        Object.keys(localStorage).forEach(key => {
                            if (key.startsWith('qcanvas-')) {
                                localStorage.removeItem(key)
                            }
                        })
                        console.log('[Auth] Demo account data cleared')
                    }
                }

                set({
                    user: null,
                    token: null,
                    isAuthenticated: false,
                    isLoading: false
                })
            },

            setLoading: (loading) => {
                set({ isLoading: loading })
            },

            updateUser: (updates) => {
                set((state) => ({
                    user: state.user ? { ...state.user, ...updates } : null
                }))
            },
        }),
        {
            name: 'qcanvas-auth',
            // Only persist user and token, not loading state
            partialize: (state) => ({
                user: state.user,
                token: state.token,
                isAuthenticated: state.isAuthenticated,
            }),
        }
    )
)
