'use client'

import { useMemo, useState } from 'react'
import { ChevronRight, ChevronDown, File as FileIcon, Folder as FolderIcon, Plus, FolderPlus } from 'lucide-react'
import { useFileStore } from '@/lib/store'
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
  const activeFileId = useFileStore((s) => s.activeFileId)
  const openFile = useFileStore((s) => s.openFile)
  const createFile = useFileStore((s) => s.createFile)

  const activeProjectId = useFileStore((s) => s.activeProjectId)

  const [expanded, setExpanded] = useState<Record<string, boolean>>({})

  const tree = useMemo(() => buildTree(folders, files), [folders, files])

  const toggleFolder = (folderId: string) => {
    setExpanded((p) => ({ ...p, [folderId]: !(p[folderId] ?? true) }))
  }

  const renderNode = (node: TreeNode, idx: number) => {
    const pad = 8 + node.depth * 12
    if (node.kind === 'folder') {
      const isOpen = expanded[node.folder.id] ?? true
      return (
        <div key={`folder-${node.folder.id}-${idx}`}>
          <button
            type="button"
            className="w-full flex items-center gap-2 py-1.5 pr-2 text-sm text-editor-text hover:bg-editor-border/50 rounded"
            style={{ paddingLeft: pad }}
            onClick={() => toggleFolder(node.folder.id)}
          >
            {isOpen ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            <FolderIcon className="w-4 h-4 text-quantum-blue-light" />
            <span className="truncate">{node.folder.name}</span>
          </button>
          {isOpen && node.children.map((child, childIdx) => renderNode(child, childIdx))}
        </div>
      )
    }

    return (
      <button
        key={`file-${node.file.id}-${idx}`}
        type="button"
        className={`w-full flex items-center gap-2 py-1.5 pr-2 text-sm rounded ${
          activeFileId === node.file.id ? 'bg-editor-accent text-white' : 'text-editor-text hover:bg-editor-border/50'
        }`}
        style={{ paddingLeft: pad + 18 }}
        onClick={() => openFile(node.file.id)}
      >
        <FileIcon className="w-4 h-4" />
        <span className="truncate">{node.file.name}</span>
      </button>
    )
  }

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="h-10 px-3 flex items-center justify-between border-b border-editor-border">
        <div className="text-xs font-semibold tracking-wider text-black dark:text-gray-400 uppercase">Explorer</div>
        <div className="flex items-center gap-1">
          <button
            type="button"
            className="p-1 rounded hover:bg-editor-border/50 text-editor-text"
            title="New Folder (coming next)"
            onClick={() => {}}
          >
            <FolderPlus className="w-4 h-4" />
          </button>
          <button
            type="button"
            className="p-1 rounded hover:bg-editor-border/50 text-editor-text"
            title="New File"
            onClick={() => createFile('new.py', '', activeProjectId ?? undefined, false)}
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-2">{tree.map((n, i) => renderNode(n, i))}</div>
    </div>
  )
}

