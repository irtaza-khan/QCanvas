'use client'

import { useState, useEffect } from 'react'
import { 
  Terminal, 
  BarChart3, 
  Minimize2, 
  Maximize2, 
  Trash2,
  Copy,
  Download,
  Play,
  FileCode2,
  AlertCircle,
  AlertTriangle,
  XCircle,
  CheckCircle,
  Activity,
  Clock,
  Cpu,
  Zap,
  TrendingUp,
  Database
} from 'lucide-react'
import toast from 'react-hot-toast'
import { useFileStore } from '@/lib/store'

interface LogEntry {
  id: string
  timestamp: string
  type: 'info' | 'success' | 'error' | 'warning'
  message: string
}

interface ErrorEntry {
  id: string
  severity: 'error' | 'warning' | 'info'
  message: string
  line: number
  column: number
  file: string
  code: string
  suggestion?: string
}

export default function ResultsPane() {
  const { resultsCollapsed, toggleResults, compiledQasm, getActiveFile, conversionStats } = useFileStore()
  
  // Helper function to get display stats from backend conversion stats
  const getDisplayStats = () => {
    if (!conversionStats) {
      // Default empty stats when no conversion has been done
      return {
        compilation: {
          status: 'pending',
          time: '-',
          originalGates: 0,
          optimizedGates: 0,
          reductionPercentage: 0,
          circuitDepth: 0,
          qubits: 0,
          classicalBits: 0,
          warnings: 0,
          errors: 0
        },
        circuit: {
          gates: {},
          depth: 0,
          width: 0,
          complexity: 'Unknown',
          entanglingGates: 0,
          singleQubitGates: 0
        },
        execution: {
          status: 'pending',
          totalTime: '-',
          simulationTime: '-',
          postProcessingTime: '-',
          shots: 0,
          successfulShots: 0,
          backend: 'N/A',
          memoryUsage: '-',
          cpuUsage: '-',
          fidelity: 0
        },
        optimization: {
          level: 0,
          timeSpent: '-',
          gatesReduced: 0,
          depthReduced: 0,
          techniques: [] as string[]
        }
      }
    }

    // Convert backend stats to display format
    const gates = conversionStats.gates || {}
    const totalGates = Object.values(gates).reduce((sum: number, count) => sum + (count || 0), 0)
    const entanglingGates = ['cx', 'cnot', 'cz', 'swap', 'ccx'].reduce((sum, gate) => sum + (gates[gate] || 0), 0)
    const singleQubitGates = totalGates - entanglingGates

    return {
      compilation: {
        status: conversionStats.success ? 'success' : 'failed',
        time: conversionStats.conversion_time || 'N/A',
        originalGates: totalGates,
        optimizedGates: totalGates, // Same for now
        reductionPercentage: 0,
        circuitDepth: conversionStats.depth || 0,
        qubits: conversionStats.qubits || 0,
        classicalBits: 0, // Not tracked yet
        warnings: 0,
        errors: conversionStats.error ? 1 : 0
      },
      circuit: {
        gates: gates,
        depth: conversionStats.depth || 0,
        width: conversionStats.qubits || 0,
        complexity: totalGates > 10 ? 'High' : totalGates > 5 ? 'Medium' : 'Low',
        entanglingGates: entanglingGates,
        singleQubitGates: singleQubitGates
      },
      execution: {
        status: 'pending',
        totalTime: '-',
        simulationTime: '-',
        postProcessingTime: '-',
        shots: 0,
        successfulShots: 0,
        backend: 'N/A',
        memoryUsage: '-',
        cpuUsage: '-',
        fidelity: 0
      },
      optimization: {
        level: 0,
        timeSpent: '-',
        gatesReduced: 0,
        depthReduced: 0,
        techniques: [] as string[]
      }
    }
  }
  const [activeTab, setActiveTab] = useState<'console' | 'output' | 'histogram' | 'qasm' | 'errors' | 'stats'>('console')
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      id: '1',
      timestamp: new Date().toISOString(),
      type: 'info',
      message: 'QCanvas Quantum Editor initialized'
    }
  ])

  // Mock errors data - in real app, this would come from actual code analysis
  // Errors disabled for now; will be implemented later
  const [errors, setErrors] = useState<ErrorEntry[]>([])

  // Get dynamic stats from backend conversion or use defaults
  const executionStats = getDisplayStats()
  const [legacyExecutionStats, setLegacyExecutionStats] = useState({
    compilation: {
      status: 'success',
      time: '142ms',
      originalGates: 15,
      optimizedGates: 12,
      reductionPercentage: 20,
      circuitDepth: 8,
      qubits: 3,
      classicalBits: 3,
      warnings: 1,
      errors: 0
    },
    execution: {
      status: 'completed',
      totalTime: '2.1s',
      simulationTime: '1.8s',
      postProcessingTime: '0.3s',
      shots: 1024,
      successfulShots: 1024,
      backend: 'qasm_simulator',
      memoryUsage: '45.2MB',
      cpuUsage: '23%',
      fidelity: 99.2
    },
    circuit: {
      gates: {
        h: 3,
        cx: 4,
        measure: 3,
        rz: 2,
        ry: 1
      },
      depth: 8,
      width: 3,
      complexity: 'Medium',
      entanglingGates: 4,
      singleQubitGates: 6
    },
    optimization: {
      level: 2,
      timeSpent: '38ms',
      gatesReduced: 3,
      depthReduced: 2,
      techniques: ['Gate cancellation', 'Commutation analysis', 'Single-qubit optimization']
    }
  })

  // Mock quantum results data
  const [quantumResults, setQuantumResults] = useState({
    counts: { '00': 512, '11': 512 },
    shots: 1024,
    backend: 'qasm_simulator',
    execution_time: '2.1s',
    circuit_info: {
      depth: 2,
      qubits: 2,
      gates: 3
    }
  })

  // Listen for execution events
  useEffect(() => {
    const handleExecution = () => {
      addLog('info', 'Starting quantum circuit execution...')
      
      setTimeout(() => {
        addLog('success', 'Circuit executed successfully')
        addLog('info', `Execution time: ${quantumResults.execution_time}`)
        
        // Update execution stats with new data
        setLegacyExecutionStats(prev => ({
          ...prev,
          execution: {
            ...prev.execution,
            status: 'completed',
            totalTime: quantumResults.execution_time,
            simulationTime: '1.8s',
            postProcessingTime: '0.3s'
          }
        }))
        
        // Automatically switch to stats tab after execution
        setActiveTab('stats')
        toast.success('Execution complete! View stats for detailed analysis.')
      }, 2000)
    }

    // Listen for custom events from TopBar
    window.addEventListener('circuit-execute', handleExecution)
    return () => window.removeEventListener('circuit-execute', handleExecution)
  }, [quantumResults.execution_time])

  useEffect(() => {
    const showQasm = () => setActiveTab('qasm')
    window.addEventListener('show-qasm', showQasm)
    return () => window.removeEventListener('show-qasm', showQasm)
  }, [])

  const addLog = (type: LogEntry['type'], message: string) => {
    const newLog: LogEntry = {
      id: Date.now().toString(),
      timestamp: new Date().toISOString(),
      type,
      message
    }
    setLogs(prev => [...prev, newLog])
  }

  const clearLogs = () => {
    setLogs([])
    toast.success('Console cleared')
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    toast.success('Copied to clipboard')
  }

  const downloadResults = () => {
    const results = {
      timestamp: new Date().toISOString(),
      quantum_results: quantumResults,
      logs: logs
    }
    
    const dataStr = JSON.stringify(results, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = `qcanvas-results-${Date.now()}.json`
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
    
    toast.success('Results downloaded')
  }

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  const getLogIcon = (type: LogEntry['type']) => {
    switch (type) {
      case 'success':
        return '✓'
      case 'error':
        return '✗'
      case 'warning':
        return '⚠'
      default:
        return 'ℹ'
    }
  }

  const getLogColor = (type: LogEntry['type']) => {
    switch (type) {
      case 'success':
        return 'text-green-400'
      case 'error':
        return 'text-red-400'
      case 'warning':
        return 'text-yellow-400'
      default:
        return 'text-blue-400'
    }
  }

  const getErrorIcon = (severity: ErrorEntry['severity']) => {
    switch (severity) {
      case 'error':
        return <XCircle className="w-4 h-4 text-red-400" />
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-yellow-400" />
      case 'info':
        return <AlertCircle className="w-4 h-4 text-blue-400" />
      default:
        return <AlertCircle className="w-4 h-4 text-gray-400" />
    }
  }

  const getErrorColor = (severity: ErrorEntry['severity']) => {
    switch (severity) {
      case 'error':
        return 'text-red-400'
      case 'warning':
        return 'text-yellow-400'
      case 'info':
        return 'text-blue-400'
      default:
        return 'text-gray-400'
    }
  }

  const clearErrors = () => {
    setErrors([])
    toast.success('Errors cleared')
  }

  if (resultsCollapsed) {
    return (
      <div className="h-8 bg-editor-sidebar border-t border-editor-border flex items-center justify-between px-4">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-editor-text" />
          <span className="text-sm text-editor-text">Results</span>
        </div>
        <button
          onClick={toggleResults}
          className="btn-ghost p-1"
          title="Expand Results"
        >
          <Maximize2 className="w-4 h-4" />
        </button>
      </div>
    )
  }

  return (
    <div className="h-full results-panel flex flex-col">
      {/* Results Header */}
      <div className="h-12 bg-editor-sidebar border-b border-editor-border flex items-center justify-between px-4 flex-shrink-0">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-editor-text" />
            <span className="text-sm font-medium text-white">Results</span>
          </div>
          
          {/* Tabs */}
          <div className="flex items-center space-x-1">
            {[
              { id: 'console', label: 'Console', icon: Terminal },
              { id: 'output', label: 'Output', icon: Terminal },
              { id: 'histogram', label: 'Histogram', icon: BarChart3 },
              { id: 'qasm', label: 'OpenQASM', icon: FileCode2 },
              { id: 'errors', label: 'Errors', icon: AlertCircle, count: errors.filter(e => e.severity === 'error').length },
              { id: 'stats', label: 'Stats', icon: Activity },
            ].map(({ id, label, icon: Icon, count }) => (
              <button
                key={id}
                onClick={() => setActiveTab(id as any)}
                className={`px-3 py-1 text-xs rounded-md transition-colors flex items-center ${
                  activeTab === id
                    ? 'bg-editor-accent text-white'
                    : 'text-editor-text hover:bg-editor-border'
                }`}
              >
                <Icon className="w-3 h-3 mr-1" />
                {label}
                {count !== undefined && count > 0 && (
                  <span className="ml-1 px-1.5 py-0.5 text-xs bg-red-500 text-white rounded-full">
                    {count}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={downloadResults}
            className="btn-ghost p-1"
            title="Download Results"
          >
            <Download className="w-4 h-4" />
          </button>
          
          {activeTab === 'errors' ? (
            <button
              onClick={clearErrors}
              className="btn-ghost p-1"
              title="Clear Errors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          ) : (
            <button
              onClick={clearLogs}
              className="btn-ghost p-1"
              title="Clear Console"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
          
          <button
            onClick={toggleResults}
            className="btn-ghost p-1"
            title="Minimize Results"
          >
            <Minimize2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Results Content */}
      <div className="flex-1 overflow-hidden">
        {activeTab === 'console' && (
          <div className="h-full overflow-y-auto results-content">
            {logs.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Terminal className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No console output yet</p>
              </div>
            ) : (
              <div className="space-y-1">
                {logs.map((log) => (
                  <div key={log.id} className="flex items-start space-x-3 py-1 hover:bg-editor-border hover:bg-opacity-50 rounded px-2">
                    <span className="text-xs text-gray-500 mt-0.5 min-w-[60px]">
                      {formatTimestamp(log.timestamp)}
                    </span>
                    <span className={`${getLogColor(log.type)} mt-0.5`}>
                      {getLogIcon(log.type)}
                    </span>
                    <span className="flex-1 text-sm text-editor-text">
                      {log.message}
                    </span>
                    <button
                      onClick={() => copyToClipboard(log.message)}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:bg-editor-border rounded"
                      title="Copy"
                    >
                      <Copy className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'output' && (
          <div className="h-full overflow-y-auto results-content">
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-white mb-2">Quantum Results</h4>
                <div className="bg-editor-bg border border-editor-border rounded p-3">
                  <pre className="text-sm text-editor-text">
                    {JSON.stringify(quantumResults, null, 2)}
                  </pre>
                </div>
              </div>
              
              <div>
                <h4 className="text-sm font-medium text-white mb-2">Circuit Information</h4>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-gray-400">Qubits:</span>
                    <span className="text-white ml-2">{quantumResults.circuit_info.qubits}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Depth:</span>
                    <span className="text-white ml-2">{quantumResults.circuit_info.depth}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Gates:</span>
                    <span className="text-white ml-2">{quantumResults.circuit_info.gates}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'histogram' && (
          <div className="h-full overflow-y-auto results-content">
            <div>
              <h4 className="text-sm font-medium text-white mb-4">Measurement Results</h4>
              
              {/* Histogram Bars */}
              <div className="space-y-2">
                {Object.entries(quantumResults.counts).map(([state, count]) => {
                  const percentage = (count / quantumResults.shots) * 100
                  const barWidth = percentage
                  
                  return (
                    <div key={state} className="flex items-center space-x-3">
                      <span className="text-sm font-mono text-white min-w-[30px]">
                        |{state}⟩
                      </span>
                      <div className="flex-1 relative">
                        <div className="h-6 bg-editor-border rounded-full overflow-hidden">
                          <div
                            className="h-full quantum-gradient rounded-full transition-all duration-500"
                            style={{ width: `${barWidth}%` }}
                          />
                        </div>
                        <span className="absolute inset-0 flex items-center justify-center text-xs font-medium text-white">
                          {count} ({percentage.toFixed(1)}%)
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>
              
              <div className="mt-4 pt-4 border-t border-editor-border">
                <div className="flex justify-between text-sm text-gray-400">
                  <span>Total Shots: {quantumResults.shots}</span>
                  <span>Backend: {quantumResults.backend}</span>
                  <span>Time: {quantumResults.execution_time}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'qasm' && (
          <div className="h-full overflow-y-auto results-content">
            {!compiledQasm ? (
              <div className="text-center py-8 text-gray-500">
                <FileCode2 className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No compiled OpenQASM yet. Use "Compile to QASM" in the top bar.</p>
              </div>
            ) : (
              <div className="bg-editor-bg border border-editor-border rounded p-3">
                <pre className="text-sm text-editor-text whitespace-pre-wrap">{compiledQasm}</pre>
              </div>
            )}
          </div>
        )}

        {activeTab === 'errors' && (
          <div className="h-full overflow-y-auto results-content">
            {errors.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <CheckCircle className="w-8 h-8 mx-auto mb-2 opacity-50 text-green-400" />
                <p className="text-sm">No errors found! Your code looks good.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {/* Error Summary */}
                <div className="bg-editor-bg border border-editor-border rounded-lg p-4 mb-4">
                  <h4 className="text-sm font-medium text-white mb-3">Error Summary</h4>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
                      <div className="text-lg font-bold text-red-400">
                        {errors.filter(e => e.severity === 'error').length}
                      </div>
                      <div className="text-xs text-red-300">Errors</div>
                    </div>
                    <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
                      <div className="text-lg font-bold text-yellow-400">
                        {errors.filter(e => e.severity === 'warning').length}
                      </div>
                      <div className="text-xs text-yellow-300">Warnings</div>
                    </div>
                    <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
                      <div className="text-lg font-bold text-blue-400">
                        {errors.filter(e => e.severity === 'info').length}
                      </div>
                      <div className="text-xs text-blue-300">Info</div>
                    </div>
                  </div>
                </div>

                {/* Error List */}
                <div className="space-y-3">
                  {errors.map((error) => (
                    <div key={error.id} className="bg-editor-bg border border-editor-border rounded-lg p-4 hover:border-quantum-blue-light/30 transition-colors">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0 mt-0.5">
                          {getErrorIcon(error.severity)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <p className={`text-sm font-medium ${getErrorColor(error.severity)}`}>
                                {error.message}
                              </p>
                              <div className="flex items-center space-x-4 mt-1 text-xs text-gray-400">
                                <span>📁 {error.file}</span>
                                <span>📍 Line {error.line}:{error.column}</span>
                                <span className="px-2 py-1 bg-editor-border rounded text-white capitalize">
                                  {error.severity}
                                </span>
                              </div>
                            </div>
                            <button
                              onClick={() => copyToClipboard(error.message)}
                              className="p-1 hover:bg-editor-border rounded transition-colors ml-2"
                              title="Copy error message"
                            >
                              <Copy className="w-3 h-3 text-gray-400" />
                            </button>
                          </div>

                          {/* Code snippet */}
                          <div className="mt-3 bg-gray-900 border border-gray-700 rounded p-2">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-xs text-gray-400">Problematic code:</span>
                              <span className="text-xs text-gray-500">Line {error.line}</span>
                            </div>
                            <pre className="text-xs text-red-300 font-mono bg-red-900/20 px-2 py-1 rounded">
                              {error.code}
                            </pre>
                          </div>

                          {/* Suggestion */}
                          {error.suggestion && (
                            <div className="mt-3 bg-blue-900/20 border border-blue-700/30 rounded p-3">
                              <div className="flex items-center space-x-2 mb-2">
                                <AlertCircle className="w-3 h-3 text-blue-400" />
                                <span className="text-xs font-medium text-blue-300">Suggestion:</span>
                              </div>
                              <p className="text-sm text-blue-200">{error.suggestion}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'stats' && (
          <div className="h-full overflow-y-auto results-content">
            <div className="space-y-6">
              {/* Execution Summary */}
              <div className="bg-editor-bg border border-editor-border rounded-lg p-4">
                <h4 className="text-sm font-medium text-white mb-4 flex items-center">
                  <Activity className="w-4 h-4 mr-2" />
                  Execution Summary
                </h4>
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3 text-center">
                    <div className="text-lg font-bold text-green-400">{executionStats.execution.status}</div>
                    <div className="text-xs text-green-300">Status</div>
                  </div>
                  <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 text-center">
                    <div className="text-lg font-bold text-blue-400">{executionStats.execution.totalTime}</div>
                    <div className="text-xs text-blue-300">Total Time</div>
                  </div>
                  <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-3 text-center">
                    <div className="text-lg font-bold text-purple-400">{executionStats.execution.fidelity}%</div>
                    <div className="text-xs text-purple-300">Fidelity</div>
                  </div>
                </div>
              </div>

              {/* Performance Metrics */}
              <div className="bg-editor-bg border border-editor-border rounded-lg p-4">
                <h4 className="text-sm font-medium text-white mb-4 flex items-center">
                  <TrendingUp className="w-4 h-4 mr-2" />
                  Performance Metrics
                </h4>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h5 className="text-xs font-medium text-gray-400 mb-3">Timing Breakdown</h5>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Simulation:</span>
                        <span className="text-sm text-white">{executionStats.execution.simulationTime}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Post-processing:</span>
                        <span className="text-sm text-white">{executionStats.execution.postProcessingTime}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Memory Usage:</span>
                        <span className="text-sm text-white">{executionStats.execution.memoryUsage}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">CPU Usage:</span>
                        <span className="text-sm text-white">{executionStats.execution.cpuUsage}</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h5 className="text-xs font-medium text-gray-400 mb-3">Shot Statistics</h5>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Total Shots:</span>
                        <span className="text-sm text-white">{executionStats.execution.shots.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Successful:</span>
                        <span className="text-sm text-green-400">{executionStats.execution.successfulShots.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Backend:</span>
                        <span className="text-sm text-white">{executionStats.execution.backend}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Circuit Analysis */}
              <div className="bg-editor-bg border border-editor-border rounded-lg p-4">
                <h4 className="text-sm font-medium text-white mb-4 flex items-center">
                  <Cpu className="w-4 h-4 mr-2" />
                  Circuit Analysis
                </h4>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h5 className="text-xs font-medium text-gray-400 mb-3">Circuit Properties</h5>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Depth:</span>
                        <span className="text-sm text-white">{executionStats.circuit.depth}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Width:</span>
                        <span className="text-sm text-white">{executionStats.circuit.width} qubits</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Complexity:</span>
                        <span className="text-sm text-yellow-400">{executionStats.circuit.complexity}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Entangling Gates:</span>
                        <span className="text-sm text-white">{executionStats.circuit.entanglingGates}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Single-Qubit Gates:</span>
                        <span className="text-sm text-white">{executionStats.circuit.singleQubitGates}</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h5 className="text-xs font-medium text-gray-400 mb-3">Gate Distribution</h5>
                    <div className="space-y-2">
                      {Object.entries(executionStats.circuit.gates).map(([gate, count]) => (
                        <div key={gate} className="flex justify-between items-center">
                          <span className="text-sm text-editor-text font-mono">{gate.toUpperCase()}:</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-16 h-2 bg-editor-border rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-quantum-blue-light rounded-full"
                                style={{ 
                                  width: `${(count / Math.max(...Object.values(executionStats.circuit.gates))) * 100}%` 
                                }}
                              />
                            </div>
                            <span className="text-sm text-white w-6">{count}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              {/* Compilation & Optimization */}
              <div className="bg-editor-bg border border-editor-border rounded-lg p-4">
                <h4 className="text-sm font-medium text-white mb-4 flex items-center">
                  <Zap className="w-4 h-4 mr-2" />
                  Compilation & Optimization
                </h4>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h5 className="text-xs font-medium text-gray-400 mb-3">Compilation Results</h5>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Status:</span>
                        <span className="text-sm text-green-400">{executionStats.compilation.status}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Time:</span>
                        <span className="text-sm text-white">{executionStats.compilation.time}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Warnings:</span>
                        <span className="text-sm text-yellow-400">{executionStats.compilation.warnings}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Errors:</span>
                        <span className="text-sm text-red-400">{executionStats.compilation.errors}</span>
                      </div>
                    </div>
                  </div>
                  <div>
                    <h5 className="text-xs font-medium text-gray-400 mb-3">Optimization (Level {executionStats.optimization.level})</h5>
                    <div className="space-y-2">
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Gates Reduced:</span>
                        <span className="text-sm text-green-400">-{executionStats.optimization.gatesReduced} ({executionStats.compilation.reductionPercentage}%)</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Depth Reduced:</span>
                        <span className="text-sm text-green-400">-{executionStats.optimization.depthReduced}</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-editor-text">Time Spent:</span>
                        <span className="text-sm text-white">{executionStats.optimization.timeSpent}</span>
                      </div>
                    </div>
                    <div className="mt-3">
                      <h6 className="text-xs font-medium text-gray-400 mb-2">Techniques Used:</h6>
                      <div className="flex flex-wrap gap-1">
                        {executionStats.optimization.techniques.map((technique: string, index: number) => (
                          <span key={index} className="px-2 py-1 text-xs bg-quantum-blue-light/20 text-quantum-blue-light rounded">
                            {technique}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
