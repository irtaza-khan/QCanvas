"use client";

import Link from "next/link";
import { ArrowRight, Zap, BookOpen, Layers } from "lucide-react";
import { CirqIcon, QiskitIcon, PennyLaneIcon, Globe } from "@/components/Icons";

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  href: string;
  isExternal?: boolean;
  accentColor: string;
  glowColor: string;
  bgColor: string;
  hoverTextColor: string;
  linkColor: string;
  badgeColor: string;
  badgeBg: string;
  badgeBorder: string;
  badge: string;
  delay: string;
}

function FeatureCard({
  icon,
  title,
  description,
  href,
  isExternal = false,
  glowColor,
  bgColor,
  hoverTextColor,
  linkColor,
  badgeColor,
  badgeBg,
  badgeBorder,
  badge,
  delay,
}: FeatureCardProps) {
  const linkProps = isExternal
    ? { target: "_blank", rel: "noopener noreferrer" }
    : {};

  const CardContent = (
    <div
      className={`quantum-glass-dark rounded-2xl p-8 hover-lift transition-all duration-500 group feature-card opacity-0 animate-fade-in ${glowColor} h-full flex flex-col`}
      style={{ animationDelay: delay }}
    >
      {/* Icon area */}
      <div
        className={`w-14 h-14 ${bgColor} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-all duration-300 shadow-lg`}
      >
        {icon}
      </div>

      {/* Badge */}
      <span
        className={`inline-block text-xs font-semibold ${badgeBg} ${badgeColor} px-3 py-1 rounded-full border ${badgeBorder} mb-4 w-fit`}
      >
        {badge}
      </span>

      {/* Title */}
      <h3
        className={`text-xl font-bold text-white mb-3 ${hoverTextColor} transition-colors duration-300`}
      >
        {title}
      </h3>

      {/* Description */}
      <p className="text-gray-400 text-sm leading-relaxed mb-6 flex-grow group-hover:text-gray-300 transition-colors duration-300">
        {description}
      </p>

      {/* CTA link */}
      <div
        className={`flex items-center text-sm font-semibold ${linkColor} transition-colors duration-300 mt-auto`}
      >
        <span>{isExternal ? "View docs" : "Explore"}</span>
        <ArrowRight className="w-4 h-4 ml-1.5 group-hover:translate-x-2 transition-transform duration-300" />
      </div>
    </div>
  );

  if (isExternal) {
    return (
      <a href={href} {...linkProps} className="block h-full" aria-label={title}>
        {CardContent}
      </a>
    );
  }

  return (
    <Link href={href as any} className="block h-full" aria-label={title}>
      {CardContent}
    </Link>
  );
}

