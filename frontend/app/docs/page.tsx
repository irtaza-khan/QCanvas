'use client'

import { useState } from 'react'
import { Moon, Sun } from 'lucide-react'
import { useFileStore } from '@/lib/store'
import { ArrowLeft, BookOpen, Code, Cpu, BarChart3, Zap, Users, Github, Mail, Globe, FileText, Settings, Play, Download } from 'lucide-react'
import Link from 'next/link'

interface DocSection {
  id: string
  title: string
  icon: React.ReactNode
  content: React.ReactNode
}

export default function DocsPage() {
  const [activeSection, setActiveSection] = useState('getting-started')
  const { theme, toggleTheme } = useFileStore()

  const sections: DocSection[] = [
    {
      id: 'getting-started',
      title: 'Getting Started',
      icon: <Play className="w-5 h-5" />,
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Welcome to QCanvas</h3>
            <p className="text-editor-text mb-4">
              QCanvas is a modern quantum computing platform that enables seamless conversion between different quantum frameworks, 
              real-time simulation, and visualization of quantum circuits.
            </p>
            <div className="bg-editor-bg rounded-lg p-4 border border-editor-border">
              <h4 className="text-white font-medium mb-2">Quick Start Steps:</h4>
              <ol className="text-editor-text space-y-2 list-decimal list-inside">
                <li>Sign in to your QCanvas account</li>
                <li>Choose your source framework (Qiskit, Cirq, or PennyLane)</li>
                <li>Paste your quantum circuit code</li>
                <li>Select target framework for conversion</li>
                <li>Run simulation and view results</li>
              </ol>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Supported Frameworks</h3>
            <div className="grid md:grid-cols-3 gap-4">
              <div className="quantum-glass-dark rounded-lg p-4 border border-white/10">
                <div className="flex items-center mb-2">
                  <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center mr-3">
                    <Code className="w-4 h-4 text-white" />
                  </div>
                  <h4 className="text-white font-medium">Qiskit</h4>
                </div>
                <p className="text-editor-text text-sm mb-2">IBM&apos;s quantum computing framework with comprehensive tools for circuit design and execution.</p>
                <ul className="text-xs text-gray-400 space-y-1">
                  <li>• Full quantum circuit support</li>
                  <li>• Advanced optimization</li>
                  <li>• IBM Quantum backends</li>
                </ul>
              </div>
              <div className="quantum-glass-dark rounded-lg p-4 border border-white/10">
                <div className="flex items-center mb-2">
                  <div className="w-8 h-8 bg-purple-500 rounded-lg flex items-center justify-center mr-3">
                    <Code className="w-4 h-4 text-white" />
                  </div>
                  <h4 className="text-white font-medium">Cirq</h4>
                </div>
                <p className="text-editor-text text-sm mb-2">Google&apos;s quantum computing framework focused on near-term quantum computers and algorithms.</p>
                <ul className="text-xs text-gray-400 space-y-1">
                  <li>• Near-term quantum algorithms</li>
                  <li>• Noise modeling</li>
                  <li>• Google Quantum AI integration</li>
                </ul>
              </div>
              <div className="quantum-glass-dark rounded-lg p-4 border border-white/10">
                <div className="flex items-center mb-2">
                  <div className="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center mr-3">
                    <Code className="w-4 h-4 text-white" />
                  </div>
                  <h4 className="text-white font-medium">PennyLane</h4>
                </div>
                <p className="text-editor-text text-sm mb-2">Xanadu&apos;s quantum machine learning framework for variational quantum algorithms.</p>
                <ul className="text-xs text-gray-400 space-y-1">
                  <li>• Quantum machine learning</li>
                  <li>• Variational algorithms</li>
                  <li>• Hybrid quantum-classical</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'api-reference',
      title: 'API Reference',
      icon: <Code className="w-5 h-5" />,
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Conversion API</h3>
            <div className="bg-editor-bg rounded-lg p-4 border border-editor-border mb-4">
              <h4 className="text-white font-medium mb-2">POST /api/convert</h4>
              <p className="text-editor-text text-sm mb-3">Convert quantum circuits between frameworks</p>
              <pre className="text-xs text-editor-text overflow-x-auto">
{`{
  "source_framework": "qiskit",
  "target_framework": "cirq", 
  "source_code": "your_quantum_circuit_code",
  "optimization_level": 1
}`}
              </pre>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Simulation API</h3>
            <div className="bg-editor-bg rounded-lg p-4 border border-editor-border mb-4">
              <h4 className="text-white font-medium mb-2">POST /api/simulate</h4>
              <p className="text-editor-text text-sm mb-3">Simulate quantum circuits</p>
              <pre className="text-xs text-editor-text overflow-x-auto">
{`{
  "qasm_code": "your_openqasm_code",
  "backend": "statevector",
  "shots": 1000,
  "noise_model": null,
  "optimization_level": 1
}`}
              </pre>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Available Backends</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="quantum-glass-dark rounded-lg p-4 border border-white/10">
                <h4 className="text-white font-medium mb-2">Statevector Backend</h4>
                <p className="text-editor-text text-sm">Perfect simulation with full quantum state representation. Best for small circuits and exact results.</p>
              </div>
              <div className="quantum-glass-dark rounded-lg p-4 border border-white/10">
                <h4 className="text-white font-medium mb-2">Density Matrix Backend</h4>
                <p className="text-editor-text text-sm">Supports noise modeling and mixed states. Good for realistic quantum computer simulation.</p>
              </div>
              <div className="quantum-glass-dark rounded-lg p-4 border border-white/10">
                <h4 className="text-white font-medium mb-2">Stabilizer Backend</h4>
                <p className="text-editor-text text-sm">Efficient simulation for Clifford circuits. Scales well with circuit size.</p>
              </div>
              <div className="quantum-glass-dark rounded-lg p-4 border border-white/10">
                <h4 className="text-white font-medium mb-2">Noise Models</h4>
                <p className="text-editor-text text-sm">Support for depolarizing, bit-flip, phase-flip, and amplitude damping noise.</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'features',
      title: 'Features',
      icon: <Zap className="w-5 h-5" />,
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Core Features</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="quantum-glass-dark rounded-lg p-6 border border-white/10">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 quantum-gradient rounded-lg flex items-center justify-center mr-4">
                    <Code className="w-6 h-6 text-white" />
                  </div>
                  <h4 className="text-white font-medium text-lg">Framework Conversion</h4>
                </div>
                <ul className="text-editor-text space-y-2">
                  <li>• Convert between Qiskit, Cirq, and PennyLane</li>
                  <li>• Automatic OpenQASM 3.0 generation</li>
                  <li>• Circuit optimization levels 0-3</li>
                  <li>• Gate fusion and dead code elimination</li>
                </ul>
              </div>

              <div className="quantum-glass-dark rounded-lg p-6 border border-white/10">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 quantum-gradient rounded-lg flex items-center justify-center mr-4">
                    <Cpu className="w-6 h-6 text-white" />
                  </div>
                  <h4 className="text-white font-medium text-lg">Quantum Simulation</h4>
                </div>
                <ul className="text-editor-text space-y-2">
                  <li>• Multiple simulation backends</li>
                  <li>• Configurable shot counts</li>
                  <li>• Noise modeling support</li>
                  <li>• Real-time execution</li>
                </ul>
              </div>

              <div className="quantum-glass-dark rounded-lg p-6 border border-white/10">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 quantum-gradient rounded-lg flex items-center justify-center mr-4">
                    <BarChart3 className="w-6 h-6 text-white" />
                  </div>
                  <h4 className="text-white font-medium text-lg">Visualization</h4>
                </div>
                <ul className="text-editor-text space-y-2">
                  <li>• Circuit diagrams</li>
                  <li>• Measurement histograms</li>
                  <li>• State vector plots</li>
                  <li>• Interactive charts</li>
                </ul>
              </div>

              <div className="quantum-glass-dark rounded-lg p-6 border border-white/10">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 quantum-gradient rounded-lg flex items-center justify-center mr-4">
                    <Settings className="w-6 h-6 text-white" />
                  </div>
                  <h4 className="text-white font-medium text-lg">Advanced Features</h4>
                </div>
                <ul className="text-editor-text space-y-2">
                  <li>• File management system</li>
                  <li>• Keyboard shortcuts</li>
                  <li>• Auto-save functionality</li>
                  <li>• Export capabilities</li>
                </ul>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Optimization Levels</h3>
            <div className="grid md:grid-cols-4 gap-4">
              <div className="quantum-glass-dark rounded-lg p-4 border border-white/10 text-center">
                <div className="w-12 h-12 quantum-gradient rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-white font-bold">0</span>
                </div>
                <h4 className="text-white font-medium mb-2">Level 0</h4>
                <p className="text-editor-text text-sm">No optimization, direct conversion</p>
              </div>
              <div className="quantum-glass-dark rounded-lg p-4 border border-white/10 text-center">
                <div className="w-12 h-12 quantum-gradient rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-white font-bold">1</span>
                </div>
                <h4 className="text-white font-medium mb-2">Level 1</h4>
                <p className="text-editor-text text-sm">Basic gate fusion and simplification</p>
              </div>
              <div className="quantum-glass-dark rounded-lg p-4 border border-white/10 text-center">
                <div className="w-12 h-12 quantum-gradient rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-white font-bold">2</span>
                </div>
                <h4 className="text-white font-medium mb-2">Level 2</h4>
                <p className="text-editor-text text-sm">Advanced optimization and dead code elimination</p>
              </div>
              <div className="quantum-glass-dark rounded-lg p-4 border border-white/10 text-center">
                <div className="w-12 h-12 quantum-gradient rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-white font-bold">3</span>
                </div>
                <h4 className="text-white font-medium mb-2">Level 3</h4>
                <p className="text-editor-text text-sm">Maximum optimization with custom algorithms</p>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'tutorials',
      title: 'Tutorials',
      icon: <BookOpen className="w-5 h-5" />,
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Step-by-Step Tutorials</h3>
            
            <div className="space-y-4">
              <div className="quantum-glass-dark rounded-lg p-6 border border-white/10">
                <h4 className="text-white font-medium text-lg mb-3">Tutorial 1: Your First Quantum Circuit</h4>
                <div className="text-editor-text space-y-3">
                  <p>Learn how to create and convert your first quantum circuit using QCanvas.</p>
                  <div className="bg-editor-bg rounded p-3 border border-editor-border">
                    <h5 className="text-white font-medium mb-2">Steps:</h5>
                    <ol className="space-y-1 text-sm">
                      <li>1. Open QCanvas and sign in</li>
                      <li>2. Create a new file with Qiskit Bell state code</li>
                      <li>3. Convert to Cirq format</li>
                      <li>4. Run simulation and view results</li>
                    </ol>
                  </div>
                </div>
              </div>

              <div className="quantum-glass-dark rounded-lg p-6 border border-white/10">
                <h4 className="text-white font-medium text-lg mb-3">Tutorial 2: Advanced Optimization</h4>
                <div className="text-editor-text space-y-3">
                  <p>Explore different optimization levels and their effects on circuit performance.</p>
                  <div className="bg-editor-bg rounded p-3 border border-editor-border">
                    <h5 className="text-white font-medium mb-2">Steps:</h5>
                    <ol className="space-y-1 text-sm">
                      <li>1. Create a complex quantum circuit</li>
                      <li>2. Test conversion with different optimization levels</li>
                      <li>3. Compare circuit depth and gate counts</li>
                      <li>4. Analyze performance improvements</li>
                    </ol>
                  </div>
                </div>
              </div>

              <div className="quantum-glass-dark rounded-lg p-6 border border-white/10">
                <h4 className="text-white font-medium text-lg mb-3">Tutorial 3: Noise Simulation</h4>
                <div className="text-editor-text space-y-3">
                  <p>Learn how to simulate quantum circuits with realistic noise models.</p>
                  <div className="bg-editor-bg rounded p-3 border border-editor-border">
                    <h5 className="text-white font-medium mb-2">Steps:</h5>
                    <ol className="space-y-1 text-sm">
                      <li>1. Create a quantum circuit</li>
                      <li>2. Select density matrix backend</li>
                      <li>3. Configure noise parameters</li>
                      <li>4. Compare results with and without noise</li>
                    </ol>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Best Practices</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="quantum-glass-dark rounded-lg p-4 border border-white/10">
                <h4 className="text-white font-medium mb-2">Code Organization</h4>
                <ul className="text-editor-text text-sm space-y-1">
                  <li>• Use descriptive variable names</li>
                  <li>• Add comments for complex operations</li>
                  <li>• Break large circuits into functions</li>
                  <li>• Test with small examples first</li>
                </ul>
              </div>
              <div className="quantum-glass-dark rounded-lg p-4 border border-white/10">
                <h4 className="text-white font-medium mb-2">Performance Tips</h4>
                <ul className="text-editor-text text-sm space-y-1">
                  <li>• Choose appropriate optimization level</li>
                  <li>• Use suitable backend for your circuit</li>
                  <li>• Consider circuit depth and width</li>
                  <li>• Monitor execution time</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'best-practices',
      title: 'Best Practices',
      icon: <BookOpen className="w-5 h-5" />,
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Code Organization</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="quantum-glass-dark rounded-lg p-6 border border-white/10">
                <h4 className="text-white font-medium mb-3">File Structure</h4>
                <ul className="text-editor-text space-y-2 text-sm">
                  <li>• Use descriptive file names</li>
                  <li>• Organize circuits by functionality</li>
                  <li>• Keep imports at the top</li>
                  <li>• Use consistent naming conventions</li>
                </ul>
              </div>
              <div className="quantum-glass-dark rounded-lg p-6 border border-white/10">
                <h4 className="text-white font-medium mb-3">Circuit Design</h4>
                <ul className="text-editor-text space-y-2 text-sm">
                  <li>• Start with simple circuits</li>
                  <li>• Use meaningful variable names</li>
                  <li>• Add comments for complex operations</li>
                  <li>• Test incrementally</li>
                </ul>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Performance Optimization</h3>
            <div className="space-y-4">
              <div className="quantum-glass-dark rounded-lg p-6 border border-white/10">
                <h4 className="text-white font-medium mb-3">Circuit Optimization</h4>
                <div className="text-editor-text space-y-3">
                  <p>Choose the right optimization level for your needs:</p>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="bg-editor-bg rounded p-3 border border-editor-border">
                      <h5 className="text-white font-medium mb-2">Level 0-1: Development</h5>
                      <p className="text-sm">Fast conversion, minimal optimization. Good for testing and debugging.</p>
                    </div>
                    <div className="bg-editor-bg rounded p-3 border border-editor-border">
                      <h5 className="text-white font-medium mb-2">Level 2-3: Production</h5>
                      <p className="text-sm">Maximum optimization, best performance. Use for final circuits.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Common Patterns</h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="quantum-glass-dark rounded-lg p-6 border border-white/10">
                <h4 className="text-white font-medium mb-3">Entanglement Patterns</h4>
                <div className="bg-editor-bg rounded p-3 border border-editor-border">
                  <pre className="text-xs text-editor-text">
{`# Bell State
qc.h(0)
qc.cx(0, 1)

# GHZ State  
qc.h(0)
for i in range(1, n):
    qc.cx(0, i)`}
                  </pre>
                </div>
              </div>
              <div className="quantum-glass-dark rounded-lg p-6 border border-white/10">
                <h4 className="text-white font-medium mb-3">Measurement Patterns</h4>
                <div className="bg-editor-bg rounded p-3 border border-editor-border">
                  <pre className="text-xs text-editor-text">
{`# Single qubit
qc.measure(0, 0)

# Multiple qubits
qc.measure([0,1,2], [0,1,2])

# All qubits
qc.measure_all()`}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'troubleshooting',
      title: 'Troubleshooting',
      icon: <Settings className="w-5 h-5" />,
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Common Issues</h3>
            
            <div className="space-y-4">
              <div className="quantum-glass-dark rounded-lg p-6 border border-white/10">
                <h4 className="text-white font-medium text-lg mb-3">Conversion Errors</h4>
                <div className="text-editor-text space-y-3">
                  <p><strong>Problem:</strong> Circuit conversion fails with syntax errors</p>
                  <p><strong>Solution:</strong> Check that your source code follows the framework&apos;s syntax. Ensure all imports are included and variables are properly defined.</p>
                  <div className="bg-editor-bg rounded p-3 border border-editor-border">
                    <p className="text-sm"><strong>Example:</strong> Make sure to import required modules:</p>
                    <pre className="text-xs text-editor-text mt-2">from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister</pre>
                  </div>
                </div>
              </div>

              <div className="quantum-glass-dark rounded-lg p-6 border border-white/10">
                <h4 className="text-white font-medium text-lg mb-3">Simulation Timeouts</h4>
                <div className="text-editor-text space-y-3">
                  <p><strong>Problem:</strong> Large circuits take too long to simulate</p>
                  <p><strong>Solution:</strong> Use optimization levels 1-3, reduce shot count, or switch to stabilizer backend for Clifford circuits.</p>
                  <div className="bg-editor-bg rounded p-3 border border-editor-border">
                    <p className="text-sm"><strong>Tip:</strong> Start with smaller circuits and gradually increase complexity.</p>
                  </div>
                </div>
              </div>

              <div className="quantum-glass-dark rounded-lg p-6 border border-white/10">
                <h4 className="text-white font-medium text-lg mb-3">Memory Issues</h4>
                <div className="text-editor-text space-y-3">
                  <p><strong>Problem:</strong> Out of memory errors with large circuits</p>
                  <p><strong>Solution:</strong> Use density matrix or stabilizer backends instead of statevector for large circuits.</p>
                  <div className="bg-editor-bg rounded p-3 border border-editor-border">
                    <p className="text-sm"><strong>Note:</strong> Statevector backend requires 2^n complex numbers for n qubits.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-semibold text-white mb-4">Error Codes</h3>
            <div className="bg-editor-bg rounded-lg p-4 border border-editor-border">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h4 className="text-white font-medium mb-2">Conversion Errors</h4>
                  <ul className="text-editor-text text-sm space-y-1">
                    <li><strong>E001:</strong> Invalid source framework</li>
                    <li><strong>E002:</strong> Syntax error in source code</li>
                    <li><strong>E003:</strong> Unsupported gate or operation</li>
                    <li><strong>E004:</strong> Target framework not supported</li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-white font-medium mb-2">Simulation Errors</h4>
                  <ul className="text-editor-text text-sm space-y-1">
                    <li><strong>E101:</strong> Invalid QASM syntax</li>
                    <li><strong>E102:</strong> Backend not available</li>
                    <li><strong>E103:</strong> Memory limit exceeded</li>
                    <li><strong>E104:</strong> Timeout error</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      )
    }
  ]

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
              <BookOpen className="w-12 h-12 text-white" />
            </div>
            <h1 className="text-5xl font-bold text-white mb-4">
              <span className="quantum-gradient bg-clip-text text-transparent">Documentation</span>
            </h1>
            <div className="flex justify-center mb-4">
              <button onClick={toggleTheme} className="btn-ghost p-2 hover:bg-quantum-blue-light/20 rounded-lg" title="Toggle theme">
                {theme === 'dark' ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>
            </div>
            <p className="text-xl text-editor-text max-w-3xl mx-auto">
              Comprehensive guide to using QCanvas for quantum circuit conversion, simulation, and visualization. 
              Learn how to leverage the power of quantum computing across multiple frameworks.
            </p>
          </div>
        </div>
      </div>

      {/* Content */}
      <main className="px-4 py-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col lg:flex-row gap-8">
            {/* Sidebar */}
            <div className="lg:w-64 flex-shrink-0">
              <div className="quantum-glass-dark rounded-2xl p-6 backdrop-blur-xl border border-white/10 lg:sticky lg:top-8">
                <h3 className="text-lg font-semibold text-white mb-4">Contents</h3>
                <nav className="space-y-2">
                  {sections.map(section => (
                    <button
                      key={section.id}
                      onClick={() => setActiveSection(section.id)}
                      className={`w-full flex items-center px-3 py-2 rounded-lg text-left transition-colors ${
                        activeSection === section.id
                          ? 'bg-quantum-blue-light text-white'
                          : 'text-editor-text hover:text-white hover:bg-editor-border'
                      }`}
                    >
                      {section.icon}
                      <span className="ml-3">{section.title}</span>
                    </button>
                  ))}
                </nav>
              </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 min-w-0">
              <div className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10">
                {sections.find(section => section.id === activeSection)?.content}
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="px-4 py-8 border-t border-editor-border">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-editor-text">
            Need help? Check out our examples or contact our support team.
          </p>
          <div className="flex justify-center space-x-6 mt-4">
            <Link href="/examples" className="text-editor-text hover:text-white transition-colors">
              Examples
            </Link>
            <Link href="/about" className="text-editor-text hover:text-white transition-colors">
              About QCanvas
            </Link>
            <a href="https://github.com" className="text-editor-text hover:text-white transition-colors">
              GitHub
            </a>
            <a href="mailto:support@qcanvas.dev" className="text-editor-text hover:text-white transition-colors">
              Support
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
