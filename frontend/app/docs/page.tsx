'use client'

import { useState, useEffect, useRef } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import Navbar from '@/components/Navbar'
import { Moon, Sun, Book, Code, Cpu, BarChart3, Zap, Settings, Play, Star, Atom, Lightbulb, Database, Layers, Terminal, FileText, Cloud, Server, Wrench, Target, Rocket, Clock, TrendingUp, GitBranch, FrameworkConversionIcon, FlagIcon, SparklesIcon, ApiIcon, CirqIcon, PennyLaneIcon, QiskitIcon } from '@/components/Icons';
import { Menu, X, ChevronRight, ArrowRight, CheckCircle, Shield, Monitor, Sparkles, Info } from 'lucide-react';
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
  const [scrollY, setScrollY] = useState(0)
  const observerRef = useRef<IntersectionObserver | null>(null)

  useEffect(() => {
    setIsVisible(true)
    const handleScroll = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', handleScroll, { passive: true })

    // Intersection Observer for scroll spy
    const sectionIds = ['overview', 'getting-started', 'features', 'architecture', 'api', 'hybrid-execution']
    
    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.id
            setActiveSection(id)
            
            // Auto-scroll sub-nav horizontally when section changes
            const navItem = document.getElementById(`nav-${id}`)
            if (navItem) {
              navItem.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
            }
          }
        })
      },
      {
        // Detect when the section is in the top portion of the viewport
        rootMargin: '-10% 0% -70% 0%',
        threshold: 0
      }
    )

    sectionIds.forEach((id) => {
      const el = document.getElementById(id)
      if (el) observerRef.current?.observe(el)
    })

    return () => {
      window.removeEventListener('scroll', handleScroll)
      observerRef.current?.disconnect()
    }
  }, [])

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    if (element) {
      // Use scrollIntoView which respects scroll-margin-top
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
      setActiveSection(sectionId)

      // Synchronize horizontal sub-nav scroll
      const navItem = document.getElementById(`nav-${sectionId}`)
      if (navItem) {
        navItem.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
      }
    }
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
              <span className="quantum-gradient bg-clip-text text-transparent">Overview</span>
            </h2>
            <p className="text-xl text-editor-text max-w-3xl mx-auto leading-relaxed">
              {config.project.description}
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="quantum-glass-dark rounded-xl p-6 text-center hover-lift">
              <div className="w-12 h-12 quantum-gradient rounded-lg flex items-center justify-center mx-auto mb-4">
                <FrameworkConversionIcon className="w-6 h-6 text-white" />
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
                <Book className="w-6 h-6 text-white" />
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
      icon: <FlagIcon className="w-5 h-5" />,
      badge: 'Beginner',
      category: 'Getting Started',
      content: (
        <div className="space-y-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full quantum-gradient mb-6 shadow-xl">
              <FlagIcon className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-3xl font-bold mb-4">
              <span className="quantum-gradient bg-clip-text text-transparent">Getting Started</span>
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
              <div className="bg-black/20 rounded-lg p-4 border border-white/5 mb-4">
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
                  <QiskitIcon className="w-8 h-8 text-black dark:text-white" />
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
                  <CirqIcon className="w-8 h-8 text-purple-400" />
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
                  <PennyLaneIcon className="w-8 h-8 text-green-400" />
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
      icon: <SparklesIcon className="w-5 h-5" />,
      badge: 'Complete',
      category: 'Platform',
      content: (
        <div className="space-y-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full quantum-gradient mb-6 shadow-xl">
              <SparklesIcon className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-3xl font-bold mb-4">
              <span className="quantum-gradient bg-clip-text text-transparent">Features</span>
            </h2>
            <p className="text-lg text-editor-text max-w-2xl mx-auto">
              Comprehensive quantum computing tools for conversion, simulation, and visualization
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="quantum-glass-dark rounded-xl p-6 hover-lift">
              <div className="flex items-center mb-4">
                <div className="w-12 h-12 quantum-gradient rounded-lg flex items-center justify-center mr-4">
                  <FrameworkConversionIcon className="w-6 h-6 text-white" />
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
                  <Book className="w-6 h-6 text-white" />
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
              <span className="quantum-gradient bg-clip-text text-transparent">Architecture</span>
            </h2>
            <p className="text-lg text-editor-text max-w-2xl mx-auto">
              Modern, scalable architecture designed for quantum computing workflows
            </p>
          </div>

          <div className="quantum-glass-dark rounded-xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6">High-Level Architecture</h3>
            <div className="bg-black/20 rounded-lg p-6 border border-white/5">
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
                <div className="bg-black/20 rounded-lg p-4 border border-white/5">
                  <div className="flex items-center space-x-4 text-sm">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-blue-400 rounded-full"></div>
                      <span className="text-editor-text">User Input</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-black dark:text-gray-400" />
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-purple-400 rounded-full"></div>
                      <span className="text-editor-text">API Request</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-black dark:text-gray-400" />
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-green-400 rounded-full"></div>
                      <span className="text-editor-text">Framework Parser</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-black dark:text-gray-400" />
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-orange-400 rounded-full"></div>
                      <span className="text-editor-text">OpenQASM 3.0</span>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h4 className="text-lg font-semibold text-white mb-3">Simulation Flow</h4>
                <div className="bg-black/20 rounded-lg p-4 border border-white/5">
                  <div className="flex items-center space-x-4 text-sm">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-teal-400 rounded-full"></div>
                      <span className="text-editor-text">QASM Code</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-black dark:text-gray-400" />
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-cyan-400 rounded-full"></div>
                      <span className="text-editor-text">Backend Selection</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-black dark:text-gray-400" />
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-pink-400 rounded-full"></div>
                      <span className="text-editor-text">Circuit Execution</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-black dark:text-gray-400" />
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
      icon: <ApiIcon className="w-5 h-5" />,
      badge: 'Reference',
      category: 'Technical',
      content: (
        <div className="space-y-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full quantum-gradient mb-6 shadow-xl">
              <ApiIcon className="w-8 h-8 text-white" />
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
                <FrameworkConversionIcon className="w-5 h-5 mr-2 text-blue-400" />
                Conversion API
              </h3>
              <div className="space-y-4">
                <div className="bg-black/20 rounded-lg p-4 border border-white/5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">POST /api/converter/convert</span>
                    <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">Active</span>
                  </div>
                  <p className="text-editor-text text-sm mb-3">Convert framework code to OpenQASM 3.0</p>
                  <pre className="text-xs text-editor-text overflow-x-auto bg-gray-900 dark:bg-gray-900 bg-gray-100 p-2 rounded">
                    {`{
  "source_code": "from qiskit import...",
  "source_framework": "qiskit",
  "conversion_type": "classic"
}
// Response includes: qasm_code, gates, depth, qubits`}
                  </pre>
                </div>

                <div className="bg-black/20 rounded-lg p-4 border border-white/5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">GET /api/health</span>
                    <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">Health</span>
                  </div>
                  <p className="text-editor-text text-sm">Check API health status</p>
                </div>
              </div>
            </div>

            <div className="quantum-glass-dark rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <Play className="w-5 h-5 mr-2 text-green-400" />
                Simulation API (QSim)
              </h3>
              <div className="space-y-4">
                <div className="bg-black/20 rounded-lg p-4 border border-white/5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">POST /api/simulator/execute</span>
                    <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">Active</span>
                  </div>
                  <p className="text-editor-text text-sm mb-3">Execute OpenQASM 3.0 with QSim</p>
                  <pre className="text-xs text-editor-text overflow-x-auto bg-gray-900 dark:bg-gray-900 bg-gray-100 p-2 rounded">
                    {`{
  "qasm_code": "OPENQASM 3.0; ...",
  "backend": "cirq",  // cirq, qiskit, pennylane
  "shots": 1024
}
// Response includes: counts, metadata, probs`}
                  </pre>
                </div>

                <div className="bg-black/20 rounded-lg p-4 border border-white/5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white font-medium">Response Metadata</span>
                    <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded">Stats</span>
                  </div>
                  <p className="text-editor-text text-sm">execution_time, simulation_time, memory_usage, cpu_usage, fidelity</p>
                </div>
              </div>
            </div>
          </div>

          <div className="quantum-glass-dark rounded-xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6">QSim Simulation Backends</h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-black/20 rounded-lg p-6 border border-white/5 hover:border-blue-500/50 transition-colors">
                <div className="flex items-center mb-4">
                  <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
                    <CirqIcon className="w-6 h-6 text-blue-400" />
                  </div>
                  <h4 className="text-lg font-semibold text-white ml-3">Cirq</h4>
                </div>
                <p className="text-editor-text text-sm mb-3">Google&apos;s quantum computing framework with statevector simulation</p>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-black dark:text-gray-400">Shots:</span>
                    <span className="text-white">1 - 10,000</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-black dark:text-gray-400">Best for:</span>
                    <span className="text-white">Near-term devices</span>
                  </div>
                </div>
              </div>

              <div className="bg-black/20 rounded-lg p-6 border border-white/5 hover:border-purple-500/50 transition-colors">
                <div className="flex items-center mb-4">
                  <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                    <QiskitIcon className="w-6 h-6 text-black dark:text-white" />
                  </div>
                  <h4 className="text-lg font-semibold text-white ml-3">Qiskit</h4>
                </div>
                <p className="text-editor-text text-sm mb-3">IBM&apos;s comprehensive quantum SDK with QASM simulator backend</p>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-black dark:text-gray-400">Shots:</span>
                    <span className="text-white">1 - 10,000</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-black dark:text-gray-400">Best for:</span>
                    <span className="text-white">IBM Quantum</span>
                  </div>
                </div>
              </div>

              <div className="bg-black/20 rounded-lg p-6 border border-white/5 hover:border-green-500/50 transition-colors">
                <div className="flex items-center mb-4">
                  <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
                    <PennyLaneIcon className="w-6 h-6 text-green-400" />
                  </div>
                  <h4 className="text-lg font-semibold text-white ml-3">PennyLane</h4>
                </div>
                <p className="text-editor-text text-sm mb-3">Xanadu&apos;s quantum ML framework with default.qubit device</p>
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-black dark:text-gray-400">Shots:</span>
                    <span className="text-white">1 - 10,000</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-black dark:text-gray-400">Best for:</span>
                    <span className="text-white">QML & Variational</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="quantum-glass-dark rounded-xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6">WebSocket API</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-black/20 rounded-lg p-4 border border-white/5">
                <h4 className="text-white font-medium mb-2">Connection</h4>
                <pre className="text-xs text-editor-text bg-gray-900 dark:bg-gray-900 bg-gray-100 p-2 rounded">
                  ws://localhost:8000/ws
                </pre>
              </div>
              <div className="bg-black/20 rounded-lg p-4 border border-white/5">
                <h4 className="text-white font-medium mb-2">Real-time Updates</h4>
                <p className="text-editor-text text-sm">Live progress updates for long-running operations</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'hybrid-execution',
      title: 'Hybrid Execution API',
      subtitle: 'Python API for hybrid CPU-QPU execution',
      icon: <Cpu className="w-5 h-5" />,
      badge: 'New',
      category: 'Technical',
      content: (
        <div className="space-y-8">
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full quantum-gradient mb-6 shadow-xl">
              <Cpu className="w-8 h-8 text-white" />
            </div>
            <h2 className="text-3xl font-bold mb-4">
              <span className="quantum-gradient bg-clip-text text-transparent">Hybrid Execution API</span>
            </h2>
            <p className="text-lg text-editor-text max-w-2xl mx-auto">
              Execute Python code with quantum circuits. Compile circuits, run simulations, and access results programmatically.
            </p>
          </div>

          {/* API Functions */}
          <div className="quantum-glass-dark rounded-xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
              <Code className="w-6 h-6 mr-3 text-quantum-blue-light" />
              Available Functions
            </h3>

            <div className="space-y-6">
              {/* compile function */}
              <div className="bg-black/20 rounded-lg p-6 border border-white/5">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-xl font-semibold text-white flex items-center">
                    <span className="text-quantum-blue-light mr-2">compile</span>
                    <span className="text-sm font-normal text-black dark:text-gray-400">(circuit, framework=None)</span>
                  </h4>
                  <span className="text-xs bg-blue-500/20 text-blue-400 px-3 py-1 rounded-full">Function</span>
                </div>
                <p className="text-editor-text mb-4">Compile a quantum circuit object to OpenQASM 3.0 format.</p>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-black dark:text-gray-400 mb-2">Parameters:</p>
                    <ul className="text-sm text-editor-text space-y-1 ml-4">
                      <li><code className="text-quantum-blue-light">circuit</code> - Circuit object from Cirq, Qiskit, or PennyLane</li>
                      <li><code className="text-quantum-blue-light">framework</code> - Optional: "cirq", "qiskit", "pennylane" (auto-detected if not provided)</li>
                    </ul>
                  </div>
                  <div>
                    <p className="text-sm text-black dark:text-gray-400 mb-2">Returns:</p>
                    <p className="text-sm text-editor-text ml-4"><code className="text-quantum-blue-light">str</code> - OpenQASM 3.0 code</p>
                  </div>
                  <div className="bg-gray-900 dark:bg-gray-900 bg-gray-100 rounded-lg p-4 mt-4">
                    <pre className="text-xs text-editor-text overflow-x-auto">
                      {`from qcanvas import compile
import cirq

q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(q[0], q[1], key='result')
])

qasm = compile(circuit, framework="cirq")
print(qasm)`}
                    </pre>
                  </div>
                </div>
              </div>

              {/* qsim.run function */}
              <div className="bg-black/20 rounded-lg p-6 border border-white/5">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-xl font-semibold text-white flex items-center">
                    <span className="text-quantum-blue-light mr-2">qsim.run</span>
                    <span className="text-sm font-normal text-black dark:text-gray-400">(qasm_code, shots=1024, backend="cirq")</span>
                  </h4>
                  <span className="text-xs bg-green-500/20 text-green-400 px-3 py-1 rounded-full">Function</span>
                </div>
                <p className="text-editor-text mb-4">Execute OpenQASM 3.0 code using QSim quantum simulator.</p>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-black dark:text-gray-400 mb-2">Parameters:</p>
                    <ul className="text-sm text-editor-text space-y-1 ml-4">
                      <li><code className="text-quantum-blue-light">qasm_code</code> - OpenQASM 3.0 code string</li>
                      <li><code className="text-quantum-blue-light">shots</code> - Number of measurement shots (default: 1024, use 0 for exact statevector)</li>
                      <li><code className="text-quantum-blue-light">backend</code> - "cirq", "qiskit", or "pennylane" (default: "cirq")</li>
                    </ul>
                  </div>
                  <div>
                    <p className="text-sm text-black dark:text-gray-400 mb-2">Returns:</p>
                    <p className="text-sm text-editor-text ml-4"><code className="text-quantum-blue-light">SimulationResult</code> - Result object with counts, probabilities, and metadata</p>
                  </div>
                  <div className="bg-gray-900 dark:bg-gray-900 bg-gray-100 rounded-lg p-4 mt-4">
                    <pre className="text-xs text-editor-text overflow-x-auto">
                      {`import qsim

qasm = '''
OPENQASM 3.0;
include "stdgates.inc";
qubit[2] q;
bit[2] c;
h q[0];
cx q[0], q[1];
c[0] = measure q[0];
c[1] = measure q[1];
'''

result = qsim.run(qasm, shots=1000, backend="cirq")
print(result.counts)
print(result.probabilities)`}
                    </pre>
                  </div>
                </div>
              </div>

              {/* compile_and_execute function */}
              <div className="bg-black/20 rounded-lg p-6 border border-white/5">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-xl font-semibold text-white flex items-center">
                    <span className="text-quantum-blue-light mr-2">compile_and_execute</span>
                    <span className="text-sm font-normal text-black dark:text-gray-400">(circuit, framework=None, shots=1024, backend="cirq")</span>
                  </h4>
                  <span className="text-xs bg-purple-500/20 text-purple-400 px-3 py-1 rounded-full">Convenience</span>
                </div>
                <p className="text-editor-text mb-4">Compile a circuit and execute it in a single call.</p>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-black dark:text-gray-400 mb-2">Parameters:</p>
                    <ul className="text-sm text-editor-text space-y-1 ml-4">
                      <li><code className="text-quantum-blue-light">circuit</code> - Circuit object from Cirq, Qiskit, or PennyLane</li>
                      <li><code className="text-quantum-blue-light">framework</code> - Optional: auto-detected if not provided</li>
                      <li><code className="text-quantum-blue-light">shots</code> - Number of measurement shots (default: 1024)</li>
                      <li><code className="text-quantum-blue-light">backend</code> - Simulation backend (default: "cirq")</li>
                    </ul>
                  </div>
                  <div>
                    <p className="text-sm text-black dark:text-gray-400 mb-2">Returns:</p>
                    <p className="text-sm text-editor-text ml-4"><code className="text-quantum-blue-light">SimulationResult</code> - Result object with counts, probabilities, and metadata</p>
                  </div>
                  <div className="bg-gray-900 dark:bg-gray-900 bg-gray-100 rounded-lg p-4 mt-4">
                    <pre className="text-xs text-editor-text overflow-x-auto">
                      {`from qcanvas import compile_and_execute
import cirq

q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(q[0], q[1], key='result')
])

result = compile_and_execute(circuit, framework="cirq", shots=1000)
print(result.counts)
print(result.probabilities)`}
                    </pre>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* SimulationResult Attributes Table */}
          <div className="quantum-glass-dark rounded-xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
              <BarChart3 className="w-6 h-6 mr-3 text-quantum-blue-light" />
              SimulationResult Attributes
            </h3>
            <p className="text-editor-text mb-6">
              The <code className="text-quantum-blue-light">SimulationResult</code> object returned by <code className="text-quantum-blue-light">qsim.run()</code> and <code className="text-quantum-blue-light">compile_and_execute()</code> provides comprehensive access to simulation data.
            </p>

            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b border-white/5">
                    <th className="text-left py-3 px-4 text-white font-semibold">Attribute</th>
                    <th className="text-left py-3 px-4 text-white font-semibold">Type</th>
                    <th className="text-left py-3 px-4 text-white font-semibold">Description</th>
                    <th className="text-left py-3 px-4 text-white font-semibold">Example</th>
                  </tr>
                </thead>
                <tbody className="text-editor-text">
                  <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4"><code className="text-quantum-blue-light">counts</code></td>
                    <td className="py-3 px-4 text-sm"><code>Dict[str, int]</code></td>
                    <td className="py-3 px-4">Measurement counts for each outcome</td>
                    <td className="py-3 px-4 text-sm"><code>{`{'00': 512, '11': 512}`}</code></td>
                  </tr>
                  <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4"><code className="text-quantum-blue-light">probabilities</code></td>
                    <td className="py-3 px-4 text-sm"><code>Dict[str, float]</code></td>
                    <td className="py-3 px-4">Probability of each measurement outcome</td>
                    <td className="py-3 px-4 text-sm"><code>{`{'00': 0.5, '11': 0.5}`}</code></td>
                  </tr>
                  <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4"><code className="text-quantum-blue-light">statevector</code></td>
                    <td className="py-3 px-4 text-sm"><code>List[complex]</code></td>
                    <td className="py-3 px-4">Full quantum statevector (only when shots=0)</td>
                    <td className="py-3 px-4 text-sm"><code>{`[0.707+0j, 0+0j, ...]`}</code></td>
                  </tr>
                  <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4"><code className="text-quantum-blue-light">n_qubits</code></td>
                    <td className="py-3 px-4 text-sm"><code>int</code></td>
                    <td className="py-3 px-4">Number of qubits in the circuit</td>
                    <td className="py-3 px-4 text-sm"><code>2</code></td>
                  </tr>
                  <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4"><code className="text-quantum-blue-light">shots</code></td>
                    <td className="py-3 px-4 text-sm"><code>int</code></td>
                    <td className="py-3 px-4">Number of measurement shots executed</td>
                    <td className="py-3 px-4 text-sm"><code>1000</code></td>
                  </tr>
                  <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4"><code className="text-quantum-blue-light">backend</code></td>
                    <td className="py-3 px-4 text-sm"><code>str</code></td>
                    <td className="py-3 px-4">Backend used for simulation</td>
                    <td className="py-3 px-4 text-sm"><code>"cirq"</code></td>
                  </tr>
                  <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4"><code className="text-quantum-blue-light">execution_time</code></td>
                    <td className="py-3 px-4 text-sm"><code>str</code></td>
                    <td className="py-3 px-4">Total execution time (human-readable)</td>
                    <td className="py-3 px-4 text-sm"><code>"1.23ms"</code></td>
                  </tr>
                  <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4"><code className="text-quantum-blue-light">simulation_time</code></td>
                    <td className="py-3 px-4 text-sm"><code>str</code></td>
                    <td className="py-3 px-4">Time spent in quantum simulation</td>
                    <td className="py-3 px-4 text-sm"><code>"0.98ms"</code></td>
                  </tr>
                  <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4"><code className="text-quantum-blue-light">memory_usage</code></td>
                    <td className="py-3 px-4 text-sm"><code>str</code></td>
                    <td className="py-3 px-4">Memory consumed during simulation</td>
                    <td className="py-3 px-4 text-sm"><code>"45.2 MB"</code></td>
                  </tr>
                  <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4"><code className="text-quantum-blue-light">cpu_usage</code></td>
                    <td className="py-3 px-4 text-sm"><code>str</code></td>
                    <td className="py-3 px-4">CPU utilization during simulation</td>
                    <td className="py-3 px-4 text-sm"><code>"12.5%"</code></td>
                  </tr>
                  <tr className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4"><code className="text-quantum-blue-light">fidelity</code></td>
                    <td className="py-3 px-4 text-sm"><code>float</code></td>
                    <td className="py-3 px-4">Simulation fidelity as percentage</td>
                    <td className="py-3 px-4 text-sm"><code>100.0</code></td>
                  </tr>
                  <tr className="hover:bg-white/5 transition-colors">
                    <td className="py-3 px-4"><code className="text-quantum-blue-light">metadata</code></td>
                    <td className="py-3 px-4 text-sm"><code>Dict[str, Any]</code></td>
                    <td className="py-3 px-4">Additional backend-specific metadata</td>
                    <td className="py-3 px-4 text-sm"><code>{`{'gate_count': 5}`}</code></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Printing Circuits */}
          <div className="quantum-glass-dark rounded-xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
              <FileText className="w-6 h-6 mr-3 text-quantum-blue-light" />
              Printing Circuits
            </h3>
            <p className="text-editor-text mb-6">
              You can print circuit objects directly to visualize their structure in all supported frameworks.
            </p>

            <div className="grid md:grid-cols-3 gap-6">
              {/* Cirq */}
              <div className="bg-black/20 rounded-lg p-6 border border-white/5">
                <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
                  <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center mr-3">
                    <CirqIcon className="w-5 h-5 text-blue-400" />
                  </div>
                  Cirq
                </h4>
                <div className="bg-gray-900 dark:bg-gray-900 bg-gray-100 rounded-lg p-4 mb-4">
                  <pre className="text-xs text-editor-text overflow-x-auto">
                    {`import cirq

q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(q[0], q[1])
])

print(circuit)`}
                  </pre>
                </div>
                <div className="bg-gray-800 dark:bg-gray-800 bg-gray-100 rounded-lg p-3 border border-gray-700 dark:border-gray-700 border-gray-300">
                  <pre className="text-xs text-black dark:text-gray-300 dark:text-gray-300 text-gray-800 font-mono">
                    {`0: ───H───@───M───
           │
1: ────────X───M───`}
                  </pre>
                </div>
              </div>

              {/* Qiskit */}
              <div className="bg-black/20 rounded-lg p-6 border border-white/5">
                <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
                  <div className="w-8 h-8 bg-purple-500/20 rounded-lg flex items-center justify-center mr-3">
                    <QiskitIcon className="w-5 h-5 text-black dark:text-white" />
                  </div>
                  Qiskit
                </h4>
                <div className="bg-gray-900 dark:bg-gray-900 bg-gray-100 rounded-lg p-4 mb-4">
                  <pre className="text-xs text-editor-text overflow-x-auto">
                    {`from qiskit import QuantumCircuit

qc = QuantumCircuit(2, 2)
qc.h(0)
qc.cx(0, 1)
qc.measure([0, 1], [0, 1])

print(qc)`}
                  </pre>
                </div>
                <div className="bg-gray-800 dark:bg-gray-800 bg-gray-100 rounded-lg p-3 border border-gray-700 dark:border-gray-700 border-gray-300">
                  <pre className="text-xs text-black dark:text-gray-300 dark:text-gray-300 text-gray-800 font-mono">
                    {`     ┌───┐     ┌─┐
q_0: ┤ H ├──■──┤M├
     └───┘ │ ┌┴┐└╥┘
q_1: ──────┼─┤M├─╫─
           │ └╥┘ ║
c: 2/══════╪══╬══╩═`}
                  </pre>
                </div>
              </div>

              {/* PennyLane */}
              <div className="bg-black/20 rounded-lg p-6 border border-white/5">
                <h4 className="text-lg font-semibold text-white mb-4 flex items-center">
                  <div className="w-8 h-8 bg-green-500/20 rounded-lg flex items-center justify-center mr-3">
                    <PennyLaneIcon className="w-5 h-5 text-green-400" />
                  </div>
                  PennyLane
                </h4>
                <div className="bg-gray-900 dark:bg-gray-900 bg-gray-100 rounded-lg p-4 mb-4">
                  <pre className="text-xs text-editor-text overflow-x-auto">
                    {`import pennylane as qml

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.expval(qml.PauliZ(0))

print(qml.draw(circuit)())`}
                  </pre>
                </div>
                <div className="bg-gray-800 dark:bg-gray-800 bg-gray-100 rounded-lg p-3 border border-gray-700 dark:border-gray-700 border-gray-300">
                  <pre className="text-xs text-black dark:text-gray-300 dark:text-gray-300 text-gray-800 font-mono">
                    {`0: ──H──╭C──┤ ⟨Z⟩
1: ──────╰X──┤`}
                  </pre>
                </div>
              </div>
            </div>
          </div>

          {/* Complete Example */}
          <div className="quantum-glass-dark rounded-xl p-8">
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
              <Lightbulb className="w-6 h-6 mr-3 text-yellow-400" />
              Complete Workflow Example
            </h3>
            <div className="bg-black/20 rounded-lg p-6 border border-white/5">
              <div className="bg-gray-900 dark:bg-gray-900 bg-gray-100 rounded-lg p-4">
                <pre className="text-sm text-editor-text overflow-x-auto">
                  {`import cirq
from qcanvas import compile, compile_and_execute
import qsim

# Step 1: Create circuit
q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(q[0], q[1], key='result')
])

# Step 2: Print circuit (optional)
print("Circuit Structure:")
print(circuit)

# Step 3: Compile to QASM
qasm = compile(circuit, framework="cirq")
print("\\nGenerated QASM:")
print(qasm)

# Step 4: Execute simulation
result = qsim.run(qasm, shots=1000, backend="cirq")

# Step 5: Access results
print("\\nSimulation Results:")
print(f"  Counts: {result.counts}")
print(f"  Probabilities: {result.probabilities}")
print(f"  Execution time: {result.execution_time}")
print(f"  Qubits: {result.n_qubits}")
print(f"  Shots: {result.shots}")
print(f"  Backend: {result.backend}")

# Alternative: Compile and execute in one step
result2 = compile_and_execute(circuit, framework="cirq", shots=1000)
print(f"\\nOne-step result: {result2.counts}")`}
                </pre>
              </div>
            </div>
          </div>
        </div>
      )
    },
  ]

  return (
    <div className="min-h-screen bg-[#0a0a1a] relative overflow-x-hidden text-white">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-grid-pattern opacity-30 pointer-events-none" />
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a1a] via-transparent to-[#0a0a1a] pointer-events-none" />
      <div className="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[800px] h-[600px] hero-spotlight opacity-30 blur-3xl pointer-events-none" />
      {/* Enhanced Navigation */}
      <Navbar />

      {/* Docs Sub-Navigation */}
      <div className={`fixed left-0 right-0 z-40 transition-all duration-300 ${scrollY > 50 ? 'top-[73px] dark:bg-[#0a0a1a]/90 bg-white/90 backdrop-blur-md border-b dark:border-white/10 border-gray-200' : 'top-[76px] bg-transparent'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center overflow-x-auto py-3 hide-scrollbar text-sm">
            {[
              { id: 'overview', label: 'Overview', active: activeSection === 'overview' },
              { id: 'getting-started', label: 'Getting Started', active: activeSection === 'getting-started' },
              { id: 'features', label: 'Features', active: activeSection === 'features' },
              { id: 'architecture', label: 'Architecture', active: activeSection === 'architecture' },
              { id: 'api', label: 'API', active: activeSection === 'api' },
              { id: 'hybrid-execution', label: 'Hybrid API', active: activeSection === 'hybrid-execution' }
            ].map((item) => (
              <button
                key={item.id}
                id={`nav-${item.id}`}
                onClick={() => scrollToSection(item.id)}
                className={`flex-shrink-0 transition-colors duration-200 px-4 py-1.5 rounded-full mr-2 ${item.active
                  ? 'bg-quantum-blue-light/10 text-quantum-blue-light dark:text-quantum-blue-light'
                  : 'text-gray-600 dark:text-gray-400 dark:hover:text-white hover:text-gray-900 dark:hover:bg-white/5 hover:bg-gray-100'
                  }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-4 pt-20 overflow-hidden">
        {/* Subtle background orbs — fewer, more vibrant */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-32 -right-32 w-[500px] h-[500px] bg-indigo-500 opacity-[0.07] rounded-full blur-[100px]"></div>
          <div className="absolute -bottom-32 -left-32 w-[500px] h-[500px] bg-violet-500 opacity-[0.07] rounded-full blur-[100px]"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-cyan-500 opacity-[0.05] rounded-full blur-[80px]"></div>
        </div>

        {/* Floating elements — fewer, more visible */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-24 left-[8%] animate-float">
            <Atom className="w-8 h-8 text-indigo-400 opacity-20" />
          </div>
          <div className="absolute top-1/3 right-[8%] animate-float-reverse" style={{ animationDelay: '2s' }}>
            <Sparkles className="w-6 h-6 text-violet-400 opacity-25" />
          </div>
          <div className="absolute bottom-1/3 left-[12%] animate-float" style={{ animationDelay: '4s' }}>
            <Cpu className="w-7 h-7 text-cyan-400 opacity-20" />
          </div>
          <div className="absolute top-16 right-1/4 w-1.5 h-1.5 bg-indigo-400 rounded-full animate-ping opacity-40"></div>
          <div className="absolute bottom-1/4 left-1/3 w-1.5 h-1.5 bg-cyan-400 rounded-full animate-ping opacity-30" style={{ animationDelay: '1s' }}></div>
        </div>

        <div className={`text-center max-w-6xl mx-auto relative z-10 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-full quantum-gradient mb-8 shadow-2xl">
            <Book className="w-10 h-10 text-white" />
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
              <Book className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform duration-300 relative z-10" />
              <span className="relative z-10">Read Documentation</span>
            </button>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-5xl mx-auto">
            <div className="quantum-glass-dark rounded-xl p-4 text-center">
              <div className="text-2xl font-bold quantum-gradient bg-clip-text text-transparent mb-1">{config.stats.frameworks}</div>
              <div className="text-editor-text text-sm">Quantum Frameworks</div>
            </div>
            <div className="quantum-glass-dark rounded-xl p-4 text-center">
              <div className="text-2xl font-bold quantum-gradient bg-clip-text text-transparent mb-1 whitespace-nowrap">OpenQASM 3.0</div>
              <div className="text-editor-text text-sm whitespace-nowrap">Standard Support</div>
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
            <div className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10">
              {section.content}
            </div>
          </div>
        </section>
      ))}

      {/* Footer */}
      <footer className="px-4 py-12 border-t border-white/5">
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
