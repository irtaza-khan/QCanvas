'use client'

import { useEffect, useRef, useState } from 'react'
import dynamic from 'next/dynamic'
import { File as FileIcon, Save, Code } from '@/components/Icons';
import { useFileStore } from '@/lib/store'
import { debounce } from '@/lib/utils'
import { getHoverForSymbol, formatHoverMarkdown } from '@/lib/quantumHoverSymbols'
import { parseCircuit, calculateQubitCount, parseCircuitWithCountAsync, ParsedGate } from '@/lib/circuitParser'
import FindReplace from './FindReplace'
import CircuitVisualization from './CircuitVisualization'

// Dynamically import 3D Visualization to avoid SSR issues
const CircuitVisualization3D = dynamic(() => import('./CircuitVisualization3D'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full text-black dark:text-gray-500">
      Loading 3D View...
    </div>
  ),
})

// Dynamically import Monaco Editor with SSR disabled to prevent server-side rendering issues
const Editor = dynamic(() => import('@monaco-editor/react').then(mod => mod.Editor), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full bg-editor-bg">
      <div className="flex items-center space-x-2">
        <div className="w-6 h-6 border-2 border-quantum-blue-light border-t-transparent rounded-full spinner"></div>
        <span className="text-editor-text">Loading editor...</span>
      </div>
    </div>
  ),
})

