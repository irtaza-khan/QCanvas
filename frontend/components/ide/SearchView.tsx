'use client'

import { useMemo, useState } from 'react'
import { Search } from 'lucide-react'
import { useFileStore } from '@/lib/store'

type ContentMatch = {
  fileId: string
  fileName: string
  lineNumber: number
  column: number
  lineText: string
}

function escapeRegExp(input: string) {
  return input.replaceAll(/[.*+?^${}()|[\]\\]/g, String.raw`\$&`)
}

function snippetFromLine(line: string, column: number, queryLength: number, maxLen = 120) {
  const start = Math.max(0, column - Math.floor((maxLen - queryLength) / 2))
  const end = Math.min(line.length, start + maxLen)
  const prefixEllipsis = start > 0 ? '…' : ''
  const suffixEllipsis = end < line.length ? '…' : ''
  return `${prefixEllipsis}${line.slice(start, end)}${suffixEllipsis}`
}

function HighlightedSnippet({
  text,
  query,
}: Readonly<{
  text: string
  query: string
}>) {
  const q = query.trim()
  if (!q) return <span>{text}</span>

  const re = new RegExp(escapeRegExp(q), 'ig')
  const parts: Array<{ t: string; m: boolean }> = []
  let lastIndex = 0
  for (const match of text.matchAll(re)) {
    const idx = match.index ?? 0
    if (idx > lastIndex) parts.push({ t: text.slice(lastIndex, idx), m: false })
    parts.push({ t: text.slice(idx, idx + match[0].length), m: true })
    lastIndex = idx + match[0].length
  }
  if (lastIndex < text.length) parts.push({ t: text.slice(lastIndex), m: false })

  return (
    <span>
      {parts.map((p, i) =>
        p.m ? (
          <mark
            // eslint-disable-next-line react/no-array-index-key
            key={i}
            className="bg-quantum-blue-light/30 text-white rounded px-0.5"
          >
            {p.t}
          </mark>
        ) : (
          // eslint-disable-next-line react/no-array-index-key
          <span key={i}>{p.t}</span>
        ),
      )}
    </span>
  )
}

export default function SearchView() {
  const files = useFileStore((s) => s.files)
  const openFile = useFileStore((s) => s.openFile)
  const [query, setQuery] = useState('')

  const results = useMemo(() => {
    const q = query.trim()
    if (!q) {
      return {
        fileNameMatches: [] as Array<{ id: string; name: string }>,
        contentMatches: [] as ContentMatch[],
      }
    }

    const qLower = q.toLowerCase()

    const fileNameMatches = files
      .filter((f) => f.name.toLowerCase().includes(qLower))
      .slice(0, 25)
      .map((f) => ({ id: f.id, name: f.name }))

    const contentMatches: ContentMatch[] = []
    const MAX_MATCHES = 200

    for (const f of files) {
      if (!f.content) continue

      const lines = f.content.split('\n')
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i]
        const idx = line.toLowerCase().indexOf(qLower)
        if (idx === -1) continue

        contentMatches.push({
          fileId: f.id,
          fileName: f.name,
          lineNumber: i + 1,
          column: idx + 1,
          lineText: line,
        })

        if (contentMatches.length >= MAX_MATCHES) break
      }

      if (contentMatches.length >= MAX_MATCHES) break
    }

    return { fileNameMatches, contentMatches }
  }, [files, query])

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="h-10 px-3 flex items-center gap-2 border-b border-editor-border">
        <Search className="w-4 h-4 text-editor-text" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search (files + contents)..."
          className="flex-1 bg-editor-bg border border-editor-border rounded px-2 py-1 text-sm text-white focus-quantum"
        />
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        {(() => {
          const hasQuery = query.trim().length > 0
          if (!hasQuery) {
            return (
              <div className="text-xs text-black dark:text-gray-500 p-2">
                Type to search across <span className="text-editor-text">filenames</span> and{' '}
                <span className="text-editor-text">file contents</span>.
              </div>
            )
          }
          if (results.fileNameMatches.length === 0 && results.contentMatches.length === 0) {
            return <div className="text-xs text-black dark:text-gray-500 p-2">No matches.</div>
          }
          return (
            <div className="space-y-3">
              {results.fileNameMatches.length > 0 && (
                <div>
                  <div className="px-2 pt-1 pb-1 text-[11px] font-semibold tracking-wider uppercase text-black dark:text-gray-500">
                    Files
                  </div>
                  <div className="space-y-1">
                    {results.fileNameMatches.map((f) => (
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
                </div>
              )}

              {results.contentMatches.length > 0 && (
                <div>
                  <div className="px-2 pt-1 pb-1 flex items-center justify-between">
                    <div className="text-[11px] font-semibold tracking-wider uppercase text-black dark:text-gray-500">
                      Results
                    </div>
                    <div className="text-[11px] text-black dark:text-gray-500">
                      {(() => {
                        if (results.contentMatches.length >= 200) return 'Showing first 200 matches'
                        const count = results.contentMatches.length
                        return `${count} match${count === 1 ? '' : 'es'}`
                      })()}
                    </div>
                  </div>

                  <div className="space-y-1">
                    {results.contentMatches.map((m) => {
                      const snippet = snippetFromLine(m.lineText, m.column - 1, query.trim().length)
                      return (
                        <button
                          key={`${m.fileId}:${m.lineNumber}:${m.column}`}
                          type="button"
                          className="w-full text-left px-2 py-2 rounded hover:bg-editor-border/50"
                          onClick={() => {
                            openFile(m.fileId)
                            globalThis.window?.dispatchEvent(
                              new CustomEvent('qcanvas:reveal-in-editor', {
                                detail: {
                                  fileId: m.fileId,
                                  lineNumber: m.lineNumber,
                                  column: m.column,
                                  query: query.trim(),
                                },
                              }),
                            )
                          }}
                        >
                          <div className="flex items-baseline justify-between gap-2">
                            <div className="text-xs text-editor-text truncate">
                              <span className="font-semibold text-white">{m.fileName}</span>
                            </div>
                            <div className="text-[11px] text-black dark:text-gray-500 shrink-0 font-mono">
                              Ln {m.lineNumber}
                            </div>
                          </div>
                          <div className="mt-1 text-[12px] font-mono text-editor-text/90 whitespace-pre truncate">
                            <HighlightedSnippet text={snippet} query={query.trim()} />
                          </div>
                        </button>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          )
        })()}
      </div>
    </div>
  )
}

