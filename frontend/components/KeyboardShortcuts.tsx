'use client'

import { useEffect } from 'react'
import { useFileStore } from '@/lib/store'
import toast from 'react-hot-toast'

export default function KeyboardShortcuts() {
  const { 
    toggleSidebar, 
    toggleResults, 
    toggleTheme,
    addFile,
    files,
    activeFileId,
    setActiveFile 
  } = useFileStore()

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isCtrlOrCmd = e.ctrlKey || e.metaKey
      
      // Prevent default for our shortcuts
      if (isCtrlOrCmd) {
        switch (e.key) {
          case 's':
            e.preventDefault()
            // Save file (handled by editor)
            window.dispatchEvent(new CustomEvent('save-file'))
            break
            
          case 'n':
            e.preventDefault()
            // New file
            const fileName = prompt('Enter file name:')
            if (fileName) {
              addFile(fileName)
              toast.success(`Created ${fileName}`)
            }
            break
            
          case 'b':
            e.preventDefault()
            // Toggle sidebar
            toggleSidebar()
            break
            
          case 'j':
            e.preventDefault()
            // Toggle results panel
            toggleResults()
            break
            
          case 'k':
            if (e.shiftKey) {
              e.preventDefault()
              // Toggle theme
              toggleTheme()
            }
            break
            
          case 'r':
            if (e.shiftKey) {
              e.preventDefault()
              // Run circuit
              window.dispatchEvent(new CustomEvent('circuit-execute'))
              toast.success('Running circuit...')
            }
            break
        }
      }

      // File navigation with Tab
      if (e.key === 'Tab' && isCtrlOrCmd && files.length > 0) {
        e.preventDefault()
        const currentIndex = files.findIndex(f => f.id === activeFileId)
        const nextIndex = e.shiftKey 
          ? (currentIndex - 1 + files.length) % files.length
          : (currentIndex + 1) % files.length
        setActiveFile(files[nextIndex].id)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [toggleSidebar, toggleResults, toggleTheme, addFile, files, activeFileId, setActiveFile])

  return null // This component only handles keyboard events
}