export default function FeatureGrid() {
  const cards: FeatureCardProps[] = [
    {
      icon: <CirqIcon size={32} className="text-blue-400" />,
      title: "Cirq Converter",
      description:
        "Translate Google Cirq circuits to OpenQASM 3.0 — the universal intermediate format for cross-framework quantum portability.",
      href: "/app",
      accentColor: "card-accent-blue",
      glowColor: "hover:shadow-[0_0_30px_rgba(96,165,250,0.15)]",
      bgColor: "bg-blue-500/15 group-hover:bg-blue-500/25",
      hoverTextColor: "group-hover:text-blue-400",
      linkColor: "text-blue-400 group-hover:text-blue-300",
      badge: "Google Cirq",
      badgeColor: "text-blue-300",
      badgeBg: "bg-blue-500/10",
      badgeBorder: "border-blue-500/25",
      delay: "0ms",
    },
    {
      icon: <QiskitIcon size={32} className="text-violet-400" />,
      title: "Qiskit Bridge",
      description:
        "Port IBM Qiskit code to other quantum frameworks instantly — bi-directional conversion with full gate fidelity.",
      href: "/app",
      accentColor: "card-accent-purple",
      glowColor: "hover:shadow-[0_0_30px_rgba(167,139,250,0.15)]",
      bgColor: "bg-violet-500/15 group-hover:bg-violet-500/25",
      hoverTextColor: "group-hover:text-violet-400",
      linkColor: "text-violet-400 group-hover:text-violet-300",
      badge: "IBM Qiskit",
      badgeColor: "text-violet-300",
      badgeBg: "bg-violet-500/10",
      badgeBorder: "border-violet-500/25",
      delay: "80ms",
    },
    {
      icon: <PennyLaneIcon size={32} className="text-emerald-400" />,
      title: "PennyLane Optimizer",
      description:
        "Unified simulation for Xanadu PennyLane workflows — seamlessly bridge quantum machine learning circuits to other runtimes.",
      href: "/app",
      accentColor: "card-accent-teal",
      glowColor: "hover:shadow-[0_0_30px_rgba(52,211,153,0.15)]",
      bgColor: "bg-emerald-500/15 group-hover:bg-emerald-500/25",
      hoverTextColor: "group-hover:text-emerald-400",
      linkColor: "text-emerald-400 group-hover:text-emerald-300",
      badge: "Xanadu PennyLane",
      badgeColor: "text-emerald-300",
      badgeBg: "bg-emerald-500/10",
      badgeBorder: "border-emerald-500/25",
      delay: "160ms",
    },
    {
      icon: <Zap className="w-7 h-7 text-amber-400" />,
      title: "Real-time Simulator",
      description:
        "Execute circuits instantly with multi-agent RAG support — watch your quantum state evolve step-by-step in real time.",
      href: "/app",
      accentColor: "card-accent-orange",
      glowColor: "hover:shadow-[0_0_30px_rgba(251,191,36,0.12)]",
      bgColor: "bg-amber-500/15 group-hover:bg-amber-500/25",
      hoverTextColor: "group-hover:text-amber-400",
      linkColor: "text-amber-400 group-hover:text-amber-300",
      badge: "RAG-powered",
      badgeColor: "text-amber-300",
      badgeBg: "bg-amber-500/10",
      badgeBorder: "border-amber-500/25",
      delay: "240ms",
    },
    {
      icon: <BookOpen className="w-7 h-7 text-cyan-400" />,
      title: "Interactive Examples",
      description:
        "Learn quantum concepts with pre-built circuit templates — Bell states, teleportation, Grover's search and more, ready to run.",
      href: "/examples",
      accentColor: "card-accent-teal",
      glowColor: "hover:shadow-[0_0_30px_rgba(34,211,238,0.12)]",
      bgColor: "bg-cyan-500/15 group-hover:bg-cyan-500/25",
      hoverTextColor: "group-hover:text-cyan-400",
      linkColor: "text-cyan-400 group-hover:text-cyan-300",
      badge: "Templates",
      badgeColor: "text-cyan-300",
      badgeBg: "bg-cyan-500/10",
      badgeBorder: "border-cyan-500/25",
      delay: "320ms",
    },
    {
      icon: <Globe className="w-7 h-7 text-pink-400" />,
      title: "OpenQASM 3.0 Docs",
      description:
        "Deep dive into our standardized intermediate representation — full specification, examples, and integration guides.",
      href: "https://openqasm.com/",
      isExternal: true,
      accentColor: "card-accent-pink",
      glowColor: "hover:shadow-[0_0_30px_rgba(244,114,182,0.12)]",
      bgColor: "bg-pink-500/15 group-hover:bg-pink-500/25",
      hoverTextColor: "group-hover:text-pink-400",
      linkColor: "text-pink-400 group-hover:text-pink-300",
      badge: "OpenQASM 3.0",
      badgeColor: "text-pink-300",
      badgeBg: "bg-pink-500/10",
      badgeBorder: "border-pink-500/25",
      delay: "400ms",
    },
  ];

  return (
    <section id="explore-features" className="py-24 px-4 relative">
      {/* Subtle background */}
      <div className="absolute inset-0 bg-grid-pattern opacity-20" />
      <div className="absolute inset-0">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[500px] bg-indigo-500 opacity-[0.04] rounded-full blur-[120px]" />
      </div>

      <div className="max-w-7xl mx-auto relative z-10">
        {/* Section header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center bg-indigo-500/10 rounded-full px-5 py-2 mb-6 border border-indigo-500/20">
            <Layers className="w-4 h-4 text-indigo-400 mr-2" />
            <span className="text-sm font-medium text-indigo-300">
              Explore Features
            </span>
          </div>

          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            <span className="quantum-gradient bg-clip-text text-transparent">
              Everything You Need to
            </span>
            <br />
            <span className="text-white">Build Quantum Circuits</span>
          </h2>

          <p className="text-lg text-gray-400 max-w-2xl mx-auto leading-relaxed">
            Six powerful tools — one unified platform. Convert between Cirq,
            Qiskit, and PennyLane, simulate in real time, and explore quantum
            algorithms at every level.
          </p>
        </div>

        {/* Card grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cards.map((card) => (
            <FeatureCard key={card.title} {...card} />
          ))}
        </div>
      </div>
    </section>
  );
}
