'use client'

import { useState } from 'react'
import { 
  File as FileIcon, 
  Folder, 
  Plus, 
  MoreHorizontal, 
  Edit2, 
  Trash2, 
  X,
  Check,
  ChevronDown,
  ChevronRight,
  Code,
  FileText,
  Zap,
  Star,
  Clock,
  Search,
  Filter,
  Download,
  Upload,
  FolderPlus,
  FileCode,
  Languages
} from 'lucide-react'
import toast from 'react-hot-toast'
import { useFileStore } from '@/lib/store'
import { File } from '@/types'
import { isValidFilename, sanitizeFilename, formatFileSize, formatTimestamp } from '@/lib/utils'
import AddNewLanguage from './AddNewLanguage'

interface FileTemplate {
  name: string
  description: string
  content: string
  language: string
  icon: React.ReactNode
}

const fileTemplates: FileTemplate[] = [
  {
    name: 'Bell State (Qiskit)',
    description: 'Create a Bell state using Qiskit',
    content: `from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

# Create quantum and classical registers
qr = QuantumRegister(2, 'q')
cr = ClassicalRegister(2, 'c')

# Create quantum circuit
qc = QuantumCircuit(qr, cr)

# Apply Hadamard gate to first qubit
qc.h(qr[0])

# Apply CNOT gate between qubits 0 and 1
qc.cx(qr[0], qr[1])

# Measure both qubits
qc.measure(qr, cr)

print("Bell State Circuit (Qiskit):")
print(qc)`,
    language: 'python',
    icon: <Code className="w-4 h-4 text-blue-400" />
  },
  {
    name: 'Bell State (Cirq)',
    description: 'Create a Bell state using Cirq',
    content: `import cirq

# Create qubits
q0, q1 = cirq.LineQubit.range(2)

# Create Bell state circuit
circuit = cirq.Circuit(
    cirq.H(q0),           # Hadamard on first qubit
    cirq.CNOT(q0, q1),    # CNOT with q0 as control
    cirq.measure(q0, q1)  # Measure both qubits
)

print("Bell State Circuit (Cirq):")
print(circuit)`,
    language: 'python',
    icon: <Code className="w-4 h-4 text-purple-400" />
  },
  {
    name: 'Quantum Fourier Transform',
    description: 'Implement QFT algorithm',
    content: `from qiskit import QuantumCircuit
import numpy as np

def create_qft_circuit(n_qubits):
    qc = QuantumCircuit(n_qubits)
    
    for i in range(n_qubits):
        qc.h(i)
        
        for j in range(i + 1, n_qubits):
            angle = 2 * np.pi / (2 ** (j - i + 1))
            qc.cp(angle, j, i)
    
    # Swap qubits to get correct order
    for i in range(n_qubits // 2):
        qc.swap(i, n_qubits - 1 - i)
    
    return qc

# Create 4-qubit QFT
qft_circuit = create_qft_circuit(4)
print("Quantum Fourier Transform (4 qubits):")
print(qft_circuit)`,
    language: 'python',
    icon: <Code className="w-4 h-4 text-green-400" />
  },
  {
    name: 'OpenQASM Circuit',
    description: 'Basic OpenQASM 3 circuit',
    content: `OPENQASM 3.0;
include "stdgates.inc";

qubit[2] q;
bit[2] c;

h q[0];
cx q[0], q[1];
c = measure q;`,
    language: 'qasm',
    icon: <FileIcon className="w-4 h-4 text-purple-400" />
  }
]

