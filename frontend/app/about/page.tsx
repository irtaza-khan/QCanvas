'use client'

import { ArrowLeft, Zap, Code, Cpu, BarChart3, Users, Github, Mail, Globe, BookOpen, Moon, Sun } from 'lucide-react'
import Link from 'next/link'
import { useFileStore } from '@/lib/store'

export default function AboutPage() {
  const { theme, toggleTheme } = useFileStore()
  return (
    <div className="min-h-screen bg-gradient-to-br from-editor-bg via-gray-900 to-editor-bg overflow-x-hidden">
      {/* Header */}
      <div className="relative overflow-hidden">
        <div className="absolute inset-0">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-quantum-blue-light opacity-10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500 opacity-10 rounded-full blur-3xl animate-pulse delay-1000"></div>
        </div>
        
        <div className="relative z-10 px-4 py-8">
          <Link 
            href="/login" 
            className="inline-flex items-center text-editor-text hover:text-white transition-colors mb-8"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Login
          </Link>
          
          <div className="text-center mb-12">
            <div className="inline-flex items-center justify-center w-24 h-24 rounded-full quantum-gradient mb-6 shadow-2xl">
              <Zap className="w-12 h-12 text-white" />
            </div>
            <h1 className="text-5xl font-bold text-white mb-4">
              About <span className="quantum-gradient bg-clip-text text-transparent">QCanvas</span>
            </h1>
            <div className="flex justify-center mb-4">
              <button onClick={toggleTheme} className="btn-ghost p-2 hover:bg-quantum-blue-light/20 rounded-lg" title="Toggle theme">
                {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>
            </div>
            <p className="text-xl text-editor-text max-w-3xl mx-auto">
              A modern quantum computing platform that bridges the gap between different quantum frameworks, 
              enabling seamless conversion, simulation, and visualization of quantum circuits.
            </p>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <main className="px-4 py-16">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">Key Features</h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Framework Conversion */}
            <div className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10 hover:border-quantum-blue-light transition-all duration-300">
              <div className="w-16 h-16 quantum-gradient rounded-xl flex items-center justify-center mb-6">
                <Code className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Framework Conversion</h3>
              <p className="text-editor-text">
                Convert quantum circuits between Qiskit, Cirq, and PennyLane with automatic optimization 
                and OpenQASM 3.0 generation.
              </p>
            </div>

            {/* Quantum Simulation */}
            <div className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10 hover:border-quantum-blue-light transition-all duration-300">
              <div className="w-16 h-16 quantum-gradient rounded-xl flex items-center justify-center mb-6">
                <Cpu className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Quantum Simulation</h3>
              <p className="text-editor-text">
                Run quantum circuits on multiple backends including statevector, density matrix, 
                and stabilizer simulations with noise modeling.
              </p>
            </div>

            {/* Real-time Visualization */}
            <div className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10 hover:border-quantum-blue-light transition-all duration-300">
              <div className="w-16 h-16 quantum-gradient rounded-xl flex items-center justify-center mb-6">
                <BarChart3 className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Real-time Visualization</h3>
              <p className="text-editor-text">
                Visualize quantum circuits, measurement results, and state vectors with 
                interactive charts and diagrams.
              </p>
            </div>

            {/* Multi-language Support */}
            <div className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10 hover:border-quantum-blue-light transition-all duration-300">
              <div className="w-16 h-16 quantum-gradient rounded-xl flex items-center justify-center mb-6">
                <Globe className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Multi-language Support</h3>
              <p className="text-editor-text">
                Support for Python quantum computing frameworks including Qiskit, Cirq, 
                PennyLane, and Amazon Braket.
              </p>
            </div>

            {/* Advanced Optimization */}
            <div className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10 hover:border-quantum-blue-light transition-all duration-300">
              <div className="w-16 h-16 quantum-gradient rounded-xl flex items-center justify-center mb-6">
                <Zap className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Advanced Optimization</h3>
              <p className="text-editor-text">
                Circuit optimization with gate fusion, dead code elimination, and 
                custom optimization algorithms for better performance.
              </p>
            </div>

            {/* Collaborative Features */}
            <div className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10 hover:border-quantum-blue-light transition-all duration-300">
              <div className="w-16 h-16 quantum-gradient rounded-xl flex items-center justify-center mb-6">
                <Users className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4">Collaborative Features</h3>
              <p className="text-editor-text">
                Share circuits, collaborate on projects, and access a library of 
                pre-built quantum algorithms and examples.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Technology Stack */}
      <div className="px-4 py-16 bg-black/20">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">Technology Stack</h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="w-20 h-20 quantum-gradient rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-lg">Next.js</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Frontend</h3>
              <p className="text-editor-text text-sm">React-based UI with TypeScript</p>
            </div>
            
            <div className="text-center">
              <div className="w-20 h-20 quantum-gradient rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-lg">FastAPI</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Backend</h3>
              <p className="text-editor-text text-sm">Python API with async support</p>
            </div>
            
            <div className="text-center">
              <div className="w-20 h-20 quantum-gradient rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-lg">QASM</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Quantum</h3>
              <p className="text-editor-text text-sm">OpenQASM 3.0 standard</p>
            </div>
            
            <div className="text-center">
              <div className="w-20 h-20 quantum-gradient rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-white font-bold text-lg">Docker</span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Deployment</h3>
              <p className="text-editor-text text-sm">Containerized architecture</p>
            </div>
          </div>
        </div>
      </div>

      {/* Team Section */}
      <div className="px-4 py-16">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">Our Team</h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10 text-center">
              <div className="w-24 h-24 quantum-gradient rounded-full flex items-center justify-center mx-auto mb-6">
                <Users className="w-12 h-12 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Development Team</h3>
              <p className="text-editor-text mb-4">
                Passionate developers working on quantum computing tools and education.
              </p>
              <div className="flex justify-center space-x-4">
                <a href="https://github.com" className="text-editor-text hover:text-white transition-colors">
                  <Github className="w-5 h-5" />
                </a>
                <a href="mailto:team@qcanvas.dev" className="text-editor-text hover:text-white transition-colors">
                  <Mail className="w-5 h-5" />
                </a>
              </div>
            </div>

            <div className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10 text-center">
              <div className="w-24 h-24 quantum-gradient rounded-full flex items-center justify-center mx-auto mb-6">
                <BookOpen className="w-12 h-12 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Research Team</h3>
              <p className="text-editor-text mb-4">
                Quantum computing researchers and educators advancing the field.
              </p>
              <div className="flex justify-center space-x-4">
                <a href="https://github.com" className="text-editor-text hover:text-white transition-colors">
                  <Github className="w-5 h-5" />
                </a>
                <a href="mailto:research@qcanvas.dev" className="text-editor-text hover:text-white transition-colors">
                  <Mail className="w-5 h-5" />
                </a>
              </div>
            </div>

            <div className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10 text-center">
              <div className="w-24 h-24 quantum-gradient rounded-full flex items-center justify-center mx-auto mb-6">
                <Globe className="w-12 h-12 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-2">Community</h3>
              <p className="text-editor-text mb-4">
                Open source contributors and quantum computing enthusiasts worldwide.
              </p>
              <div className="flex justify-center space-x-4">
                <a href="https://github.com" className="text-editor-text hover:text-white transition-colors">
                  <Github className="w-5 h-5" />
                </a>
                <a href="mailto:community@qcanvas.dev" className="text-editor-text hover:text-white transition-colors">
                  <Mail className="w-5 h-5" />
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="px-4 py-8 border-t border-editor-border">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-editor-text">
            © 2024 QCanvas. Built with ❤️ for the quantum computing community.
          </p>
          <div className="flex justify-center space-x-6 mt-4">
            <a href="mailto:team@qcanvas.dev" className="text-editor-text hover:text-white transition-colors">
              Contact Team
            </a>
            <a href="mailto:research@qcanvas.dev" className="text-editor-text hover:text-white transition-colors">
              Research
            </a>
            <a href="https://github.com" className="text-editor-text hover:text-white transition-colors">
              GitHub
            </a>
            <a href="mailto:community@qcanvas.dev" className="text-editor-text hover:text-white transition-colors">
              Community
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
