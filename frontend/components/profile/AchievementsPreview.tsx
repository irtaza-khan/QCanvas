"use client";

import { useEffect } from "react";
import Link from "next/link";
import { ChevronRight, Trophy } from "lucide-react";
import AchievementCard from "@/components/gamification/AchievementCard";
import { useGamificationStore, getCategoryDisplayName, AchievementData } from "@/lib/gamificationStore";
import { useAuthStore } from "@/lib/authStore";

// Map backend data to AchievementCard format
function mapToCardFormat(a: AchievementData) {
    const rarityMap: Record<string, "Common" | "Uncommon" | "Rare" | "Epic" | "Legendary"> = {
        common: "Common",
        uncommon: "Uncommon",
        rare: "Rare",
        epic: "Epic",
        legendary: "Legendary",
    };

    return {
        id: a.id,
        name: a.name,
        description: a.description,
        category: getCategoryDisplayName(a.category),
        rarity: rarityMap[a.rarity] || "Common" as const,
        xpReward: a.xp_reward,
        iconName: a.icon_name,
        isUnlocked: a.is_unlocked,
        progress: a.progress,
        target: a.target,
        unlockedAt: a.unlocked_at || undefined,
    };
}

export default function AchievementsPreview() {
    const { achievements, fetchAchievements } = useGamificationStore();
    const { token } = useAuthStore();

    useEffect(() => {
        if (token) {
            fetchAchievements(token);
        }
    }, [token, fetchAchievements]);

    // Show up to 3 achievements: prioritize recently unlocked, then closest to unlocking
    const mapped = achievements.map(mapToCardFormat);
    const unlocked = mapped.filter(a => a.isUnlocked).slice(0, 2);
    const inProgress = mapped
        .filter(a => !a.isUnlocked && a.progress > 0)
        .sort((a, b) => (b.progress / b.target) - (a.progress / a.target))
        .slice(0, 3 - unlocked.length);
    const previewItems = [...unlocked, ...inProgress].slice(0, 3);

    // Fallback if no data yet
    if (previewItems.length === 0 && !token) {
        return (
            <div className="bg-quantum-glass-dark border border-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold text-lg text-white flex items-center gap-2">
                        <Trophy className="w-5 h-5 text-yellow-400" />
                        Achievements
                    </h3>
                </div>
                <p className="text-gray-500 text-sm">Sign in to track your achievements.</p>
            </div>
        );
    }

    return (
        <div className="bg-quantum-glass-dark border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-lg text-white flex items-center gap-2">
                    <Trophy className="w-5 h-5 text-yellow-400" />
                    Achievements
                    {achievements.length > 0 && (
                        <span className="text-xs text-gray-500 font-normal">
                            {mapped.filter(a => a.isUnlocked).length}/{mapped.length}
                        </span>
                    )}
                </h3>
                <Link
                    href="/achievements"
                    className="text-xs text-quantum-blue-light hover:text-white flex items-center gap-1 transition-colors"
                >
                    View All <ChevronRight className="w-3 h-3" />
                </Link>
            </div>

            <div className="grid grid-cols-1 gap-3">
                {previewItems.map(achievement => (
                    <AchievementCard key={achievement.id} achievement={achievement} />
                ))}
            </div>

            {previewItems.length === 0 && (
                <p className="text-gray-500 text-sm text-center py-4">
                    Start using QCanvas to earn your first achievements!
                </p>
            )}
        </div>
    );
}