export default function Sidebar() {
  const { 
    files, 
    activeFileId, 
    sidebarCollapsed, 
    setActiveFile, 
    addFile, 
    deleteFile, 
    renameFile 
  } = useFileStore()

  const [isExpanded, setIsExpanded] = useState(true)
  const [showNewFileInput, setShowNewFileInput] = useState(false)
  const [showTemplates, setShowTemplates] = useState(false)
  const [newFileName, setNewFileName] = useState('')
  const [editingFileId, setEditingFileId] = useState<string | null>(null)
  const [editingFileName, setEditingFileName] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState<'all' | 'python' | 'qasm' | 'javascript' | 'json'>('all')
  const [showAddLanguage, setShowAddLanguage] = useState(false)

  const filteredFiles = files.filter(file => {
    const matchesSearch = file.name.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesFilter = filterType === 'all' || file.language === filterType
    return matchesSearch && matchesFilter
  })

  const handleCreateFile = () => {
    if (!newFileName.trim()) {
      toast.error('Please enter a file name')
      return
    }

    if (!isValidFilename(newFileName)) {
      toast.error('Invalid file name')
      return
    }

    // Check if file with same name exists
    const existingFile = files.find(f => f.name === newFileName)
    if (existingFile) {
      toast.error('File with this name already exists')
      return
    }

    try {
      addFile(newFileName)
      setNewFileName('')
      setShowNewFileInput(false)
      toast.success(`Created ${newFileName}`)
    } catch (error) {
      toast.error('Failed to create file')
    }
  }

  const handleCreateFromTemplate = (template: FileTemplate) => {
    const fileName = `${template.name.toLowerCase().replace(/[^a-z0-9]/g, '_')}.${template.language === 'python' ? 'py' : template.language}`
    try {
      const newFile = addFile(fileName, template.content)
      setActiveFile(newFile.id)
      setShowTemplates(false)
      toast.success(`Created ${fileName} from template`)
    } catch (error) {
      toast.error('Failed to create file from template')
    }
  }

  const handleDeleteFile = (fileId: string, fileName: string) => {
    if (window.confirm(`Are you sure you want to delete "${fileName}"?`)) {
      try {
        deleteFile(fileId)
        toast.success(`Deleted ${fileName}`)
      } catch (error) {
        toast.error('Failed to delete file')
      }
    }
  }

  const handleRenameFile = (fileId: string) => {
    if (!editingFileName.trim()) {
      toast.error('Please enter a file name')
      return
    }

    if (!isValidFilename(editingFileName)) {
      toast.error('Invalid file name')
      return
    }

    // Check if file with same name exists (excluding current file)
    const existingFile = files.find(f => f.name === editingFileName && f.id !== fileId)
    if (existingFile) {
      toast.error('File with this name already exists')
      return
    }

    try {
      renameFile(fileId, editingFileName)
      setEditingFileId(null)
      setEditingFileName('')
      toast.success('File renamed successfully')
    } catch (error) {
      toast.error('Failed to rename file')
    }
  }

  const startRename = (file: File) => {
    setEditingFileId(file.id)
    setEditingFileName(file.name)
  }

  const cancelRename = () => {
    setEditingFileId(null)
    setEditingFileName('')
  }

  const getFileIcon = (file: File) => {
    switch (file.language) {
      case 'python':
        return <Code className="w-4 h-4 text-blue-400" />
      case 'qasm':
        return <FileIcon className="w-4 h-4 text-purple-400" />
      case 'javascript':
      case 'typescript':
        return <Code className="w-4 h-4 text-yellow-400" />
      case 'json':
        return <FileText className="w-4 h-4 text-green-400" />
      default:
        return <FileIcon className="w-4 h-4 text-gray-400" />
    }
  }

  if (sidebarCollapsed) {
    return (
      <div className="w-12 bg-gradient-to-b from-editor-sidebar to-gray-900 border-r border-editor-border flex flex-col items-center py-4 space-y-2">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="p-2 hover:bg-quantum-blue-light/20 rounded-lg transition-colors"
          title="Expand Sidebar"
        >
          <Folder className="w-5 h-5 text-editor-text" />
        </button>
        <button
          onClick={() => setShowTemplates(true)}
          className="p-2 hover:bg-quantum-blue-light/20 rounded-lg transition-colors"
          title="Templates"
        >
          <FileCode className="w-5 h-5 text-editor-text" />
        </button>
        <button
          onClick={() => setShowAddLanguage(true)}
          className="p-2 hover:bg-quantum-blue-light/20 rounded-lg transition-colors"
          title="Add Language"
        >
          <Languages className="w-5 h-5 text-editor-text" />
        </button>
      </div>
    )
  }

  return (
    <div className="sidebar bg-gradient-to-b from-editor-sidebar to-gray-900 border-r border-editor-border flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-editor-border flex-shrink-0">
        <div className="flex items-center justify-between mb-3">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="flex items-center space-x-2 text-editor-text hover:text-white transition-colors"
          >
            {isExpanded ? (
              <ChevronDown className="w-4 h-4" />
            ) : (
              <ChevronRight className="w-4 h-4" />
            )}
            <Folder className="w-4 h-4" />
            <span className="font-medium">Files</span>
          </button>
          
          <div className="flex items-center space-x-1">
            <button
              onClick={() => setShowTemplates(true)}
              className="btn-ghost p-1.5 hover:bg-quantum-blue-light/20 rounded-lg transition-colors"
              title="Templates"
            >
              <FileCode className="w-4 h-4" />
            </button>
            <button
              onClick={() => setShowAddLanguage(true)}
              className="btn-ghost p-1.5 hover:bg-quantum-blue-light/20 rounded-lg transition-colors"
              title="Add New Language"
            >
              <Languages className="w-4 h-4" />
            </button>
            <button
              onClick={() => setShowNewFileInput(true)}
              className="btn-ghost p-1.5 hover:bg-quantum-blue-light/20 rounded-lg transition-colors"
              title="New File"
            >
              <Plus className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Search and Filter */}
        {isExpanded && (
          <div className="space-y-2">
            <div className="relative">
              <Search className="absolute left-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search files..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-8 pr-2 py-1.5 bg-editor-bg border border-editor-border rounded-lg text-sm focus-quantum text-white placeholder-gray-400"
              />
            </div>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as any)}
              className="w-full px-2 py-1.5 bg-editor-bg border border-editor-border rounded-lg text-sm focus-quantum text-white"
            >
              <option value="all">All Files</option>
              <option value="python">Python</option>
              <option value="qasm">OpenQASM</option>
              <option value="javascript">JavaScript</option>
              <option value="json">JSON</option>
            </select>
          </div>
        )}
      </div>

      {/* File List */}
      {isExpanded && (
        <div className="flex-1 overflow-y-auto">
          {/* New File Input */}
          {showNewFileInput && (
            <div className="p-3 border-b border-editor-border bg-editor-bg/50">
              <div className="flex items-center space-x-2">
                <FileIcon className="w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={newFileName}
                  onChange={(e) => setNewFileName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleCreateFile()
                    if (e.key === 'Escape') {
                      setShowNewFileInput(false)
                      setNewFileName('')
                    }
                  }}
                  placeholder="filename.py"
                  className="flex-1 bg-editor-bg border border-editor-border rounded-lg px-3 py-1.5 text-sm focus-quantum text-white"
                  autoFocus
                />
                <button
                  onClick={handleCreateFile}
                  className="p-1.5 hover:bg-green-500/20 rounded-lg transition-colors"
                >
                  <Check className="w-3 h-3 text-green-400" />
                </button>
                <button
                  onClick={() => {
                    setShowNewFileInput(false)
                    setNewFileName('')
                  }}
                  className="p-1.5 hover:bg-red-500/20 rounded-lg transition-colors"
                >
                  <X className="w-3 h-3 text-red-400" />
                </button>
              </div>
            </div>
          )}

          {/* Files */}
          <div className="file-tree p-2">
            {filteredFiles.map((file) => (
              <div key={file.id} className="group mb-1">
                {editingFileId === file.id ? (
                  /* Rename Input */
                  <div className="flex items-center space-x-2 px-3 py-2 bg-editor-bg/50 rounded-lg">
                    {getFileIcon(file)}
                    <input
                      type="text"
                      value={editingFileName}
                      onChange={(e) => setEditingFileName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') handleRenameFile(file.id)
                        if (e.key === 'Escape') cancelRename()
                      }}
                      className="flex-1 bg-editor-bg border border-editor-border rounded-lg px-2 py-1 text-sm focus-quantum text-white"
                      autoFocus
                    />
                    <button
                      onClick={() => handleRenameFile(file.id)}
                      className="p-1 hover:bg-green-500/20 rounded transition-colors"
                    >
                      <Check className="w-3 h-3 text-green-400" />
                    </button>
                    <button
                      onClick={cancelRename}
                      className="p-1 hover:bg-red-500/20 rounded transition-colors"
                    >
                      <X className="w-3 h-3 text-red-400" />
                    </button>
                  </div>
                ) : (
                  /* File Item */
                  <div className="relative">
                    <div
                      className={`file-tree-item rounded-lg px-3 py-2 transition-all duration-200 ${
                        activeFileId === file.id 
                          ? 'bg-quantum-blue-light text-white shadow-lg' 
                          : 'hover:bg-editor-border/50'
                      }`}
                      onClick={() => setActiveFile(file.id)}
                    >
                      <div className="flex items-center space-x-2">
                        {getFileIcon(file)}
                        <span className="flex-1 truncate text-sm font-medium">{file.name}</span>
                        <span className="text-xs text-gray-400">
                          {formatFileSize(file.size)}
                        </span>
                      </div>
                    </div>

                    {/* File Actions */}
                    <div className="absolute right-2 top-1/2 transform -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <div className="flex items-center space-x-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            startRename(file)
                          }}
                          className="p-1 hover:bg-quantum-blue-light/20 rounded transition-colors"
                          title="Rename"
                        >
                          <Edit2 className="w-3 h-3" />
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleDeleteFile(file.id, file.name)
                          }}
                          className="p-1 hover:bg-red-500/20 rounded transition-colors text-red-400"
                          title="Delete"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                )}

                {/* File Details */}
                {activeFileId === file.id && (
                  <div className="px-6 py-3 text-xs text-gray-400 border-b border-editor-border bg-editor-bg/30 rounded-lg mt-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="font-medium">Language:</span>
                      <span className="px-2 py-0.5 bg-editor-border rounded text-white">{file.language}</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Clock className="w-3 h-3" />
                      <span>Modified: {formatTimestamp(file.updatedAt)}</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Empty State */}
          {filteredFiles.length === 0 && (
            <div className="p-8 text-center text-gray-500">
              <FileIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p className="text-sm mb-2">
                {searchTerm || filterType !== 'all' ? 'No files match your search' : 'No files yet'}
              </p>
              <button
                onClick={() => setShowNewFileInput(true)}
                className="text-xs text-quantum-blue-light hover:underline"
              >
                Create your first file
              </button>
            </div>
          )}
        </div>
      )}

      {/* Templates Modal */}
      {showTemplates && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="quantum-glass-dark rounded-2xl p-6 max-w-2xl w-full max-h-96 overflow-y-auto backdrop-blur-xl border border-white/10 shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-bold text-white">File Templates</h3>
              <button
                onClick={() => setShowTemplates(false)}
                className="btn-ghost p-1 hover:bg-quantum-blue-light/20 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4">
              {fileTemplates.map((template, index) => (
                <div
                  key={index}
                  className="quantum-glass-dark rounded-lg p-4 border border-white/10 hover:border-quantum-blue-light transition-all duration-200 cursor-pointer"
                  onClick={() => handleCreateFromTemplate(template)}
                >
                  <div className="flex items-center space-x-3 mb-2">
                    {template.icon}
                    <h4 className="font-medium text-white">{template.name}</h4>
                  </div>
                  <p className="text-sm text-editor-text mb-3">{template.description}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-400">{template.language}</span>
                    <button className="text-xs text-quantum-blue-light hover:underline">
                      Use Template
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Add New Language Modal */}
      <AddNewLanguage 
        isOpen={showAddLanguage} 
        onClose={() => setShowAddLanguage(false)} 
      />
    </div>
  )
}
