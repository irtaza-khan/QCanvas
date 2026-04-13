"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import {
  Users,
  Github,
  Linkedin,
  Mail,
  Sparkles,
  ShieldCheck,
  Zap,
  Layout,
  Globe,
} from "lucide-react";
import Navbar from "@/components/Navbar";
import { hasValidAuth, useAuthStore } from "@/lib/authStore";
import {
  config,
  getCopyrightText,
  socialLinks,
  projectUrls,
  type TeamMember,
} from "@/lib/config";

type SpotlightTeam = "QCanvas" | "QSim";

type ActiveSpotlight = {
  team: SpotlightTeam;
  memberName: string;
} | null;

const teamAccentStyles: Record<
  SpotlightTeam,
  {
    title: string;
    line: string;
    panel: string;
    panelBorder: string;
    badge: string;
    cardBorder: string;
    cardBackground: string;
    overlay: string;
    detailIcon: string;
  }
> = {
  QCanvas: {
    title: "text-blue-600 dark:text-blue-400",
    line: "bg-blue-600 dark:bg-blue-400",
    panel: "bg-white/90 dark:bg-slate-950/85",
    panelBorder: "border-blue-100/80 dark:border-blue-500/15",
    badge:
      "bg-blue-600/10 text-blue-700 dark:bg-blue-400/10 dark:text-blue-300",
    cardBorder: "border-slate-100 dark:border-white/5",
    cardBackground: "bg-white dark:bg-slate-900",
    overlay: "bg-blue-600/12 dark:bg-blue-400/12",
    detailIcon: "text-blue-600 dark:text-blue-400",
  },
  QSim: {
    title: "text-indigo-600 dark:text-purple-400",
    line: "bg-indigo-600 dark:bg-purple-400",
    panel: "bg-white/90 dark:bg-slate-950/85",
    panelBorder: "border-indigo-100/80 dark:border-purple-500/15",
    badge:
      "bg-indigo-600/10 text-indigo-700 dark:bg-purple-400/10 dark:text-purple-300",
    cardBorder: "border-slate-100 dark:border-white/5",
    cardBackground: "bg-white dark:bg-slate-900",
    overlay: "bg-indigo-600/12 dark:bg-purple-400/12",
    detailIcon: "text-indigo-600 dark:text-purple-400",
  },
};

type TeamMemberCardProps = {
  member: TeamMember;
  sectionKey: SpotlightTeam;
  active: boolean;
  variant: "grid" | "main" | "stack";
  onHoverActivate: () => void;
  onImmediateActivate: () => void;
};

// Reusable team card used for the spotlighted member and the smaller side cards.
function TeamMemberCard({
  member,
  sectionKey,
  active,
  variant,
  onHoverActivate,
  onImmediateActivate,
}: TeamMemberCardProps) {
  const accent = teamAccentStyles[sectionKey];
  const compact = variant === "stack";

  return (
    <button
      type="button"
      onMouseEnter={onHoverActivate}
      onFocus={onImmediateActivate}
      onClick={onImmediateActivate}
      aria-pressed={active}
      className={`group w-full text-left rounded-[2rem] border shadow-xl transform-gpu transition-[transform,box-shadow,border-color,background-color,opacity] duration-[1200ms] ease-[cubic-bezier(0.16,1,0.3,1)] focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500/60 dark:focus-visible:ring-blue-400/60 ${accent.cardBorder} ${accent.cardBackground} ${active ? "shadow-2xl" : variant === "stack" ? "opacity-90 hover:-translate-y-1 lg:-mt-16 lg:translate-x-2 lg:scale-[0.68] lg:origin-right" : "hover:-translate-y-1"}`}
    >
      <div className="relative aspect-square overflow-hidden rounded-[2rem]">
        {member.image ? (
          <Image
            src={member.image}
            alt={member.name}
            fill
            sizes="(max-width: 768px) 100vw, 33vw"
            className={`object-cover transform-gpu transition-[transform,filter,opacity] duration-[1100ms] ease-[cubic-bezier(0.16,1,0.3,1)] ${active ? "grayscale-0" : "group-hover:scale-105"}`}
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center bg-slate-100 dark:bg-slate-800">
            <Users className="w-20 h-20 text-slate-300 dark:text-slate-700" />
          </div>
        )}

        <div
          className={`absolute inset-0 transition-all duration-[1100ms] ease-[cubic-bezier(0.16,1,0.3,1)] ${active ? accent.overlay : "bg-black/10 opacity-0 group-hover:opacity-100"}`}
        />
      </div>

      <div
        className={`${compact ? "p-3" : "p-4"} ${compact ? "space-y-1.5" : "space-y-3"} transition-transform duration-[1100ms] ease-[cubic-bezier(0.16,1,0.3,1)] ${active ? "translate-y-0" : ""}`}
      >
        <div
          className={`inline-flex items-center rounded-full px-3 py-1 text-[0.65rem] font-bold uppercase tracking-[0.28em] ${accent.badge}`}
        >
          {member.role}
        </div>
        <h4
          className={`${compact ? "text-lg" : "text-2xl"} font-headline font-bold leading-tight`}
        >
          {member.name}
        </h4>
        {!compact && (
          <p className="text-sm leading-relaxed text-slate-600 dark:text-slate-400">
            {member.bio}
          </p>
        )}
      </div>
    </button>
  );
}

