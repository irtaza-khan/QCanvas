'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Eye, EyeOff, Github, BookOpen, Play, Moon, Sun, User, Mail, Lock } from 'lucide-react'
import toast from 'react-hot-toast'
import { useFileStore } from '@/lib/store'
import { useAuthStore } from '@/lib/authStore'
import { authApi } from '@/lib/api'
import Image from 'next/image'
import Link from 'next/link'

export default function SignupPage() {
  const router = useRouter()
  const { theme, toggleTheme } = useFileStore()
  const { isAuthenticated, setAuth, setLoading } = useAuthStore()

  const [formData, setFormData] = useState({
    fullName: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  })
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isLogoHovered, setIsLogoHovered] = useState(false)

  // Check if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/app')
    }
  }, [isAuthenticated, router])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setLoading(true)

    try {
      // Validation
      if (!formData.fullName || !formData.username || !formData.email || !formData.password || !formData.confirmPassword) {
        throw new Error('Please fill in all fields')
      }

      if (!formData.email.includes('@')) {
        throw new Error('Please enter a valid email')
      }

      if (formData.password.length < 6) {
        throw new Error('Password must be at least 6 characters')
      }

      if (formData.password !== formData.confirmPassword) {
        throw new Error('Passwords do not match')
      }

      // Call backend register API
      const response = await authApi.register({
        email: formData.email,
        username: formData.username,
        password: formData.password,
        full_name: formData.fullName,
      })

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Registration failed')
      }

      const { access_token, user } = response.data

      // Store auth data
      setAuth(user, access_token)

      // Show success message
      toast.success(`Welcome to QCanvas, ${user.full_name}!`)

      // Navigate to app
      router.push('/app')
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Registration failed')
    } finally {
      setIsLoading(false)
      setLoading(false)
    }
  }

  const handleDemoLogin = async () => {
    // Auto-submit demo credentials
    setIsLoading(true)
    setLoading(true)

    try {
      const response = await authApi.login('demo@qcanvas.dev', 'demo123')

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Demo login failed')
      }

      const { access_token, user } = response.data
      setAuth(user, access_token)

      toast.success('Logged in as Demo User!')
      toast('Demo data will be cleared on logout', { icon: 'ℹ️' })

      router.push('/app')
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Demo login failed')
    } finally {
      setIsLoading(false)
      setLoading(false)
    }
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

      <div className="w-full max-w-md relative z-10 my-8">
        {/* Logo and Header */}
        <div className="text-center mb-8">
          <div
            className="relative inline-flex items-center justify-center mb-6 group cursor-pointer"
            onMouseEnter={() => setIsLogoHovered(true)}
            onMouseLeave={() => setIsLogoHovered(false)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                setIsLogoHovered(!isLogoHovered)
              }
            }}
          >
            {/* Centered logo container */}
            <div className="relative flex items-center justify-center">
              {/* Animated container - logo moves left on hover */}
              <div className={`transition-all duration-500 ease-out ${isLogoHovered ? '-translate-x-40' : 'translate-x-0'}`}>
                {/* Light mode logo (black) */}
                <Image
                  src="/QCanvas-logo-Black.svg"
                  alt="QCanvas Logo"
                  width={80}
                  height={80}
                  className={`object-contain block dark:hidden transition-all duration-300 ${isLogoHovered ? 'scale-110 drop-shadow-lg' : 'scale-100 hover:scale-105'} animate-pulse`}
                  priority
                />

                {/* Dark mode logo (white) */}
                <Image
                  src="/QCanvas-logo-White.svg"
                  alt="QCanvas Logo"
                  width={80}
                  height={80}
                  className={`object-contain hidden dark:block transition-all duration-300 ${isLogoHovered ? 'scale-110 drop-shadow-2xl' : 'scale-100 hover:scale-105'} animate-pulse`}
                  priority
                />
              </div>

              {/* Animated text that appears on hover - centered above logo */}
              <div className={`absolute -top-16 left-1/2 transform -translate-x-1/2 transition-all duration-500 ease-out ${isLogoHovered ? 'opacity-100 translate-y-[5.5rem]' : 'opacity-0 -translate-y-4'}`}>
                <h1 className="text-4xl font-bold text-white whitespace-nowrap text-center">
                  <span className="quantum-gradient bg-clip-text text-transparent animate-pulse">
                    QCanvas
                  </span>
                </h1>
                <div className="w-24 h-0.5 bg-quantum-blue-light rounded-full animate-pulse delay-200 mx-auto mt-1"></div>
              </div>
            </div>
          </div>

          <div className={`transition-all duration-500 ${isLogoHovered ? 'opacity-0 translate-y-4' : 'opacity-100 translate-y-0'}`}>
            <h1 className="text-3xl font-bold text-white mb-2">
              Create Account
            </h1>
            <p className="text-editor-text">
              Join the Quantum Unified Simulator
            </p>
          </div>
        </div>

        {/* Signup Form */}
        <div className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl shadow-2xl border border-white/10">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Full Name Field */}
            <div>
              <label htmlFor="fullName" className="block text-sm font-medium text-editor-text mb-1.5">
                Full Name
              </label>
              <div className="relative">
                <input
                  id="fullName"
                  type="text"
                  required
                  value={formData.fullName}
                  onChange={(e) => setFormData(prev => ({ ...prev, fullName: e.target.value }))}
                  className="w-full pl-10 pr-4 py-2.5 bg-editor-bg border border-editor-border rounded-lg focus-quantum text-white placeholder-gray-400 transition-all duration-200 hover:border-quantum-blue-light"
                  placeholder="Enter your full name"
                  disabled={isLoading}
                />
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              </div>
            </div>

            {/* Username Field */}
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-editor-text mb-1.5">
                Username
              </label>
              <div className="relative">
                <input
                  id="username"
                  type="text"
                  required
                  value={formData.username}
                  onChange={(e) => setFormData(prev => ({ ...prev, username: e.target.value }))}
                  className="w-full pl-10 pr-4 py-2.5 bg-editor-bg border border-editor-border rounded-lg focus-quantum text-white placeholder-gray-400 transition-all duration-200 hover:border-quantum-blue-light"
                  placeholder="Enter username"
                  disabled={isLoading}
                />
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              </div>
            </div>

            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-editor-text mb-1.5">
                Email Address
              </label>
              <div className="relative">
                <input
                  id="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                  className="w-full pl-10 pr-4 py-2.5 bg-editor-bg border border-editor-border rounded-lg focus-quantum text-white placeholder-gray-400 transition-all duration-200 hover:border-quantum-blue-light"
                  placeholder="Enter your email address"
                  disabled={isLoading}
                />
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-editor-text mb-1.5">
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                  className="w-full pl-10 pr-12 py-2.5 bg-editor-bg border border-editor-border rounded-lg focus-quantum text-white placeholder-gray-400 transition-all duration-200 hover:border-quantum-blue-light"
                  placeholder="Create a password"
                  disabled={isLoading}
                />
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 flex items-center px-3 text-editor-text hover:text-white transition-colors"
                  disabled={isLoading}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Confirm Password Field */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-editor-text mb-1.5">
                Confirm Password
              </label>
              <div className="relative">
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                  className="w-full pl-10 pr-12 py-2.5 bg-editor-bg border border-editor-border rounded-lg focus-quantum text-white placeholder-gray-400 transition-all duration-200 hover:border-quantum-blue-light"
                  placeholder="Confirm your password"
                  disabled={isLoading}
                />
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 flex items-center px-3 text-editor-text hover:text-white transition-colors"
                  disabled={isLoading}
                >
                  {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-quantum disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center py-3 text-lg font-semibold mt-2"
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full spinner mr-2"></div>
                  Creating Account...
                </>
              ) : (
                'Sign Up'
              )}
            </button>
          </form>

          {/* Login Link */}
          <div className="mt-6 pt-6 border-t border-editor-border text-center">
            <p className="text-sm text-editor-text">
              Already have an account?{' '}
              <Link href="/login" className="text-blue-400 hover:text-blue-300 font-medium transition-colors">
                Sign In
              </Link>
            </p>
          </div>

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
        </div>
      </div>
    </div>
  )
}
