'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { Zap, Users, Github, Moon, Sun, Menu, X, Linkedin, Mail } from 'lucide-react'
import { useFileStore } from '@/lib/store'
import { config, getCopyrightText } from '@/lib/config'

export default function AboutPage() {
  const { theme, toggleTheme } = useFileStore()
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [scrollY, setScrollY] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-editor-bg via-gray-900 to-editor-bg relative overflow-x-hidden">
      {/* Navigation */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrollY > 50 ? 'bg-black/80 backdrop-blur-lg border-b border-white/10' : 'bg-transparent'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <Link href="/" className="flex items-center space-x-2 group">
              <div className="relative">
                <Image
                  src="/QCanvas-logo-Black.svg"
                  alt="QCanvas Logo"
                  width={48}
                  height={48}
                  className="object-contain block dark:hidden transition-all duration-300 hover:scale-110 animate-pulse"
                  priority
                />
                <Image
                  src="/QCanvas-logo-White.svg"
                  alt="QCanvas Logo"
                  width={48}
                  height={48}
                  className="object-contain hidden dark:block transition-all duration-300 hover:scale-110 animate-pulse"
                  priority
                />
              </div>
              <span className="text-2xl font-bold quantum-gradient bg-clip-text text-transparent transition-all duration-200">
                QCanvas
              </span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-8">
              <Link href="/" className="text-editor-text hover:text-white transition-colors duration-200">
                Home
              </Link>
              <Link href="/examples" className="text-editor-text hover:text-white transition-colors duration-200">
                Examples
              </Link>
              <Link href="/docs" className="text-editor-text hover:text-white transition-colors duration-200">
                Documentation
              </Link>
              <Link href="/about" className="text-white font-medium underline decoration-quantum-blue-light decoration-2 underline-offset-4">
                About Us
              </Link>

              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg bg-editor-bg/50 border border-editor-border hover:border-quantum-blue-light transition-colors duration-200"
                title="Toggle theme"
              >
                {theme === 'dark' ? <Sun className="w-5 h-5 text-editor-text" /> : <Moon className="w-5 h-5 text-editor-text" />}
              </button>

              {/* Auth Buttons */}
              <div className="flex items-center space-x-3">
                <Link
                  href="/login"
                  className="text-editor-text hover:text-white transition-colors duration-200 font-medium"
                >
                  Sign In
                </Link>
                <Link
                  href="/login"
                  className="btn-quantum text-sm px-4 py-2"
                >
                  Get Started
                </Link>
              </div>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 rounded-lg bg-editor-bg/50 border border-editor-border"
            >
              {isMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>

          {/* Mobile Menu */}
          {isMenuOpen && (
            <div className="md:hidden bg-black/95 backdrop-blur-lg border-t border-white/10">
              <div className="px-4 py-4 space-y-4">
                <Link href="/" className="block text-editor-text hover:text-white transition-colors duration-200">
                  Home
                </Link>
                <Link href="/examples" className="block text-editor-text hover:text-white transition-colors duration-200">
                  Examples
                </Link>
                <Link href="/docs" className="block text-editor-text hover:text-white transition-colors duration-200">
                  Documentation
                </Link>
                <Link href="/about" className="block text-white font-medium transition-colors duration-200">
                  About Us
                </Link>

                <div className="flex items-center justify-between pt-4 border-t border-white/10">
                  <button
                    onClick={toggleTheme}
                    className="flex items-center space-x-2 text-editor-text hover:text-white transition-colors duration-200"
                  >
                    {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                    <span>Theme</span>
                  </button>
                  <div className="flex space-x-3">
                    <Link href="/login" className="text-editor-text hover:text-white transition-colors duration-200">
                      Sign In
                    </Link>
                    <Link href="/login" className="btn-quantum text-sm px-3 py-1">
                      Get Started
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-4 pt-20">
        {/* Animated Background */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-96 h-96 bg-quantum-blue-light opacity-10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-500 opacity-10 rounded-full blur-3xl animate-pulse delay-1000"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-teal-500 opacity-5 rounded-full blur-3xl animate-pulse delay-500"></div>
        </div>

        <div className="text-center max-w-6xl mx-auto relative z-10">
          <div className="inline-flex items-center justify-center w-24 h-24 rounded-full quantum-gradient mb-6 shadow-2xl">
            <Zap className="w-12 h-12 text-white" />
          </div>
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            About <span className="quantum-gradient bg-clip-text text-transparent">Us</span>
          </h1>
          <p className="text-xl md:text-2xl text-editor-text mb-8 max-w-3xl mx-auto leading-relaxed">
            Meet the passionate team behind QCanvas, dedicated to advancing quantum computing education 
            and research through innovative simulation tools and framework unification.
          </p>
        </div>
      </section>

      {/* Team Section */}
      <div className="px-4 py-16">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-white text-center mb-12">Our Teams</h2>
          
          {/* QCanvas Team */}
          <div className="mb-16">
            <h3 className="text-2xl font-bold text-white text-center mb-8">QCanvas Team</h3>
            <div className="grid md:grid-cols-3 gap-8">
              {config.qcanvasTeam.map((member) => (
                <div key={member.name} className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10 text-center hover:border-quantum-blue-light transition-all duration-300">
                  <div className="w-20 h-20 quantum-gradient rounded-full flex items-center justify-center mx-auto mb-6">
                    <Users className="w-10 h-10 text-white" />
                  </div>
                  <h4 className="text-xl font-semibold text-white mb-4">{member.name}</h4>
                  <div className="flex justify-center space-x-3">
                    {member.email && (
                      <a href={`mailto:${member.email}`} className="p-2 bg-editor-bg rounded-lg text-editor-text hover:text-white hover:bg-red-600 transition-colors" title="Email">
                        <Mail className="w-5 h-5" />
                      </a>
                    )}
                    {member.github && (
                      <a href={member.github} target="_blank" rel="noopener noreferrer" className="p-2 bg-editor-bg rounded-lg text-editor-text hover:text-white hover:bg-gray-700 transition-colors" title="GitHub">
                        <Github className="w-5 h-5" />
                      </a>
                    )}
                    {member.linkedin && (
                      <a href={member.linkedin} target="_blank" rel="noopener noreferrer" className="p-2 bg-editor-bg rounded-lg text-editor-text hover:text-white hover:bg-blue-600 transition-colors" title="LinkedIn">
                        <Linkedin className="w-5 h-5" />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* QSim Team */}
          <div>
            <h3 className="text-2xl font-bold text-white text-center mb-8">QSim Team</h3>
            <div className="grid md:grid-cols-3 gap-8">
              {config.qsimTeam.map((member) => (
                <div key={member.name} className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10 dark:border-white/10 border-gray-200 text-center hover:border-purple-500 dark:hover:border-purple-500 hover:border-purple-400 transition-all duration-300">
                  <div className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg bg-gradient-to-r from-pink-500 to-rose-500 dark:from-purple-500 dark:to-pink-500">
                    <Users className="w-10 h-10 text-white" />
                  </div>
                  <h4 className="text-xl font-semibold text-white mb-4">{member.name}</h4>
                  <div className="flex justify-center space-x-3">
                    {member.email && (
                      <a href={`mailto:${member.email}`} className="p-2 bg-editor-bg rounded-lg text-editor-text hover:text-white hover:bg-red-600 transition-colors" title="Email">
                        <Mail className="w-5 h-5" />
                      </a>
                    )}
                    {member.github && (
                      <a href={member.github} target="_blank" rel="noopener noreferrer" className="p-2 bg-editor-bg rounded-lg text-editor-text hover:text-white hover:bg-gray-700 transition-colors" title="GitHub">
                        <Github className="w-5 h-5" />
                      </a>
                    )}
                    {member.linkedin && (
                      <a href={member.linkedin} target="_blank" rel="noopener noreferrer" className="p-2 bg-editor-bg rounded-lg text-editor-text hover:text-white hover:bg-blue-600 transition-colors" title="LinkedIn">
                        <Linkedin className="w-5 h-5" />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Initiative Section */}
      <div className="px-4 py-16 bg-gradient-to-b from-transparent to-editor-bg/20">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-white mb-8">Built under</h2>
          <div className="quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10">
            <div className="text-4xl font-bold quantum-gradient bg-clip-text text-transparent mb-2">
              {config.initiative.name}
            </div>
            <p className="text-xl text-editor-text">{config.initiative.tagline}</p>
          </div>

          {/* <div className="mt-12">
            <h3 className="text-2xl font-semibold text-white mb-6">Project Supervisors</h3>
            <div className="grid md:grid-cols-2 gap-6">
              {config.supervisors.map((supervisor) => (
                <div key={supervisor.name} className="quantum-glass-dark rounded-xl p-6 backdrop-blur-xl border border-white/10 text-center">
                  <h4 className="text-lg font-semibold text-white mb-2">{supervisor.name}</h4>
                  <p className="text-editor-text">{supervisor.role}</p>
                </div>
              ))}
            </div>
          </div> */}

          <div className='mt-12'>
            <h3 className="text-2xl font-bold text-white text-center mb-6">Supervisors</h3>
            <div className="grid md:grid-cols-2 gap-6">
              {config.supervisors.map((supervisor) => (
                <div key={supervisor.name} className="quantum-glass-dark rounded-xl p-6 backdrop-blur-xl border border-white/10 dark:border-white/10 border-gray-200 text-center hover:border-purple-500 dark:hover:border-purple-500 hover:border-purple-400 transition-all duration-300">
                  {/* <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-6">
                    <Users className="w-10 h-10 text-white" />
                  </div> */}
                  <h4 className="text-xl font-semibold text-white mb-4">{supervisor.name}</h4>
                  <div className="flex justify-center space-x-3">
                    {supervisor.email && (
                      <a href={`mailto:${supervisor.email}`} className="p-2 bg-editor-bg rounded-lg text-editor-text hover:text-white hover:bg-red-600 transition-colors" title="Email">
                        <Mail className="w-5 h-5" />
                      </a>
                    )}
                    {supervisor.github && (
                      <a href={supervisor.github} target="_blank" rel="noopener noreferrer" className="p-2 bg-editor-bg rounded-lg text-editor-text hover:text-white hover:bg-gray-700 transition-colors" title="GitHub">
                        <Github className="w-5 h-5" />
                      </a>
                    )}
                    {supervisor.linkedin && (
                      <a href={supervisor.linkedin} target="_blank" rel="noopener noreferrer" className="p-2 bg-editor-bg rounded-lg text-editor-text hover:text-white hover:bg-blue-600 transition-colors" title="LinkedIn">
                        <Linkedin className="w-5 h-5" />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="px-4 py-8 border-t border-editor-border">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-editor-text">
            {getCopyrightText()}
          </p>
          <div className="flex justify-center space-x-6 mt-4">
            {config.footer.support.map((link) => (
              <a
                key={link.email || link.name}
                href={link.email ? `mailto:${link.email}` : '#'}
                className="text-editor-text hover:text-white transition-colors"
              >
                {link.name}
              </a>
            ))}
            <a
              href={config.social.github}
              target="_blank"
              rel="noopener noreferrer"
              className="text-editor-text hover:text-white transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
      </footer>
    </div>
  )
}
