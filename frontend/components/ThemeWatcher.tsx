'use client'

import { useEffect } from 'react'
import { useFileStore } from '@/lib/store'

export default function ThemeWatcher() {
  const theme = useFileStore((s) => s.theme)
  const setTheme = useFileStore((s) => s.setTheme)

  useEffect(() => {
    // Initialize theme on mount - ALWAYS default to dark
    if (typeof window === 'undefined') return
    
    try {
      const saved = localStorage.getItem('qcanvas-theme') as 'light' | 'dark' | null
      const effective = saved === 'light' ? 'light' : 'dark' // Only use light if explicitly set
      
      // Apply theme to document immediately
      document.documentElement.classList.remove('light', 'dark')
      document.documentElement.classList.add(effective)
      
      // Update store only if different
      if (effective !== theme) {
        setTheme(effective)
      }
    } catch {
      // Fallback to dark theme
      document.documentElement.classList.remove('light')
      document.documentElement.classList.add('dark')
      setTheme('dark')
    }
  }, [setTheme]) // Only run once on mount

  useEffect(() => {
    // Apply theme changes from store to document
    if (typeof window === 'undefined') return
    
    document.documentElement.classList.remove('light', 'dark')
    document.documentElement.classList.add(theme)
  }, [theme])

  return null
}


