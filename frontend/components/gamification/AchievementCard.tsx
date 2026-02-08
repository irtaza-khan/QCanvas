"use client";

import { Award, Lock, CheckCircle2, Star, Zap, Activity } from "lucide-react";

export type AchievementRarity = "Common" | "Uncommon" | "Rare" | "Epic" | "Legendary";

export interface Achievement {
  id: string;
  name: string;
  description: string;
  category: string;
  rarity: AchievementRarity;
  xpReward: number;
  iconName: string; // Map to Lucide icons
  isUnlocked: boolean;
  progress: number;
  target: number;
  unlockedAt?: string;
}

interface AchievementCardProps {
  achievement: Achievement;
}

const RARITY_STYLES = {
  Common: "border-gray-200 bg-white text-gray-600 dark:border-gray-600/50 dark:bg-gray-900/40 dark:text-gray-400",
  Uncommon: "border-green-200 bg-green-50 text-green-700 dark:border-green-500/50 dark:bg-green-900/20 dark:text-green-400 shadow-sm dark:shadow-[0_0_15px_-3px_rgba(34,197,94,0.1)]",
  Rare: "border-blue-200 bg-blue-50 text-blue-700 dark:border-blue-500/50 dark:bg-blue-900/20 dark:text-blue-400 shadow-sm dark:shadow-[0_0_15px_-3px_rgba(59,130,246,0.15)]",
  Epic: "border-purple-200 bg-purple-50 text-purple-700 dark:border-purple-500/50 dark:bg-purple-900/20 dark:text-purple-400 shadow-sm dark:shadow-[0_0_20px_-3px_rgba(168,85,247,0.2)]",
  Legendary: "border-yellow-200 bg-yellow-50 text-yellow-700 dark:border-yellow-500/50 dark:bg-yellow-900/20 dark:text-yellow-400 shadow-sm dark:shadow-[0_0_25px_-3px_rgba(234,179,8,0.25)] ring-1 ring-yellow-200 dark:ring-yellow-500/20",
};

const RARITY_COLORS = {
  Common: "text-gray-500 dark:text-gray-500",
  Uncommon: "text-green-600 dark:text-green-500",
  Rare: "text-blue-600 dark:text-blue-500",
  Epic: "text-purple-600 dark:text-purple-500",
  Legendary: "text-yellow-600 dark:text-yellow-500",
};

// Helper to get icon component
const getIcon = (name: string) => {
  switch (name) {
    case "rocket": return Zap;
    case "target": return CheckCircle2;
    case "compass": return Activity;
    case "award": return Award;
    case "star": return Star;
    default: return Award;
  }
};

export default function AchievementCard({ achievement }: AchievementCardProps) {
  const Icon = getIcon(achievement.iconName);
  const rarityStyle = RARITY_STYLES[achievement.rarity];
  const isLocked = !achievement.isUnlocked;

  // Progress calculation
  const progressPercent = Math.min(100, (achievement.progress / achievement.target) * 100);

  return (
    <div
      className={`relative group rounded-xl border p-4 transition-all duration-300 ${isLocked
        ? "border-gray-200 bg-gray-50/50 dark:border-white/5 dark:bg-white/5 opacity-70 hover:opacity-100 hover:bg-gray-100 dark:hover:bg-white/10"
        : `${rarityStyle} hover:scale-[1.02] hover:-translate-y-1 bg-white dark:bg-transparent`
        }`}
    >
      {/* Glow effect for unlocked high-rarity items */}
      {!isLocked && (achievement.rarity === "Epic" || achievement.rarity === "Legendary") && (
        <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-white/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
      )}

      <div className="flex gap-4 items-start">
        {/* Icon Container */}
        <div className={`
          w-14 h-14 rounded-xl flex items-center justify-center shrink-0 border
          ${isLocked
            ? "bg-gray-100 border-gray-200 text-gray-400 dark:bg-black/30 dark:border-white/10 dark:text-gray-600"
            : `bg-opacity-10 dark:bg-black/20 border-current ${RARITY_COLORS[achievement.rarity]}`
          }
        `}>
          {isLocked ? <Lock className="w-7 h-7" /> : <Icon className="w-7 h-7" />}
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start mb-1">
            <h3 className={`font-bold text-base truncate pr-2 ${isLocked ? "text-gray-500 dark:text-gray-400" : "text-gray-900 dark:text-white"}`}>
              {achievement.name}
            </h3>
            <span className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border border-current ${isLocked ? "text-gray-500 border-gray-200 dark:text-gray-600 dark:border-gray-700" : RARITY_COLORS[achievement.rarity]
              }`}>
              {achievement.rarity}
            </span>
          </div>

          <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
            {achievement.description}
          </p>

          {/* Progress Bar or Unlocked Date */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-medium text-gray-500 dark:text-gray-400">
              <span>{isLocked ? "In Progress" : "Completed"}</span>
              <span className={!isLocked ? "text-quantum-blue dark:text-quantum-blue-light" : ""}>
                {achievement.progress} / {achievement.target}
              </span>
            </div>

            <div className={`h-2 rounded-full overflow-hidden ${isLocked ? "bg-gray-200 dark:bg-white/5" : "bg-gray-200 dark:bg-black/30"}`}>
              <div
                className={`h-full transition-all duration-500 ${isLocked
                  ? "bg-gray-400 dark:bg-gray-600"
                  : `bg-gradient-to-r from-current to-white/50 ${RARITY_COLORS[achievement.rarity]}`
                  }`}
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* XP Reward Badge */}
      <div className={`
        absolute -top-2 -right-2 px-2 py-0.5 rounded-full text-[10px] font-bold shadow-lg border
        ${isLocked
          ? "bg-gray-800 border-gray-700 text-gray-500"
          : "bg-editor-bg border-white/10 text-yellow-400 border-yellow-500/20"
        }
      `}>
        +{achievement.xpReward} XP
      </div>
    </div>
  );
}
