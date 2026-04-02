'use client'

import { Search, Folder as FolderIcon, Play } from 'lucide-react'

export type ActivityView = 'explorer' | 'search' | 'run'

export default function ActivityBar({
  active,
  onChange,
}: {
  active: ActivityView
  onChange: (v: ActivityView) => void
}) {
  const items: Array<{ id: ActivityView; label: string; Icon: any }> = [
    { id: 'explorer', label: 'Explorer', Icon: FolderIcon },
    { id: 'search', label: 'Search', Icon: Search },
    { id: 'run', label: 'Run', Icon: Play },
  ]

  return (
    <div className="w-12 bg-editor-sidebar border-r border-editor-border flex flex-col items-center py-2 gap-1">
      {items.map(({ id, label, Icon }) => (
        <button
          key={id}
          type="button"
          title={label}
          onClick={() => onChange(id)}
          className={`w-10 h-10 rounded-md flex items-center justify-center transition-colors ${
            active === id ? 'bg-editor-border text-white' : 'text-editor-text hover:bg-editor-border hover:text-white'
          }`}
        >
          <Icon className="w-5 h-5" />
        </button>
      ))}
    </div>
  )
}

