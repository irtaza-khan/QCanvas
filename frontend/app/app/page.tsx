'use client'

import { useEffect, useState, useRef } from 'react'
import { useFileStore } from '@/lib/store'
import { fileApi } from '@/lib/api'
import EditorPane from '@/components/EditorPane'
import ResultsPane from '@/components/ResultsPane'
import TopBar from '@/components/TopBar'
import Sidebar from '@/components/Sidebar'
import KeyboardShortcuts from '@/components/KeyboardShortcuts'
import toast from 'react-hot-toast'

// Disable static generation for this page
export const dynamic = 'force-dynamic'

export default function AppPage() {
  const [isMobile, setIsMobile] = useState(false)
  const [resultsHeight, setResultsHeight] = useState(320) // Default height
  const [isDragging, setIsDragging] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)
  const { 
    setFiles, 
    files, 
    sidebarCollapsed, 
    toggleSidebar,
    resultsCollapsed 
  } = useFileStore()

  // Check for mobile screen size
  useEffect(() => {
    const checkMobile = () => {
      if (typeof window !== 'undefined') {
        setIsMobile(window.innerWidth < 768)
      }
    }
    
    checkMobile()
    if (typeof window !== 'undefined') {
      window.addEventListener('resize', checkMobile)
      return () => window.removeEventListener('resize', checkMobile)
    }
  }, [])

  // Auto-collapse sidebar on mobile
  useEffect(() => {
    if (isMobile && !sidebarCollapsed) {
      toggleSidebar()
    }
  }, [isMobile]) // eslint-disable-line react-hooks/exhaustive-deps

  // Load files on component mount
  useEffect(() => {
    const loadFiles = async () => {
      try {
        const result = await fileApi.getFiles()
        if (result.success && result.data) {
          setFiles(result.data)
        }
      } catch (error) {
        console.error('Failed to load files:', error)
        // Keep using the mock files from store if API fails
      }
    }

    // Only load from API if we don't have files yet
    if (files.length === 0) {
      loadFiles()
    }
  }, [setFiles, files.length])

  // Listen for inter-tab messages to add files from examples page
  useEffect(() => {
    if (typeof window === 'undefined') return
    
    const channel = new BroadcastChannel('qcanvas-examples')

    channel.onmessage = (event) => {
      if (event.data.type === 'add-example-file') {
        const { filename, code } = event.data
        // Add the file and set it as active
        useFileStore.getState().addFile(filename, code)
        toast.success(`Loaded example: ${filename}`)

        // Send confirmation back to examples page
        channel.postMessage({
          type: 'file-added',
          filename
        })
      }
    }

    return () => {
      channel.close()
    }
  }, [])

  // Handle global save event
  useEffect(() => {
    if (typeof window === 'undefined') return
    
    const handleSave = async () => {
      const activeFile = useFileStore.getState().getActiveFile()
      if (!activeFile) {
        toast.error('No file to save')
        return
      }

      try {
        const result = await fileApi.updateFile(activeFile.id, {
          content: activeFile.content,
        })

        if (result.success) {
          toast.success(`Saved ${activeFile.name}`)
        } else {
          throw new Error(result.error)
        }
      } catch (error) {
        toast.error('Save failed')
        console.error('Save error:', error)
      }
    }

    window.addEventListener('save-file', handleSave)
    return () => window.removeEventListener('save-file', handleSave)
  }, [])

  // Handle drag resize for results panel
  useEffect(() => {
    if (!isDragging) return

    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return

      const containerRect = containerRef.current.getBoundingClientRect()
      const newHeight = containerRect.bottom - e.clientY
      const minHeight = 100
      const maxHeight = containerRect.height - 200 // Leave space for editor

      setResultsHeight(Math.max(minHeight, Math.min(maxHeight, newHeight)))
    }

    const handleMouseUp = () => {
      setIsDragging(false)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging])

  const handleDragStart = (e: React.MouseEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <KeyboardShortcuts />
      <TopBar />
      
      <div className="flex flex-1 min-h-0 overflow-hidden">
        {/* Sidebar */}
        <div className={`${
          sidebarCollapsed 
            ? 'w-0 md:w-12' 
            : 'w-full md:w-80'
        } transition-all duration-300 ${
          isMobile && !sidebarCollapsed 
            ? 'absolute inset-y-0 left-0 z-50 shadow-xl' 
            : ''
        } overflow-hidden`}>
          <Sidebar />
        </div>

        {/* Mobile overlay when sidebar is open */}
        {isMobile && !sidebarCollapsed && (
          <div 
            className="absolute inset-0 bg-black bg-opacity-50 z-40"
            onClick={toggleSidebar}
          />
        )}
        
        {/* Main content */}
        <main ref={containerRef} className="flex-1 flex flex-col min-h-0 overflow-hidden">
          <div className="flex flex-col h-full overflow-hidden">
            {/* Editor Area */}
            <div 
              className="flex-1 overflow-hidden"
              style={{ height: resultsCollapsed ? '100%' : `calc(100% - ${resultsHeight}px)` }}
            >
              <EditorPane />
            </div>

            {/* Drag Handle */}
            {!resultsCollapsed && (
              <div
                className={`h-1 bg-editor-border hover:bg-quantum-blue-light cursor-row-resize transition-colors ${
                  isDragging ? 'bg-quantum-blue-light' : ''
                }`}
                onMouseDown={handleDragStart}
                title="Drag to resize"
              />
            )}

            {/* Results Panel */}
            {!resultsCollapsed && (
              <div 
                className="overflow-hidden border-t border-editor-border"
                style={{ height: `${resultsHeight}px` }}
              >
                <ResultsPane />
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
