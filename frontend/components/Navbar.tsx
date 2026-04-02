'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { Moon, Sun } from '@/components/Icons';
import { Menu, X } from 'lucide-react'
import { usePathname } from 'next/navigation'
import { useFileStore } from '@/lib/store'
import { useAuthStore } from '@/lib/authStore'
import { config } from '@/lib/config'

interface NavbarProps {
  /** If provided, a "Features" button is rendered that scrolls to this section ID on the current page. */
  scrollToFeatures?: (sectionId: string) => void
}

export default function Navbar({ scrollToFeatures }: NavbarProps) {
  const pathname = usePathname()
  const { theme, toggleTheme } = useFileStore()
  const { isAuthenticated } = useAuthStore()
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [scrollY, setScrollY] = useState(0)

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navLinks = [
    ...(scrollToFeatures
      ? [{ name: 'Features', path: '#features', isScrollButton: true }]
      : [{ name: 'Home', path: '/', isScrollButton: false }]),
    { name: 'Examples', path: '/examples', isScrollButton: false },
    { name: 'Documentation', path: '/docs', isScrollButton: false },
    { name: 'About', path: '/about', isScrollButton: false },
  ]

  const isActive = (path: string) => {
    if (path.startsWith('#')) return false
    return pathname === path
  }

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrollY > 50 ? 'dark:bg-black/80 bg-white/90 backdrop-blur-lg border-b dark:border-white/10 border-gray-200 shadow-sm' : 'dark:bg-black/60 bg-white/70 backdrop-blur-md border-b dark:border-white/5 border-gray-200'}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <Link href="/" className="flex items-center space-x-2.5 group">
            <div className="relative logo-glow">
              <Image
                src="/QCanvas-logo-Black.svg"
                alt="QCanvas Logo"
                width={44}
                height={44}
                className="object-contain block dark:hidden transition-all duration-300 group-hover:scale-110"
                priority
              />
              <Image
                src="/QCanvas-logo-White.svg"
                alt="QCanvas Logo"
                width={44}
                height={44}
                className="object-contain hidden dark:block transition-all duration-300 group-hover:scale-110"
                priority
              />
            </div>
            <span className="text-2xl font-bold quantum-gradient bg-clip-text text-transparent">
              QCanvas
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navLinks.map((item) =>
              item.isScrollButton ? (
                <button
                  key={item.name}
                  onClick={() => scrollToFeatures?.('features')}
                  className={
                    pathname === '/'
                      ? 'text-white font-medium text-sm relative after:absolute after:bottom-[-4px] after:left-0 after:w-full after:h-[2px] after:bg-gradient-to-r after:from-indigo-500 after:to-cyan-500 after:rounded-full'
                      : 'text-black dark:text-gray-400 hover:text-white transition-colors duration-200 hover-underline text-sm font-medium'
                  }
                >
                  {item.name}
                </button>
              ) : (
                <Link
                  key={item.path}
                  href={item.path as any}
                  className={
                    isActive(item.path)
                      ? 'text-white font-medium text-sm relative after:absolute after:bottom-[-4px] after:left-0 after:w-full after:h-[2px] after:bg-gradient-to-r after:from-indigo-500 after:to-cyan-500 after:rounded-full'
                      : 'text-black dark:text-gray-400 hover:text-white transition-colors duration-200 hover-underline text-sm font-medium'
                  }
                >
                  {item.name}
                </Link>
              )
            )}

            {/* Theme Toggle */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl bg-white/5 border border-white/10 hover:border-indigo-500/40 hover:bg-white/10 transition-all duration-300"
              title="Toggle theme"
            >
              {theme === 'dark' ? <Sun className="w-4 h-4 text-black dark:text-gray-400" /> : <Moon className="w-4 h-4 text-black dark:text-gray-400" />}
            </button>

            {/* Auth Buttons */}
            <div className="flex items-center space-x-3">
              {isAuthenticated ? (
                <Link
                  href="/app"
                  className="btn-quantum text-sm px-5 py-2.5"
                >
                  Go to App
                </Link>
              ) : (
                <>
                  <Link
                    href="/login"
                    className="text-black dark:text-gray-400 hover:text-white transition-colors duration-200 font-medium text-sm"
                  >
                    Sign In
                  </Link>
                  <Link
                    href="/login"
                    className="btn-quantum text-sm px-5 py-2.5"
                  >
                    Get Started
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-xl bg-white/5 border border-white/10"
          >
            {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden bg-[#0a0a1a]/95 backdrop-blur-xl border-t border-white/5 rounded-b-2xl">
            <div className="px-4 py-4 space-y-4">
              {navLinks.map((item) =>
                item.isScrollButton ? (
                  <button
                    key={item.name}
                    onClick={() => {
                      scrollToFeatures?.('features')
                      setIsMenuOpen(false)
                    }}
                    className="block w-full text-left text-black dark:text-gray-400 hover:text-white transition-colors duration-200"
                  >
                    {item.name}
                  </button>
                ) : (
                  <Link
                    key={item.path}
                    href={item.path as any}
                    className={
                      isActive(item.path)
                        ? 'block text-white font-medium'
                        : 'block text-black dark:text-gray-400 hover:text-white transition-colors duration-200'
                    }
                    onClick={() => setIsMenuOpen(false)}
                  >
                    {item.name}
                  </Link>
                )
              )}

              <div className="flex items-center justify-between pt-4 border-t border-white/5">
                <button
                  onClick={toggleTheme}
                  className="flex items-center space-x-2 text-black dark:text-gray-400 hover:text-white transition-colors duration-200"
                >
                  {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                  <span>Theme</span>
                </button>
                <div className="flex space-x-3">
                  {isAuthenticated ? (
                    <Link href="/app" className="btn-quantum text-sm px-3 py-1.5">
                      Go to App
                    </Link>
                  ) : (
                    <>
                      <Link href="/login" className="text-black dark:text-gray-400 hover:text-white transition-colors duration-200">
                        Sign In
                      </Link>
                      <Link href="/login" className="btn-quantum text-sm px-3 py-1.5">
                        Get Started
                      </Link>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