// Coordinates the spotlight layout for one team section, including active state and stacked members.
type TeamSpotlightSectionProps = {
  title: string;
  description: string;
  teamKey: SpotlightTeam;
  members: TeamMember[];
  activeSpotlight: ActiveSpotlight;
  setActiveSpotlight: (spotlight: ActiveSpotlight) => void;
  scheduleSpotlight: (spotlight: ActiveSpotlight) => void;
  clearScheduledSpotlight: () => void;
};

function TeamSpotlightSection({
  title,
  description,
  teamKey,
  members,
  activeSpotlight,
  setActiveSpotlight,
  scheduleSpotlight,
  clearScheduledSpotlight,
}: TeamSpotlightSectionProps) {
  const accent = teamAccentStyles[teamKey];
  const activeMember =
    activeSpotlight?.team === teamKey
      ? (members.find((member) => member.name === activeSpotlight.memberName) ??
        null)
      : null;

  const handleActivate = (memberName: string) => {
    setActiveSpotlight({ team: teamKey, memberName });
  };

  const handleHoverActivate = (memberName: string) => {
    scheduleSpotlight({ team: teamKey, memberName });
  };

  const handleClear = () => {
    clearScheduledSpotlight();
    setActiveSpotlight(null);
  };

  return (
    <section className="mb-20" onMouseLeave={handleClear}>
      {/* Section heading and spotlight reset control. */}
      <div className="mb-10 flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <h3
            className={`font-headline text-2xl font-bold flex items-center gap-3 ${accent.title}`}
          >
            <div className={`w-10 h-1 rounded-full ${accent.line}`} />
            {title}
          </h3>
          <p className="mt-4 max-w-2xl text-slate-600 dark:text-slate-400 text-lg leading-relaxed">
            {description}
          </p>
        </div>

        {activeMember && (
          <button
            type="button"
            onClick={handleClear}
            className={`w-fit rounded-full border px-4 py-2 text-xs font-bold uppercase tracking-[0.28em] transition-colors ${accent.cardBorder} ${accent.title} hover:bg-slate-50 dark:hover:bg-white/5`}
          >
            Clear spotlight
          </button>
        )}
      </div>

      {/* Default grid when no member is active, spotlight layout after hover or tap. */}
      {!activeMember ? (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
          {members.map((member) => (
            <TeamMemberCard
              key={member.name}
              member={member}
              sectionKey={teamKey}
              active={false}
              variant="grid"
              onHoverActivate={() => handleHoverActivate(member.name)}
              onImmediateActivate={() => handleActivate(member.name)}
            />
          ))}
        </div>
      ) : (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1.08fr)_minmax(280px,0.92fr)_minmax(0,0.82fr)] lg:items-start">
          <div className="animate-[spotlight-main-in_1100ms_cubic-bezier(0.16,1,0.3,1)_both]">
            <TeamMemberCard
              member={activeMember}
              sectionKey={teamKey}
              active
              variant="main"
              onHoverActivate={() => handleHoverActivate(activeMember.name)}
              onImmediateActivate={() => handleActivate(activeMember.name)}
            />
          </div>

          <div
            className={`rounded-[2rem] border p-6 shadow-xl backdrop-blur-xl transition-all duration-[1100ms] ${accent.panel} ${accent.panelBorder} animate-[spotlight-panel-in_1100ms_cubic-bezier(0.16,1,0.3,1)_both]`}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p
                  className={`text-xs font-bold uppercase tracking-[0.32em] ${accent.title}`}
                >
                  Spotlight
                </p>
                <h4 className="mt-3 font-headline text-3xl font-bold leading-tight">
                  {activeMember.name}
                </h4>
                <p
                  className={`mt-2 inline-flex rounded-full px-3 py-1 text-xs font-bold uppercase tracking-[0.24em] ${accent.badge}`}
                >
                  {activeMember.role}
                </p>
              </div>

              <button
                type="button"
                onClick={handleClear}
                className={`rounded-full border px-3 py-2 text-xs font-bold uppercase tracking-[0.24em] transition-colors ${accent.cardBorder} ${accent.title} hover:bg-slate-50 dark:hover:bg-white/5`}
              >
                Reset
              </button>
            </div>

            <p className="mt-5 text-base leading-7 text-slate-600 dark:text-slate-300">
              {activeMember.bio}
            </p>

            <div className="mt-8 space-y-4">
              {activeMember.email && (
                <a
                  href={`mailto:${activeMember.email}`}
                  className={`flex items-center gap-3 rounded-2xl border px-4 py-3 text-sm font-medium transition-colors ${accent.cardBorder} hover:bg-slate-50 dark:hover:bg-white/5`}
                >
                  <Mail className={`w-5 h-5 ${accent.detailIcon}`} />
                  <span className="truncate">{activeMember.email}</span>
                </a>
              )}

              <div className="flex flex-wrap gap-3">
                {activeMember.github && (
                  <a
                    href={activeMember.github}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-bold transition-all hover:-translate-y-0.5 ${accent.cardBorder} hover:bg-slate-50 dark:hover:bg-white/5`}
                  >
                    <Github className={`w-4 h-4 ${accent.detailIcon}`} />
                    GitHub
                  </a>
                )}

                {activeMember.linkedin && (
                  <a
                    href={activeMember.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`flex items-center gap-2 rounded-full border px-4 py-2 text-sm font-bold transition-all hover:-translate-y-0.5 ${accent.cardBorder} hover:bg-slate-50 dark:hover:bg-white/5`}
                  >
                    <Linkedin className={`w-4 h-4 ${accent.detailIcon}`} />
                    LinkedIn
                  </a>
                )}
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-0">
            {members
              .filter((member) => member.name !== activeMember.name)
              .map((member, index) => (
                <div
                  key={member.name}
                  className={`animate-[spotlight-stack-in_1100ms_cubic-bezier(0.16,1,0.3,1)_both] ${index > 0 ? "-mt-4 lg:-mt-8" : ""}`}
                  style={{ animationDelay: `${180 + index * 180}ms` }}
                >
                  <TeamMemberCard
                    member={member}
                    sectionKey={teamKey}
                    active={false}
                    variant="stack"
                    onHoverActivate={() => handleHoverActivate(member.name)}
                    onImmediateActivate={() => handleActivate(member.name)}
                  />
                </div>
              ))}
          </div>
        </div>
      )}
    </section>
  );
}

export default function AboutPage() {
  const { isAuthenticated, token } = useAuthStore();
  const canAccessApp = hasValidAuth({ isAuthenticated, token });

  const [activeSpotlight, setActiveSpotlight] = useState<ActiveSpotlight>(null);
  const hoverTimerRef = useRef<number | null>(null);

  const clearHoverTimer = () => {
    if (hoverTimerRef.current !== null) {
      window.clearTimeout(hoverTimerRef.current);
      hoverTimerRef.current = null;
    }
  };

  const activateSpotlight = (spotlight: ActiveSpotlight) => {
    clearHoverTimer();
    setActiveSpotlight(spotlight);
  };

  const scheduleSpotlight = (spotlight: ActiveSpotlight) => {
    clearHoverTimer();
    hoverTimerRef.current = window.setTimeout(() => {
      setActiveSpotlight(spotlight);
      hoverTimerRef.current = null;
    }, 220);
  };

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("reveal-show");
          }
        });
      },
      { threshold: 0.1 },
    );

    document.querySelectorAll(".reveal-on-scroll").forEach((el) => {
      observer.observe(el);
    });

    return () => {
      observer.disconnect();
    };
  }, []);

  useEffect(() => {
    return () => {
      clearHoverTimer();
    };
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-[#0a0a1a] text-slate-900 dark:text-slate-100 selection:bg-blue-500/30 font-sans transition-colors duration-300">
      {/* Background glow behind the page content. */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-blue-600/10 dark:bg-blue-600/5 rounded-full blur-[120px]"></div>
      </div>

      <Navbar />

      <main className="relative z-10 pt-20">
        {/* Hero / mission intro section. */}
        <section className="relative min-h-[600px] flex flex-col items-center justify-center px-8 py-24 text-center overflow-hidden">
          <div className="max-w-4xl mx-auto">
            <span className="font-semibold text-blue-600 dark:text-blue-400 text-xs uppercase tracking-[0.3em] mb-6 block animate-fade-in">
              Our Mission
            </span>
            <h1 className="font-headline text-5xl md:text-7xl font-bold mb-8 tracking-tighter leading-tight animate-slide-up">
              Democratizing the{" "}
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-indigo-600 to-violet-600 dark:from-blue-400 dark:via-indigo-500 dark:to-violet-500">
                Quantum Horizon
              </span>
            </h1>
            <p className="font-sans text-lg md:text-xl text-slate-600 dark:text-slate-400 leading-relaxed mb-12 max-w-2xl mx-auto animate-fade-in stagger-delay-1">
              At {config.project.name}, we translate the complex mathematics of
              quantum state vectors into an intuitive, visual playground. We
              believe the future of computing shouldn&apos;t be locked behind a
              terminal.
            </p>

            <div className="flex flex-wrap justify-center gap-4 animate-fade-in stagger-delay-2">
              <div className="bg-white/40 dark:bg-slate-900/40 backdrop-blur-xl border border-white/20 dark:border-white/10 px-6 py-4 rounded-xl flex items-center gap-3 shadow-lg">
                <ShieldCheck className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                <span className="font-semibold text-sm font-medium">
                  Empirical Research
                </span>
              </div>
              <div className="bg-white/40 dark:bg-slate-900/40 backdrop-blur-xl border border-white/20 dark:border-white/10 px-6 py-4 rounded-xl flex items-center gap-3 shadow-lg">
                <Sparkles className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                <span className="font-semibold text-sm font-medium">
                  Visual Discovery
                </span>
              </div>
            </div>
          </div>
          <div className="absolute bottom-0 w-full h-px bg-gradient-to-r from-transparent via-slate-200 dark:via-white/10 to-transparent"></div>
        </section>

        {/* Stats and visual highlight cards. */}
        <section className="px-8 py-24 max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-white dark:bg-slate-900 md:col-span-2 p-10 rounded-3xl flex flex-col justify-between shadow-xl border border-slate-100 dark:border-white/5 reveal-on-scroll">
              <div>
                <h3 className="font-headline text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                  {config.stats.examples}
                </h3>
                <p className="text-slate-500 dark:text-slate-400 uppercase tracking-widest text-xs font-bold">
                  Standard Examples
                </p>
              </div>
              <p className="mt-8 text-slate-500 dark:text-slate-400/80 italic text-lg leading-relaxed">
                &quot;{config.project.name} has changed how students visualize
                multi-qubit entanglement through immersive simulation.&quot;
              </p>
            </div>

            <div className="bg-white dark:bg-slate-900 p-10 rounded-3xl shadow-xl border border-slate-100 dark:border-white/5 reveal-on-scroll stagger-delay-1">
              <h3 className="font-headline text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                {config.stats.frameworks}
              </h3>
              <p className="text-slate-500 dark:text-slate-400 uppercase tracking-widest text-xs font-bold">
                Frameworks Unified
              </p>
            </div>

            <div className="bg-white dark:bg-slate-900 p-10 rounded-3xl shadow-xl border border-slate-100 dark:border-white/5 reveal-on-scroll stagger-delay-2">
              <h3 className="font-headline text-4xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                {config.stats.simulations}
              </h3>
              <p className="text-slate-500 dark:text-slate-400 uppercase tracking-widest text-xs font-bold">
                Simulation Speed
              </p>
            </div>

            <div className="md:col-span-1 bg-slate-100 dark:bg-slate-800 p-8 rounded-3xl border-b-2 border-blue-600/30 dark:border-blue-500/20 reveal-on-scroll stagger-delay-3">
              <Globe className="w-10 h-10 text-blue-600 dark:text-blue-400 mb-4" />
              <p className="font-headline font-bold text-xl">Open Standard</p>
              <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
                Built on {config.stats.standards} kernel.
              </p>
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
                <h2 className="font-headline text-3xl font-bold max-w-xs text-white">
                  Building the Infrastructure for Tomorrow
                </h2>
              </div>
            </div>
          </div>
        </section>

        {/* Team sections with the spotlight interaction. */}
        <section className="px-8 py-24 bg-white/30 dark:bg-slate-950 transition-colors">
          <div className="max-w-7xl mx-auto">
            <div className="flex flex-col md:flex-row justify-between items-end mb-16 gap-8">
              <div className="max-w-2xl reveal-on-scroll">
                <h2 className="font-headline text-4xl md:text-5xl font-bold mb-4 tracking-tight">
                  The Minds Behind the Machine
                </h2>
                <p className="text-slate-600 dark:text-slate-400 text-lg leading-relaxed">
                  A FAST University initiative working at the intersection of
                  high-fidelity graphics and quantum logic.
                </p>
              </div>
            </div>

            <TeamSpotlightSection
              title="QCanvas Team"
              description="Core developers building the editor, converter, and simulation experience inside QCanvas."
              teamKey="QCanvas"
              members={config.qcanvasTeam}
              activeSpotlight={activeSpotlight}
              setActiveSpotlight={activateSpotlight}
              scheduleSpotlight={scheduleSpotlight}
              clearScheduledSpotlight={clearHoverTimer}
            />

            <TeamSpotlightSection
              title="QSim Team"
              description="Simulation researchers shaping the backend execution and visualization flow for QSim."
              teamKey="QSim"
              members={config.qsimTeam}
              activeSpotlight={activeSpotlight}
              setActiveSpotlight={activateSpotlight}
              scheduleSpotlight={scheduleSpotlight}
              clearScheduledSpotlight={clearHoverTimer}
            />

            {/* Supervisors section keeps the simpler static layout. */}
            <div className="mt-32">
              <h3 className="font-headline text-2xl font-bold mb-10 text-slate-400 flex items-center gap-3 reveal-on-scroll">
                <div className="w-10 h-1 bg-slate-400 rounded-full" />
                Supervisors
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-10">
                {config.supervisors.map((supervisor, idx) => (
                  <div
                    key={supervisor.name}
                    className="flex items-center gap-8 bg-white dark:bg-slate-900 p-8 rounded-3xl shadow-lg border border-slate-100 dark:border-white/5 reveal-on-scroll"
                    style={{ transitionDelay: `${idx * 100}ms` }}
                  >
                    <div className="w-20 h-20 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center flex-shrink-0">
                      <Users className="w-10 h-10 text-slate-300 dark:text-slate-600" />
                    </div>
                    <div>
                      <h4 className="font-headline text-xl font-bold">
                        {supervisor.name}
                      </h4>
                      <p className="text-slate-500 dark:text-slate-400 text-sm font-medium">
                        {supervisor.role}
                      </p>
                      <div className="flex gap-3 mt-3">
                        <a
                          href={`mailto:${supervisor.email}`}
                          className="text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                        >
                          <Mail className="w-5 h-5" />
                        </a>
                        <a
                          href={supervisor.linkedin}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                        >
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

        {/* Three design/value statements with large numbered accents. */}
        <section className="px-8 py-32 max-w-5xl mx-auto">
          <div className="flex flex-col gap-24">
            <div className="flex flex-col md:flex-row items-start gap-12 group reveal-on-scroll">
              <span className="font-headline text-8xl font-black text-blue-800/50 dark:text-slate-900 group-hover:text-blue-600/10 dark:group-hover:text-blue-400/10 light:text-blue-300 transition-colors duration-500 leading-none">
                01
              </span>
              <div>
                <h3 className="font-headline text-3xl font-bold mb-4 flex items-center gap-4">
                  Uncompromising Precision
                  <Zap className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </h3>
                <p className="text-slate-600 dark:text-slate-400 text-lg leading-relaxed max-w-2xl">
                  Our visualization engines are built on rigorous mathematical
                  models, ensuring that what you see in the canvas reflects the
                  true physical state of your qubit operations.
                </p>
              </div>
            </div>

            <div className="flex flex-col md:flex-row items-start gap-12 group reveal-on-scroll">
              <span className="font-headline text-8xl font-black text-slate-100 dark:text-slate-900 group-hover:text-blue-600/10 dark:group-hover:text-blue-400/10 transition-colors duration-500 leading-none">
                02
              </span>
              <div>
                <h3 className="font-headline text-3xl font-bold mb-4 flex items-center gap-4">
                  Radical Accessibility
                  <Layout className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </h3>
                <p className="text-slate-600 dark:text-slate-400 text-lg leading-relaxed max-w-2xl">
                  We remove the gatekeepers of innovation. Whether you are a
                  student or a research professor, the tools remain equally
                  powerful and equally accessible.
                </p>
              </div>
            </div>

            <div className="flex flex-col md:flex-row items-start gap-12 group reveal-on-scroll">
              <span className="font-headline text-8xl font-black text-blue-800/50 dark:text-slate-900 group-hover:text-blue-600/10 dark:group-hover:text-blue-400/10 transition-colors duration-500 leading-none">
                03
              </span>
              <div>
                <h3 className="font-headline text-3xl font-bold mb-4 flex items-center gap-4">
                  Ethereal Design
                  <Sparkles className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                </h3>
                <p className="text-slate-600 dark:text-slate-400 text-lg leading-relaxed max-w-2xl">
                  Software should be beautiful. We treat every interface
                  component as a piece of digital craftsmanship, designed to
                  fade into the background while you focus on discovery.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Final call-to-action section. */}
        <section className="px-8 py-32 text-center reveal-on-scroll">
          <div className="max-w-4xl mx-auto rounded-[3rem] p-16 relative overflow-hidden bg-white dark:bg-gradient-to-br dark:from-slate-900 dark:to-slate-950 shadow-2xl border border-slate-100 dark:border-white/5">
            {/* Animated background elements for CTA */}
            <div className="absolute top-0 right-0 p-8 opacity-5">
              <Zap className="w-64 h-64 text-blue-600 dark:text-blue-400 rotate-12" />
            </div>

            <h2 className="font-headline text-4xl md:text-5xl font-bold mb-6">
              Ready to observe the future?
            </h2>
            <p className="text-slate-600 dark:text-slate-400 text-lg mb-10 max-w-xl mx-auto">
              Join operators already exploring the quantum landscape on{" "}
              {config.project.name}.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4 relative z-10">
              <Link
                href={canAccessApp ? "/app" : "/login"}
                className="bg-blue-600 dark:bg-gradient-to-r dark:from-blue-600 dark:to-indigo-600 text-gray-100 dark:text-white px-10 py-4 rounded-2xl font-bold text-lg hover:shadow-[0_0_30px_rgba(37,99,235,0.4)] transition-all hover:-translate-y-1 active:scale-95"
              >
                Start Experimenting
              </Link>
              <Link
                href="/docs"
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

      {/* Local animation helpers for scroll reveal and spotlight motion. */}
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
        .stagger-delay-1 {
          transition-delay: 150ms;
        }
        .stagger-delay-2 {
          transition-delay: 300ms;
        }
        .stagger-delay-3 {
          transition-delay: 450ms;
        }
        .stagger-delay-4 {
          transition-delay: 600ms;
        }

        @keyframes fade-in {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        @keyframes slide-up {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes spotlight-main-in {
          from {
            opacity: 0;
            transform: translateX(-22px) scale(0.985);
          }
          to {
            opacity: 1;
            transform: translateX(0) scale(1);
          }
        }
        @keyframes spotlight-panel-in {
          from {
            opacity: 0;
            transform: translateY(14px) scale(0.985);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
        @keyframes spotlight-stack-in {
          from {
            opacity: 0;
            transform: translateX(20px) scale(0.98);
          }
          to {
            opacity: 1;
            transform: translateX(0) scale(1);
          }
        }
        .animate-fade-in {
          animation: fade-in 1s ease-out forwards;
        }
        .animate-slide-up {
          animation: slide-up 0.8s ease-out forwards;
        }
      `}</style>
    </div>
  );
}
