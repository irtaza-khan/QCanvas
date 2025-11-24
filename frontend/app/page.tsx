'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import {
  Zap,
  Code,
  Play,
  BookOpen,
  GitBranch,
  ChevronDown,
  Sparkles,
  Cpu,
  Atom,
  Lightbulb,
  ArrowRight,
  Star,
  Users,
  Globe,
  Moon,
  Sun,
  Menu,
  X
} from 'lucide-react'
import { useFileStore } from '@/lib/store'
import { config, getCopyrightText } from '@/lib/config'

export default function HomePage() {
  const { theme, toggleTheme } = useFileStore()
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isVisible, setIsVisible] = useState(false)
  const [scrollY, setScrollY] = useState(0)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  // Check authentication status
  useEffect(() => {
    const authStatus = localStorage.getItem('qcanvas-auth')
    setIsAuthenticated(!!authStatus)
  }, [])

  useEffect(() => {
    setIsVisible(true)

    const handleScroll = () => {
      setScrollY(window.scrollY)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const scrollToSection = (sectionId: string) => {
    const element = document.getElementById(sectionId)
    element?.scrollIntoView({ behavior: 'smooth' })
  }

  // Get example code by type
  const getExampleCode = (exampleType: string) => {
    const examples = {
      'bell-state': {
        name: 'bell_state_cirq.py',
        content: `import cirq

# Create qubits
q0, q1 = cirq.LineQubit.range(2)

# Create Bell State circuit
circuit = cirq.Circuit()
circuit.append(cirq.H(q0))          # Hadamard gate
circuit.append(cirq.CNOT(q0, q1))   # CNOT gate
circuit.append(cirq.measure(q0, key='m0'))
circuit.append(cirq.measure(q1, key='m1'))

# Expected: 50% |00⟩, 50% |11⟩`
      },
      'quantum-teleportation': {
        name: 'teleportation_qiskit.py',
        content: `from qiskit import QuantumCircuit

# Quantum Teleportation Circuit
qc = QuantumCircuit(3, 3)

# STEP 1: Prepare state to teleport
qc.h(0)

# STEP 2: Create Bell pair (q1, q2)
qc.h(1)
qc.cx(1, 2)

# STEP 3: Bell measurement
qc.cx(0, 1)
qc.h(0)
qc.measure(0, 0)
qc.measure(1, 1)

# STEP 4: Classical corrections
c = [0, 0, 0]  # Placeholder for conditions
if c[1] == 1:
    qc.x(2)
if c[0] == 1:
    qc.z(2)

# Measure teleported qubit
qc.measure(2, 2)`
      },
      'grovers-search': {
        name: 'grovers_pennylane.py',
        content: `import pennylane as qml

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def grovers_search():
    # Initialize superposition
    qml.Hadamard(wires=0)
    qml.Hadamard(wires=1)
    
    # Oracle: mark |11⟩
    qml.CZ(wires=[0, 1])
    
    # Diffusion operator
    qml.Hadamard(wires=0)
    qml.Hadamard(wires=1)
    qml.PauliX(wires=0)
    qml.PauliX(wires=1)
    qml.CZ(wires=[0, 1])
    qml.PauliX(wires=0)
    qml.PauliX(wires=1)
    qml.Hadamard(wires=0)
    qml.Hadamard(wires=1)
    
    return qml.probs(wires=[0, 1])

# Expected: High probability for |11⟩`
      }
    }
    return examples[exampleType as keyof typeof examples] || examples['bell-state']
  }

  // Handle trying an example
  const handleTryExample = (example: { name: string, content: string }) => {
    if (isAuthenticated) {
      // If authenticated, store the example data and navigate to app
      sessionStorage.setItem('pending-example', JSON.stringify(example))
      window.location.href = '/app'
    } else {
      // If not authenticated, store the example data and go to login
      sessionStorage.setItem('pending-example', JSON.stringify(example))
      window.location.href = '/login'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-editor-bg via-gray-900 to-editor-bg relative overflow-x-hidden">
      {/* Navigation */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrollY > 50 ? 'bg-black/80 backdrop-blur-lg border-b border-white/10' : 'bg-transparent'}`}>
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
              <button
                onClick={() => scrollToSection('features')}
                className="text-editor-text hover:text-white transition-colors duration-200"
              >
                Features
              </button>
              {config.navigation.slice(1).map((item) => (
                <Link
                  key={item.path}
                  href={item.path as any}
                  className="text-editor-text hover:text-white transition-colors duration-200"
                >
                  {item.name}
                </Link>
              ))}

              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg bg-editor-bg/50 border border-editor-border hover:border-quantum-blue-light transition-colors duration-200"
                title="Toggle theme"
              >
                {theme === 'dark' ? <Sun className="w-5 h-5 text-editor-text" /> : <Moon className="w-5 h-5 text-editor-text" />}
              </button>

              {/* Auth Buttons */}
              <div className="flex items-center space-x-3">
                {isAuthenticated ? (
                  <Link
                    href="/app"
                    className="btn-quantum text-sm px-4 py-2"
                  >
                    Go to App
                  </Link>
                ) : (
                  <>
                    <Link
                      href="/login"
                      className="text-editor-text hover:text-white transition-colors duration-200 font-medium"
                    >
                      Sign In
                    </Link>
                    <Link
                      href="/login"
                      className="btn-quantum text-sm px-4 py-2"
                    >
                      Get Started
                    </Link>
                  </>
                )}
              </div>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 rounded-lg bg-editor-bg/50 border border-editor-border"
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>

          {/* Mobile Menu */}
          {isMenuOpen && (
            <div className="md:hidden bg-black/95 backdrop-blur-lg border-t border-white/10">
              <div className="px-4 py-4 space-y-4">
                <button
                  onClick={() => scrollToSection('features')}
                  className="block w-full text-left text-editor-text hover:text-white transition-colors duration-200"
                >
                  Features
                </button>
                {config.navigation.slice(1).map((item) => (
                  <Link
                    key={item.path}
                    href={item.path as any}
                    className="block text-editor-text hover:text-white transition-colors duration-200"
                  >
                    {item.name}
                  </Link>
                ))}

                <div className="flex items-center justify-between pt-4 border-t border-white/10">
                  <button
                    onClick={toggleTheme}
                    className="flex items-center space-x-2 text-editor-text hover:text-white transition-colors duration-200"
                  >
                    {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                    <span>Theme</span>
                  </button>
                  <div className="flex space-x-3">
                    {isAuthenticated ? (
                      <Link href="/app" className="btn-quantum text-sm px-3 py-1">
                        Go to App
                      </Link>
                    ) : (
                      <>
                        <Link href="/login" className="text-editor-text hover:text-white transition-colors duration-200">
                          Sign In
                        </Link>
                        <Link href="/login" className="btn-quantum text-sm px-3 py-1">
                          Get Started
                        </Link>
                      </>
                    )}
                  </div>
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

        <div className="text-center max-w-6xl mx-auto relative z-10">
          <div className={`transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <div className="inline-flex items-center bg-quantum-blue-light/10 border border-quantum-blue-light/20 rounded-full px-6 py-2 mb-8 backdrop-blur-sm hover:bg-quantum-blue-light/20 transition-all duration-500 hover:scale-105">
              <Zap className="w-4 h-4 text-quantum-blue-light mr-2 animate-pulse" />
              <span className="text-sm font-medium text-quantum-blue-light">Next-Generation Quantum Development</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              <span className="quantum-gradient bg-clip-text text-transparent animate-pulse">Quantum</span>
              <br />
              <span className="text-white transition-all duration-1000 delay-500">Computing Made</span>
              <br />
              <span className="gradient-text animate-pulse delay-700">Simple</span>
            </h1>

            <p className="text-xl md:text-2xl text-editor-text mb-8 max-w-3xl mx-auto leading-relaxed transition-all duration-1000 delay-800">
              {config.project.description}
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12 transition-all duration-1000 delay-1000">
              <button
                onClick={() => handleTryExample(getExampleCode('bell-state'))}
                className="btn-quantum text-lg px-8 py-4 flex items-center group hover-lift relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                <Play className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform duration-300 relative z-10" />
                <span className="relative z-10">Try QCanvas Now</span>
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform duration-300 relative z-10" />
              </button>
              <button
                onClick={() => scrollToSection('features')}
                className="btn-ghost text-lg px-8 py-4 flex items-center group hover-lift relative overflow-hidden"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-quantum-blue-light/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
                <Lightbulb className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform duration-300 relative z-10" />
                <span className="relative z-10">Explore Features</span>
              </button>
            </div>

            {/* Enhanced Stats */}
            <div className='grid grid-rows-1 gap-4'>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-3xl mx-auto transition-all duration-1000 delay-1200">
              <div className="text-center group hover:scale-105 transition-transform duration-300">
                <div className="text-3xl font-bold quantum-gradient bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform duration-300">{config.stats.frameworks}</div>
                <div className="text-sm text-editor-text group-hover:text-white transition-colors duration-300">Quantum Frameworks</div>
                <div className="w-0 group-hover:w-full h-0.5 bg-quantum-blue-light rounded-full transition-all duration-500 mx-auto mt-2"></div>
              </div>
              <div className="text-center group hover:scale-105 transition-transform duration-300">
                <div className="text-3xl font-bold quantum-gradient bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform duration-300">{config.stats.standards}</div>
                <div className="text-sm text-editor-text group-hover:text-white transition-colors duration-300">Compatible</div>
                <div className="w-0 group-hover:w-full h-0.5 bg-purple-400 rounded-full transition-all duration-500 mx-auto mt-2"></div>
              </div>
              <div className="text-center group hover:scale-105 transition-transform duration-300">
                <div className="text-3xl font-bold quantum-gradient bg-clip-text text-transparent mb-2 group-hover:scale-110 transition-transform duration-300">{config.stats.simulations}</div>
                <div className="text-sm text-editor-text group-hover:text-white transition-colors duration-300">Simulation</div>
                <div className="w-0 group-hover:w-full h-0.5 bg-teal-400 rounded-full transition-all duration-500 mx-auto mt-2"></div>
              </div>
            </div>
            {/* Scroll Indicator */}
            <div className="relative transform -translate-x-1/2 animate-bounce">
              <button
                onClick={() => scrollToSection('features')}
                className="text-editor-text hover:text-white transition-colors duration-200"
              >
                <ChevronDown className="w-6 h-6" />
              </button>
            </div>
            </div>
          </div>

        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-black/20">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-6">
              <span className="quantum-gradient bg-clip-text text-transparent">Powerful Features</span>
            </h2>
            <p className="text-xl text-editor-text max-w-3xl mx-auto">
              Everything you need to build, convert, and simulate quantum circuits
              with professional-grade tools and real-time feedback.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="quantum-glass-dark rounded-2xl p-8 hover-lift hover:shadow-quantum-lg transition-all duration-500 group feature-card opacity-0 animate-fade-in">
              <div className="w-12 h-12 bg-quantum-blue-light/20 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 group-hover:bg-quantum-blue-light/30">
                <Code className="w-6 h-6 text-quantum-blue-light group-hover:scale-110 transition-transform duration-300" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4 group-hover:text-quantum-blue-light transition-colors duration-300">Framework Conversion</h3>
              <p className="text-editor-text mb-4 group-hover:text-gray-200 transition-colors duration-300">
                Seamlessly convert between Cirq, Qiskit, and PennyLane with
                intelligent parsing and OpenQASM 3.0 as the universal intermediate format.
              </p>
              <div className="flex items-center text-sm text-quantum-blue-light group-hover:text-white transition-colors duration-300">
                <span>Learn more</span>
                <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-2 transition-transform duration-300" />
              </div>
            </div>

            {/* Feature 2 */}
            <div className="quantum-glass-dark rounded-2xl p-8 hover-lift hover:shadow-quantum-lg transition-all duration-500 group feature-card opacity-0 animate-fade-in">
              <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 group-hover:bg-purple-500/30">
                <Play className="w-6 h-6 text-purple-400 group-hover:scale-110 transition-transform duration-300" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4 group-hover:text-purple-400 transition-colors duration-300">Real-time Simulation</h3>
              <p className="text-editor-text mb-4 group-hover:text-gray-200 transition-colors duration-300">
                Experience instant quantum circuit simulation with multiple backends,
                progress tracking, and interactive visualization powered by WebSocket.
              </p>
              <div className="flex items-center text-sm text-purple-400 group-hover:text-white transition-colors duration-300">
                <span>Try simulation</span>
                <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-2 transition-transform duration-300" />
              </div>
            </div>

            {/* Feature 3 */}
            <div className="quantum-glass-dark rounded-2xl p-8 hover-lift hover:shadow-quantum-lg transition-all duration-500 group feature-card opacity-0 animate-fade-in">
              <div className="w-12 h-12 bg-teal-500/20 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 group-hover:bg-teal-500/30">
                <BookOpen className="w-6 h-6 text-teal-400 group-hover:scale-110 transition-transform duration-300" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4 group-hover:text-teal-400 transition-colors duration-300">Educational Platform</h3>
              <p className="text-editor-text mb-4 group-hover:text-gray-200 transition-colors duration-300">
                Learn quantum computing with guided examples, tutorials, and
                an intuitive interface designed for both beginners and experts.
              </p>
              <div className="flex items-center text-sm text-teal-400 group-hover:text-white transition-colors duration-300">
                <span>Start learning</span>
                <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-2 transition-transform duration-300" />
              </div>
            </div>

            {/* Feature 4 */}
            <div className="quantum-glass-dark rounded-2xl p-8 hover-lift hover:shadow-quantum-lg transition-all duration-500 group feature-card opacity-0 animate-fade-in">
              <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 group-hover:bg-green-500/30">
                <Zap className="w-6 h-6 text-green-400 group-hover:scale-110 transition-transform duration-300" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4 group-hover:text-green-400 transition-colors duration-300">Web IDE</h3>
              <p className="text-editor-text mb-4 group-hover:text-gray-200 transition-colors duration-300">
                Professional code editor with syntax highlighting, IntelliSense,
                and live preview for quantum circuit development and debugging.
              </p>
              <div className="flex items-center text-sm text-green-400 group-hover:text-white transition-colors duration-300">
                <span>Open editor</span>
                <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-2 transition-transform duration-300" />
              </div>
            </div>

            {/* Feature 5 */}
            <div className="quantum-glass-dark rounded-2xl p-8 hover-lift hover:shadow-quantum-lg transition-all duration-500 group feature-card opacity-0 animate-fade-in">
              <div className="w-12 h-12 bg-orange-500/20 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 group-hover:bg-orange-500/30">
                <Users className="w-6 h-6 text-orange-400 group-hover:scale-110 transition-transform duration-300" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4 group-hover:text-orange-400 transition-colors duration-300">Community Sharing</h3>
              <p className="text-editor-text mb-4 group-hover:text-gray-200 transition-colors duration-300">
                Share your quantum circuits with the community through GitHub-style
                repositories, collaboration tools, and public circuit galleries.
              </p>
              <div className="flex items-center text-sm text-orange-400 group-hover:text-white transition-colors duration-300">
                <span>Join community</span>
                <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-2 transition-transform duration-300" />
              </div>
            </div>

            {/* Feature 6 */}
            <div className="quantum-glass-dark rounded-2xl p-8 hover-lift hover:shadow-quantum-lg transition-all duration-500 group feature-card opacity-0 animate-fade-in">
              <div className="w-12 h-12 bg-pink-500/20 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 group-hover:bg-pink-500/30">
                <Globe className="w-6 h-6 text-pink-400 group-hover:scale-110 transition-transform duration-300" />
              </div>
              <h3 className="text-xl font-semibold text-white mb-4 group-hover:text-pink-400 transition-colors duration-300">OpenQASM 3.0</h3>
              <p className="text-editor-text mb-4 group-hover:text-gray-200 transition-colors duration-300">
                Full support for OpenQASM 3.0 standard with advanced features,
                validation, and compatibility across all major quantum platforms.
              </p>
              <div className="flex items-center text-sm text-pink-400 group-hover:text-white transition-colors duration-300">
                <span>View standard</span>
                <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-2 transition-transform duration-300" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Examples Preview */}
      <section className="py-20 px-4 bg-gradient-to-b from-transparent via-black/10 to-transparent">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16 transition-all duration-1000">
            <h2 className="text-4xl md:text-5xl font-bold mb-6 transition-all duration-1000">
              <span className="quantum-gradient bg-clip-text text-transparent animate-pulse">Interactive Examples</span>
            </h2>
            <p className="text-xl text-editor-text max-w-3xl mx-auto mb-8 transition-all duration-1000 delay-200">
              Explore quantum computing through hands-on examples and live demonstrations
            </p>
            <Link
              href="/examples"
              className="btn-quantum inline-flex items-center group hover-lift transition-all duration-1000 delay-400"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
              <Play className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform duration-300 relative z-10" />
              <span className="relative z-10">View All Examples</span>
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 transition-all duration-1000 delay-600">
            {/* Example 1 */}
            <div
              onClick={() => handleTryExample(getExampleCode('bell-state'))}
              className="quantum-glass-dark rounded-2xl p-6 hover-lift transition-all duration-500 group cursor-pointer feature-card opacity-0 animate-fade-in"
            >
              <div className="w-full h-32 bg-gradient-to-br from-quantum-blue-light/20 to-purple-500/20 rounded-lg mb-4 flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                <Code className="w-12 h-12 text-quantum-blue-light group-hover:scale-110 transition-transform duration-300" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-quantum-blue-light transition-colors duration-300">Bell State (Cirq)</h3>
              <p className="text-editor-text text-sm mb-4 group-hover:text-gray-200 transition-colors duration-300">
                Create quantum entanglement with H + CNOT gates. Expect 50% |00⟩ and 50% |11⟩
              </p>
              <div className="flex items-center justify-between">
                <span className="text-xs bg-quantum-blue-light/20 text-quantum-blue-light px-2 py-1 rounded group-hover:bg-quantum-blue-light/40 transition-colors duration-300">Beginner</span>
                <ArrowRight className="w-4 h-4 text-quantum-blue-light group-hover:translate-x-2 transition-transform duration-300" />
              </div>
            </div>

            {/* Example 2 */}
            <div
              onClick={() => handleTryExample(getExampleCode('quantum-teleportation'))}
              className="quantum-glass-dark rounded-2xl p-6 hover-lift transition-all duration-500 group cursor-pointer feature-card opacity-0 animate-fade-in"
            >
              <div className="w-full h-32 bg-gradient-to-br from-purple-500/20 to-teal-500/20 rounded-lg mb-4 flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                <Play className="w-12 h-12 text-purple-400 group-hover:scale-110 transition-transform duration-300" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-purple-400 transition-colors duration-300">Teleportation (Qiskit)</h3>
              <p className="text-editor-text text-sm mb-4 group-hover:text-gray-200 transition-colors duration-300">
                Transfer quantum states using entanglement with Bell measurement and classical corrections
              </p>
              <div className="flex items-center justify-between">
                <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded group-hover:bg-purple-500/40 transition-colors duration-300">Intermediate</span>
                <ArrowRight className="w-4 h-4 text-purple-400 group-hover:translate-x-2 transition-transform duration-300" />
              </div>
            </div>

            {/* Example 3 */}
            <div
              onClick={() => handleTryExample(getExampleCode('grovers-search'))}
              className="quantum-glass-dark rounded-2xl p-6 hover-lift transition-all duration-500 group cursor-pointer feature-card opacity-0 animate-fade-in"
            >
              <div className="w-full h-32 bg-gradient-to-br from-teal-500/20 to-green-500/20 rounded-lg mb-4 flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                <Atom className="w-12 h-12 text-teal-400 group-hover:scale-110 transition-transform duration-300" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-teal-400 transition-colors duration-300">Grover&apos;s Search (PennyLane)</h3>
              <p className="text-editor-text text-sm mb-4 group-hover:text-gray-200 transition-colors duration-300">
                Quantum search algorithm with oracle and diffusion operator for quadratic speedup
              </p>
              <div className="flex items-center justify-between">
                <span className="text-xs bg-teal-500/20 text-teal-400 px-2 py-1 rounded group-hover:bg-teal-500/40 transition-colors duration-300">Advanced</span>
                <ArrowRight className="w-4 h-4 text-teal-400 group-hover:translate-x-2 transition-transform duration-300" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-quantum-blue-light/10 to-purple-500/10 relative overflow-hidden">
        {/* Additional floating elements for CTA */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-10 left-10 animate-float delay-1000">
            <Star className="w-6 h-6 text-quantum-blue-light opacity-30" />
          </div>
          <div className="absolute bottom-10 right-10 animate-float-reverse delay-1500">
            <Sparkles className="w-5 h-5 text-purple-400 opacity-40" />
          </div>
        </div>

        <div className="max-w-4xl mx-auto text-center relative z-10 transition-all duration-1000">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 transition-all duration-1000">
            <span className="quantum-gradient bg-clip-text text-transparent animate-pulse">Ready to Start Your</span>
            <br />
            <span className="text-white transition-all duration-1000 delay-200">Quantum Journey?</span>
          </h2>
          <p className="text-xl text-editor-text mb-8 max-w-2xl mx-auto transition-all duration-1000 delay-400">
            Join thousands of researchers, students, and developers building
            the future of quantum computing with {config.project.name}.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center transition-all duration-1000 delay-600">
            <Link
              href="/login"
              className="btn-quantum text-lg px-8 py-4 flex items-center justify-center group hover-lift relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
              <Zap className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform duration-300 relative z-10" />
              <span className="relative z-10">Launch QCanvas</span>
            </Link>
            <Link
              href="/docs"
              className="btn-ghost text-lg px-8 py-4 flex items-center justify-center group hover-lift relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-quantum-blue-light/10 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
              <BookOpen className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform duration-300 relative z-10" />
              <span className="relative z-10">Read Documentation</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 border-t border-white/10">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
            <div className="md:col-span-2">
              <Link href="/" className="flex items-center space-x-2 mb-4 group">
                <div className="relative">
                  <Image
                    src="/QCanvas-logo-Black.svg"
                    alt="QCanvas Logo"
                    width={40}
                    height={40}
                    className="object-contain block dark:hidden transition-all duration-300 group-hover:scale-110 group-hover:rotate-6 animate-pulse"
                  />
                  <Image
                    src="/QCanvas-logo-White.svg"
                    alt="QCanvas Logo"
                    width={40}
                    height={40}
                    className="object-contain hidden dark:block transition-all duration-300 group-hover:scale-110 group-hover:rotate-6 animate-pulse"
                  />
                </div>
                <span className="text-xl font-bold quantum-gradient bg-clip-text text-transparent group-hover:scale-105 transition-transform duration-200">
                  QCanvas
                </span>
              </Link>
            <p className="text-editor-text mb-4 max-w-md">
              {config.project.description}
            </p>
              <div className="flex space-x-4">
                <a
                  href={config.social.github}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-editor-text hover:text-white transition-colors duration-200"
                >
                  <GitBranch className="w-5 h-5" />
                </a>
                <a
                  href={config.social.linkedin}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-editor-text hover:text-white transition-colors duration-200"
                >
                  <Globe className="w-5 h-5" />
                </a>
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-white mb-4">Platform</h4>
              <div className="space-y-2">
                {config.footer.platform.map((link) => (
                  <Link
                    key={link.path}
                    href={link.path as any}
                    className="block text-editor-text hover:text-white transition-colors duration-200"
                  >
                    {link.name}
                  </Link>
                ))}
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-white mb-4">Community</h4>
              <div className="space-y-2">
                {config.footer.community.map((link) => (
                  <a
                    key={link.url}
                    href={link.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block text-editor-text hover:text-white transition-colors duration-200"
                  >
                    {link.name}
                  </a>
                ))}
              </div>
            </div>
          </div>

          <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-editor-text text-sm">
              {getCopyrightText()}
            </p>
            <div className="flex items-center space-x-6 mt-4 md:mt-0">
              <button className="text-editor-text hover:text-white transition-colors duration-200 text-sm cursor-not-allowed opacity-60" title="Coming Soon">Privacy</button>
              <button className="text-editor-text hover:text-white transition-colors duration-200 text-sm cursor-not-allowed opacity-60" title="Coming Soon">Terms</button>
              <a href={`mailto:${config.contact.support}`} className="text-editor-text hover:text-white transition-colors duration-200 text-sm">Support</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
