'use client'

import { useEffect, useMemo, useState } from 'react'
import { ChevronRight, ChevronDown, File as FileIcon, Folder as FolderIcon, FolderPlus, Plus, Trash2, Check, X, Edit2 } from 'lucide-react'
import { useFileStore } from '@/lib/store'
import { useAuthStore } from '@/lib/authStore'
import { Folder, File } from '@/types'

type TreeNode =
  | { kind: 'folder'; folder: Folder; children: TreeNode[]; depth: number }
  | { kind: 'file'; file: File; depth: number }

function buildTree(folders: Folder[], files: File[]): TreeNode[] {
  const byParent = new Map<string | null, Folder[]>()
  for (const f of folders) {
    const key = f.parentId ?? null
    const list = byParent.get(key) ?? []
    list.push(f)
    byParent.set(key, list)
  }
  Array.from(byParent.values()).forEach((list) => {
    list.sort((a, b) => a.name.localeCompare(b.name))
  })

  const filesByFolder = new Map<string | null, File[]>()
  for (const file of files) {
    const key = file.folderId ?? null
    const list = filesByFolder.get(key) ?? []
    list.push(file)
    filesByFolder.set(key, list)
  }
  Array.from(filesByFolder.values()).forEach((list) => {
    list.sort((a, b) => a.name.localeCompare(b.name))
  })

  const walk = (parentId: string | null, depth: number): TreeNode[] => {
    const nodes: TreeNode[] = []

    const childFolders = byParent.get(parentId) ?? []
    for (const folder of childFolders) {
      nodes.push({
        kind: 'folder',
        folder,
        children: walk(folder.id, depth + 1),
        depth,
      })
    }

    const childFiles = filesByFolder.get(parentId) ?? []
    for (const file of childFiles) {
      nodes.push({ kind: 'file', file, depth })
    }

    return nodes
  }

  return walk(null, 0)
}

