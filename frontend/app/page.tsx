'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function HomePage() {
  const router = useRouter()

  useEffect(() => {
    // Redirect to app page immediately
    router.push('/app')
  }, [router])

  return (
    <div className="flex items-center justify-center h-screen bg-editor-bg">
      <div className="flex flex-col items-center space-y-4">
        <div className="w-8 h-8 border-4 border-quantum-blue-light border-t-transparent rounded-full spinner"></div>
        <p className="text-editor-text">Loading QCanvas...</p>
      </div>
    </div>
  )
}
