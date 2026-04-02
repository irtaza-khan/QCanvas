'use client'

import { useFileStore } from '@/lib/store'
import SimulationControls from '@/components/SimulationControls'
import { InputLanguage } from '@/types'

export default function RunView({
  inputLanguage,
  setInputLanguage,
  simBackend,
  setSimBackend,
  shots,
  setShots,
}: Readonly<{
  inputLanguage: InputLanguage | ''
  setInputLanguage: (language: InputLanguage | '') => void
  simBackend: 'cirq' | 'qiskit' | 'pennylane' | ''
  setSimBackend: (backend: 'cirq' | 'qiskit' | 'pennylane' | '') => void
  shots: number
  setShots: (shots: number) => void
}>) {
  const { executionMode, setExecutionMode } = useFileStore()
  const activeFile = useFileStore((s) => s.getActiveFile())

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="h-10 px-3 flex items-center border-b border-editor-border">
        <div className="text-xs font-semibold tracking-wider text-black dark:text-gray-400 uppercase">Run</div>
      </div>

      <div className="p-3 space-y-3 overflow-y-auto">
        <div className="text-xs text-black dark:text-gray-400">Execution mode</div>
        <div className="grid grid-cols-3 gap-2">
          {(['compile', 'execute', 'hybrid'] as const).map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => setExecutionMode(m)}
              className={`px-2 py-2 text-xs rounded border ${
                executionMode === m
                  ? 'bg-editor-accent border-editor-accent text-white'
                  : 'bg-editor-bg border-editor-border text-editor-text hover:bg-editor-border'
              }`}
            >
              {m}
            </button>
          ))}
        </div>

        <button
          type="button"
          disabled={!activeFile}
          className="w-full px-3 py-2 rounded text-sm font-semibold disabled:opacity-50 btn-quantum"
          onClick={() => globalThis.window?.dispatchEvent(new CustomEvent('menu-run'))}
        >
          Run
        </button>

        {executionMode !== 'hybrid' && (
          <div className="pt-3 border-t border-editor-border">
            <SimulationControls
              inputLanguage={inputLanguage}
              setInputLanguage={setInputLanguage}
              simBackend={simBackend}
              setSimBackend={setSimBackend}
              shots={shots}
              setShots={setShots}
            />
          </div>
        )}
      </div>
    </div>
  )
}

