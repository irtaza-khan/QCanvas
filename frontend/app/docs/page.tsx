'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import {
  Moon, Sun, Menu, X, BookOpen, Code, Cpu, BarChart3, Zap, Settings, Play,
  ChevronRight, Star, Atom, Sparkles, Lightbulb,
  ArrowRight, CheckCircle, Info, Database,
  Layers, Terminal, FileText, Shield, Cloud, Server,
  Monitor, Wrench, Target, Rocket, Clock, TrendingUp, GitBranch
} from 'lucide-react'
import { useFileStore } from '@/lib/store'
import { config, getCopyrightText } from '@/lib/config'

interface DocSection {
  id: string
  title: string
  subtitle?: string
  icon: React.ReactNode
  badge?: string
  content: React.ReactNode
  category?: string
}

export default function DocsPage() {
  const [activeSection, setActiveSection] = useState('overview')
  const [isVisible, setIsVisible] = useState(false)
  const { theme, toggleTheme } = useFileStore()
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [scrollY, setScrollY] = useState(0)

  useEffect(() => {
    setIsVisible(true)
    const handleScroll = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' })
      setActiveSection(sectionId)
    }
    setIsMenuOpen(false)
  }

  const sections: DocSection[] = [
    {
      id: 'overview',
      title: 'Overview',
      subtitle: 'Introduction to QCanvas',
      icon: <Info className="w-5 h-5" />,
      badge: 'Essential',
      category: 'Getting Started',
      content: (
        <div className="space-y-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-20 h-20 rounded-full quantum-gradient mb-6 shadow-2xl">
              <Atom className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              <span className="quantum-gradient bg-clip-text text-transparent">Welcome to QCanvas</span>
            </h2>
            <p className="text-xl text-editor-text max-w-3xl mx-auto leading-relaxed">
              {config.project.description}
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="quantum-glass-dark rounded-xl p-6 text-center hover-lift">
              <div className="w-12 h-12 quantum-gradient rounded-lg flex items-center justify-center mx-auto mb-4">
                <Code className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Framework Conversion</h3>
              <p className="text-editor-text text-sm">Convert between Qiskit, Cirq, and PennyLane seamlessly</p>
            </div>
            <div className="quantum-glass-dark rounded-xl p-6 text-center hover-lift">
              <div className="w-12 h-12 quantum-gradient rounded-lg flex items-center justify-center mx-auto mb-4">
                <Play className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Real-time Simulation</h3>
              <p className="text-editor-text text-sm">Execute quantum circuits with multiple backends</p>
            </div>
            <div className="quantum-glass-dark rounded-xl p-6 text-center hover-lift">
              <div className="w-12 h-12 quantum-gradient rounded-lg flex items-center justify-center mx-auto mb-4">
                <BarChart3 className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Interactive Visualization</h3>
              <p className="text-editor-text text-sm">Visualize quantum states and measurement results</p>
            </div>
            <div className="quantum-glass-dark rounded-xl p-6 text-center hover-lift">
              <div className="w-12 h-12 quantum-gradient rounded-lg flex items-center justify-center mx-auto mb-4">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Educational Platform</h3>
              <p className="text-editor-text text-sm">Learn quantum computing through guided examples</p>
            </div>
          </div>

          <div className="quantum-glass-dark rounded-xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
              <Rocket className="w-6 h-6 mr-3 text-quantum-blue-light" />
              Project Mission
            </h3>
            <p className="text-editor-text text-lg leading-relaxed mb-6">
              QCanvas addresses the critical standardization gap in multi-framework quantum programming by providing a universal intermediary that translates quantum circuits into the standardized OpenQASM 3.0 intermediate representation. This enables seamless integration, comparison, and execution of quantum circuits across different hardware platforms and software ecosystems.
            </p>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold quantum-gradient bg-clip-text text-transparent mb-2">Unification</div>
                <p className="text-editor-text text-sm">Bridge the gap between quantum frameworks</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold quantum-gradient bg-clip-text text-transparent mb-2">Accessibility</div>
                <p className="text-editor-text text-sm">Make quantum computing approachable for all</p>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold quantum-gradient bg-clip-text text-transparent mb-2">Innovation</div>
                <p className="text-editor-text text-sm">Accelerate quantum software development</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'getting-started',
      title: 'Getting Started',
      subtitle: 'Quick start guide',
      icon: <Play className="w-5 h-5" />,
      badge: 'Beginner',
      category: 'Getting Started',
      content: (
        <div className="space-y-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full quantum-gradient mb-6 shadow-xl">
              <Play className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-3xl font-bold mb-4">
              <span className="quantum-gradient bg-clip-text text-transparent">Your First Steps</span>
            </h2>
            <p className="text-lg text-editor-text max-w-2xl mx-auto">
              Get up and running with QCanvas in minutes. Learn the basics and start building quantum circuits.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="quantum-glass-dark rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                <Target className="w-5 h-5 mr-2 text-quantum-blue-light" />
                Quick Start Guide
              </h3>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-quantum-blue-light/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-sm font-bold text-quantum-blue-light">1</span>
                  </div>
                  <div>
                    <h4 className="text-white font-medium mb-1">Access QCanvas</h4>
                    <p className="text-editor-text text-sm">Navigate to the web application and create your account</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-sm font-bold text-purple-400">2</span>
                  </div>
                  <div>
                    <h4 className="text-white font-medium mb-1">Choose Framework</h4>
                    <p className="text-editor-text text-sm">Select your preferred quantum framework (Qiskit, Cirq, PennyLane)</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-teal-500/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-sm font-bold text-teal-400">3</span>
                  </div>
                  <div>
                    <h4 className="text-white font-medium mb-1">Create Circuit</h4>
                    <p className="text-editor-text text-sm">Write or paste your quantum circuit code</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-sm font-bold text-green-400">4</span>
                  </div>
                  <div>
                    <h4 className="text-white font-medium mb-1">Convert & Simulate</h4>
                    <p className="text-editor-text text-sm">Convert between frameworks and run simulations</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="quantum-glass-dark rounded-xl p-6">
              <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
                <Lightbulb className="w-5 h-5 mr-2 text-yellow-400" />
                First Example
              </h3>
              <div className="bg-editor-bg rounded-lg p-4 border border-editor-border mb-4">
                <h4 className="text-white font-medium mb-3">Bell State Circuit</h4>
                <pre className="text-xs text-editor-text overflow-x-auto">
{`# Qiskit Bell State
from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)
qc.h(0)      # Hadamard on qubit 0
qc.cx(0, 1)  # CNOT gate
qc.measure_all()

print(qc)`}
                </pre>
              </div>
              <p className="text-editor-text text-sm">
                This creates a quantum entanglement between two qubits, producing the famous Bell state |Φ⁺⟩ = (|00⟩ + |11⟩)/√2
              </p>
            </div>
          </div>

          <div className="quantum-glass-dark rounded-xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6">Supported Frameworks</h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center group hover:scale-105 transition-transform duration-300">
                <div className="w-16 h-16 bg-blue-500/20 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:bg-blue-500/30 transition-colors duration-300">
                  <Code className="w-8 h-8 text-blue-400" />
                </div>
                <h4 className="text-xl font-semibold text-white mb-2">Qiskit</h4>
                <p className="text-editor-text text-sm mb-3">IBM&apos;s comprehensive quantum computing framework</p>
                <div className="flex flex-wrap justify-center gap-2">
                  <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">Circuit Design</span>
                  <span className="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full">IBM Quantum</span>
                </div>
              </div>
              <div className="text-center group hover:scale-105 transition-transform duration-300">
                <div className="w-16 h-16 bg-purple-500/20 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:bg-purple-500/30 transition-colors duration-300">
                  <Code className="w-8 h-8 text-purple-400" />
                </div>
                <h4 className="text-xl font-semibold text-white mb-2">Cirq</h4>
                <p className="text-editor-text text-sm mb-3">Google&apos;s framework for near-term quantum devices</p>
                <div className="flex flex-wrap justify-center gap-2">
                  <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded-full">Noise Modeling</span>
                  <span className="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded-full">Google AI</span>
                </div>
              </div>
              <div className="text-center group hover:scale-105 transition-transform duration-300">
                <div className="w-16 h-16 bg-green-500/20 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:bg-green-500/30 transition-colors duration-300">
                  <Code className="w-8 h-8 text-green-400" />
                </div>
                <h4 className="text-xl font-semibold text-white mb-2">PennyLane</h4>
                <p className="text-editor-text text-sm mb-3">Xanadu&apos;s quantum machine learning framework</p>
                <div className="flex flex-wrap justify-center gap-2">
                  <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">ML Integration</span>
                  <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full">Variational</span>
                </div>
              </div>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="quantum-glass-dark rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-green-400" />
                Learning Path
              </h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Basic quantum gates and circuits</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Framework conversion concepts</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Clock className="w-4 h-4 text-yellow-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Advanced algorithms and optimization</span>
                </div>
                <div className="flex items-center space-x-3">
                  <Clock className="w-4 h-4 text-yellow-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Noise modeling and error correction</span>
                </div>
              </div>
            </div>

            <div className="quantum-glass-dark rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <Wrench className="w-5 h-5 mr-2 text-orange-400" />
                Resources
              </h3>
              <div className="space-y-3">
                <Link href="/examples" className="flex items-center space-x-3 text-editor-text hover:text-white transition-colors group">
                  <Play className="w-4 h-4 group-hover:text-quantum-blue-light" />
                  <span className="text-sm">Interactive Examples</span>
                  <ChevronRight className="w-4 h-4 ml-auto group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link href="/docs" className="flex items-center space-x-3 text-editor-text hover:text-white transition-colors group">
                  <FileText className="w-4 h-4 group-hover:text-quantum-blue-light" />
                  <span className="text-sm">Complete Documentation</span>
                  <ChevronRight className="w-4 h-4 ml-auto group-hover:translate-x-1 transition-transform" />
                </Link>
                <a href={config.social.github} target="_blank" rel="noopener noreferrer" className="flex items-center space-x-3 text-editor-text hover:text-white transition-colors group">
                  <GitBranch className="w-4 h-4 group-hover:text-quantum-blue-light" />
                  <span className="text-sm">Source Code</span>
                  <ChevronRight className="w-4 h-4 ml-auto group-hover:translate-x-1 transition-transform" />
                </a>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'features',
      title: 'Features',
      subtitle: 'Platform capabilities',
      icon: <Zap className="w-5 h-5" />,
      badge: 'Complete',
      category: 'Platform',
      content: (
        <div className="space-y-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full quantum-gradient mb-6 shadow-xl">
              <Zap className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-3xl font-bold mb-4">
              <span className="quantum-gradient bg-clip-text text-transparent">Powerful Features</span>
            </h2>
            <p className="text-lg text-editor-text max-w-2xl mx-auto">
              Comprehensive quantum computing tools for conversion, simulation, and visualization
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="quantum-glass-dark rounded-xl p-6 hover-lift">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 quantum-gradient rounded-lg flex items-center justify-center mr-4">
                  <Code className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white">Framework Conversion</h3>
                  <p className="text-editor-text text-sm">Convert between Qiskit, Cirq, and PennyLane</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">AST-based parsing and intelligent gate mapping</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">OpenQASM 3.0 as universal intermediate representation</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Circuit optimization levels 0-3</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Validation and error reporting</span>
                </div>
              </div>
            </div>

            <div className="quantum-glass-dark rounded-xl p-6 hover-lift">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 quantum-gradient rounded-lg flex items-center justify-center mr-4">
                  <Play className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white">Quantum Simulation</h3>
                  <p className="text-editor-text text-sm">Multiple backends for accurate simulation</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Statevector backend for exact simulation</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Density matrix backend for noise modeling</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Stabilizer backend for Clifford circuits</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Configurable shot counts (1-10,000)</span>
                </div>
              </div>
            </div>

            <div className="quantum-glass-dark rounded-xl p-6 hover-lift">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 quantum-gradient rounded-lg flex items-center justify-center mr-4">
                  <BarChart3 className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white">Visualization</h3>
                  <p className="text-editor-text text-sm">Interactive charts and circuit diagrams</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Real-time circuit visualization</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Histogram plots for measurement results</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">State vector and probability displays</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Export capabilities (JSON, CSV, PNG)</span>
                </div>
              </div>
            </div>

            <div className="quantum-glass-dark rounded-xl p-6 hover-lift">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 quantum-gradient rounded-lg flex items-center justify-center mr-4">
                  <BookOpen className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white">Educational Tools</h3>
                  <p className="text-editor-text text-sm">Learning resources and guided examples</p>
                </div>
              </div>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Pre-built example circuits</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Framework comparison tutorials</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Interactive learning modules</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Beginner to advanced difficulty levels</span>
                </div>
              </div>
            </div>
          </div>

          <div className="quantum-glass-dark rounded-xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
              <Settings className="w-6 h-6 mr-3 text-quantum-blue-light" />
              Advanced Features
            </h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <Terminal className="w-6 h-6 text-orange-400" />
                </div>
                <h4 className="text-lg font-semibold text-white mb-2">Web IDE</h4>
                <p className="text-editor-text text-sm">Professional code editor with syntax highlighting and IntelliSense</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-pink-500/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <Shield className="w-6 h-6 text-pink-400" />
                </div>
                <h4 className="text-lg font-semibold text-white mb-2">Security</h4>
                <p className="text-editor-text text-sm">Input validation, rate limiting, and secure API endpoints</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-cyan-500/20 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <Cloud className="w-6 h-6 text-cyan-400" />
                </div>
                <h4 className="text-lg font-semibold text-white mb-2">Scalability</h4>
                <p className="text-editor-text text-sm">Docker deployment, load balancing, and high availability</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'architecture',
      title: 'Architecture',
      subtitle: 'System design',
      icon: <Layers className="w-5 h-5" />,
      badge: 'Technical',
      category: 'Technical',
      content: (
        <div className="space-y-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full quantum-gradient mb-6 shadow-xl">
              <Layers className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-3xl font-bold mb-4">
              <span className="quantum-gradient bg-clip-text text-transparent">System Architecture</span>
            </h2>
            <p className="text-lg text-editor-text max-w-2xl mx-auto">
              Modern, scalable architecture designed for quantum computing workflows
            </p>
          </div>

          <div className="quantum-glass-dark rounded-xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6">High-Level Architecture</h3>
            <div className="bg-editor-bg rounded-lg p-6 border border-editor-border">
              <pre className="text-xs text-editor-text overflow-x-auto">
{`Frontend (Next.js)          Backend (FastAPI)          Quantum Processing
├── React Components     ├── REST API Layer       ├── Quantum Converters
├── Code Editor          ├── WebSocket Manager    ├── Quantum Simulator
├── Visualization        ├── Service Layer        └── Circuit Optimizers
└── Real-time Updates    └── Database Layer`}
              </pre>
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="quantum-glass-dark rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <Monitor className="w-5 h-5 mr-2 text-blue-400" />
                Frontend Layer
              </h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Next.js 14 with App Router</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">React 18 with TypeScript</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Monaco Editor integration</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Real-time WebSocket updates</span>
                </div>
              </div>
            </div>

            <div className="quantum-glass-dark rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <Server className="w-5 h-5 mr-2 text-purple-400" />
                Backend Layer
              </h3>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">FastAPI with async support</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">PostgreSQL with SQLAlchemy</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Redis caching layer</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                  <span className="text-editor-text text-sm">Pydantic data validation</span>
                </div>
              </div>
            </div>
          </div>

          <div className="quantum-glass-dark rounded-xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6">Data Flow Architecture</h3>
            <div className="space-y-6">
              <div>
                <h4 className="text-lg font-semibold text-white mb-3">Circuit Conversion Flow</h4>
                <div className="bg-editor-bg rounded-lg p-4 border border-editor-border">
                  <div className="flex items-center space-x-4 text-sm">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-blue-400 rounded-full"></div>
                      <span className="text-editor-text">User Input</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400" />
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-purple-400 rounded-full"></div>
                      <span className="text-editor-text">API Request</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400" />
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                      <span className="text-editor-text">Framework Parser</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400" />
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-orange-400 rounded-full"></div>
                      <span className="text-editor-text">OpenQASM 3.0</span>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-lg font-semibold text-white mb-3">Simulation Flow</h4>
                <div className="bg-editor-bg rounded-lg p-4 border border-editor-border">
                  <div className="flex items-center space-x-4 text-sm">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-teal-400 rounded-full"></div>
                      <span className="text-editor-text">QASM Code</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400" />
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-cyan-400 rounded-full"></div>
                      <span className="text-editor-text">Backend Selection</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400" />
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-pink-400 rounded-full"></div>
                      <span className="text-editor-text">Circuit Execution</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400" />
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
                      <span className="text-editor-text">Results</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'api',
      title: 'API Reference',
      subtitle: 'Technical documentation',
      icon: <Terminal className="w-5 h-5" />,
      badge: 'Reference',
      category: 'Technical',
      content: (
        <div className="space-y-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full quantum-gradient mb-6 shadow-xl">
              <Terminal className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-3xl font-bold mb-4">
              <span className="quantum-gradient bg-clip-text text-transparent">API Reference</span>
            </h2>
            <p className="text-lg text-editor-text max-w-2xl mx-auto">
              Complete REST API documentation for QCanvas platform integration
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="quantum-glass-dark rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <Code className="w-5 h-5 mr-2 text-blue-400" />
                Conversion API
              </h3>
              <div className="space-y-4">
                <div className="bg-editor-bg rounded-lg p-4 border border-editor-border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">POST /api/convert</span>
                    <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">Active</span>
                  </div>
                  <p className="text-editor-text text-sm mb-3">Convert quantum circuits between frameworks</p>
                  <pre className="text-xs text-editor-text overflow-x-auto bg-gray-900 p-2 rounded">
{`{
  "source_framework": "qiskit",
  "target_framework": "cirq",
  "source_code": "your_circuit_code",
  "optimization_level": 1
}`}
                  </pre>
                </div>

                <div className="bg-editor-bg rounded-lg p-4 border border-editor-border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">GET /api/convert/frameworks</span>
                    <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">Info</span>
                  </div>
                  <p className="text-editor-text text-sm">Get supported frameworks and versions</p>
                </div>
              </div>
            </div>

            <div className="quantum-glass-dark rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <Play className="w-5 h-5 mr-2 text-green-400" />
                Simulation API
              </h3>
              <div className="space-y-4">
                <div className="bg-editor-bg rounded-lg p-4 border border-editor-border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">POST /api/simulate</span>
                    <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">Active</span>
                  </div>
                  <p className="text-editor-text text-sm mb-3">Execute quantum circuit simulation</p>
                  <pre className="text-xs text-editor-text overflow-x-auto bg-gray-900 p-2 rounded">
{`{
  "qasm_code": "OPENQASM 3.0; ...",
  "backend": "statevector",
  "shots": 1000
}`}
                  </pre>
                </div>

                <div className="bg-editor-bg rounded-lg p-4 border border-editor-border">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">GET /api/simulate/backends</span>
                    <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">Info</span>
                  </div>
                  <p className="text-editor-text text-sm">Get available simulation backends</p>
                </div>
              </div>
            </div>
          </div>

          <div className="quantum-glass-dark rounded-xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6">Available Backends</h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-editor-bg rounded-lg p-6 border border-editor-border">
                <div className="flex items-center mb-4">
                  <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                    <Database className="w-5 h-5 text-blue-400" />
                  </div>
                  <h4 className="text-lg font-semibold text-white ml-3">Statevector</h4>
                </div>
                <p className="text-editor-text text-sm mb-3">Perfect simulation with full quantum state representation</p>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Max Qubits:</span>
                    <span className="text-white">32</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Best for:</span>
                    <span className="text-white">Exact results</span>
                  </div>
                </div>
              </div>

              <div className="bg-editor-bg rounded-lg p-6 border border-editor-border">
                <div className="flex items-center mb-4">
                  <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                    <Layers className="w-5 h-5 text-purple-400" />
                  </div>
                  <h4 className="text-lg font-semibold text-white ml-3">Density Matrix</h4>
                </div>
                <p className="text-editor-text text-sm mb-3">Supports noise modeling and mixed quantum states</p>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Max Qubits:</span>
                    <span className="text-white">16</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Best for:</span>
                    <span className="text-white">Noise simulation</span>
                  </div>
                </div>
              </div>

              <div className="bg-editor-bg rounded-lg p-6 border border-editor-border">
                <div className="flex items-center mb-4">
                  <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                    <Zap className="w-5 h-5 text-green-400" />
                  </div>
                  <h4 className="text-lg font-semibold text-white ml-3">Stabilizer</h4>
                </div>
                <p className="text-editor-text text-sm mb-3">Efficient simulation for Clifford circuits</p>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Max Qubits:</span>
                    <span className="text-white">64</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Best for:</span>
                    <span className="text-white">Clifford circuits</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="quantum-glass-dark rounded-xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6">WebSocket API</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-editor-bg rounded-lg p-4 border border-editor-border">
                <h4 className="text-white font-medium mb-2">Connection</h4>
                <pre className="text-xs text-editor-text bg-gray-900 p-2 rounded">
ws://localhost:8000/ws
                </pre>
              </div>
              <div className="bg-editor-bg rounded-lg p-4 border border-editor-border">
                <h4 className="text-white font-medium mb-2">Real-time Updates</h4>
                <p className="text-editor-text text-sm">Live progress updates for long-running operations</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-editor-bg via-gray-900 to-editor-bg relative overflow-x-hidden">
      {/* Enhanced Navigation */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrollY > 50 ? 'bg-black/90 backdrop-blur-xl border-b border-white/10' : 'bg-transparent'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <Link href="/" className="flex items-center space-x-2 group">
              <div className="relative">
                <Image
                  src="/QCanvas-logo-Black.svg"
                  alt="QCanvas Logo"
                  width={48}
                  height={48}
                  className="object-contain block dark:hidden transition-all duration-300 hover:scale-110 animate-pulse"
                  priority
                />
                <Image
                  src="/QCanvas-logo-White.svg"
                  alt="QCanvas Logo"
                  width={48}
                  height={48}
                  className="object-contain hidden dark:block transition-all duration-300 hover:scale-110 animate-pulse"
                  priority
                />
              </div>
              <span className="text-2xl font-bold quantum-gradient bg-clip-text text-transparent transition-all duration-200">
                QCanvas
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              {[
                { id: 'overview', label: 'Overview', active: activeSection === 'overview' },
                { id: 'getting-started', label: 'Getting Started', active: activeSection === 'getting-started' },
                { id: 'features', label: 'Features', active: activeSection === 'features' },
                { id: 'architecture', label: 'Architecture', active: activeSection === 'architecture' },
                { id: 'api', label: 'API', active: activeSection === 'api' }
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => scrollToSection(item.id)}
                  className={`transition-colors duration-200 ${
                    item.active
                      ? 'text-quantum-blue-light'
                      : 'text-editor-text hover:text-white'
                  }`}
                >
                  {item.label}
                </button>
              ))}

              <Link
                href="/"
                className="text-editor-text hover:text-white transition-colors duration-200"
              >
                Home
              </Link>
            </div>

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg bg-editor-bg/50 border border-editor-border hover:border-quantum-blue-light transition-all duration-200 hover:scale-105"
              aria-label="Toggle theme"
            >
              {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
            </button>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 rounded-lg bg-editor-bg/50 border border-editor-border hover:border-quantum-blue-light transition-all duration-200 hover:scale-105"
              aria-label="Toggle menu"
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>

          {/* Mobile Menu */}
          {isMenuOpen && (
            <div className="md:hidden bg-black/95 backdrop-blur-xl border-t border-white/10">
              <div className="px-4 py-4 space-y-4">
                {[
                  { id: 'overview', label: 'Overview' },
                  { id: 'getting-started', label: 'Getting Started' },
                  { id: 'features', label: 'Features' },
                  { id: 'architecture', label: 'Architecture' },
                  { id: 'api', label: 'API' }
                ].map((item) => (
                  <button
                    key={item.id}
                    onClick={() => scrollToSection(item.id)}
                    className={`block w-full text-left transition-colors duration-200 ${
                      activeSection === item.id
                        ? 'text-quantum-blue-light'
                        : 'text-editor-text hover:text-white'
                    }`}
                  >
                    {item.label}
                  </button>
                ))}

                <Link
                  href="/"
                  className="block text-editor-text hover:text-white transition-colors duration-200"
                >
                  Home
                </Link>

                <div className="flex items-center justify-between pt-4 border-t border-white/10">
                  <button
                    onClick={toggleTheme}
                    className="flex items-center space-x-2 text-editor-text hover:text-white transition-colors duration-200"
                  >
                    {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                    <span>Theme</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-4 pt-20 overflow-hidden">
        {/* Enhanced Animated Background */}
        <div className="absolute inset-0 overflow-hidden">
          {/* Large background orbs */}
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-quantum-blue-light opacity-8 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-500 opacity-8 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-teal-500 opacity-3 rounded-full blur-3xl animate-pulse delay-500"></div>

          {/* Additional floating orbs */}
          <div className="absolute top-1/4 left-1/4 w-32 h-32 bg-blue-400 opacity-6 rounded-full blur-2xl animate-float delay-300"></div>
          <div className="absolute top-3/4 right-1/4 w-24 h-24 bg-pink-400 opacity-5 rounded-full blur-2xl animate-float delay-700"></div>
          <div className="absolute bottom-1/4 left-1/3 w-20 h-20 bg-green-400 opacity-4 rounded-full blur-2xl animate-float delay-1100"></div>
        </div>

        {/* Enhanced Floating Elements */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {/* Quantum-themed floating icons */}
          <div className="absolute top-20 left-10 animate-float delay-1000 hover:scale-110 transition-transform duration-300">
            <Atom className="w-8 h-8 text-quantum-blue-light opacity-40 animate-pulse" />
          </div>
          <div className="absolute top-40 right-20 animate-float-reverse delay-2000 hover:scale-110 transition-transform duration-300">
            <Sparkles className="w-6 h-6 text-purple-400 opacity-50 animate-pulse delay-500" />
          </div>
          <div className="absolute bottom-40 left-20 animate-float delay-3000 hover:scale-110 transition-transform duration-300">
            <Cpu className="w-10 h-10 text-teal-400 opacity-35 animate-pulse delay-1000" />
          </div>
          <div className="absolute top-1/3 right-10 animate-float-reverse delay-4000 hover:scale-110 transition-transform duration-300">
            <Zap className="w-7 h-7 text-yellow-400 opacity-45 animate-pulse delay-1500" />
          </div>
          <div className="absolute bottom-1/3 left-1/5 animate-float delay-5000 hover:scale-110 transition-transform duration-300">
            <Lightbulb className="w-6 h-6 text-orange-400 opacity-40 animate-pulse delay-2000" />
          </div>
          <div className="absolute top-2/3 right-1/3 animate-float-reverse delay-6000 hover:scale-110 transition-transform duration-300">
            <Star className="w-5 h-5 text-indigo-400 opacity-50 animate-pulse delay-2500" />
          </div>

          {/* Geometric shapes */}
          <div className="absolute top-16 right-1/4 w-2 h-2 bg-quantum-blue-light rounded-full animate-ping opacity-60"></div>
          <div className="absolute bottom-32 right-16 w-1 h-8 bg-purple-400 rounded-full animate-pulse opacity-40"></div>
          <div className="absolute top-1/2 left-16 w-3 h-3 bg-teal-400 rounded-full animate-bounce opacity-50"></div>
        </div>

        <div className={`text-center max-w-6xl mx-auto relative z-10 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full quantum-gradient mb-8 shadow-2xl">
            <BookOpen className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="quantum-gradient bg-clip-text text-transparent">Documentation</span>
          </h1>
          <p className="text-xl md:text-2xl text-editor-text mb-8 max-w-3xl mx-auto leading-relaxed">
            Comprehensive guide to using QCanvas for quantum circuit conversion, simulation, and visualization.
            Everything you need to build quantum applications with confidence.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
            <Link
              href="/login"
              className="btn-quantum text-lg px-8 py-4 flex items-center group hover-lift relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
              <Play className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform duration-300 relative z-10" />
              <span className="relative z-10">Try QCanvas Now</span>
            </Link>
            <button
              onClick={() => scrollToSection('getting-started')}
              className="btn-ghost text-lg px-8 py-4 flex items-center group hover-lift relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-quantum-blue-light/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
              <BookOpen className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform duration-300 relative z-10" />
              <span className="relative z-10">Read Documentation</span>
            </button>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            <div className="quantum-glass-dark rounded-xl p-4 text-center">
              <div className="text-2xl font-bold quantum-gradient bg-clip-text text-transparent mb-1">{config.stats.frameworks}</div>
              <div className="text-editor-text text-sm">Quantum Frameworks</div>
            </div>
            <div className="quantum-glass-dark rounded-xl p-4 text-center">
              <div className="text-2xl font-bold quantum-gradient bg-clip-text text-transparent mb-1">OpenQASM 3.0</div>
              <div className="text-editor-text text-sm">Standard Support</div>
            </div>
            <div className="quantum-glass-dark rounded-xl p-4 text-center">
              <div className="text-2xl font-bold quantum-gradient bg-clip-text text-transparent mb-1">Real-time</div>
              <div className="text-editor-text text-sm">Simulation</div>
            </div>
            <div className="quantum-glass-dark rounded-xl p-4 text-center">
              <div className="text-2xl font-bold quantum-gradient bg-clip-text text-transparent mb-1">Educational</div>
              <div className="text-editor-text text-sm">Platform</div>
            </div>
          </div>
        </div>
      </section>

      {/* Content Sections */}
      {sections.map((section) => (
        <section key={section.id} id={section.id} className="py-20 px-4">
          <div className="max-w-7xl mx-auto">
            <div className="text-center mb-12">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full quantum-gradient mb-6 shadow-xl">
                {section.icon}
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-4">
                <span className="quantum-gradient bg-clip-text text-transparent">{section.title}</span>
              </h2>
              {section.subtitle && (
                <p className="text-lg text-editor-text max-w-2xl mx-auto">{section.subtitle}</p>
              )}
              {section.badge && (
                <span className="inline-block mt-4 px-3 py-1 bg-quantum-blue-light/20 text-quantum-blue-light text-sm rounded-full border border-quantum-blue-light/30">
                  {section.badge}
                </span>
              )}
            </div>

            <div className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10">
              {section.content}
            </div>
          </div>
        </section>
      ))}

      {/* Footer */}
      <footer className="px-4 py-12 border-t border-editor-border">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-editor-text">
            {getCopyrightText()}
          </p>
          <div className="flex justify-center space-x-6 mt-4">
            {config.footer.support.map((link) => (
              <a
                key={link.email || link.name}
                href={link.email ? `mailto:${link.email}` : '#'}
                className="text-editor-text hover:text-white transition-colors"
              >
                {link.name}
              </a>
            ))}
            <a
              href={config.social.github}
              target="_blank"
              rel="noopener noreferrer"
              className="text-editor-text hover:text-white transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
