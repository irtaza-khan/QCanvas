'use client'

import { useState } from 'react'
import { 
  Play, 
  Save, 
  RefreshCw, 
  Moon, 
  Sun, 
  Menu, 
  LogOut,
  Settings,
  Zap,
  Keyboard,
  X,
  HelpCircle,
  BookOpen,
  Code,
  Github,
  Mail,
  ChevronDown,
  FileText,
  Download,
  Share2,
  Search,
  Replace
} from 'lucide-react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import { useFileStore } from '@/lib/store'
import { fileApi } from '@/lib/api'
import { InputLanguage, ResultFormat } from '@/types'

export default function TopBar() {
  const router = useRouter()
  const { 
    theme, 
    toggleTheme, 
    toggleSidebar, 
    getActiveFile, 
    updateFileContent 
  } = useFileStore()
  const { setCompileOptions, compileActiveToQasm, setCompiledQasm } = useFileStore()
  
  const [isRunning, setIsRunning] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [showShortcuts, setShowShortcuts] = useState(false)
  const [showHelpMenu, setShowHelpMenu] = useState(false)
  const [inputLanguage, setInputLanguage] = useState<InputLanguage>('qasm')
  const [resultFormat, setResultFormat] = useState<ResultFormat>('json')
  const [resultStyle, setResultStyle] = useState<'classic' | 'compact'>('classic')

  const activeFile = getActiveFile()

  const shortcuts = [
    { key: 'Ctrl/Cmd + S', action: 'Save file' },
    { key: 'Ctrl/Cmd + N', action: 'New file' },
    { key: 'Ctrl/Cmd + B', action: 'Toggle sidebar' },
    { key: 'Ctrl/Cmd + J', action: 'Toggle results panel' },
    { key: 'Ctrl/Cmd + F', action: 'Find' },
    { key: 'Ctrl/Cmd + H', action: 'Find and Replace' },
    { key: 'Ctrl/Cmd + Shift + K', action: 'Toggle theme' },
    { key: 'Ctrl/Cmd + Shift + R', action: 'Run circuit' },
    { key: 'Ctrl/Cmd + Tab', action: 'Next file' },
    { key: 'Ctrl/Cmd + Shift + Tab', action: 'Previous file' },
  ]

  const helpMenuItems = [
    {
      icon: <BookOpen className="w-4 h-4" />,
      label: 'Documentation',
      action: () => window.open('/docs', '_blank')
    },
    {
      icon: <Code className="w-4 h-4" />,
      label: 'Examples',
      action: () => window.open('/examples', '_blank')
    },
    {
      icon: <Github className="w-4 h-4" />,
      label: 'GitHub',
      action: () => window.open('https://github.com', '_blank')
    },
    {
      icon: <Mail className="w-4 h-4" />,
      label: 'Contact Support',
      action: () => window.open('mailto:support@qcanvas.dev', '_blank')
    }
  ]

  const handleRun = async () => {
    if (!activeFile) {
      toast.error('No file selected')
      return
    }

    setIsRunning(true)
    try {
      // Dispatch custom event for results panel
      window.dispatchEvent(new CustomEvent('circuit-execute'))
      
      // Mock quantum execution
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Simulate different results based on file content
      let mockResults = ''
      if (activeFile.content.includes('Bell') || activeFile.content.includes('h q[0]')) {
        mockResults = 'Bell State Results:\n{"00": 512, "11": 512}\nTotal shots: 1024\nExecution time: 2.1s'
      } else if (activeFile.content.includes('Grover') || activeFile.content.includes('grovers')) {
        mockResults = 'Grover\'s Algorithm Results:\n{"11": 769, "00": 85, "01": 85, "10": 85}\nTotal shots: 1024\nExecution time: 3.2s'
      } else if (activeFile.content.includes('teleport')) {
        mockResults = 'Quantum Teleportation Results:\nTeleportation fidelity: 99.8%\nExecution time: 1.8s'
      } else {
        mockResults = 'Quantum Circuit Results:\n{"0": 524, "1": 500}\nTotal shots: 1024\nExecution time: 1.5s'
      }
      
      toast.success('Circuit executed successfully!')
      
      // In a real app, this would update the results panel
      console.log('Execution results:', mockResults)
    } catch (error) {
      toast.error('Execution failed')
    } finally {
      setIsRunning(false)
    }
  }

  const handleSave = async () => {
    if (!activeFile) {
      toast.error('No file to save')
      return
    }

    setIsSaving(true)
    try {
      const result = await fileApi.updateFile(activeFile.id, {
        content: activeFile.content,
      })

      if (result.success) {
        toast.success(`Saved ${activeFile.name}`)
      } else {
        throw new Error(result.error)
      }
    } catch (error) {
      toast.error('Save failed')
    } finally {
      setIsSaving(false)
    }
  }

  const handleConvertToQASM = () => {
    if (!activeFile) {
      toast.error('No file selected')
      return
    }

    setCompileOptions({ inputLanguage, resultFormat, style: resultStyle })
    const qasm = compileActiveToQasm()
    if (qasm) {
      // Open or focus a QASM tab
      const newName = activeFile.name.replace(/\.[^.]+$/, '') + '.qasm'
      const existing = useFileStore.getState().files.find(f => f.name === newName)
      if (existing) {
        updateFileContent(existing.id, qasm)
        useFileStore.getState().setActiveFile(existing.id)
      } else {
        const created = useFileStore.getState().addFile(newName, qasm)
        useFileStore.getState().setActiveFile(created.id)
      }
      setCompiledQasm(qasm)
      toast.success('Converted to OpenQASM 3.0')
      // Focus QASM tab in results
      window.dispatchEvent(new CustomEvent('show-qasm'))
    } else {
      toast.error('Conversion failed')
    }
  }

  const handleExport = () => {
    if (!activeFile) {
      toast.error('No file to export')
      return
    }

    const blob = new Blob([activeFile.content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = activeFile.name
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast.success('File exported successfully!')
  }

  const handleShare = () => {
    if (!activeFile) {
      toast.error('No file to share')
      return
    }

    // In a real app, this would generate a shareable link
    navigator.clipboard.writeText(activeFile.content)
    toast.success('Code copied to clipboard for sharing!')
  }

  const handleFind = () => {
    // Dispatch custom event for find
    window.dispatchEvent(new CustomEvent('open-find', { detail: { mode: 'find' } }))
  }

  const handleFindReplace = () => {
    // Dispatch custom event for find and replace
    window.dispatchEvent(new CustomEvent('open-find', { detail: { mode: 'replace' } }))
  }

  const handleLogout = () => {
    localStorage.removeItem('qcanvas-auth')
    toast.success('Logged out successfully')
    router.push('/login')
  }

  return (
    <>
      <div className="topbar bg-gradient-to-r from-editor-bg to-gray-900 border-b border-editor-border shadow-lg">
        {/* Left side - Logo and Navigation */}
        <div className="flex items-center space-x-2 md:space-x-4">
          <button
            onClick={toggleSidebar}
            className="btn-ghost p-2 hover:bg-quantum-blue-light/20 transition-colors"
            title="Toggle Sidebar (Ctrl/Cmd+B)"
          >
            <Menu className="w-5 h-5" />
          </button>
          
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-lg quantum-gradient flex items-center justify-center shadow-lg">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg hidden sm:block quantum-gradient bg-clip-text text-transparent">QCanvas</span>
          </div>
        </div>

        {/* Center - Compile/Run and Options */}
        <div className="flex items-center space-x-1 md:space-x-2">
          {/* Input Language */}
          <select
            value={inputLanguage}
            onChange={(e) => setInputLanguage(e.target.value as InputLanguage)}
            className="hidden md:block bg-editor-bg border border-editor-border text-sm text-editor-text rounded-lg px-3 py-1.5 focus-quantum transition-colors"
            title="Input Language"
          >
            <option value="qasm">OpenQASM</option>
            <option value="qiskit">Qiskit</option>
            <option value="cirq">Cirq</option>
            <option value="pennylane">PennyLane</option>
          </select>

          {/* Output Format */}
          <select
            value={resultFormat}
            onChange={(e) => setResultFormat(e.target.value as ResultFormat)}
            className="hidden md:block bg-editor-bg border border-editor-border text-sm text-editor-text rounded-lg px-3 py-1.5 focus-quantum transition-colors"
            title="Result Format"
          >
            <option value="json">JSON</option>
            <option value="histogram">Histogram</option>
            <option value="text">Text</option>
          </select>

          {/* Result Style */}
          <select
            value={resultStyle}
            onChange={(e) => setResultStyle(e.target.value as any)}
            className="hidden lg:block bg-editor-bg border border-editor-border text-sm text-editor-text rounded-lg px-3 py-1.5 focus-quantum transition-colors"
            title="Result Style"
          >
            <option value="classic">Classic</option>
            <option value="compact">Compact</option>
          </select>

          <button
            onClick={handleRun}
            disabled={isRunning || !activeFile}
            className="btn-quantum flex items-center space-x-1 md:space-x-2 disabled:opacity-50 px-3 md:px-4 py-1.5 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200"
            title="Run Circuit (Ctrl/Cmd+Shift+R)"
          >
            {isRunning ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full spinner" />
                <span className="hidden sm:inline">Running...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span className="hidden sm:inline">Run</span>
              </>
            )}
          </button>

          <button
            onClick={handleConvertToQASM}
            disabled={!activeFile}
            className="btn-ghost flex items-center space-x-1 md:space-x-2 disabled:opacity-50 px-2 md:px-3 py-1.5 rounded-lg hover:bg-quantum-blue-light/20 transition-colors hidden md:flex"
            title="Convert to OpenQASM"
          >
            <RefreshCw className="w-4 h-4" />
            <span className="hidden lg:inline">Compile to QASM</span>
          </button>

          <button
            onClick={handleSave}
            disabled={isSaving || !activeFile}
            className="btn-ghost flex items-center space-x-1 md:space-x-2 disabled:opacity-50 px-2 md:px-3 py-1.5 rounded-lg hover:bg-quantum-blue-light/20 transition-colors"
            title="Save File (Ctrl/Cmd+S)"
          >
            {isSaving ? (
              <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full spinner" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            <span className="hidden md:inline">Save</span>
          </button>

          <button
            onClick={handleExport}
            disabled={!activeFile}
            className="btn-ghost flex items-center space-x-1 disabled:opacity-50 px-2 py-1.5 rounded-lg hover:bg-quantum-blue-light/20 transition-colors hidden lg:flex"
            title="Export File"
          >
            <Download className="w-4 h-4" />
          </button>

          <button
            onClick={handleShare}
            disabled={!activeFile}
            className="btn-ghost flex items-center space-x-1 disabled:opacity-50 px-2 py-1.5 rounded-lg hover:bg-quantum-blue-light/20 transition-colors hidden lg:flex"
            title="Share Code"
          >
            <Share2 className="w-4 h-4" />
          </button>

          <div className="hidden md:block w-px h-6 bg-editor-border mx-2"></div>

          <button
            onClick={handleFind}
            disabled={!activeFile}
            className="btn-ghost flex items-center space-x-1 disabled:opacity-50 px-2 py-1.5 rounded-lg hover:bg-quantum-blue-light/20 transition-colors"
            title="Find (Ctrl/Cmd+F)"
          >
            <Search className="w-4 h-4" />
            <span className="hidden lg:inline">Find</span>
          </button>

          <button
            onClick={handleFindReplace}
            disabled={!activeFile}
            className="btn-ghost flex items-center space-x-1 disabled:opacity-50 px-2 py-1.5 rounded-lg hover:bg-quantum-blue-light/20 transition-colors"
            title="Find and Replace (Ctrl/Cmd+H)"
          >
            <Replace className="w-4 h-4" />
            <span className="hidden lg:inline">Replace</span>
          </button>
        </div>

        {/* Right side - Settings and Theme */}
        <div className="flex items-center space-x-1 md:space-x-2">
          {/* Help Menu */}
          <div className="relative">
            <button
              onClick={() => setShowHelpMenu(!showHelpMenu)}
              className="btn-ghost p-2 hover:bg-quantum-blue-light/20 transition-colors relative"
              title="Help & Resources"
            >
              <HelpCircle className="w-5 h-5" />
            </button>
            
            {showHelpMenu && (
              <div className="absolute right-0 top-full mt-2 w-48 quantum-glass-dark rounded-lg shadow-xl border border-white/10 backdrop-blur-xl z-50">
                <div className="py-2">
                  {helpMenuItems.map((item, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        item.action()
                        setShowHelpMenu(false)
                      }}
                      className="w-full flex items-center px-4 py-2 text-sm text-editor-text hover:text-white hover:bg-quantum-blue-light/20 transition-colors"
                    >
                      {item.icon}
                      <span className="ml-3">{item.label}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          <button
            onClick={() => setShowShortcuts(true)}
            className="btn-ghost p-2 hover:bg-quantum-blue-light/20 transition-colors hidden md:block"
            title="Keyboard Shortcuts"
          >
            <Keyboard className="w-5 h-5" />
          </button>

          <button
            onClick={toggleTheme}
            className="btn-ghost p-2 hover:bg-quantum-blue-light/20 transition-colors"
            title="Toggle Theme (Ctrl/Cmd+Shift+K)"
          >
            {theme === 'dark' ? (
              <Sun className="w-5 h-5" />
            ) : (
              <Moon className="w-5 h-5" />
            )}
          </button>

          <button
            className="btn-ghost p-2 hover:bg-quantum-blue-light/20 transition-colors hidden lg:block"
            title="Settings"
          >
            <Settings className="w-5 h-5" />
          </button>

          <button
            onClick={handleLogout}
            className="btn-ghost text-red-400 hover:text-red-300 hover:bg-red-500/20 p-2 rounded-lg transition-colors"
            title="Logout"
          >
            <LogOut className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Keyboard Shortcuts Modal */}
      {showShortcuts && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="quantum-glass-dark rounded-2xl p-6 max-w-md w-full max-h-96 overflow-y-auto backdrop-blur-xl border border-white/10 shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">Keyboard Shortcuts</h3>
              <button
                onClick={() => setShowShortcuts(false)}
                className="btn-ghost p-1 hover:bg-quantum-blue-light/20 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-3">
              {shortcuts.map((shortcut, index) => (
                <div key={index} className="flex justify-between items-center py-3 border-b border-editor-border last:border-b-0">
                  <span className="text-sm text-editor-text">{shortcut.action}</span>
                  <kbd className="px-3 py-1.5 bg-editor-bg border border-editor-border rounded-lg text-xs font-mono text-white shadow-sm">
                    {shortcut.key}
                  </kbd>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Click outside to close help menu */}
      {showHelpMenu && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={() => setShowHelpMenu(false)}
        />
      )}
    </>
  )
}
