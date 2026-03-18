"use client";

import { useEffect, useState } from "react";
import { Trophy, Star, Zap, Award, Target, Activity } from '@/components/Icons';
import { X } from 'lucide-react';
import { AchievementUnlock } from "@/lib/gamificationStore";

interface AchievementToastProps {
    achievement: AchievementUnlock | null;
    onClose: () => void;
}

const RARITY_GRADIENTS: Record<string, string> = {
    common: "from-gray-600/90 to-gray-800/90",
    uncommon: "from-green-600/90 to-green-900/90",
    rare: "from-blue-600/90 to-blue-900/90",
    epic: "from-purple-600/90 to-purple-900/90",
    legendary: "from-yellow-500/90 via-orange-500/90 to-red-600/90",
};

const RARITY_BORDERS: Record<string, string> = {
    common: "border-gray-400/50",
    uncommon: "border-green-400/50",
    rare: "border-blue-400/50",
    epic: "border-purple-400/50",
    legendary: "border-yellow-400/60 shadow-[0_0_30px_rgba(234,179,8,0.3)]",
};

const RARITY_ICON_BG: Record<string, string> = {
    common: "bg-gray-500/30",
    uncommon: "bg-green-500/30",
    rare: "bg-blue-500/30",
    epic: "bg-purple-500/30",
    legendary: "bg-yellow-500/30",
};

const RARITY_LABELS: Record<string, string> = {
    common: "Common",
    uncommon: "Uncommon",
    rare: "Rare",
    epic: "Epic",
    legendary: "Legendary",
};

const getIcon = (name: string) => {
    switch (name) {
        case "rocket": return Zap;
        case "target": return Target;
        case "compass": return Activity;
        case "award": return Award;
        case "star": return Star;
        default: return Trophy;
    }
};

export default function AchievementToast({ achievement, onClose }: AchievementToastProps) {
    const [isVisible, setIsVisible] = useState(false);
    const [isExiting, setIsExiting] = useState(false);

    useEffect(() => {
        if (achievement) {
            setIsVisible(true);
            setIsExiting(false);

            const timer = setTimeout(() => {
                handleClose();
            }, 6000);

            return () => clearTimeout(timer);
        }
    }, [achievement]);

    const handleClose = () => {
        setIsExiting(true);
        setTimeout(() => {
            setIsVisible(false);
            setIsExiting(false);
            onClose();
        }, 400);
    };

    if (!achievement || !isVisible) return null;

    const rarity = achievement.rarity?.toLowerCase() || "common";
    const gradient = RARITY_GRADIENTS[rarity] || RARITY_GRADIENTS.common;
    const border = RARITY_BORDERS[rarity] || RARITY_BORDERS.common;
    const iconBg = RARITY_ICON_BG[rarity] || RARITY_ICON_BG.common;
    const rarityLabel = RARITY_LABELS[rarity] || "Common";
    const Icon = getIcon(achievement.icon_name);

    return (
        <div
            className={`
        fixed top-6 right-6 z-[9999] w-[360px] max-w-[calc(100vw-2rem)]
        transition-all duration-400
        ${isExiting
                    ? "translate-x-[120%] opacity-0 scale-95"
                    : "translate-x-0 opacity-100 scale-100"
                }
      `}
            style={{
                animation: !isExiting ? "slideInRight 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)" : undefined,
            }}
        >
            {/* Glow effect for epic/legendary */}
            {(rarity === "epic" || rarity === "legendary") && (
                <div
                    className={`absolute -inset-1 rounded-2xl bg-gradient-to-r ${gradient} blur-lg opacity-40 animate-pulse pointer-events-none`}
                />
            )}

            <div
                className={`
          relative overflow-hidden rounded-xl border-2 ${border}
          bg-gradient-to-r ${gradient}
          backdrop-blur-xl
          shadow-2xl
        `}
            >
                {/* Shimmer animation */}
                <div
                    className="absolute inset-0 pointer-events-none"
                    style={{
                        background: "linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.08) 45%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.08) 55%, transparent 60%)",
                        animation: "shimmer 2.5s ease-in-out infinite",
                    }}
                />

                {/* Header badge */}
                <div className="flex items-center gap-2 px-4 pt-3 pb-1">
                    <Trophy className="w-4 h-4 text-yellow-300" />
                    <span className="text-yellow-300 text-xs font-bold uppercase tracking-widest">
                        Achievement Unlocked!
                    </span>
                    <div className="flex-1" />
                    <button
                        onClick={handleClose}
                        className="text-white/50 hover:text-white transition-colors p-0.5 rounded"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>

                {/* Content */}
                <div className="flex items-center gap-4 px-4 pb-4 pt-2">
                    {/* Icon */}
                    <div className={`w-14 h-14 rounded-xl ${iconBg} flex items-center justify-center shrink-0 border border-white/10`}>
                        <Icon className="w-7 h-7 text-white" />
                    </div>

                    {/* Text */}
                    <div className="flex-1 min-w-0">
                        <h4 className="text-white font-bold text-base truncate">
                            {achievement.name}
                        </h4>
                        <p className="text-white/70 text-sm line-clamp-1">
                            {achievement.description}
                        </p>
                        <div className="flex items-center gap-3 mt-1.5">
                            <span className="text-xs font-bold uppercase tracking-wider text-white/60 border border-white/20 px-2 py-0.5 rounded">
                                {rarityLabel}
                            </span>
                            <span className="text-yellow-300 text-xs font-bold">
                                +{achievement.xp_reward} XP
                            </span>
                        </div>
                    </div>
                </div>

                {/* Progress bar animation at bottom */}
                <div className="h-1 bg-black/20">
                    <div
                        className="h-full bg-white/40 rounded-r"
                        style={{
                            animation: "shrinkWidth 6s linear forwards",
                        }}
                    />
                </div>
            </div>

            <style jsx>{`
        @keyframes slideInRight {
          from {
            transform: translateX(120%) scale(0.9);
            opacity: 0;
          }
          to {
            transform: translateX(0) scale(1);
            opacity: 1;
          }
        }
        @keyframes shimmer {
          0% { transform: translateX(-200%); }
          50% { transform: translateX(200%); }
          100% { transform: translateX(200%); }
        }
        @keyframes shrinkWidth {
          from { width: 100%; }
          to { width: 0%; }
        }
      `}</style>
        </div>
    );
}
