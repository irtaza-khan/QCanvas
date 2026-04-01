'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { AboutUsIcon, Moon, Sun, Atom } from '@/components/Icons';
import { Users, Github, Menu, X, Linkedin, Mail, MessageSquare, ExternalLink, Code, ChevronRight, Sparkles, Cpu } from 'lucide-react';
import Navbar from '@/components/Navbar';
import { config, getCopyrightText, socialLinks, projectUrls } from '@/lib/config'

export default function AboutPage() {
  const [scrollY, setScrollY] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY)
    }

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('reveal-show')
        }
      })
    }, { threshold: 0.1 })

    document.querySelectorAll('.reveal-on-scroll').forEach(el => {
      observer.observe(el)
    })

    window.addEventListener('scroll', handleScroll)
    return () => {
      window.removeEventListener('scroll', handleScroll)
      observer.disconnect()
    }
  }, [])

  return (
    <div className="min-h-screen bg-[#0a0a1a] relative overflow-x-hidden text-white">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-grid-pattern opacity-30 pointer-events-none" />
      <div className="absolute inset-0 bg-gradient-to-b from-[#0a0a1a] via-transparent to-[#0a0a1a] pointer-events-none" />
      <div className="absolute top-[-20%] left-1/2 -translate-x-1/2 w-[800px] h-[600px] hero-spotlight opacity-30 blur-3xl pointer-events-none" />
      <Navbar />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-4 pt-20">
        {/* Subtle background orbs — fewer, more vibrant */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-32 -right-32 w-[500px] h-[500px] bg-indigo-500 opacity-[0.07] rounded-full blur-[100px]"></div>
          <div className="absolute -bottom-32 -left-32 w-[500px] h-[500px] bg-violet-500 opacity-[0.07] rounded-full blur-[100px]"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[400px] h-[400px] bg-cyan-500 opacity-[0.05] rounded-full blur-[80px]"></div>
        </div>

        {/* Floating elements — visible in background */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-24 left-[8%] animate-float">
            <Atom className="w-8 h-8 text-indigo-400 opacity-20" />
          </div>
          <div className="absolute top-1/3 right-[10%] animate-float-reverse" style={{ animationDelay: '2s' }}>
            <Sparkles className="w-6 h-6 text-violet-400 opacity-25" />
          </div>
          <div className="absolute bottom-1/4 left-[12%] animate-float" style={{ animationDelay: '4s' }}>
            <Cpu className="w-7 h-7 text-cyan-400 opacity-20" />
          </div>
        </div>

        <div className="text-center max-w-6xl mx-auto relative z-10">
          <div className="inline-flex items-center justify-center w-24 h-24 rounded-full quantum-gradient mb-6 shadow-2xl">
            <AboutUsIcon className="w-12 h-12 text-white" />
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
              {config.qcanvasTeam.map((member, idx) => (
                <div 
                  key={member.name} 
                  className="reveal-on-scroll quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10 text-center hover-lift hover:border-quantum-blue-light transition-all duration-300"
                  style={{ animationDelay: `${idx * 150}ms` }}
                >
                  <div className="w-20 h-20 quantum-gradient rounded-full flex items-center justify-center mx-auto mb-6 shadow-[0_0_20px_rgba(59,130,246,0.3)]">
                    <Users className="w-10 h-10 text-white" />
                  </div>
                  <h4 className="text-xl font-semibold text-white mb-1">{member.name}</h4>
                  <p className="text-sm text-editor-text mb-4">Core Developer</p>
                  <div className="flex justify-center space-x-3">
                    {member.email && (
                      <a href={`mailto:${member.email}`} className="p-2 bg-white/5 border border-white/10 rounded-lg text-black dark:text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="Email">
                        <Mail className="w-5 h-5" />
                      </a>
                    )}
                    {member.github && (
                      <a href={member.github} target="_blank" rel="noopener noreferrer" className="p-2 bg-white/5 border border-white/10 rounded-lg text-black dark:text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="GitHub">
                        <Github className="w-5 h-5" />
                      </a>
                    )}
                    {member.linkedin && (
                      <a href={member.linkedin} target="_blank" rel="noopener noreferrer" className="p-2 bg-white/5 border border-white/10 rounded-lg text-black dark:text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="LinkedIn">
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
              {config.qsimTeam.map((member, idx) => (
                <div 
                  key={member.name} 
                  className="reveal-on-scroll quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border dark:border-white/10 border-gray-200 text-center hover-lift hover:border-purple-500 dark:hover:border-purple-500 hover:border-purple-400 transition-all duration-300"
                  style={{ animationDelay: `${(idx + 3) * 150}ms` }}
                >
                  <div className="w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg bg-gradient-to-r from-pink-500 to-rose-500 dark:from-purple-500 dark:to-pink-500 shadow-[0_0_20px_rgba(236,72,153,0.3)]">
                    <Users className="w-10 h-10 text-white" />
                  </div>
                  <h4 className="text-xl font-semibold text-white mb-1">{member.name}</h4>
                  <p className="text-sm text-editor-text mb-4">Core Developer</p>
                  <div className="flex justify-center space-x-3">
                    {member.email && (
                      <a href={`mailto:${member.email}`} className="p-2 bg-white/5 border border-white/10 rounded-lg text-black dark:text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="Email">
                        <Mail className="w-5 h-5" />
                      </a>
                    )}
                    {member.github && (
                      <a href={member.github} target="_blank" rel="noopener noreferrer" className="p-2 bg-white/5 border border-white/10 rounded-lg text-black dark:text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="GitHub">
                        <Github className="w-5 h-5" />
                      </a>
                    )}
                    {member.linkedin && (
                      <a href={member.linkedin} target="_blank" rel="noopener noreferrer" className="p-2 bg-white/5 border border-white/10 rounded-lg text-black dark:text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="LinkedIn">
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
          <div className="reveal-on-scroll quantum-glass-dark rounded-2xl p-8 backdrop-blur-xl border border-white/10">
            <div className="text-4xl font-bold quantum-gradient bg-clip-text text-transparent mb-2">
              {config.initiative.name}
            </div>
            <p className="text-xl text-editor-text">{config.initiative.tagline}</p>
          </div>

          <div className='mt-12'>
            <h3 className="text-2xl font-bold text-white text-center mb-6">Supervisors</h3>
            <div className="grid md:grid-cols-2 gap-6">
              {config.supervisors.map((supervisor, idx) => (
                <div 
                  key={supervisor.name} 
                  className="reveal-on-scroll quantum-glass-dark rounded-xl p-6 backdrop-blur-xl border dark:border-white/10 border-gray-200 text-center hover-lift hover:border-quantum-blue-light transition-all duration-300"
                  style={{ animationDelay: `${(idx + 6) * 150}ms` }}
                >
                  <h4 className="text-xl font-semibold text-white mb-2">{supervisor.name}</h4>
                  <p className="text-sm text-editor-text mb-4">{supervisor.role}</p>
                  <div className="flex justify-center space-x-3">
                    {supervisor.email && (
                      <a href={`mailto:${supervisor.email}`} className="p-2 bg-white/5 border border-white/10 rounded-lg text-black dark:text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="Email">
                        <Mail className="w-5 h-5" />
                      </a>
                    )}
                    {supervisor.github && (
                      <a href={supervisor.github} target="_blank" rel="noopener noreferrer" className="p-2 bg-white/5 border border-white/10 rounded-lg text-black dark:text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="GitHub">
                        <Github className="w-5 h-5" />
                      </a>
                    )}
                    {supervisor.linkedin && (
                      <a href={supervisor.linkedin} target="_blank" rel="noopener noreferrer" className="p-2 bg-white/5 border border-white/10 rounded-lg text-black dark:text-gray-400 hover:text-white hover:bg-quantum-blue-light/20 transition-all duration-200" title="LinkedIn">
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

      {/* CTA Section */}
      <div className="px-4 py-16">
        <div className="max-w-4xl mx-auto rounded-3xl p-10 relative overflow-hidden group">
          {/* Animated Background */}
          <div className="absolute inset-0 bg-gradient-to-br from-indigo-600/20 via-purple-600/20 to-blue-600/20 group-hover:scale-110 transition-transform duration-700" />
          <div className="absolute inset-0 backdrop-blur-xl border border-white/10 group-hover:border-white/20 transition-colors duration-300 rounded-3xl" />
          
          <div className="relative z-10 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">Want to Contribute?</h2>
            <p className="text-lg text-editor-text mb-8 max-w-2xl mx-auto font-medium">
              Join us in building the next generation of quantum computing tools. 
              We're open to contributions, research collaborations, and feedback from the quantum community.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <a 
                href={socialLinks.github} 
                target="_blank" 
                rel="noopener noreferrer"
                className="btn-quantum w-full sm:w-auto px-8 py-3 flex items-center justify-center gap-2 group/btn shadow-[0_0_20px_rgba(59,130,246,0.3)]"
              >
                <Github className="w-5 h-5" />
                <span>View on GitHub</span>
                <ChevronRight className="w-4 h-4 ml-1 group-hover/btn:translate-x-1 transition-transform" />
              </a>
              <Link 
                href={projectUrls.docs as any}
                className="btn-ghost w-full sm:w-auto px-8 py-3 flex items-center justify-center gap-2"
              >
                <Code className="w-5 h-5" />
                <span>Browse Docs</span>
              </Link>
            </div>
          </div>
          
          {/* Decorative elements */}
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <Atom className="w-32 h-32 text-white" />
          </div>
          <div className="absolute bottom-0 left-0 p-4 opacity-10">
            <Cpu className="w-24 h-24 text-white" />
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
