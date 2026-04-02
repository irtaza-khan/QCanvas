'use client'

import { useMemo, useState } from 'react'
import { Search } from 'lucide-react'
import { useFileStore } from '@/lib/store'

export default function SearchView() {
  const files = useFileStore((s) => s.files)
  const openFile = useFileStore((s) => s.openFile)
  const [query, setQuery] = useState('')

  const results = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return []
    return files
      .filter((f) => f.name.toLowerCase().includes(q))
      .slice(0, 50)
  }, [files, query])

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="h-10 px-3 flex items-center gap-2 border-b border-editor-border">
        <Search className="w-4 h-4 text-editor-text" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search files..."
          className="flex-1 bg-editor-bg border border-editor-border rounded px-2 py-1 text-sm text-white focus-quantum"
        />
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        {(() => {
          const hasQuery = query.trim().length > 0
          if (!hasQuery) {
            return <div className="text-xs text-black dark:text-gray-500 p-2">Type to search by filename.</div>
          }
          if (results.length === 0) {
            return <div className="text-xs text-black dark:text-gray-500 p-2">No matches.</div>
          }
          return (
            <div className="space-y-1">
              {results.map((f) => (
                <button
                  key={f.id}
                  type="button"
                  className="w-full text-left px-2 py-2 rounded hover:bg-editor-border/50 text-sm text-editor-text"
                  onClick={() => openFile(f.id)}
                >
                  {f.name}
                </button>
              ))}
            </div>
          )
        })()}
      </div>
    </div>
  )
}

