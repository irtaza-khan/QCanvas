import type { Metadata, Viewport } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import { Toaster } from 'react-hot-toast'
import './globals.css'
import ThemeWatcher from '@/components/ThemeWatcher'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'QCanvas - Quantum Code Editor',
  description: 'A modern quantum circuit code editor with real-time conversion to OpenQASM 3.0 and visualization',
  keywords: ['quantum', 'qiskit', 'cirq', 'pennylane', 'quantum computing', 'code editor'],
  authors: [{ name: 'QCanvas Team' }],
  icons: {
    icon: '/favicon.svg?v=2',
    shortcut: '/favicon.svg?v=2',
    apple: '/favicon.svg?v=2',
  },
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  themeColor: '#1e3c72',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
        {/* Theme watcher mounts on client to sync html class based on store/localStorage */}
        <ThemeWatcher />
        <div className="app-layout">
          {children}
        </div>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 3000,
            className: 'toast-custom',
            style: {
              background: '#252526',
              color: '#d4d4d4',
              border: '1px solid #3e3e42',
            },
          }}
        />
      </body>
    </html>
  )
}
