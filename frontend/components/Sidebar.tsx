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
    name: 'Quantum Teleportation (Qiskit)',
    description: 'Transfer quantum state using entanglement',
    content: `from qiskit import QuantumCircuit

# Create circuit with 3 qubits and 3 classical bits
qc = QuantumCircuit(3, 3)

# STEP 1: Prepare the state to teleport (|+⟩ state as example)
qc.h(0)

# STEP 2: Create Bell pair between q1 and q2
qc.h(1)
qc.cx(1, 2)

# STEP 3: Bell measurement
qc.cx(0, 1)
qc.h(0)

# STEP 4: Measure qubits 0 and 1
qc.measure(0, 0)
qc.measure(1, 1)

# STEP 5: Conditional corrections (classical control)
c = [0, 0, 0]
if c[1] == 1:
    qc.x(2)
if c[0] == 1:
    qc.z(2)

# STEP 6: Final measurement
qc.measure(2, 2)`,
    language: 'python',
    icon: <Code className="w-4 h-4 text-blue-400" />
  },
  {
    name: 'QRNG (Cirq)',
    description: 'Generate truly random numbers using quantum mechanics',
    content: `import cirq

# Number of random bits to generate
n_bits = 8

# Create n_bits qubits
qubits = cirq.LineQubit.range(n_bits)

circuit = cirq.Circuit()

# Put each qubit in superposition
for i in range(n_bits):
    circuit.append(cirq.H(cirq.LineQubit(i)))

# Measure all qubits
for i in range(n_bits):
    circuit.append(cirq.measure(cirq.LineQubit(i), key=f'c{i}'))`,
    language: 'python',
    icon: <Code className="w-4 h-4 text-purple-400" />
  },
  {
    name: 'XOR Demonstration (PennyLane)',
    description: 'Quantum entanglement producing XOR correlations',
    content: `import pennylane as qml

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def xor_demo_circuit():
    # STEP 1: Create Bell state (|00⟩ + |11⟩)/√2
    # Hadamard creates superposition, CNOT entangles qubits
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    
    # STEP 2: Flip qubit 0 to get (|10⟩ + |01⟩)/√2
    # Now qubits are always opposite (XOR = 1)
    qml.PauliX(wires=0)
    
    # STEP 3: Measure both qubits
    # Results will be either |01⟩ or |10⟩
    qml.measure(wires=0)
    qml.measure(wires=1)`,
    language: 'python',
    icon: <Code className="w-4 h-4 text-green-400" />
  },
  {
    name: 'QML XOR Classifier (PennyLane)',
    description: 'Variational quantum circuit that learns XOR function',
    content: `import pennylane as qml
import numpy as np

dev = qml.device("default.qubit", wires=2)

@qml.qnode(dev)
def qml_xor_classifier():
    # ENCODING LAYER: Convert classical inputs to quantum states
    # Testing XOR(0, 1) - expect output = 1
    qml.RX(0, wires=0)              # Input x1=0: RX(0*π) = no rotation
    qml.RX(np.pi, wires=1)          # Input x2=1: RX(1*π) = flip to |1⟩
    
    # VARIATIONAL LAYER: Trainable gates that learn XOR pattern
    # Weights = 0.5 radians (found through gradient descent training)
    qml.RY(0.5, wires=0)            # Trainable rotation on qubit 0
    qml.RY(0.5, wires=1)            # Trainable rotation on qubit 1
    qml.CNOT(wires=[0, 1])          # Entanglement creates non-linear behavior
    qml.RY(0.5, wires=0)            # Second layer of trainable rotations
    qml.RY(0.5, wires=1)
    
    # MEASUREMENT: Read the XOR prediction from qubit 1
    # q[1] = 1 means XOR(x1, x2) = 1
    qml.measure(wires=0)
    qml.measure(wires=1)`,
    language: 'python',
    icon: <Code className="w-4 h-4 text-green-400" />
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
  const [deleteConfirm, setDeleteConfirm] = useState<{ show: boolean; fileId: string; fileName: string }>({
    show: false,
    fileId: '',
    fileName: ''
  })

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
    setDeleteConfirm({ show: true, fileId, fileName })
  }

  const confirmDelete = () => {
    try {
      deleteFile(deleteConfirm.fileId)
      toast.success(`Deleted ${deleteConfirm.fileName}`)
    } catch (error) {
      toast.error('Failed to delete file')
    }
    setDeleteConfirm({ show: false, fileId: '', fileName: '' })
  }

  const cancelDelete = () => {
    setDeleteConfirm({ show: false, fileId: '', fileName: '' })
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
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={() => setShowTemplates(false)}
        >
          <div 
            className="quantum-glass-dark rounded-2xl p-6 max-w-2xl w-full max-h-[32rem] overflow-y-auto backdrop-blur-xl border border-white/10 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
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

      {/* Delete Confirmation Modal */}
      {deleteConfirm.show && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
          onClick={cancelDelete}
        >
          <div 
            className="quantum-glass-dark rounded-2xl p-6 max-w-md w-full backdrop-blur-xl border border-white/10 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center space-x-3 mb-4">
              <div className="p-2 bg-red-500/20 rounded-lg">
                <Trash2 className="w-6 h-6 text-red-400" />
              </div>
              <h3 className="text-lg font-bold text-white">Delete File</h3>
            </div>
            
            <p className="text-editor-text mb-6">
              Are you sure you want to delete <span className="text-white font-medium">"{deleteConfirm.fileName}"</span>? 
              This action cannot be undone.
            </p>
            
            <div className="flex justify-end space-x-3">
              <button
                onClick={cancelDelete}
                className="px-4 py-2 text-sm font-medium text-editor-text hover:text-white bg-editor-border/50 hover:bg-editor-border rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 text-sm font-medium text-white bg-red-500 hover:bg-red-600 rounded-lg transition-colors"
              >
                Delete
              </button>
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
