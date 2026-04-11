'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { 
  Users, 
  Github, 
  Linkedin, 
  Mail, 
  ChevronRight, 
  Sparkles, 
  ArrowLeft, 
  ArrowRight,
  ShieldCheck,
  Zap,
  Layout,
  Globe
} from 'lucide-react'
import Navbar from '@/components/Navbar'
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
    <div className="min-h-screen bg-slate-50 dark:bg-[#0a0a1a] text-slate-900 dark:text-slate-100 selection:bg-blue-500/30 font-sans transition-colors duration-300">
      {/* Background Decor */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-blue-600/10 dark:bg-blue-600/5 rounded-full blur-[120px]"></div>
      </div>

      <Navbar />

      <main className="relative z-10 pt-20">
        {/* --- Hero / Mission Section --- */}
        <section className="relative min-h-[600px] flex flex-col items-center justify-center px-8 py-24 text-center overflow-hidden">
          <div className="max-w-4xl mx-auto">
            <span className="font-mono text-blue-600 dark:text-blue-400 text-xs uppercase tracking-[0.3em] mb-6 block animate-fade-in">
              Our Mission
            </span>
            <h1 className="font-headline text-5xl md:text-7xl font-bold mb-8 tracking-tighter leading-tight animate-slide-up">
              Democratizing the <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 dark:from-blue-400 dark:via-indigo-500 dark:to-violet-500">Quantum Horizon</span>
            </h1>
            <p className="font-sans text-lg md:text-xl text-slate-600 dark:text-slate-400 leading-relaxed mb-12 max-w-2xl mx-auto animate-fade-in stagger-delay-1">
              At {config.project.name}, we translate the complex mathematics of quantum state vectors into an intuitive, visual playground. We believe the future of computing shouldn&apos;t be locked behind a terminal.
            </p>
            
            <div className="flex flex-wrap justify-center gap-4 animate-fade-in stagger-delay-2">
              <div className="bg-white/40 dark:bg-slate-900/40 backdrop-blur-xl border border-white/20 dark:border-white/10 px-6 py-4 rounded-xl flex items-center gap-3 shadow-lg">
                <ShieldCheck className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                <span className="font-mono text-sm font-medium">Empirical Research</span>
              </div>
              <div className="bg-white/40 dark:bg-slate-900/40 backdrop-blur-xl border border-white/20 dark:border-white/10 px-6 py-4 rounded-xl flex items-center gap-3 shadow-lg">
                <Sparkles className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                <span className="font-mono text-sm font-medium">Visual Discovery</span>
              </div>
            </div>
          </div>
          <div className="absolute bottom-0 w-full h-px bg-gradient-to-r from-transparent via-slate-200 dark:via-white/10 to-transparent"></div>
        </section>

        {/* --- Stats Bento Grid --- */}
        <section className="px-8 py-24 max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white dark:bg-slate-900 md:col-span-2 p-10 rounded-3xl flex flex-col justify-between shadow-xl border border-slate-100 dark:border-white/5 reveal-on-scroll">
              <div>
                <h3 className="font-headline text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                  {config.stats.examples}
                </h3>
                <p className="text-slate-500 dark:text-slate-400 uppercase tracking-widest text-xs font-bold">Standard Examples</p>
              </div>
              <p className="mt-8 text-slate-500 dark:text-slate-400/80 italic text-lg leading-relaxed">
                &quot;{config.project.name} has changed how students visualize multi-qubit entanglement through immersive simulation.&quot;
              </p>
            </div>

            <div className="bg-white dark:bg-slate-900 p-10 rounded-3xl shadow-xl border border-slate-100 dark:border-white/5 reveal-on-scroll stagger-delay-1">
              <h3 className="font-headline text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                {config.stats.frameworks}
              </h3>
              <p className="text-slate-500 dark:text-slate-400 uppercase tracking-widest text-xs font-bold">Frameworks Unified</p>
            </div>

            <div className="bg-white dark:bg-slate-900 p-10 rounded-3xl shadow-xl border border-slate-100 dark:border-white/5 reveal-on-scroll stagger-delay-2">
              <h3 className="font-headline text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                {config.stats.simulations}
              </h3>
              <p className="text-slate-500 dark:text-slate-400 uppercase tracking-widest text-xs font-bold">Simulation Speed</p>
            </div>

            <div className="md:col-span-1 bg-slate-100 dark:bg-slate-800 p-8 rounded-3xl border-b-2 border-blue-600/30 dark:border-blue-500/20 reveal-on-scroll stagger-delay-3">
              <Globe className="w-10 h-10 text-blue-600 dark:text-blue-400 mb-4" />
              <p className="font-headline font-bold text-xl">Open Standard</p>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">Built on {config.stats.standards} kernel.</p>
            </div>

            <div className="md:col-span-3 h-56 rounded-3xl overflow-hidden relative reveal-on-scroll stagger-delay-4 border border-slate-100 dark:border-transparent">
               <div className="absolute inset-0 bg-blue-900/40 dark:bg-blue-900/20 z-10 transition-colors" />
               <Image 
                src="https://images.unsplash.com/photo-1635070041078-e363dbe005cb?q=80&w=2070&auto=format&fit=crop"
                alt="Quantum Visualization"
                fill
                className="object-cover opacity-60 grayscale group-hover:grayscale-0 transition-all duration-500"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-slate-900 dark:from-slate-950 via-slate-900/40 dark:via-slate-950/40 to-transparent flex items-center px-10 z-20">
                <h2 className="font-headline text-3xl font-bold max-w-xs text-white">Building the Infrastructure for Tomorrow</h2>
              </div>
            </div>
          </div>
        </section>

        {/* --- Team Sections --- */}
        <section className="px-8 py-24 bg-white/30 dark:bg-slate-950 transition-colors">
          <div className="max-w-7xl mx-auto">
            <div className="flex flex-col md:flex-row justify-between items-end mb-16 gap-8">
              <div className="max-w-2xl reveal-on-scroll">
                <h2 className="font-headline text-4xl md:text-5xl font-bold mb-4 tracking-tight">The Minds Behind the Machine</h2>
                <p className="text-slate-600 dark:text-slate-400 text-lg leading-relaxed">
                  A FAST University initiative working at the intersection of high-fidelity graphics and quantum logic.
                </p>
              </div>
            </div>

            {/* QCanvas Core Team */}
            <div className="mb-20">
              <h3 className="font-headline text-2xl font-bold mb-10 text-blue-600 dark:text-blue-400 flex items-center gap-3 reveal-on-scroll">
                <div className="w-10 h-1 bg-blue-600 dark:bg-blue-400 rounded-full" />
                QCanvas Team
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-10">
                {config.qcanvasTeam.map((member, idx) => (
                  <div key={member.name} className="group reveal-on-scroll" style={{ transitionDelay: `${idx * 100}ms` }}>
                    <div className="aspect-square rounded-3xl overflow-hidden bg-slate-200 dark:bg-slate-900 mb-6 relative shadow-lg">
                      {/* Portrait Image */}
                      <div className="absolute inset-0">
                        {member.image ? (
                          <Image src={member.image} alt={member.name} fill className="object-cover grayscale group-hover:grayscale-0 transition-all duration-500" />
                        ) : (
                          <div className="absolute inset-0 flex items-center justify-center bg-slate-100 dark:bg-slate-800">
                            <Users className="w-20 h-20 text-slate-300 dark:text-slate-700" />
                          </div>
                        )}
                      </div>
                      <div className="absolute inset-0 bg-blue-600/20 dark:bg-blue-400/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4 z-20">
                        {member.github && (
                          <a href={member.github} target="_blank" rel="noopener noreferrer" className="w-12 h-12 bg-white dark:bg-slate-950 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-400 shadow-xl hover:scale-110 transition-transform">
                            <Github className="w-6 h-6" />
                          </a>
                        )}
                        {member.linkedin && (
                          <a href={member.linkedin} target="_blank" rel="noopener noreferrer" className="w-12 h-12 bg-white dark:bg-slate-950 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-400 shadow-xl hover:scale-110 transition-transform">
                            <Linkedin className="w-6 h-6" />
                          </a>
                        )}
                      </div>
                    </div>
                    <h4 className="font-headline text-2xl font-bold">{member.name}</h4>
                    <p className="text-blue-600 dark:text-blue-400 text-sm uppercase tracking-widest font-bold mt-1">Core Developer</p>
                  </div>
                ))}
              </div>
            </div>

            {/* QSim Integration Team */}
            <div>
              <h3 className="font-headline text-2xl font-bold mb-10 text-indigo-600 dark:text-purple-400 flex items-center gap-3 reveal-on-scroll">
                <div className="w-10 h-1 bg-indigo-600 dark:bg-purple-400 rounded-full" />
                QSim Team
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-10">
                {config.qsimTeam.map((member, idx) => (
                  <div key={member.name} className="group reveal-on-scroll" style={{ transitionDelay: `${idx * 100}ms` }}>
                    <div className="aspect-square rounded-3xl overflow-hidden bg-slate-200 dark:bg-slate-900 mb-6 relative shadow-lg">
                      <div className="absolute inset-0">
                        {member.image ? (
                          <Image src={member.image} alt={member.name} fill className="object-cover grayscale group-hover:grayscale-0 transition-all duration-500" />
                        ) : (
                          <div className="absolute inset-0 flex items-center justify-center bg-slate-100 dark:bg-slate-800">
                            <Users className="w-20 h-20 text-slate-300 dark:text-slate-700" />
                          </div>
                        )}
                      </div>
                      <div className="absolute inset-0 bg-indigo-600/20 dark:bg-purple-400/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4 z-20">
                        {member.github && (
                          <a href={member.github} target="_blank" rel="noopener noreferrer" className="w-12 h-12 bg-white dark:bg-slate-950 rounded-full flex items-center justify-center text-indigo-600 dark:text-purple-400 shadow-xl hover:scale-110 transition-transform">
                            <Github className="w-6 h-6" />
                          </a>
                        )}
                        {member.linkedin && (
                          <a href={member.linkedin} target="_blank" rel="noopener noreferrer" className="w-12 h-12 bg-white dark:bg-slate-950 rounded-full flex items-center justify-center text-indigo-600 dark:text-purple-400 shadow-xl hover:scale-110 transition-transform">
                            <Linkedin className="w-6 h-6" />
                          </a>
                        )}
                      </div>
                    </div>
                    <h4 className="font-headline text-2xl font-bold">{member.name}</h4>
                    <p className="text-indigo-600 dark:text-purple-400 text-sm uppercase tracking-widest font-bold mt-1">Simulation Research</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Supervisors */}
             <div className="mt-32">
              <h3 className="font-headline text-2xl font-bold mb-10 text-slate-400 flex items-center gap-3 reveal-on-scroll">
                <div className="w-10 h-1 bg-slate-400 rounded-full" />
                Supervisors
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-10">
                {config.supervisors.map((supervisor, idx) => (
                  <div key={supervisor.name} className="flex items-center gap-8 bg-white dark:bg-slate-900 p-8 rounded-3xl shadow-lg border border-slate-100 dark:border-white/5 reveal-on-scroll" style={{ transitionDelay: `${idx * 100}ms` }}>
                    <div className="w-20 h-20 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center flex-shrink-0">
                      <Users className="w-10 h-10 text-slate-300 dark:text-slate-600" />
                    </div>
                    <div>
                      <h4 className="font-headline text-xl font-bold">{supervisor.name}</h4>
                      <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">{supervisor.role}</p>
                      <div className="flex gap-3 mt-3">
                        <a href={`mailto:${supervisor.email}`} className="text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                          <Mail className="w-5 h-5" />
                        </a>
                        <a href={supervisor.linkedin} target="_blank" rel="noopener noreferrer" className="text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
                          <Linkedin className="w-5 h-5" />
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* --- Values Section --- */}
        <section className="px-8 py-32 max-w-5xl mx-auto">
          <div className="flex flex-col gap-24">
            <div className="flex flex-col md:flex-row items-start gap-12 group reveal-on-scroll">
              <span className="font-headline text-8xl font-black text-slate-100 dark:text-slate-900 group-hover:text-blue-600/10 dark:group-hover:text-blue-400/10 transition-colors duration-500 leading-none">01</span>
              <div>
                <h3 className="font-headline text-3xl font-bold mb-4 flex items-center gap-4">
                  Uncompromising Precision
                  <Zap className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </h3>
                <p className="text-slate-600 dark:text-slate-400 text-lg leading-relaxed max-w-2xl">
                  Our visualization engines are built on rigorous mathematical models, ensuring that what you see in the canvas reflects the true physical state of your qubit operations.
                </p>
              </div>
            </div>

            <div className="flex flex-col md:flex-row items-start gap-12 group reveal-on-scroll">
              <span className="font-headline text-8xl font-black text-slate-100 dark:text-slate-900 group-hover:text-blue-600/10 dark:group-hover:text-blue-400/10 transition-colors duration-500 leading-none">02</span>
              <div>
                <h3 className="font-headline text-3xl font-bold mb-4 flex items-center gap-4">
                  Radical Accessibility
                  <Layout className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </h3>
                <p className="text-slate-600 dark:text-slate-400 text-lg leading-relaxed max-w-2xl">
                  We remove the gatekeepers of innovation. Whether you are a student or a research professor, the tools remain equally powerful and equally accessible.
                </p>
              </div>
            </div>

            <div className="flex flex-col md:flex-row items-start gap-12 group reveal-on-scroll">
              <span className="font-headline text-8xl font-black text-slate-100 dark:text-slate-900 group-hover:text-blue-600/10 dark:group-hover:text-blue-400/10 transition-colors duration-500 leading-none">03</span>
              <div>
                <h3 className="font-headline text-3xl font-bold mb-4 flex items-center gap-4">
                  Ethereal Design
                  <Sparkles className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </h3>
                <p className="text-slate-600 dark:text-slate-400 text-lg leading-relaxed max-w-2xl">
                  Software should be beautiful. We treat every interface component as a piece of digital craftsmanship, designed to fade into the background while you focus on discovery.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* --- CTA Section --- */}
        <section className="px-8 py-32 text-center reveal-on-scroll">
          <div className="max-w-4xl mx-auto rounded-[3rem] p-16 relative overflow-hidden bg-white dark:bg-gradient-to-br dark:from-slate-900 dark:to-slate-950 shadow-2xl border border-slate-100 dark:border-white/5">
            {/* Animated background elements for CTA */}
            <div className="absolute top-0 right-0 p-8 opacity-5">
              <Zap className="w-64 h-64 text-blue-600 dark:text-blue-400 rotate-12" />
            </div>
            
            <h2 className="font-headline text-4xl md:text-5xl font-bold mb-6">Ready to observe the future?</h2>
            <p className="text-slate-600 dark:text-slate-400 text-lg mb-10 max-w-xl mx-auto">
              Join operators already exploring the quantum landscape on {config.project.name}.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4 relative z-10">
              <Link 
                href={projectUrls.app}
                className="bg-blue-600 dark:bg-gradient-to-r dark:from-blue-600 dark:to-indigo-600 text-white dark:text-white px-10 py-4 rounded-2xl font-bold text-lg hover:shadow-[0_0_30px_rgba(37,99,235,0.4)] transition-all hover:-translate-y-1 active:scale-95"
              >
                Start Experimenting
              </Link>
              <Link 
                href={projectUrls.docs}
                className="px-10 py-4 rounded-2xl font-bold text-lg border border-slate-200 dark:border-white/10 hover:bg-slate-50 dark:hover:bg-white/5 transition-all active:scale-95"
              >
                Read Documentation
              </Link>
            </div>
          </div>
        </section>
      </main>

      {/* --- Footer --- */}
      <footer className="bg-slate-100 dark:bg-slate-950 border-t border-slate-200 dark:border-white/5 transition-colors">
        <div className="w-full max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center px-8 py-12 gap-8">
          <div>
            <p className="font-sans text-xs uppercase tracking-widest text-slate-500 dark:text-slate-500">
              {getCopyrightText()}
            </p>
          </div>
          <div className="flex flex-wrap justify-center gap-8 font-sans text-xs uppercase tracking-widest">
            {Object.entries(socialLinks).map(([key, url]) => (
              <a 
                key={key}
                href={url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-slate-500 dark:text-slate-500 hover:text-blue-600 dark:hover:text-ethereal-primary transition-colors"
              >
                {key}
              </a>
            ))}
          </div>
        </div>
      </footer>

      {/* Styles for reveal effect */}
      <style jsx global>{`
        .reveal-on-scroll {
          opacity: 0;
          transform: translateY(30px);
          transition: all 0.8s cubic-bezier(0.22, 1, 0.36, 1);
        }
        .reveal-show {
          opacity: 1 !important;
          transform: translateY(0) !important;
        }
        .stagger-delay-1 { transition-delay: 150ms; }
        .stagger-delay-2 { transition-delay: 300ms; }
        .stagger-delay-3 { transition-delay: 450ms; }
        .stagger-delay-4 { transition-delay: 600ms; }
        
        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slide-up {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in { animation: fade-in 1s ease-out forwards; }
        .animate-slide-up { animation: slide-up 0.8s ease-out forwards; }
      `}</style>
    </div>
  )
}