export default function ExplorerView() {
  const folders = useFileStore((s) => s.folders)
  const files = useFileStore((s) => s.files)
  const projects = useFileStore((s) => s.projects)
  const activeFileId = useFileStore((s) => s.activeFileId)
  const openFile = useFileStore((s) => s.openFile)
  const createFile = useFileStore((s) => s.createFile)
  const createFolder = useFileStore((s) => s.createFolder)
  const createProject = useFileStore((s) => s.createProject)
  const renameFolder = useFileStore((s) => s.renameFolder)
  const deleteFolder = useFileStore((s) => s.deleteFolder)
  const renameFile = useFileStore((s) => s.renameFile)
  const deleteFile = useFileStore((s) => s.deleteFile)
  const fetchExplorerTree = useFileStore((s) => s.fetchExplorerTree)

  const activeProjectId = useFileStore((s) => s.activeProjectId)
  const token = useAuthStore((s) => s.token)

  const [expanded, setExpanded] = useState<Record<string, boolean>>({})
  const [showNewFileInput, setShowNewFileInput] = useState(false)
  const [newFileName, setNewFileName] = useState('new.py')
  const [showNewProjectInput, setShowNewProjectInput] = useState(false)
  const [newProjectName, setNewProjectName] = useState('')
  const [showNewFolderInput, setShowNewFolderInput] = useState(false)
  const [newFolderName, setNewFolderName] = useState('New Folder')
  const [selectedFolderId, setSelectedFolderId] = useState<string | null>(null)
  const [editingFileId, setEditingFileId] = useState<string | null>(null)
  const [editingFileName, setEditingFileName] = useState('')
  const [editingFolderId, setEditingFolderId] = useState<string | null>(null)
  const [editingFolderName, setEditingFolderName] = useState('')
  const [contextMenu, setContextMenu] = useState<
    | { type: 'file'; id: string; name: string; x: number; y: number }
    | { type: 'folder'; id: string; name: string; x: number; y: number }
    | null
  >(null)

  const tree = useMemo(() => buildTree(folders, files), [folders, files])

  const toggleFolder = (folderId: string) => {
    setExpanded((p) => ({ ...p, [folderId]: !(p[folderId] ?? true) }))
  }

  useEffect(() => {
    if (!contextMenu) return
    const onDocClick = () => setContextMenu(null)
    document.addEventListener('click', onDocClick)
    return () => document.removeEventListener('click', onDocClick)
  }, [contextMenu])

  const startCreateFile = (folderId?: string) => {
    setContextMenu(null)
    setShowNewFileInput(true)
    setNewFileName('new.py')
    if (folderId !== undefined) {
      setSelectedFolderId(folderId)
      setExpanded((p) => ({ ...p, [folderId]: true }))
    }
  }

  const startCreateProject = () => {
    setShowNewProjectInput(true)
    setNewProjectName('')
  }

  const submitCreateProject = async () => {
    const projectName = newProjectName.trim()
    if (!projectName || !token) return

    try {
      await createProject(projectName, false, token)
      setShowNewProjectInput(false)
      setNewProjectName('')
      setSelectedFolderId(null)
    } catch {
      // Toast handling lives in the store.
    }
  }

  const cancelCreateProject = () => {
    setShowNewProjectInput(false)
    setNewProjectName('')
  }

  const submitCreateFile = async () => {
    const fileName = newFileName.trim()
    if (!fileName) return

    try {
      await createFile(fileName, '', activeProjectId ?? undefined, false, selectedFolderId ?? undefined)
      setShowNewFileInput(false)
      setNewFileName('new.py')
    } catch {
      // Toast handling lives in the store.
    }
  }

  const cancelCreateFile = () => {
    setShowNewFileInput(false)
    setNewFileName('new.py')
  }

  const startCreateFolder = (parentFolderId?: string) => {
    setShowNewFolderInput(true)
    setNewFolderName('New Folder')
    if (parentFolderId !== undefined) {
      setSelectedFolderId(parentFolderId)
    }
  }

  const submitCreateFolder = async () => {
    const folderName = newFolderName.trim()
    if (!folderName) return

    try {
      await createFolder(folderName, activeProjectId ?? undefined, selectedFolderId ?? undefined)
      setShowNewFolderInput(false)
      setNewFolderName('New Folder')
    } catch {
      // Toast handling lives in the store.
    }
  }

  const cancelCreateFolder = () => {
    setShowNewFolderInput(false)
    setNewFolderName('New Folder')
  }

  const startRenameFile = (fileId: string, currentName: string) => {
    setEditingFileId(fileId)
    setEditingFileName(currentName)
    setContextMenu(null)
  }

  const submitRenameFile = async (fileId: string, currentName: string) => {
    const nextName = editingFileName.trim()
    if (!nextName || nextName === currentName) {
      setEditingFileId(null)
      return
    }

    try {
      await renameFile(fileId, nextName)
    } catch {
      // Toast handling lives in the store.
    } finally {
      setEditingFileId(null)
      setEditingFileName('')
    }
  }

  const cancelRenameFile = () => {
    setEditingFileId(null)
    setEditingFileName('')
  }

  const startRenameFolder = (folderId: string, currentName: string) => {
    setEditingFolderId(folderId)
    setEditingFolderName(currentName)
    setContextMenu(null)
  }

  const submitRenameFolder = async (folderId: string, currentName: string) => {
    const nextName = editingFolderName.trim()
    if (!nextName || nextName === currentName) {
      setEditingFolderId(null)
      return
    }

    try {
      await renameFolder(folderId, nextName)
    } catch {
      // Toast handling lives in the store.
    } finally {
      setEditingFolderId(null)
      setEditingFolderName('')
    }
  }

  const cancelRenameFolder = () => {
    setEditingFolderId(null)
    setEditingFolderName('')
  }

  const handleProjectChange = (value: string) => {
    if (!token) return
    const nextProjectId = value === '' ? null : Number(value)
    fetchExplorerTree(nextProjectId, token)
  }

  const renderNode = (node: TreeNode, idx: number) => {
    const pad = 8 + node.depth * 12
    if (node.kind === 'folder') {
      const isOpen = expanded[node.folder.id] ?? true
      return (
        <div key={`folder-${node.folder.id}-${idx}`}>
          <div className="group relative" style={{ paddingLeft: pad }} data-explorer-node="true">
            {editingFolderId === node.folder.id ? (
              <div className="w-full flex items-center gap-2 py-1.5 pr-2 text-sm rounded bg-editor-border/40">
                <FolderIcon className="w-4 h-4 text-quantum-blue-light" />
                <input
                  value={editingFolderName}
                  onChange={(e) => setEditingFolderName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') void submitRenameFolder(node.folder.id, node.folder.name)
                    if (e.key === 'Escape') cancelRenameFolder()
                  }}
                  className="flex-1 bg-editor-bg border border-editor-border rounded px-2 py-1 text-xs text-editor-text focus-quantum"
                  autoFocus
                />
                <button
                  type="button"
                  className="p-1 rounded hover:bg-green-500/20 text-green-400"
                  title="Confirm rename"
                  onClick={() => void submitRenameFolder(node.folder.id, node.folder.name)}
                >
                  <Check className="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  className="p-1 rounded hover:bg-red-500/20 text-red-400"
                  title="Cancel rename"
                  onClick={cancelRenameFolder}
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            ) : (
              <>
                <button
                  type="button"
                  className={`w-full flex items-center gap-2 py-1.5 pr-12 text-sm hover:bg-editor-border/50 rounded ${selectedFolderId === node.folder.id ? 'bg-editor-border/40 text-white' : 'text-editor-text'}`}
                  onClick={() => {
                    setSelectedFolderId(node.folder.id)
                    toggleFolder(node.folder.id)
                  }}
                  onDoubleClick={() => startCreateFile(node.folder.id)}
                  onContextMenu={(e) => {
                    e.preventDefault()
                    setSelectedFolderId(node.folder.id)
                    setContextMenu({
                      type: 'folder',
                      id: node.folder.id,
                      name: node.folder.name,
                      x: e.clientX,
                      y: e.clientY,
                    })
                  }}
                  title="Click to select folder, double click to create file inside"
                >
                  {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                  <FolderIcon className="w-4 h-4 text-quantum-blue-light" />
                  <span className="truncate">{node.folder.name}</span>
                </button>

                <div className="absolute right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                  <button
                    type="button"
                    className="p-1 rounded hover:bg-editor-border/70 text-editor-text"
                    title="New file in folder"
                    onClick={(e) => {
                      e.stopPropagation()
                      startCreateFile(node.folder.id)
                    }}
                  >
                    <Plus className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    className="p-1 rounded hover:bg-editor-border/70 text-editor-text"
                    title="Rename folder"
                    onClick={(e) => {
                      e.stopPropagation()
                      startRenameFolder(node.folder.id, node.folder.name)
                    }}
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    type="button"
                    className="p-1 rounded hover:bg-editor-border/70 text-editor-text"
                    title="Delete folder"
                    onClick={(e) => {
                      e.stopPropagation()
                      void deleteFolder(node.folder.id)
                    }}
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </>
            )}
          </div>
          {isOpen && node.children.map((child, childIdx) => renderNode(child, childIdx))}
        </div>
      )
    }

    return (
      <div
        key={`file-${node.file.id}-${idx}`}
        style={{ paddingLeft: pad + 18 }}
        className="group relative"
        data-explorer-node="true"
      >
        {editingFileId === node.file.id ? (
          <div className="w-full flex items-center gap-2 py-1.5 pr-2 text-sm rounded bg-editor-border/40">
            <FileIcon className="w-4 h-4 text-editor-text" />
            <input
              value={editingFileName}
              onChange={(e) => setEditingFileName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') void submitRenameFile(node.file.id, node.file.name)
                if (e.key === 'Escape') cancelRenameFile()
              }}
              className="flex-1 bg-editor-bg border border-editor-border rounded px-2 py-1 text-xs text-editor-text focus-quantum"
              autoFocus
            />
            <button
              type="button"
              className="p-1 rounded hover:bg-green-500/20 text-green-400"
              title="Confirm rename"
              onClick={() => void submitRenameFile(node.file.id, node.file.name)}
            >
              <Check className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              className="p-1 rounded hover:bg-red-500/20 text-red-400"
              title="Cancel rename"
              onClick={cancelRenameFile}
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        ) : (
          <>
            <button
              type="button"
              className={`w-full flex items-center gap-2 py-1.5 pr-8 text-sm rounded ${
                activeFileId === node.file.id ? 'bg-editor-accent text-white' : 'text-editor-text hover:bg-editor-border/50'
              }`}
              onClick={() => openFile(node.file.id)}
              onDoubleClick={() => startRenameFile(node.file.id, node.file.name)}
              onContextMenu={(e) => {
                e.preventDefault()
                setContextMenu({
                  type: 'file',
                  id: node.file.id,
                  name: node.file.name,
                  x: e.clientX,
                  y: e.clientY,
                })
              }}
              title="Double click or right-click to rename"
            >
              <FileIcon className="w-4 h-4" />
              <span className="truncate">{node.file.name}</span>
            </button>

            <div className="absolute right-1 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
              <button
                type="button"
                className="p-1 rounded hover:bg-editor-border/70 text-editor-text"
                title="Rename file"
                onClick={(e) => {
                  e.stopPropagation()
                  startRenameFile(node.file.id, node.file.name)
                }}
              >
                <Edit2 className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                className="p-1 rounded hover:bg-editor-border/70 text-editor-text"
                title="Delete file"
                onClick={(e) => {
                  e.stopPropagation()
                  void deleteFile(node.file.id)
                }}
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </>
        )}
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="h-10 px-3 flex items-center justify-between border-b border-editor-border gap-2">
        <div className="text-xs font-semibold tracking-wider text-black dark:text-gray-400 uppercase">Explorer</div>
        <div className="flex items-center gap-1 min-w-0">
          <select
            className="max-w-[150px] bg-editor-bg border border-editor-border rounded px-2 py-1 text-xs text-editor-text"
            value={activeProjectId?.toString() ?? ''}
            onChange={(e) => handleProjectChange(e.target.value)}
            title="Switch project"
          >
            <option value="">My Files</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>{project.name}</option>
            ))}
          </select>
          <button
            type="button"
            className="p-1 rounded hover:bg-editor-border/50 text-editor-text"
            title="New Project"
            onClick={startCreateProject}
          >
            <Plus className="w-4 h-4" />
          </button>
          <button
            type="button"
            className="p-1 rounded hover:bg-editor-border/50 text-editor-text"
            title="New Folder"
            onClick={() => startCreateFolder()}
          >
            <FolderPlus className="w-4 h-4" />
          </button>
          <button
            type="button"
            className="p-1 rounded hover:bg-editor-border/50 text-editor-text"
            title={selectedFolderId ? 'New File in Selected Folder' : 'New File'}
            onClick={() => startCreateFile()}
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div
        className="flex-1 overflow-y-auto p-2 space-y-1"
        onClick={(e) => {
          const target = e.target as HTMLElement
          if (!target.closest('[data-explorer-node="true"]')) {
            setSelectedFolderId(null)
          }
        }}
      >
        {showNewProjectInput && (
          <div className="flex items-center gap-2 py-1.5 px-2 text-sm rounded bg-editor-border/40">
            <FolderIcon className="w-4 h-4 text-editor-text" />
            <input
              value={newProjectName}
              onChange={(e) => setNewProjectName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') void submitCreateProject()
                if (e.key === 'Escape') cancelCreateProject()
              }}
              placeholder="Project name"
              className="flex-1 bg-editor-bg border border-editor-border rounded px-2 py-1 text-xs text-editor-text focus-quantum"
              autoFocus
            />
            <button
              type="button"
              className="p-1 rounded hover:bg-green-500/20 text-green-400"
              title="Create project"
              onClick={() => void submitCreateProject()}
            >
              <Check className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              className="p-1 rounded hover:bg-red-500/20 text-red-400"
              title="Cancel"
              onClick={cancelCreateProject}
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {showNewFolderInput && (
          <div className="flex items-center gap-2 py-1.5 px-2 text-sm rounded bg-editor-border/40">
            <FolderIcon className="w-4 h-4 text-quantum-blue-light" />
            <input
              value={newFolderName}
              onChange={(e) => setNewFolderName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') void submitCreateFolder()
                if (e.key === 'Escape') cancelCreateFolder()
              }}
              className="flex-1 bg-editor-bg border border-editor-border rounded px-2 py-1 text-xs text-editor-text focus-quantum"
              autoFocus
            />
            <button
              type="button"
              className="p-1 rounded hover:bg-green-500/20 text-green-400"
              title="Create folder"
              onClick={() => void submitCreateFolder()}
            >
              <Check className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              className="p-1 rounded hover:bg-red-500/20 text-red-400"
              title="Cancel"
              onClick={cancelCreateFolder}
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {showNewFileInput && (
          <div className="flex items-center gap-2 py-1.5 px-2 text-sm rounded bg-editor-border/40">
            <FileIcon className="w-4 h-4 text-editor-text" />
            <input
              value={newFileName}
              onChange={(e) => setNewFileName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') void submitCreateFile()
                if (e.key === 'Escape') cancelCreateFile()
              }}
              className="flex-1 bg-editor-bg border border-editor-border rounded px-2 py-1 text-xs text-editor-text focus-quantum"
              autoFocus
            />
            <button
              type="button"
              className="p-1 rounded hover:bg-green-500/20 text-green-400"
              title="Create file"
              onClick={() => void submitCreateFile()}
            >
              <Check className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              className="p-1 rounded hover:bg-red-500/20 text-red-400"
              title="Cancel"
              onClick={cancelCreateFile}
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>
        )}

        {tree.map((n, i) => renderNode(n, i))}
      </div>

      {contextMenu && (
        <div
          className="fixed z-[120] min-w-[170px] bg-editor-sidebar border border-editor-border rounded shadow-xl p-1"
          style={{ left: contextMenu.x, top: contextMenu.y }}
          onClick={(e) => e.stopPropagation()}
        >
          {contextMenu.type === 'folder' ? (
            <>
              <button
                type="button"
                className="w-full text-left px-3 py-1.5 text-xs text-editor-text hover:bg-editor-border/70 rounded"
                onClick={() => startCreateFile(contextMenu.id)}
              >
                New File
              </button>
              <button
                type="button"
                className="w-full text-left px-3 py-1.5 text-xs text-editor-text hover:bg-editor-border/70 rounded"
                onClick={() => startCreateFolder(contextMenu.id)}
              >
                New Folder
              </button>
              <button
                type="button"
                className="w-full text-left px-3 py-1.5 text-xs text-editor-text hover:bg-editor-border/70 rounded"
                onClick={() => startRenameFolder(contextMenu.id, contextMenu.name)}
              >
                Rename
              </button>
              <button
                type="button"
                className="w-full text-left px-3 py-1.5 text-xs text-red-400 hover:bg-red-500/20 rounded"
                onClick={() => {
                  void deleteFolder(contextMenu.id)
                  setContextMenu(null)
                }}
              >
                Delete
              </button>
            </>
          ) : (
            <>
              <button
                type="button"
                className="w-full text-left px-3 py-1.5 text-xs text-editor-text hover:bg-editor-border/70 rounded"
                onClick={() => openFile(contextMenu.id)}
              >
                Open
              </button>
              <button
                type="button"
                className="w-full text-left px-3 py-1.5 text-xs text-editor-text hover:bg-editor-border/70 rounded"
                onClick={() => startRenameFile(contextMenu.id, contextMenu.name)}
              >
                Rename
              </button>
              <button
                type="button"
                className="w-full text-left px-3 py-1.5 text-xs text-red-400 hover:bg-red-500/20 rounded"
                onClick={() => {
                  void deleteFile(contextMenu.id)
                  setContextMenu(null)
                }}
              >
                Delete
              </button>
            </>
          )}
        </div>
      )}
    </div>
  )
}

