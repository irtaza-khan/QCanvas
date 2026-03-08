"use client";

import { useState, useEffect } from "react";
import { RefreshCw, Trophy, Filter, Lock } from "lucide-react";
import AchievementCard from "@/components/gamification/AchievementCard";
import StatsOverview from "@/components/gamification/StatsOverview";
import SimpleTopBar from "@/components/SimpleTopBar";
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

export default function AchievementsPage() {
    const [activeCategory, setActiveCategory] = useState("All");
    const { achievements, achievementsLoading, fetchAchievements } = useGamificationStore();
    const { token } = useAuthStore();

    // Fetch achievements on mount
    useEffect(() => {
        if (token) {
            fetchAchievements(token, true);
        }
    }, [token, fetchAchievements]);

    // Build category list from actual data
    const categories = ["All", ...Array.from(new Set(
        achievements.map(a => getCategoryDisplayName(a.category))
    )).sort()];

    // Map and filter
    const mapped = achievements.map(mapToCardFormat);
    const filtered = activeCategory === "All"
        ? mapped
        : mapped.filter(a => a.category === activeCategory);

    // Separate into 3 groups: Completed, In Progress, Not Started
    const completed = filtered.filter(a => a.isUnlocked);
    const inProgress = filtered.filter(a => !a.isUnlocked && a.progress > 0);
    const notStarted = filtered.filter(a => !a.isUnlocked && a.progress === 0);

    const handleRefresh = () => {
        if (token) fetchAchievements(token, true);
    };

    return (
        <div className="min-h-screen bg-editor-bg text-white">
            <SimpleTopBar />

            {/* Spacer to prevent topbar overlap */}
            <div className="h-20"></div>

            <div className="p-6 md:p-10">
                <div className="max-w-6xl mx-auto">
                    {/* Header */}
                    <header className="mb-10 flex items-end justify-between">
                        <div>
                            <h1 className="text-4xl font-bold quantum-gradient bg-clip-text text-transparent mb-2">
                                Achievements
                            </h1>
                            <p className="text-gray-400">
                                Track your progress and mastery of quantum computing. All achievements are tracked automatically — just use QCanvas!
                            </p>
                        </div>
                        <button
                            onClick={handleRefresh}
                            disabled={achievementsLoading}
                            className="flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm text-gray-300 hover:text-white transition-all disabled:opacity-50"
                        >
                            <RefreshCw className={`w-4 h-4 ${achievementsLoading ? 'animate-spin' : ''}`} />
                            Refresh
                        </button>
                    </header>

                    {/* Stats Overview */}
                    <StatsOverview achievements={mapped} />

                    {/* Category Filter */}
                    <div className="flex gap-2 overflow-x-auto pb-4 mb-6 border-b border-white/10">
                        {categories.map(category => (
                            <button
                                key={category}
                                onClick={() => setActiveCategory(category)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${activeCategory === category
                                    ? "bg-quantum-blue-light text-white shadow-lg shadow-quantum-blue-light/20"
                                    : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
                                    }`}
                            >
                                {category}
                            </button>
                        ))}
                    </div>

                    {/* Loading State */}
                    {achievementsLoading && achievements.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-20 gap-4">
                            <div className="w-10 h-10 border-2 border-quantum-blue-light border-t-transparent rounded-full animate-spin" />
                            <p className="text-gray-500 text-sm">Loading achievements...</p>
                        </div>
                    )}

                    {/* ✅ Completed Section */}
                    {completed.length > 0 && (
                        <div className="mb-8">
                            <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                                <Trophy className="w-5 h-5 text-yellow-400" />
                                Completed
                                <span className="text-sm font-normal text-gray-500">({completed.length})</span>
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {completed.map(achievement => (
                                    <AchievementCard key={achievement.id} achievement={achievement} />
                                ))}
                            </div>
                        </div>
                    )}

                    {/* 🔄 In Progress Section */}
                    {inProgress.length > 0 && (
                        <div className="mb-8">
                            <h2 className="text-lg font-semibold text-blue-400 mb-4 flex items-center gap-2">
                                <Filter className="w-5 h-5 text-blue-500" />
                                In Progress
                                <span className="text-sm font-normal text-gray-500">({inProgress.length})</span>
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {inProgress.map(achievement => (
                                    <AchievementCard key={achievement.id} achievement={achievement} />
                                ))}
                            </div>
                        </div>
                    )}

                    {/* 🔒 Not Started Section */}
                    {notStarted.length > 0 && (
                        <div>
                            <h2 className="text-lg font-semibold text-gray-500 mb-4 flex items-center gap-2">
                                <Lock className="w-5 h-5 text-gray-600" />
                                Not Started
                                <span className="text-sm font-normal text-gray-600">({notStarted.length})</span>
                            </h2>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                {notStarted.map(achievement => (
                                    <AchievementCard key={achievement.id} achievement={achievement} />
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Empty State */}
                    {!achievementsLoading && filtered.length === 0 && (
                        <div className="text-center py-20">
                            <Trophy className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                            <p className="text-gray-500">
                                {achievements.length === 0
                                    ? "No achievements available yet. Please sign in to view your achievements."
                                    : "No achievements found in this category."
                                }
                            </p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
