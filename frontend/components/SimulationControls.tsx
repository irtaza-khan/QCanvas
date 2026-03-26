'use client'

import { useState, useEffect } from 'react'
import { Settings } from '@/components/Icons';
import { ChevronDown } from 'lucide-react';;import { InputLanguage } from '@/types'

interface SimulationControlsProps {
  readonly inputLanguage: InputLanguage | ""
  readonly setInputLanguage: (language: InputLanguage | "") => void
  readonly simBackend: 'cirq' | 'qiskit' | 'pennylane' | ''
  readonly setSimBackend: (backend: 'cirq' | 'qiskit' | 'pennylane' | '') => void
  readonly shots: number
  readonly setShots: (shots: number) => void
}

export default function SimulationControls({
  inputLanguage,
  setInputLanguage,
  simBackend,
  setSimBackend,
  shots,
  setShots
}: Readonly<SimulationControlsProps>) {
  const [hoveredControl, setHoveredControl] = useState<string | null>(null)
  // Local state for shots input to allow empty string during editing
  const [shotsInput, setShotsInput] = useState<string>(shots.toString())

  // Sync local state when shots prop changes from outside
  useEffect(() => {
    setShotsInput(shots.toString())
  }, [shots])

  return (
    <div className="min-h-[72px] bg-editor-sidebar border-b border-editor-border flex items-center justify-between px-6 py-3 animate-fade-in">
      {/* Left Side - Title */}
      <div className="flex items-center space-x-3 animate-slide-in-left">
        <div className="p-2 bg-quantum-blue-light/10 rounded-lg border border-quantum-blue-light/20 animate-pulse-subtle">
          <Settings className="w-4 h-4 text-quantum-blue-light" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-white tracking-wide">Simulation Settings</h3>
          <p className="text-xs text-black dark:text-gray-400">Configure your quantum execution</p>
        </div>
      </div>
      
      {/* Right Side - Controls */}
      <div className="flex items-center gap-4 animate-slide-in-right">
        {/* Input Framework Dropdown */}
        <div 
          className="relative group"
          onMouseEnter={() => setHoveredControl('framework')}
          onMouseLeave={() => setHoveredControl(null)}
        >
          <div className="text-xs font-medium text-black dark:text-gray-400 mb-2 text-center transition-colors duration-200 group-hover:text-quantum-blue-light">
            Input Framework
          </div>
          <div className="relative">
            <select
              value={inputLanguage}
              onChange={(e) => setInputLanguage(e.target.value as InputLanguage)}
              className={`appearance-none bg-editor-bg border text-xs text-white rounded-lg px-4 py-2.5 pr-10 focus-quantum transition-all duration-300 cursor-pointer min-w-[160px] font-medium shadow-lg hover:shadow-quantum-blue-light/20 ${
                hoveredControl === 'framework' 
                  ? 'border-quantum-blue-light scale-105 shadow-quantum-blue-light/30' 
                  : inputLanguage 
                    ? 'border-quantum-blue-light/50' 
                    : 'border-editor-border'
              }`}
              title="Select Input Framework"
              aria-label="Input Framework"
            >
              <option value="" className="bg-editor-bg text-black dark:text-gray-400">Select Framework</option>
              <option value="qasm" className="bg-editor-bg text-white">OpenQASM</option>
              <option value="qiskit" className="bg-editor-bg text-white">Qiskit (IBM)</option>
              <option value="cirq" className="bg-editor-bg text-white">Cirq (Google)</option>
              <option value="pennylane" className="bg-editor-bg text-white">PennyLane (ML)</option>
            </select>
            <ChevronDown className={`absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-black dark:text-gray-400 pointer-events-none transition-all duration-300 ${
              hoveredControl === 'framework' ? 'text-quantum-blue-light rotate-180' : ''
            }`} />
          </div>
        </div>

        {/* Simulation Backend Dropdown */}
        <div 
          className="relative group"
          onMouseEnter={() => setHoveredControl('backend')}
          onMouseLeave={() => setHoveredControl(null)}
        >
          <div className="text-xs font-medium text-black dark:text-gray-400 mb-2 text-center transition-colors duration-200 group-hover:text-purple-400">
            Simulation Backend
          </div>
          <div className="relative">
            <select
              value={simBackend}
              onChange={(e) => setSimBackend(e.target.value as 'cirq' | 'qiskit' | 'pennylane')}
              className={`appearance-none bg-editor-bg border text-xs text-white rounded-lg px-4 py-2.5 pr-10 focus-quantum transition-all duration-300 cursor-pointer min-w-[160px] font-medium shadow-lg hover:shadow-purple-500/20 ${
                hoveredControl === 'backend' 
                  ? 'border-purple-500 scale-105 shadow-purple-500/30' 
                  : simBackend 
                    ? 'border-purple-500/50' 
                    : 'border-editor-border'
              }`}
              title="Select Simulation Backend"
              aria-label="Simulation Backend"
            >
              <option value="" className="bg-editor-bg text-black dark:text-gray-400">Select Backend</option>
              <option value="cirq" className="bg-editor-bg text-white">Cirq Simulator</option>
              <option value="qiskit" className="bg-editor-bg text-white">Qiskit Aer</option>
              <option value="pennylane" className="bg-editor-bg text-white">PennyLane</option>
            </select>
            <ChevronDown className={`absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-black dark:text-gray-400 pointer-events-none transition-all duration-300 ${
              hoveredControl === 'backend' ? 'text-purple-400 rotate-180' : ''
            }`} />
          </div>
        </div>

        {/* Shots Input */}
        <div 
          className="relative group"
          onMouseEnter={() => setHoveredControl('shots')}
          onMouseLeave={() => setHoveredControl(null)}
        >
          <div className="text-xs font-medium text-black dark:text-gray-400 mb-2 text-center transition-colors duration-200 group-hover:text-green-400">
            Measurement Shots
          </div>
          <div className="relative">
            <input
              type="text"
              value={shotsInput}
              onChange={(e) => {
                const value = e.target.value
                // Allow empty string or valid numbers
                if (value === '' || /^\d+$/.test(value)) {
                  setShotsInput(value)
                }
              }}
              onBlur={(e) => {
                // When user leaves the field, validate and set the actual shots value
                const numValue = Number.parseInt(e.target.value)
                if (isNaN(numValue) || numValue < 1) {
                  setShotsInput('1024')
                  setShots(1024)
                } else {
                  const clampedValue = Math.min(Math.max(1, numValue), 100000)
                  setShotsInput(clampedValue.toString())
                  setShots(clampedValue)
                }
              }}
              onKeyDown={(e) => {
                // Allow Enter to blur and validate
                if (e.key === 'Enter') {
                  e.currentTarget.blur()
                }
              }}
              min="1"
              max="100000"
              className={`bg-editor-bg border text-xs text-white rounded-lg px-4 py-2.5 w-32 text-center focus-quantum transition-all duration-300 font-mono font-semibold shadow-lg hover:shadow-green-500/20 ${
                hoveredControl === 'shots' 
                  ? 'border-green-500 scale-105 shadow-green-500/30' 
                  : 'border-editor-border'
              }`}
              title="Number of measurement shots"
              placeholder="1024"
              aria-label="Number of Shots"
            />
            <div className="absolute inset-0 rounded-lg bg-green-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
          </div>
        </div>
      </div>
    </div>
  )
}

