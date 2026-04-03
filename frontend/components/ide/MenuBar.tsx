'use client'

import { useEffect, useMemo, useRef, useState } from 'react'
import { useFileStore } from '@/lib/store'
import Image from 'next/image'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/authStore'
import ProfileDropdown from '@/components/ProfileDropdown'
import ShareModal from '@/components/ShareModal'
import AddNewLanguage from '@/components/AddNewLanguage'
import { FILE_TEMPLATES_PRESETS } from '@/lib/fileTemplates'

type MenuId = 'file' | 'edit' | 'selection' | 'view' | 'run' | 'terminal' | 'help'

interface MenuItem {
  label: string
  shortcut?: string
  disabled?: boolean
  onSelect: () => void
}

export default function MenuBar({ onRun }: Readonly<{ onRun: () => void | Promise<void> }>) {
  const { toggleSidebar, toggleResults, theme, toggleTheme, setExecutionMode, executionMode, activeProjectId } = useFileStore()
  const activeFile = useFileStore((s) => s.getActiveFile())
  const { isAuthenticated, clearAuth, token } = useAuthStore()
  const router = useRouter()

  const [openMenu, setOpenMenu] = useState<MenuId | null>(null)
  const [showShareModal, setShowShareModal] = useState(false)
  const [showShortcuts, setShowShortcuts] = useState(false)
  const [showTemplatesPicker, setShowTemplatesPicker] = useState(false)
  const [showAddLanguage, setShowAddLanguage] = useState(false)
  const barRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const onDocClick = (e: MouseEvent) => {
      if (!barRef.current) return
      if (!barRef.current.contains(e.target as Node)) setOpenMenu(null)
    }
    document.addEventListener('mousedown', onDocClick)
    return () => document.removeEventListener('mousedown', onDocClick)
  }, [])

  const handleExport = () => {
    if (!activeFile) return
    const blob = new Blob([activeFile.content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = activeFile.name
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }

  const handleLogout = () => {
    clearAuth()
    router.push('/login')
  }

  const menus = useMemo<Record<MenuId, MenuItem[]>>(
    () => ({
      file: [
        {
          label: 'New File',
          shortcut: 'Ctrl/Cmd+N',
          onSelect: () => {
            const entered = globalThis.window?.prompt('Enter new file name', 'new.py')
            const fileName = entered?.trim()
            if (!fileName) return

            if (token) {
              useFileStore.getState().createFile(fileName, '', activeProjectId ?? undefined, false)
            } else {
              useFileStore.getState().addFile(fileName, '')
            }
          },
        },
        {
          label: 'Templates…',
          onSelect: () => setShowTemplatesPicker(true),
        },
        {
          label: 'Save',
          shortcut: 'Ctrl/Cmd+S',
          disabled: !activeFile,
          onSelect: () => globalThis.window?.dispatchEvent(new CustomEvent('save-file')),
        },
        {
          label: 'Export',
          disabled: !activeFile,
          onSelect: handleExport,
        },
        {
          label: 'Share',
          disabled: !activeFile,
          onSelect: () => setShowShareModal(true),
        },
      ],
      edit: [
        {
          label: 'Find',
          shortcut: 'Ctrl/Cmd+F',
          disabled: !activeFile,
          onSelect: () => globalThis.window?.dispatchEvent(new CustomEvent('open-find', { detail: { mode: 'find' } })),
        },
        {
          label: 'Replace',
          shortcut: 'Ctrl/Cmd+H',
          disabled: !activeFile,
          onSelect: () => globalThis.window?.dispatchEvent(new CustomEvent('open-find', { detail: { mode: 'replace' } })),
        },
        {
          label: 'Keyboard Shortcuts',
          onSelect: () => setShowShortcuts(true),
        },
      ],
      selection: [
        {
          label: 'Select All',
          shortcut: 'Ctrl/Cmd+A',
          disabled: !activeFile,
          onSelect: () => {},
        },
      ],
      view: [
        {
          label: 'Toggle Sidebar',
          shortcut: 'Ctrl/Cmd+B',
          onSelect: toggleSidebar,
        },
        {
          label: `Theme: ${theme === 'dark' ? 'Dark' : 'Light'}`,
          shortcut: 'Ctrl/Cmd+Shift+K',
          onSelect: toggleTheme,
        },
      ],
      run: [
        {
          label: 'Mode: Compile',
          disabled: executionMode === 'compile',
          onSelect: () => setExecutionMode('compile'),
        },
        {
          label: 'Mode: Execute',
          disabled: executionMode === 'execute',
          onSelect: () => setExecutionMode('execute'),
        },
        {
          label: 'Mode: Hybrid',
          disabled: executionMode === 'hybrid',
          onSelect: () => setExecutionMode('hybrid'),
        },
        {
          label: 'Run',
          shortcut: 'Ctrl/Cmd+Shift+R',
          disabled: !activeFile,
          onSelect: () => onRun(),
        },
      ],
      terminal: [
        {
          label: 'Toggle Results Pane',
          shortcut: 'Ctrl/Cmd+J',
          onSelect: toggleResults,
        },
      ],
      help: [
        {
          label: 'Examples',
          onSelect: () => globalThis.window?.open('/examples', '_blank'),
        },
        {
          label: 'Documentation',
          onSelect: () => globalThis.window?.open('/docs', '_blank'),
        },
        {
          label: 'Add New Language…',
          onSelect: () => setShowAddLanguage(true),
        },
      ],
    }),
    [activeFile, executionMode, handleExport, onRun, setExecutionMode, theme, toggleResults, toggleSidebar, toggleTheme],
  )

  const menuLabels: Array<{ id: MenuId; label: string }> = [
    { id: 'file', label: 'File' },
    { id: 'edit', label: 'Edit' },
    { id: 'selection', label: 'Selection' },
    { id: 'view', label: 'View' },
    { id: 'run', label: 'Run' },
    { id: 'terminal', label: 'Terminal' },
    { id: 'help', label: 'Help' },
  ]

  return (
    <>
      <div ref={barRef} className="h-12 bg-editor-sidebar border-b border-editor-border flex items-center px-3 select-none">
        <Link href="/" className="flex items-center gap-2 pr-3">
          <div className="flex items-center justify-center w-6 h-6">
            <Image
              src="/QCanvas-logo-Black.svg"
              alt="QCanvas"
              width={24}
              height={24}
              className="object-contain block dark:hidden"
              priority
            />
            <Image
              src="/QCanvas-logo-White.svg"
              alt="QCanvas"
              width={24}
              height={24}
              className="object-contain hidden dark:block"
              priority
            />
          </div>
          <span className="text-sm font-bold quantum-gradient bg-clip-text text-transparent hidden sm:block">QCanvas</span>
        </Link>

        <div className="flex items-center gap-1">
        {menuLabels.map((m) => (
          <div key={m.id} className="relative">
            <button
              type="button"
              className={`px-2 py-1 text-xs rounded ${openMenu === m.id ? 'bg-editor-border text-white' : 'text-editor-text hover:bg-editor-border hover:text-white'}`}
              onClick={() => setOpenMenu((cur) => (cur === m.id ? null : m.id))}
              onMouseEnter={() => {
                if (openMenu) setOpenMenu(m.id)
              }}
            >
              {m.label}
            </button>

            {openMenu === m.id && (
              <div className="absolute left-0 top-full mt-1 w-56 bg-editor-sidebar border border-editor-border rounded-md shadow-xl z-50 overflow-hidden">
                {menus[m.id].map((item, idx) => (
                  <button
                    key={`${m.id}-${idx}`}
                    type="button"
                    disabled={item.disabled}
                    className={`w-full flex items-center justify-between px-3 py-2 text-xs text-left ${
                      item.disabled
                        ? 'opacity-50 cursor-not-allowed text-editor-text'
                        : 'text-editor-text hover:bg-editor-border hover:text-white'
                    }`}
                    onClick={() => {
                      item.onSelect()
                      setOpenMenu(null)
                    }}
                  >
                    <span>{item.label}</span>
                    {item.shortcut && <span className="text-[10px] text-black dark:text-gray-400">{item.shortcut}</span>}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
        </div>

        <div className="ml-auto flex items-center gap-2">
          <button
            type="button"
            className="text-xs text-editor-text hover:text-white px-2 py-1 rounded hover:bg-editor-border hidden sm:inline-flex"
            onClick={() => setShowTemplatesPicker(true)}
          >
            Templates
          </button>
          <div className="text-[11px] text-black dark:text-gray-400 hidden md:block">
            {activeFile ? activeFile.name : 'No file selected'}
          </div>
          {isAuthenticated ? (
            <ProfileDropdown onLogout={handleLogout} />
          ) : (
            <Link href="/login" className="text-xs text-editor-text hover:text-white px-2 py-1 rounded hover:bg-editor-border">
              Login
            </Link>
          )}
        </div>
      </div>

      <ShareModal
        isOpen={showShareModal}
        onClose={() => setShowShareModal(false)}
        fileContent={activeFile?.content || ''}
        fileName={activeFile?.name || ''}
      />

      <AddNewLanguage isOpen={showAddLanguage} onClose={() => setShowAddLanguage(false)} />

      {showTemplatesPicker && (
        <>
          <button
            type="button"
            className="fixed inset-0 bg-black/50 z-[55] cursor-default"
            onClick={() => setShowTemplatesPicker(false)}
            aria-label="Close templates picker"
          />
          <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div className="quantum-glass-dark rounded-2xl p-6 max-w-2xl w-full border border-white/10 shadow-2xl max-h-[80vh] overflow-hidden">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">Templates</h3>
                <button
                  type="button"
                  className="btn-ghost p-1 hover:bg-editor-border"
                  onClick={() => setShowTemplatesPicker(false)}
                  aria-label="Close"
                >
                  ✕
                </button>
              </div>
              <div className="overflow-y-auto max-h-[65vh] pr-1 space-y-2">
                {FILE_TEMPLATES_PRESETS.map((t) => (
                  <button
                    key={t.filename}
                    type="button"
                    className="w-full text-left px-3 py-3 rounded-lg border border-editor-border hover:bg-editor-border transition-colors"
                    onClick={async () => {
                      await useFileStore.getState().createFile(t.filename, t.content)
                      setShowTemplatesPicker(false)
                    }}
                  >
                    <div className="text-sm font-semibold text-white">{t.name}</div>
                    <div className="text-xs text-black dark:text-gray-400 mt-1">{t.description}</div>
                    <div className="text-[11px] text-black dark:text-gray-500 mt-1 font-mono">{t.filename}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </>
      )}

      {showShortcuts && (
        <>
          <button
            type="button"
            className="fixed inset-0 bg-black/50 z-[55] cursor-default"
            onClick={() => setShowShortcuts(false)}
            aria-label="Close keyboard shortcuts"
          />
          <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
            <div className="quantum-glass-dark rounded-2xl p-6 max-w-md w-full border border-white/10 shadow-2xl">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white">Keyboard Shortcuts</h3>
                <button
                  type="button"
                  className="btn-ghost p-1 hover:bg-editor-border"
                  onClick={() => setShowShortcuts(false)}
                  aria-label="Close"
                >
                  ✕
                </button>
              </div>
              <div className="space-y-2 text-sm text-editor-text">
                <div className="flex justify-between"><span>Save</span><kbd className="px-2 py-1 bg-editor-bg border border-editor-border rounded text-xs">Ctrl/Cmd+S</kbd></div>
                <div className="flex justify-between"><span>Find</span><kbd className="px-2 py-1 bg-editor-bg border border-editor-border rounded text-xs">Ctrl/Cmd+F</kbd></div>
                <div className="flex justify-between"><span>Replace</span><kbd className="px-2 py-1 bg-editor-bg border border-editor-border rounded text-xs">Ctrl/Cmd+H</kbd></div>
                <div className="flex justify-between"><span>Run</span><kbd className="px-2 py-1 bg-editor-bg border border-editor-border rounded text-xs">Ctrl/Cmd+Shift+R</kbd></div>
                <div className="flex justify-between"><span>Toggle Results</span><kbd className="px-2 py-1 bg-editor-bg border border-editor-border rounded text-xs">Ctrl/Cmd+J</kbd></div>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  )
}

