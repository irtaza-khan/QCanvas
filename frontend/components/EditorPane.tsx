'use client'

import { useEffect, useRef, useState } from 'react'
import { Editor } from '@monaco-editor/react'
import { FileIcon, Code2 } from 'lucide-react'
import { useFileStore } from '@/lib/store'
import { debounce } from '@/lib/utils'
import FindReplace from './FindReplace'
import CircuitVisualization from './CircuitVisualization'

export default function EditorPane() {
  const { getActiveFile, updateFileContent } = useFileStore()
  const editorRef = useRef<any>(null)
  const activeFile = getActiveFile()
  const [showFindReplace, setShowFindReplace] = useState(false)
  const [findReplaceMode, setFindReplaceMode] = useState<'find' | 'replace'>('find')
  const [showCircuitVisualization, setShowCircuitVisualization] = useState(false)

  // Simple circuit parsing for demonstration
  const parseCircuitFromCode = (code: string) => {
    if (!code) return []
    
    const gates = []
    const lines = code.split('\n')
    let qubitIndex = 0
    
    for (const line of lines) {
      // Simple Qiskit gate detection
      if (line.includes('.h(')) {
        const match = line.match(/\.h\((\d+)\)/)
        if (match) gates.push({ type: 'h', qubit: parseInt(match[1]) })
      }
      if (line.includes('.x(')) {
        const match = line.match(/\.x\((\d+)\)/)
        if (match) gates.push({ type: 'x', qubit: parseInt(match[1]) })
      }
      if (line.includes('.cx(')) {
        const match = line.match(/\.cx\((\d+),\s*(\d+)\)/)
        if (match) gates.push({ type: 'cx', control: parseInt(match[1]), target: parseInt(match[2]), qubit: parseInt(match[1]) })
      }
      
      // Simple Cirq gate detection
      if (line.includes('cirq.H(')) {
        gates.push({ type: 'h', qubit: qubitIndex++ })
      }
      if (line.includes('cirq.X(')) {
        gates.push({ type: 'x', qubit: qubitIndex++ })
      }
      if (line.includes('cirq.CNOT(')) {
        gates.push({ type: 'cx', control: 0, target: 1, qubit: 0 })
      }
    }
    
    return gates
  }

  // Debounced content update to avoid too frequent updates
  const debouncedUpdate = useRef(
    debounce((fileId: string, content: string) => {
      updateFileContent(fileId, content)
    }, 300)
  ).current

  const handleEditorDidMount = (editor: any, monaco: any) => {
    editorRef.current = editor

    // Configure Monaco Editor themes
    monaco.editor.defineTheme('quantum-dark', {
      base: 'vs-dark',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '6A9955' },
        { token: 'keyword', foreground: '569CD6' },
        { token: 'string', foreground: 'CE9178' },
        { token: 'number', foreground: 'B5CEA8' },
        { token: 'operator', foreground: 'D4D4D4' },
        { token: 'identifier', foreground: '9CDCFE' },
      ],
      colors: {
        'editor.background': '#1e1e1e',
        'editor.foreground': '#d4d4d4',
        'editor.lineHighlightBackground': '#2a2d2e',
        'editor.selectionBackground': '#264f78',
        'editor.inactiveSelectionBackground': '#3a3d41',
        'editorCursor.foreground': '#aeafad',
        'editorWhitespace.foreground': '#3e3e42',
      },
    })

    monaco.editor.defineTheme('quantum-light', {
      base: 'vs',
      inherit: true,
      rules: [
        { token: 'comment', foreground: '6B7280' },
        { token: 'keyword', foreground: '7C3AED' },
        { token: 'string', foreground: '059669' },
        { token: 'number', foreground: 'DC2626' },
        { token: 'operator', foreground: '1F2937' },
        { token: 'identifier', foreground: '1F2937' },
      ],
      colors: {
        'editor.background': '#ffffff',
        'editor.foreground': '#1f2937',
        'editor.lineHighlightBackground': '#f8fafc',
        'editor.selectionBackground': '#dbeafe',
        'editor.inactiveSelectionBackground': '#f1f5f9',
        'editorCursor.foreground': '#1f2937',
        'editorWhitespace.foreground': '#e5e7eb',
      },
    })

    // Set theme based on current theme
    const currentTheme = document.documentElement.classList.contains('light') ? 'quantum-light' : 'quantum-dark'
    monaco.editor.setTheme(currentTheme)

    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      // Save functionality will be handled by TopBar
      // This prevents default browser save dialog
    })

    // Find and Replace shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyF, () => {
      setFindReplaceMode('find')
      setShowFindReplace(true)
    })

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyH, () => {
      setFindReplaceMode('replace')
      setShowFindReplace(true)
    })

    // Add quantum-specific snippets for Python/Qiskit
    monaco.languages.registerCompletionItemProvider('python', {
      provideCompletionItems: () => {
        return {
          suggestions: [
            {
              label: 'qiskit-bell',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: [
                'from qiskit import QuantumCircuit, execute, Aer',
                '',
                '# Create Bell state circuit',
                'qc = QuantumCircuit(2, 2)',
                'qc.h(0)  # Hadamard gate',
                'qc.cx(0, 1)  # CNOT gate',
                'qc.measure_all()',
                '',
                '# Execute circuit',
                'backend = Aer.get_backend("qasm_simulator")',
                'job = execute(qc, backend, shots=1024)',
                'result = job.result()',
                'counts = result.get_counts(qc)',
                'print(counts)',
              ].join('\n'),
              documentation: 'Create a Bell state quantum circuit',
            },
            {
              label: 'qiskit-grover',
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: [
                'from qiskit import QuantumCircuit, execute, Aer',
                'import numpy as np',
                '',
                'def grovers_algorithm(n_qubits, oracle):',
                '    qc = QuantumCircuit(n_qubits, n_qubits)',
                '    ',
                '    # Initialize superposition',
                '    qc.h(range(n_qubits))',
                '    ',
                '    # Apply oracle',
                '    oracle(qc)',
                '    ',
                '    # Diffusion operator',
                '    qc.h(range(n_qubits))',
                '    qc.x(range(n_qubits))',
                '    qc.h(n_qubits-1)',
                '    qc.mct(list(range(n_qubits-1)), n_qubits-1)',
                '    qc.h(n_qubits-1)',
                '    qc.x(range(n_qubits))',
                '    qc.h(range(n_qubits))',
                '    ',
                '    qc.measure_all()',
                '    return qc',
              ].join('\n'),
              documentation: "Grover's algorithm template",
            },
          ],
        }
      },
    })
  }

  const handleEditorChange = (value: string | undefined) => {
    if (activeFile && value !== undefined) {
      debouncedUpdate(activeFile.id, value)
    }
  }

  // Handle keyboard shortcuts globally
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        // Trigger save action
        const event = new CustomEvent('save-file')
        window.dispatchEvent(event)
      } else if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault()
        setFindReplaceMode('find')
        setShowFindReplace(true)
      } else if ((e.ctrlKey || e.metaKey) && e.key === 'h') {
        e.preventDefault()
        setFindReplaceMode('replace')
        setShowFindReplace(true)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [])

  // Handle find events from TopBar
  useEffect(() => {
    const handleOpenFind = (e: CustomEvent) => {
      const mode = e.detail?.mode || 'find'
      setFindReplaceMode(mode)
      setShowFindReplace(true)
    }

    window.addEventListener('open-find', handleOpenFind as EventListener)
    return () => window.removeEventListener('open-find', handleOpenFind as EventListener)
  }, [])

  // Get Monaco language from file extension
  const getMonacoLanguage = (language: string) => {
    switch (language) {
      case 'python':
        return 'python'
      case 'javascript':
        return 'javascript'
      case 'typescript':
        return 'typescript'
      case 'json':
        return 'json'
      case 'qasm':
        return 'plaintext' // Monaco doesn't have QASM support, use plaintext
      default:
        return 'plaintext'
    }
  }

  if (!activeFile) {
    return (
      <div className="editor-pane">
        <div className="flex-1 flex items-center justify-center bg-editor-bg">
          <div className="text-center">
            <FileIcon className="w-16 h-16 mx-auto mb-4 text-gray-500 opacity-50" />
            <h3 className="text-lg font-medium text-editor-text mb-2">
              No File Selected
            </h3>
            <p className="text-gray-500 text-sm">
              Select a file from the sidebar to start editing
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="editor-pane">
      {/* Editor Header */}
      <div className="h-12 bg-editor-sidebar border-b border-editor-border flex items-center justify-between px-4">
        <div className="flex items-center space-x-2">
          <Code2 className="w-4 h-4 text-editor-text" />
          <span className="text-sm font-medium text-white">{activeFile.name}</span>
          <span className="text-xs text-gray-500 bg-editor-bg px-2 py-1 rounded">
            {activeFile.language}
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          {(activeFile.language === 'python' || activeFile.language === 'qasm') && (
            <button
              onClick={() => setShowCircuitVisualization(!showCircuitVisualization)}
              className={`px-3 py-1 text-xs rounded-md transition-colors ${
                showCircuitVisualization
                  ? 'bg-quantum-blue-light text-white'
                  : 'text-editor-text hover:bg-editor-border'
              }`}
            >
              Circuit View
            </button>
          )}
        </div>
      </div>

      {/* Find and Replace */}
      <FindReplace
        isVisible={showFindReplace}
        onClose={() => setShowFindReplace(false)}
        mode={findReplaceMode}
        editorRef={editorRef}
      />

      {/* Circuit Visualization */}
      {showCircuitVisualization && (
        <div className="h-48 bg-editor-bg border-b border-editor-border p-4 overflow-hidden">
          <h4 className="text-sm font-medium text-white mb-3">Circuit Visualization</h4>
          <CircuitVisualization
            gates={parseCircuitFromCode(activeFile.content)}
            qubits={Math.max(2, parseCircuitFromCode(activeFile.content).reduce((max, gate) => Math.max(max, gate.qubit + 1), 0))}
            className="h-32"
          />
        </div>
      )}

      {/* Monaco Editor */}
      <div className="flex-1 overflow-hidden">
        <Editor
          height="100%"
          language={getMonacoLanguage(activeFile.language)}
          value={activeFile.content}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          options={{
            theme: document.documentElement.classList.contains('light') ? 'quantum-light' : 'quantum-dark',
            fontSize: 14,
            fontFamily: 'JetBrains Mono, Fira Code, Monaco, Consolas, monospace',
            lineNumbers: 'on',
            rulers: [],
            wordWrap: 'on',
            minimap: {
              enabled: true,
              maxColumn: 120,
            },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4,
            insertSpaces: true,
            detectIndentation: true,
            renderWhitespace: 'selection',
            renderControlCharacters: false,
            cursorBlinking: 'smooth',
            cursorSmoothCaretAnimation: 'on',
            smoothScrolling: true,
            mouseWheelZoom: true,
            contextmenu: true,
            quickSuggestions: true,
            suggestOnTriggerCharacters: true,
            acceptSuggestionOnEnter: 'on',
            snippetSuggestions: 'top',
            wordBasedSuggestions: 'off',
            bracketPairColorization: {
              enabled: true,
            },
            guides: {
              bracketPairs: true,
              indentation: true,
            },
            padding: {
              top: 16,
              bottom: 16,
            },
          }}
          loading={
            <div className="flex items-center justify-center h-full bg-editor-bg">
              <div className="flex items-center space-x-2">
                <div className="w-6 h-6 border-2 border-quantum-blue-light border-t-transparent rounded-full spinner"></div>
                <span className="text-editor-text">Loading editor...</span>
              </div>
            </div>
          }
        />
      </div>
    </div>
  )
}
