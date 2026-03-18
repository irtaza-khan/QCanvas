'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { Zap, Moon, Sun } from '@/components/Icons';
import { Users, Github, Menu, X, Linkedin, Mail } from 'lucide-react';;import { useFileStore } from '@/lib/store'
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
    <div className="min-h-screen bg-[#0a0a1a] relative overflow-x-hidden text-white">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-grid-pattern opacity-30 pointer-events-none" />
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a1a] via-transparent to-[#0a0a1a] pointer-events-none" />
      <div className="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[800px] h-[600px] hero-spotlight opacity-30 blur-3xl pointer-events-none" />
      {/* Navigation */}
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrollY > 50 ? 'dark:bg-black/80 bg-white/90 backdrop-blur-lg border-b dark:border-white/10 border-gray-200 shadow-sm' : 'dark:bg-black/60 bg-white/70 backdrop-blur-md border-b dark:border-white/5 border-gray-200'}`}>
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
              <Link href="/" className="relative group px-3 py-2">
                <span className="relative z-10 dark:text-white text-gray-800 font-medium group-hover:text-quantum-blue-light transition-colors duration-300 text-base tracking-wide">Home</span>
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-quantum-blue-light transition-all duration-300 group-hover:w-full box-shadow-glow"></span>
              </Link>
              <Link href="/examples" className="relative group px-3 py-2">
                <span className="relative z-10 dark:text-white text-gray-800 font-medium group-hover:text-quantum-blue-light transition-colors duration-300 text-base tracking-wide">Examples</span>
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-quantum-blue-light transition-all duration-300 group-hover:w-full box-shadow-glow"></span>
              </Link>
              <Link href="/docs" className="relative group px-3 py-2">
                <span className="relative z-10 dark:text-white text-gray-800 font-medium group-hover:text-quantum-blue-light transition-colors duration-300 text-base tracking-wide">Documentation</span>
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-quantum-blue-light transition-all duration-300 group-hover:w-full box-shadow-glow"></span>
              </Link>
              <Link href="/about" className="relative group px-3 py-2">
                 <span className="relative z-10 text-quantum-blue-light font-medium transition-colors duration-300 text-base tracking-wide">About Us</span>
                 <span className="absolute bottom-0 left-0 w-full h-0.5 bg-quantum-blue-light box-shadow-glow"></span>
              </Link>

              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 rounded-lg bg-white/5 border border-white/10 hover:border-quantum-blue-light transition-colors duration-200"
                title="Toggle theme"
              >
                {theme === 'dark' ? <Sun className="w-5 h-5 text-editor-text" /> : <Moon className="w-5 h-5 text-editor-text" />}
              </button>

              {/* Auth Buttons */}
              <div className="flex items-center space-x-3">
                <Link
                  href="/login"
                  className="dark:text-white text-gray-800 hover:text-quantum-blue-light transition-colors duration-300 font-medium px-4"
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
              className="md:hidden p-2 rounded-lg bg-white/5 border border-white/10"
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
        {/* Subtle background orbs — fewer, more vibrant */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-32 -right-32 w-[500px] h-[500px] bg-indigo-500 opacity-[0.07] rounded-full blur-[100px]"></div>
          <div className="absolute -bottom-32 -left-32 w-[500px] h-[500px] bg-violet-500 opacity-[0.07] rounded-full blur-[100px]"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-cyan-500 opacity-[0.05] rounded-full blur-[80px]"></div>
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
                      <a href={`mailto:${member.email}`} className="p-2 bg-white/5 border border-white/10 rounded-lg text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="Email">
                        <Mail className="w-5 h-5" />
                      </a>
                    )}
                    {member.github && (
                      <a href={member.github} target="_blank" rel="noopener noreferrer" className="p-2 bg-white/5 border border-white/10 rounded-lg text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="GitHub">
                        <Github className="w-5 h-5" />
                      </a>
                    )}
                    {member.linkedin && (
                      <a href={member.linkedin} target="_blank" rel="noopener noreferrer" className="p-2 bg-white/5 border border-white/10 rounded-lg text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="LinkedIn">
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
                      <a href={`mailto:${member.email}`} className="p-2 bg-white/5 border border-white/10 rounded-lg text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="Email">
                        <Mail className="w-5 h-5" />
                      </a>
                    )}
                    {member.github && (
                      <a href={member.github} target="_blank" rel="noopener noreferrer" className="p-2 bg-white/5 border border-white/10 rounded-lg text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="GitHub">
                        <Github className="w-5 h-5" />
                      </a>
                    )}
                    {member.linkedin && (
                      <a href={member.linkedin} target="_blank" rel="noopener noreferrer" className="p-2 bg-white/5 border border-white/10 rounded-lg text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="LinkedIn">
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
      <div className="px-4 py-16 bg-gradient-to-b from-transparent to-black/30">
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
                      <a href={`mailto:${supervisor.email}`} className="p-2 bg-white/5 border border-white/10 rounded-lg text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="Email">
                        <Mail className="w-5 h-5" />
                      </a>
                    )}
                    {supervisor.github && (
                      <a href={supervisor.github} target="_blank" rel="noopener noreferrer" className="p-2 bg-white/5 border border-white/10 rounded-lg text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="GitHub">
                        <Github className="w-5 h-5" />
                      </a>
                    )}
                    {supervisor.linkedin && (
                      <a href={supervisor.linkedin} target="_blank" rel="noopener noreferrer" className="p-2 bg-white/5 border border-white/10 rounded-lg text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="LinkedIn">
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
      <footer className="px-4 py-8 border-t border-white/5">
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
