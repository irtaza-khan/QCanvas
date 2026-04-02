'use client'

import { X } from 'lucide-react'
import { useMemo } from 'react'
import { useFileStore } from '@/lib/store'

export default function EditorTabs() {
  const openFileIds = useFileStore((s) => s.openFileIds)
  const files = useFileStore((s) => s.files)
  const activeFileId = useFileStore((s) => s.activeFileId)
  const openFile = useFileStore((s) => s.openFile)
  const closeFile = useFileStore((s) => s.closeFile)

  const openFiles = useMemo(() => {
    const byId = new Map(files.map((f) => [f.id, f]))
    return openFileIds.map((id) => byId.get(id)).filter(Boolean)
  }, [files, openFileIds])

  if (openFiles.length === 0) return null

  return (
    <div className="h-9 bg-editor-sidebar border-b border-editor-border flex items-center overflow-x-auto">
      {openFiles.map((f: any) => (
        <button
          key={f.id}
          type="button"
          className={`flex items-center gap-2 px-3 h-full border-r border-editor-border ${
            activeFileId === f.id ? 'bg-editor-bg text-white' : 'text-editor-text hover:bg-editor-border/50'
          }`}
          onClick={() => openFile(f.id)}
          role="tab"
          aria-selected={activeFileId === f.id}
        >
          <span className="text-xs whitespace-nowrap">{f.name}</span>
          <button
            type="button"
            className="p-1 rounded hover:bg-editor-border/70"
            onClick={(e) => {
              e.stopPropagation()
              closeFile(f.id)
            }}
            title="Close"
          >
            <X className="w-3 h-3" />
          </button>
        </button>
      ))}
    </div>
  )
}

