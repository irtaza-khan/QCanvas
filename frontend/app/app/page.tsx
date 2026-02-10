'use client'

import { useEffect, useState, useRef } from 'react'
import { useFileStore } from '@/lib/store'
import { fileApi } from '@/lib/api'
import { InputLanguage } from '@/types'

type ExecutionMode = 'compile' | 'execute' | 'hybrid'
import EditorPane from '@/components/EditorPane'
import ResultsPane from '@/components/ResultsPane'
import TopBar from '@/components/TopBar'
import Sidebar from '@/components/Sidebar'
import SimulationControls from '@/components/SimulationControls'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'

export default function AppPage() {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)
  const [isMobile, setIsMobile] = useState(false)
  const [resultsHeight, setResultsHeight] = useState(320) // Default height
  const [isDragging, setIsDragging] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  // Simulation settings state
  const [inputLanguage, setInputLanguage] = useState<InputLanguage | "">("");
  const [simBackend, setSimBackend] = useState<'cirq' | 'qiskit' | 'pennylane' | ''>('');
  const [shots, setShots] = useState(1024);

  const {
    setFiles,
    files,
    sidebarCollapsed,
    toggleSidebar,
    resultsCollapsed,
    executionMode
  } = useFileStore()

  // Check for mobile screen size
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768)
    }

    checkMobile()
    window.addEventListener('resize', checkMobile)
    return () => window.removeEventListener('resize', checkMobile)
  }, [])

  // Auto-collapse sidebar on mobile
  useEffect(() => {
    if (isMobile && !sidebarCollapsed) {
      toggleSidebar()
    }
  }, [isMobile]) // eslint-disable-line react-hooks/exhaustive-deps

  // Authentication check
  useEffect(() => {
    const authStatus = localStorage.getItem('qcanvas-auth')

    if (!authStatus) {
      setIsAuthenticated(false)
    } else {
      setIsAuthenticated(true)
    }
  }, [])

  // Load files on component mount
  useEffect(() => {
    if (!isAuthenticated) return

    const loadFiles = async () => {
      try {
        const result = await fileApi.getFiles()
        if (result.success && result.data) {
          setFiles(result.data)
        }
      } catch (error) {
        console.error('Failed to load files:', error)
        // Keep using the mock files from store if API fails
      }

      // Check for pending example to add from home page
      const pendingExample = sessionStorage.getItem('pending-example')
      if (pendingExample) {
        try {
          const example = JSON.parse(pendingExample)
          const newFile = useFileStore.getState().addFile(example.name, example.content)
          useFileStore.getState().setActiveFile(newFile.id)
          toast.success(`Loaded example: ${example.name}`)
          sessionStorage.removeItem('pending-example')
        } catch (error) {
          console.error('Failed to load pending example:', error)
        }
      }
    }

    // Only load from API if we don't have files yet
    if (files.length === 0) {
      loadFiles()
    }
  }, [setFiles, files.length, isAuthenticated])

  // Listen for inter-tab messages to add files from examples page
  useEffect(() => {
    if (!isAuthenticated) return

    const channel = new BroadcastChannel('qcanvas-examples')

    channel.onmessage = (event) => {
      if (event.data.type === 'add-example-file') {
        const { filename, code } = event.data
        // Add the file and set it as active
        const newFile = useFileStore.getState().addFile(filename, code)
        toast.success(`Loaded example: ${filename}`)

        // Send confirmation back to examples page
        channel.postMessage({
          type: 'file-added',
          filename
        })
      }
    }

    return () => {
      channel.close()
    }
  }, [isAuthenticated])

  // Handle global save event
  useEffect(() => {
    const handleSave = () => {
      useFileStore.getState().saveActiveFile()
    }

    window.addEventListener('save-file', handleSave)
    return () => window.removeEventListener('save-file', handleSave)
  }, [])

  // Handle drag resize for results panel
  useEffect(() => {
    if (!isDragging) return

    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return

      const containerRect = containerRef.current.getBoundingClientRect()
      const newHeight = containerRect.bottom - e.clientY
      const minHeight = 100
      const maxHeight = containerRect.height - 200 // Leave space for editor

      setResultsHeight(Math.max(minHeight, Math.min(maxHeight, newHeight)))
    }

    const handleMouseUp = () => {
      setIsDragging(false)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging])

  const handleDragStart = (e: React.MouseEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  // Loading state
  if (isAuthenticated === null) {
    return (
      <div className="flex items-center justify-center h-screen bg-editor-bg">
        <div className="flex flex-col items-center space-y-4">
          <div className="w-8 h-8 border-4 border-quantum-blue-light border-t-transparent rounded-full spinner"></div>
          <p className="text-editor-text">Loading QCanvas...</p>
        </div>
      </div>
    )
  }

  // Not authenticated - redirect to login
  if (!isAuthenticated) {
    router.push('/login')
    return (
      <div className="flex items-center justify-center h-screen bg-editor-bg px-4">
        <div className="max-w-md mx-auto p-8 quantum-glass-dark rounded-lg text-center">
          <h2 className="text-2xl font-bold text-white mb-4">Redirecting to Login...</h2>
          <p className="text-editor-text mb-6">
            Please wait while we redirect you to the login page.
          </p>
        </div>
      </div>
    )
  }

  // Authenticated - show main app
  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <TopBar
        inputLanguage={inputLanguage}
        setInputLanguage={setInputLanguage}
        simBackend={simBackend}
        setSimBackend={setSimBackend}
        shots={shots}
        setShots={setShots}
      />
      {/* Hide simulation controls in hybrid mode - user specifies in code */}
      {executionMode !== 'hybrid' && (
        <SimulationControls
          inputLanguage={inputLanguage}
          setInputLanguage={setInputLanguage}
          simBackend={simBackend}
          setSimBackend={setSimBackend}
          shots={shots}
          setShots={setShots}
        />
      )}
      {/* Show hybrid mode info bar when in hybrid mode */}
      {executionMode === 'hybrid' && (
        <div className="min-h-[48px] bg-gradient-to-r from-green-900/30 via-emerald-900/20 to-green-900/30 border-b border-green-500/30 flex items-center justify-center px-6 py-2">
          <div className="flex items-center space-x-3">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span className="text-sm text-green-300 font-medium">Hybrid Mode</span>
            <span className="text-xs text-green-400/70">
              Use <code className="bg-green-900/40 px-1.5 py-0.5 rounded text-green-300">qcanvas.compile()</code> and <code className="bg-green-900/40 px-1.5 py-0.5 rounded text-green-300">qsim.run()</code> in your code
            </span>
          </div>
        </div>
      )}

      <div className="flex flex-1 min-h-0 overflow-hidden">
        {/* Sidebar */}
        <div className={`${sidebarCollapsed
            ? 'w-0 md:w-12'
            : 'w-full md:w-80'
          } transition-all duration-300 ${isMobile && !sidebarCollapsed
            ? 'absolute inset-y-0 left-0 z-50 shadow-xl'
            : ''
          } overflow-hidden`}>
          <Sidebar />
        </div>

        {/* Mobile overlay when sidebar is open */}
        {isMobile && !sidebarCollapsed && (
          <div
            className="absolute inset-0 bg-black bg-opacity-50 z-40"
            onClick={toggleSidebar}
          />
        )}

        {/* Main content */}
        <main ref={containerRef} className="flex-1 flex flex-col min-h-0 overflow-hidden">
          <div className="flex flex-col h-full overflow-hidden">
            {/* Editor Area */}
            <div
              className="flex-1 overflow-hidden"
              style={{ height: resultsCollapsed ? 'calc(100% - 32px)' : `calc(100% - ${resultsHeight}px)` }}
            >
              <EditorPane />
            </div>

            {/* Drag Handle */}
            {!resultsCollapsed && (
              <div
                className={`h-1 bg-editor-border hover:bg-quantum-blue-light cursor-row-resize transition-colors ${isDragging ? 'bg-quantum-blue-light' : ''
                  }`}
                onMouseDown={handleDragStart}
                title="Drag to resize"
              />
            )}

            {/* Results Panel */}
            <div
              className="overflow-hidden border-t border-editor-border"
              style={{ height: resultsCollapsed ? '32px' : `${resultsHeight}px` }}
            >
              <ResultsPane />
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