export default function EditorPane() {
  const { getActiveFile, updateFileContent, saveActiveFile } = useFileStore()
  const editorRef = useRef<any>(null)
  const monacoRef = useRef<any>(null)
  const hoverProviderRef = useRef<any>(null)
  const completionProviderRef = useRef<any>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const activeFile = getActiveFile()
  const [showFindReplace, setShowFindReplace] = useState(false)
  const [findReplaceMode, setFindReplaceMode] = useState<'find' | 'replace'>('find')
  const [showCircuitVisualization, setShowCircuitVisualization] = useState(false)
  const [is3DMode, setIs3DMode] = useState(false)
  const [isMounted, setIsMounted] = useState(false)
  const [circuitHeight, setCircuitHeight] = useState(200)
  const [isDraggingCircuit, setIsDraggingCircuit] = useState(false)
  
  // Parsed circuit state for async AST parsing
  const [parsedGates, setParsedGates] = useState<ParsedGate[]>([])
  const [parsedQubits, setParsedQubits] = useState(2)
  const [isParsing, setIsParsing] = useState(false)

  // Ensure component is mounted on client before rendering Monaco
  useEffect(() => {
    setIsMounted(true)
  }, [])
  
  // Async circuit parsing with debouncing
  // Uses backend AST parsing when available, falls back to regex
  useEffect(() => {
    if (!showCircuitVisualization || !activeFile?.content) {
      return
    }
    
    // Debounce the parsing to avoid too many API calls
    const timer = setTimeout(async () => {
      setIsParsing(true)
      try {
        const result = await parseCircuitWithCountAsync(activeFile.content)
        setParsedGates(result.gates)
        setParsedQubits(result.qubits)
      } catch (err) {
        // Fallback to sync parsing on error
        console.warn('Async parsing failed, using sync fallback:', err)
        const gates = parseCircuit(activeFile.content)
        setParsedGates(gates)
        setParsedQubits(calculateQubitCount(gates))
      } finally {
        setIsParsing(false)
      }
    }, 500) // 500ms debounce
    
    return () => clearTimeout(timer)
  }, [activeFile?.content, showCircuitVisualization])

  // Handle drag resize for circuit visualization panel
  useEffect(() => {
    if (!isDraggingCircuit) return

    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return

      const containerRect = containerRef.current.getBoundingClientRect()
      // Calculate height from the top of the container (after the header)
      const headerHeight = 48 // h-12 = 48px
      const newHeight = e.clientY - containerRect.top - headerHeight
      const minHeight = 100
      const maxHeight = containerRect.height - 200 // Leave space for editor

      setCircuitHeight(Math.max(minHeight, Math.min(maxHeight, newHeight)))
    }

    const handleMouseUp = () => {
      setIsDraggingCircuit(false)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDraggingCircuit])

  const handleCircuitDragStart = (e: React.MouseEvent) => {
    e.preventDefault()
    setIsDraggingCircuit(true)
  }

  // Debounced content update to avoid too frequent updates
  const debouncedUpdate = useRef(
    debounce((fileId: string, content: string) => {
      updateFileContent(fileId, content)
    }, 300)
  ).current

  const handleManualSave = async () => {
    if (editorRef.current && activeFile) {
      const content = editorRef.current.getValue()
      // Force update store immediately to ensure we save latest content
      updateFileContent(activeFile.id, content)
      await saveActiveFile()
      
      // Also download to computer
      try {
        // Try to capture and save the circuit visualization if it is visible
        if (showCircuitVisualization) {
          const svgElement = document.querySelector('svg.min-w-full') as SVGSVGElement | null;
          if (svgElement) {
            const serializer = new XMLSerializer();
            let source = serializer.serializeToString(svgElement);
            if (!source.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)) {
              source = source.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
            }
            source = '<?xml version="1.0" standalone="no"?>\r\n' + source;
            const svgUrl = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(source);
            const svgLink = document.createElement("a");
            svgLink.href = svgUrl;
            svgLink.download = activeFile.name.replace(/\.[^/.]+$/, "") + "_circuit.svg";
            document.body.appendChild(svgLink);
            svgLink.click();
            document.body.removeChild(svgLink);
          }
        }
      } catch (e) {
        console.error("Failed to download file or SVG", e);
      }
    }
  }

  const handleEditorDidMount = (editor: any, monacoInstance: any) => {
    // Guard against SSR - ensure we're in browser environment
    if (typeof window === 'undefined' || !editor || !monacoInstance) {
      return
    }

    editorRef.current = editor
    monacoRef.current = monacoInstance

    // Register language-level providers only once; dispose previous on re-mount
    if (hoverProviderRef.current) { hoverProviderRef.current.dispose(); hoverProviderRef.current = null }
    if (completionProviderRef.current) { completionProviderRef.current.dispose(); completionProviderRef.current = null }

    // Ensure Ctrl+A selects all text as a single continuous selection
    // The issue: setSelection might not clear existing multi-cursor selections
    // Solution: Use setSelections with exactly one selection to ensure a single continuous selection
    editor.addCommand(monacoInstance.KeyMod.CtrlCmd | monacoInstance.KeyCode.KeyA, () => {
      const model = editor.getModel()
      if (!model) return
      
      // Get the full range of the document
      const fullRange = model.getFullModelRange()
      
      // Create a Selection object from the Range
      // This ensures we have exactly one selection, clearing any existing multi-cursor state
      const selection = new monacoInstance.Selection(
        fullRange.startLineNumber,
        fullRange.startColumn,
        fullRange.endLineNumber,
        fullRange.endColumn
      )
      
      // Use setSelections with a single selection array to ensure exactly one continuous selection
      // This prevents the selection from being split into multiple parts
      editor.setSelections([selection])
      
      // Reveal the selection to ensure it's visible
      editor.revealRangeInCenter(fullRange)
    })

    // Configure Monaco Editor themes
    monacoInstance.editor.defineTheme('quantum-dark', {
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

    monacoInstance.editor.defineTheme('quantum-light', {
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

    // Set theme based on current theme (only in browser)
    if (typeof document !== 'undefined') {
      const currentTheme = document.documentElement.classList.contains('light') ? 'quantum-light' : 'quantum-dark'
      monacoInstance.editor.setTheme(currentTheme)
    }

    // Add keyboard shortcuts
    editor.addCommand(monacoInstance.KeyMod.CtrlCmd | monacoInstance.KeyCode.KeyS, () => {
      // Trigger save action
      handleManualSave()
    })

    // Find and Replace shortcuts
    editor.addCommand(monacoInstance.KeyMod.CtrlCmd | monacoInstance.KeyCode.KeyF, () => {
      setFindReplaceMode('find')
      setShowFindReplace(true)
    })

    editor.addCommand(monacoInstance.KeyMod.CtrlCmd | monacoInstance.KeyCode.KeyH, () => {
      setFindReplaceMode('replace')
      setShowFindReplace(true)
    })

    // Add quantum-specific snippets for Python/Qiskit
    completionProviderRef.current = monacoInstance.languages.registerCompletionItemProvider('python', {
      provideCompletionItems: () => {
        return {
          suggestions: [
            {
              label: 'qiskit-bell',
              kind: monacoInstance.languages.CompletionItemKind.Snippet,
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
              kind: monacoInstance.languages.CompletionItemKind.Snippet,
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

    // Quantum Explain It: hover tooltips for framework symbols (when explainItMode is on)
    hoverProviderRef.current = monacoInstance.languages.registerHoverProvider('python', {
      provideHover: (model: any, position: any) => {
        if (!useFileStore.getState().explainItMode) return null
        const wordAt = model.getWordAtPosition(position)
        if (!wordAt) return null
        const word = wordAt.word
        const line = model.getLineContent(position.lineNumber)
        let dottedPrefix: string | undefined
        const dotPos = wordAt.startColumn - 2
        if (dotPos >= 0 && line[dotPos] === '.') {
          const before = line.slice(0, dotPos)
          const match = before.match(/([a-zA-Z_]\w*)\s*$/)
          if (match) dottedPrefix = match[1]
        }
        const entry = getHoverForSymbol(word, dottedPrefix)
        if (!entry) return null
        const markdown = formatHoverMarkdown(entry)
        const range = new monacoInstance.Range(
          position.lineNumber,
          wordAt.startColumn,
          position.lineNumber,
          wordAt.endColumn
        )
        return {
          contents: [{ value: markdown }],
          range,
        }
      },
    })
  }

  const handleEditorChange = (value: string | undefined) => {
    if (activeFile && value !== undefined) {
      debouncedUpdate(activeFile.id, value)
    }
  }

  // Handle keyboard shortcuts globally (only on client)
  useEffect(() => {
    if (typeof window === 'undefined' || typeof document === 'undefined') return

    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        // Trigger save action
        handleManualSave()
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
  }, [handleManualSave])

  // Handle find events from TopBar (only on client)
  useEffect(() => {
    if (typeof window === 'undefined') return

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
            <FileIcon className="w-16 h-16 mx-auto mb-4 text-black dark:text-gray-500 opacity-50" />
            <h3 className="text-lg font-medium text-editor-text mb-2">
              No File Selected
            </h3>
            <p className="text-black dark:text-gray-500 text-sm">
              Select a file from the sidebar to start editing
            </p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div ref={containerRef} className="editor-pane">
      {/* Editor Header */}
      <div className="h-12 bg-editor-sidebar border-b border-editor-border flex items-center justify-between px-4">
        <div className="flex items-center space-x-2">
          <Code className="w-4 h-4 text-editor-text" />
          <span className="text-sm font-medium text-white">{activeFile.name}</span>
          <span className="text-xs text-black dark:text-gray-500 bg-editor-bg px-2 py-1 rounded">
            {activeFile.language}
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={handleManualSave}
            className="flex items-center space-x-1 px-3 py-1 text-xs text-editor-text hover:bg-editor-border rounded-md transition-colors"
            title="Save (Ctrl+S)"
          >
            <Save className="w-4 h-4" />
            <span>Save</span>
          </button>

          {(activeFile.language === 'python' || activeFile.language === 'qasm') && (
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setShowCircuitVisualization(!showCircuitVisualization)}
                className={`px-3 py-1.5 text-xs rounded-md transition-all border ${
                  showCircuitVisualization
                    ? 'bg-quantum-blue-light/20 border-quantum-blue-light/50 text-quantum-blue-light shadow-[0_0_10px_rgba(96,165,250,0.15)]'
                    : 'bg-editor-bg border-editor-border text-editor-text hover:bg-white/5'
                }`}
              >
                Circuit View
              </button>
              
              {showCircuitVisualization && (
                <div className="flex items-center bg-black/40 border border-white/10 rounded-md p-0.5 relative overflow-hidden">
                  <button
                    onClick={() => setIs3DMode(false)}
                    className={`relative z-10 px-3 py-1 text-xs font-medium rounded-sm transition-colors ${
                      !is3DMode ? 'text-white' : 'text-black dark:text-gray-400 hover:text-gray-200'
                    }`}
                  >
                    2D
                  </button>
                  <button
                    onClick={() => setIs3DMode(true)}
                    className={`relative z-10 px-3 py-1 text-xs font-medium rounded-sm transition-colors ${
                      is3DMode ? 'text-white' : 'text-black dark:text-gray-400 hover:text-gray-200'
                    }`}
                  >
                    3D
                  </button>
                  {/* Sliding highlight */}
                  <div 
                    className={`absolute inset-y-0.5 w-[calc(50%-2px)] rounded-sm bg-quantum-purple shadow-lg transition-transform duration-300 ease-[cubic-bezier(0.4,0,0.2,1)] ${
                      is3DMode ? 'translate-x-[calc(100%+4px)] left-0' : 'translate-x-[2px] left-0'
                    }`}
                  />
                </div>
              )}
            </div>
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

      {/* Circuit Visualization - Resizable */}
      {showCircuitVisualization && activeFile && (
        <>
          <div 
            className="bg-editor-bg border-b border-editor-border p-4 overflow-auto"
            style={{ height: `${circuitHeight}px` }}
          >
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-sm font-medium text-white">Circuit Visualization</h4>
              {isParsing && (
                <span className="text-xs text-black dark:text-gray-400 flex items-center">
                  <div className="w-3 h-3 border border-quantum-blue-light border-t-transparent rounded-full animate-spin mr-1"></div>
                  Parsing...
                </span>
              )}
            </div>
            {is3DMode ? (
              <CircuitVisualization3D
                gates={parsedGates}
                qubits={parsedQubits}
                className="h-full"
              />
            ) : (
              <CircuitVisualization
                gates={parsedGates}
                qubits={parsedQubits}
                className="h-full"
              />
            )}
          </div>
          {/* Drag Handle for Circuit Visualization */}
          <div
            role="separator"
            aria-orientation="horizontal"
            aria-label="Resize circuit visualization"
            tabIndex={0}
            className={`h-1 bg-editor-border hover:bg-quantum-blue-light cursor-row-resize transition-colors ${isDraggingCircuit ? 'bg-quantum-blue-light' : ''}`}
            onMouseDown={handleCircuitDragStart}
            onKeyDown={(e) => {
              if (e.key === 'ArrowUp') setCircuitHeight(h => Math.max(100, h - 20))
              if (e.key === 'ArrowDown') setCircuitHeight(h => Math.min(500, h + 20))
            }}
            title="Drag to resize circuit view"
          />
        </>
      )}

      {/* Monaco Editor - only render when mounted on client */}
      <div className="flex-1 overflow-hidden">
        {isMounted ? (
          <Editor
            key={activeFile.id}
            height="100%"
            path={activeFile.id}
            language={getMonacoLanguage(activeFile.language)}
            value={activeFile.content}
            onChange={handleEditorChange}
            onMount={handleEditorDidMount}
            options={{
              theme: typeof document !== 'undefined' && document.documentElement.classList.contains('light') ? 'quantum-light' : 'quantum-dark',
            fixedOverflowWidgets: true,
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
          />
        ) : (
          <div className="flex items-center justify-center h-full bg-editor-bg">
            <div className="flex items-center space-x-2">
              <div className="w-6 h-6 border-2 border-quantum-blue-light border-t-transparent rounded-full spinner"></div>
              <span className="text-editor-text">Loading editor...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
