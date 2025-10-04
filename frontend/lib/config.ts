// QCanvas Project Configuration
// Centralized configuration for all project details, team info, and shared constants
// Import this file in any component to access consistent project information

export interface TeamMember {
  name: string
  role: string
  profile: string
  github?: string
  linkedin?: string
  email?: string
}

export interface SocialLinks {
  github: string
  discord?: string
  twitter?: string
  linkedin?: string
}

export interface ContactInfo {
  email: string
  support: string
  research: string
  community: string
}

export interface ProjectInfo {
  name: string
  tagline: string
  description: string
  year: number
  version: string
  status: 'development' | 'beta' | 'production'
}

export interface TechnicalSpecs {
  frameworks: string[]
  standards: string[]
  features: string[]
}

// Main project configuration
export const projectConfig: ProjectInfo = {
  name: 'QCanvas',
  tagline: 'Quantum Code Editor & Simulation Platform',
  description: 'A modern quantum computing platform that bridges quantum frameworks, enabling seamless conversion between Cirq, Qiskit, and PennyLane with real-time simulation and visualization.',
  year: 2024,
  version: '1.0.0-beta',
  status: 'development'
}

// Team configuration
export const teamConfig: TeamMember[] = [
  {
    name: 'Umer Farooq',
    role: 'Project Lead & Backend Developer',
    profile: '22I-0891',
    github: 'https://github.com/Umer-Farooq-CS',
    linkedin: 'https://linkedin.com/in/umer-farooq',
    email: 'umer.farooq@nu.edu.pk'
  },
  {
    name: 'Hussan Waseem Syed',
    role: 'Frontend Developer',
    profile: '22I-0893',
    github: 'https://github.com/hussan-waseem',
    linkedin: 'https://linkedin.com/in/hussan-waseem',
    email: 'hussan.syed@nu.edu.pk'
  },
  {
    name: 'Muhammad Irtaza Khan',
    role: 'Backend Developer',
    profile: '22I-0911',
    github: 'https://github.com/irtaza-khan',
    linkedin: 'https://linkedin.com/in/irtaza-khan',
    email: 'irtaza.khan@nu.edu.pk'
  }
]

// Social and community links
export const socialLinks: SocialLinks = {
  github: 'https://github.com/Umer-Farooq-CS/QCanvas',
  discord: 'https://discord.gg/qcanvas',
  twitter: 'https://twitter.com/qcanvas_dev',
  linkedin: 'https://linkedin.com/company/qcanvas'
}

// Contact information
export const contactInfo: ContactInfo = {
  email: 'team@qcanvas.dev',
  support: 'support@qcanvas.dev',
  research: 'research@qcanvas.dev',
  community: 'community@qcanvas.dev'
}

// Technical specifications
export const technicalSpecs: TechnicalSpecs = {
  frameworks: ['Qiskit', 'Cirq', 'PennyLane', 'OpenQASM 3.0'],
  standards: ['OpenQASM 3.0', 'Qiskit Runtime', 'Cirq Quantum', 'PennyLane Quantum'],
  features: [
    'Framework Conversion',
    'Real-time Simulation',
    'Web IDE',
    'Educational Platform',
    'Community Sharing',
    'OpenQASM 3.0 Support'
  ]
}

// Project URLs and paths
export const projectUrls = {
  homepage: '/',
  app: '/app',
  login: '/login',
  docs: '/docs',
  examples: '/examples',
  about: '/about',
  api: '/api'
}

// University information
export const universityInfo = {
  name: 'National University of Computer and Emerging Sciences',
  shortName: 'NUCES',
  location: 'Islamabad, Pakistan',
  department: 'Department of Computer Science'
}

// Supervisor information
export const supervisors = [
  {
    name: 'Dr. Imran Ashraf',
    role: 'Project Supervisor',
    email: 'imran.ashraf@nu.edu.pk'
  },
  {
    name: 'Dr. Muhammad Nouman Noor',
    role: 'Co-Supervisor',
    email: 'nouman.noor@nu.edu.pk'
  }
]

// Project metrics and stats
export const projectStats = {
  frameworks: 3,
  standards: 'OpenQASM 3.0',
  simulations: 'Real-time',
  users: '1000+'
}

// SEO and meta information
export const seoConfig = {
  title: `${projectConfig.name} - ${projectConfig.tagline}`,
  description: projectConfig.description,
  keywords: [
    'quantum computing',
    'qiskit',
    'cirq',
    'pennylane',
    'quantum simulation',
    'quantum circuits',
    'quantum development',
    'quantum education',
    'openqasm'
  ],
  authors: teamConfig.map(member => ({ name: member.name })),
  creator: projectConfig.name,
  publisher: universityInfo.name
}

// Navigation menu configuration
export const navigationMenu = [
  { name: 'Home', path: projectUrls.homepage, icon: 'Home' },
  { name: 'Examples', path: projectUrls.examples, icon: 'Play' },
  { name: 'Documentation', path: projectUrls.docs, icon: 'BookOpen' },
  { name: 'About', path: projectUrls.about, icon: 'Info' }
]

// Footer links configuration
export const footerLinks = {
  platform: [
    { name: 'Editor', path: projectUrls.app },
    { name: 'Examples', path: projectUrls.examples },
    { name: 'Documentation', path: projectUrls.docs },
    { name: 'About', path: projectUrls.about }
  ],
  community: [
    { name: 'GitHub', url: socialLinks.github, external: true },
    { name: 'Discord', url: socialLinks.discord, external: true },
    { name: 'Twitter', url: socialLinks.twitter, external: true },
    { name: 'LinkedIn', url: socialLinks.linkedin, external: true }
  ],
  support: [
    { name: 'Contact Team', email: contactInfo.email },
    { name: 'Research', email: contactInfo.research },
    { name: 'Community', email: contactInfo.community },
    { name: 'Support', email: contactInfo.support }
  ]
}

// Helper functions for generating dynamic content
export const getTeamMemberByName = (name: string): TeamMember | undefined => {
  return teamConfig.find(member => member.name === name)
}

export const getTeamMemberByProfile = (profile: string): TeamMember | undefined => {
  return teamConfig.find(member => member.profile === profile)
}

export const getFullProjectTitle = (): string => {
  return `${projectConfig.name} - ${projectConfig.tagline}`
}

export const getProjectDescription = (): string => {
  return `${projectConfig.description} Built by ${teamConfig.map(m => m.name).join(', ')} at ${universityInfo.name}.`
}

export const getCopyrightText = (): string => {
  return `© ${projectConfig.year} ${projectConfig.name}. Built for the quantum computing community.`
}

export const getVersionText = (): string => {
  return `Version ${projectConfig.version} (${projectConfig.status})`
}

// Export all configurations as a single object for convenience
export const config = {
  project: projectConfig,
  team: teamConfig,
  social: socialLinks,
  contact: contactInfo,
  technical: technicalSpecs,
  urls: projectUrls,
  university: universityInfo,
  supervisors,
  stats: projectStats,
  seo: seoConfig,
  navigation: navigationMenu,
  footer: footerLinks
}

export default config
