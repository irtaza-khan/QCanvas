'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Eye, EyeOff, Zap, Github, BookOpen, Play, Moon, Sun } from 'lucide-react'
import toast from 'react-hot-toast'
import { useFileStore } from '@/lib/store'
import Image from 'next/image'

export default function LoginPage() {
  const router = useRouter()
  const { theme, toggleTheme } = useFileStore()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  })
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  // Check if already authenticated
  useEffect(() => {
    const authStatus = localStorage.getItem('qcanvas-auth')
    if (authStatus) {
      router.push('/app')
    }
  }, [router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000))

      // Basic validation
      if (!formData.email || !formData.password) {
        throw new Error('Please fill in all fields')
      }

      if (!formData.email.includes('@')) {
        throw new Error('Please enter a valid email')
      }

      if (formData.password.length < 6) {
        throw new Error('Password must be at least 6 characters')
      }

      // Mock successful login
      localStorage.setItem('qcanvas-auth', JSON.stringify({
        email: formData.email,
        loginTime: new Date().toISOString(),
      }))

      toast.success('Login successful!')
      router.push('/app')
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Login failed')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDemoLogin = () => {
    setFormData({
      email: 'demo@qcanvas.dev',
      password: 'demo123',
    })
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-editor-bg via-gray-900 to-editor-bg p-4 relative overflow-auto">
      {/* Theme Toggle Button */}
      <div className="absolute top-4 right-4 z-20">
        <button 
          onClick={toggleTheme} 
          className="btn-ghost p-3 hover:bg-quantum-blue-light/20 rounded-lg" 
          title="Toggle theme"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
      </div>

      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-quantum-blue-light opacity-10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500 opacity-10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-teal-500 opacity-5 rounded-full blur-3xl animate-pulse delay-500"></div>
      </div>

      <div className="w-full max-w-md relative z-10">
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full quantum-gradient mb-6 shadow-2xl overflow-hidden">
            <Image
              src="/mylogo.svg"
              alt="App Logo"
              width={64}
              height={64}
              className="object-contain"
              priority
            />
          </div>
          <h1 className="text-4xl font-bold text-white mb-3">
            Welcome to <span className="quantum-gradient bg-clip-text text-transparent">QCanvas</span>
          </h1>
          <p className="text-editor-text text-lg">
            Quantum Code Editor & Simulation Platform
          </p>
          <p className="text-gray-400 text-sm mt-2">
            Convert, simulate, and visualize quantum circuits
          </p>
        </div>

        {/* Login Form */}
        <div className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl shadow-2xl border border-white/10">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-editor-text mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                className="w-full px-4 py-3 bg-editor-bg border border-editor-border rounded-lg focus-quantum text-white placeholder-gray-400 transition-all duration-200 hover:border-quantum-blue-light"
                placeholder="Enter your email"
                disabled={isLoading}
              />
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-editor-text mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                  className="w-full px-4 py-3 bg-editor-bg border border-editor-border rounded-lg focus-quantum text-white placeholder-gray-400 pr-12 transition-all duration-200 hover:border-quantum-blue-light"
                  placeholder="Enter your password"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 flex items-center px-3 text-editor-text hover:text-white transition-colors"
                  disabled={isLoading}
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-quantum disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center py-3 text-lg font-semibold"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full spinner mr-2"></div>
                  Signing In...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Demo Login */}
          <div className="mt-6 pt-6 border-t border-editor-border">
            <p className="text-sm text-editor-text text-center mb-3">
              Want to try without signing up?
            </p>
            <button
              onClick={handleDemoLogin}
              disabled={isLoading}
              className="w-full btn-ghost flex items-center justify-center py-3"
            >
              <Play className="w-4 h-4 mr-2" />
              Use Demo Account
            </button>
          </div>

          {/* Quick Links */}
          <div className="mt-6 pt-6 border-t border-editor-border">
            <div className="flex justify-center space-x-4">
              <a 
                href="/about" 
                className="flex items-center text-sm text-editor-text hover:text-white transition-colors"
              >
                <BookOpen className="w-4 h-4 mr-1" />
                About
              </a>
              <a 
                href="/examples" 
                className="flex items-center text-sm text-editor-text hover:text-white transition-colors"
              >
                <Play className="w-4 h-4 mr-1" />
                Examples
              </a>
              <a 
                href="https://github.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center text-sm text-editor-text hover:text-white transition-colors"
              >
                <Github className="w-4 h-4 mr-1" />
                GitHub
              </a>
            </div>
          </div>

          {/* Footer */}
          <div className="mt-6 text-center">
            <p className="text-xs text-gray-500">
              This is a demo authentication system.
              <br />
              Use any email and password (6+ characters).
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
