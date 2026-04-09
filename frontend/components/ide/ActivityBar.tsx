'use client'

import { Search, Folder as FolderIcon, Sparkles } from 'lucide-react'

export type ActivityView = 'explorer' | 'search' | 'run' | 'cirqAssistant'

export default function ActivityBar({
  active,
  assistantOpen,
  onChange,
}: Readonly<{
  active: ActivityView
  assistantOpen?: boolean
  onChange: (v: ActivityView) => void
}>) {
  const items: Array<{ id: ActivityView; label: string; Icon: any }> = [
    { id: 'explorer', label: 'Explorer', Icon: FolderIcon },
    { id: 'search', label: 'Search', Icon: Search },
    { id: 'cirqAssistant', label: 'Cirq AI', Icon: Sparkles },
  ]

  return (
    <div className="w-12 bg-editor-sidebar flex flex-col items-center py-2 gap-1.5">
      {items.map(({ id, label, Icon }) => (
        (() => {
          const isActive = id === 'cirqAssistant' ? !!assistantOpen : active === id
          return (
        <button
          key={id}
          type="button"
          title={label}
          onClick={() => onChange(id)}
          className={`relative w-10 h-10 rounded-md flex items-center justify-center transition-all ${
            isActive
              ? 'bg-editor-panelHigh text-white shadow-[0_0_18px_rgba(70,234,237,0.14)]'
              : 'text-editor-text hover:bg-editor-panelHigh/80 hover:text-white'
          }`}
        >
          {isActive && (
            <span className="absolute left-0 top-1/2 h-6 w-0.5 -translate-y-1/2 rounded-r bg-framework-cirq" />
          )}
          <Icon className="w-5 h-5" />
        </button>
          )
        })()
      ))}
    </div>
  )
}

