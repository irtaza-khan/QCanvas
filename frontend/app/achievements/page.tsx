"use client";

import { useState } from "react";
import AchievementCard, { Achievement } from "@/components/gamification/AchievementCard";
import StatsOverview from "@/components/gamification/StatsOverview";
import SimpleTopBar from "@/components/SimpleTopBar";

// Mock Data based on Gamification Plan
const MOCK_ACHIEVEMENTS: Achievement[] = [
    // Getting Started
    {
        id: "1",
        name: "First Steps",
        description: "Create your first quantum circuit using QCanvas.",
        category: "Getting Started",
        rarity: "Common",
        xpReward: 50,
        iconName: "rocket",
        isUnlocked: true,
        progress: 1,
        target: 1,
        unlockedAt: "2026-01-20"
    },
    {
        id: "2",
        name: "Hello Quantum",
        description: "Simulate your first Bell state to create entanglement.",
        category: "Getting Started",
        rarity: "Common",
        xpReward: 75,
        iconName: "rocket",
        isUnlocked: true,
        progress: 1,
        target: 1,
        unlockedAt: "2026-01-21"
    },
    {
        id: "3",
        name: "Framework Explorer",
        description: "Try creating circuits in Qiskit, Cirq, and PennyLane.",
        category: "Getting Started",
        rarity: "Rare",
        xpReward: 150,
        iconName: "compass",
        isUnlocked: false,
        progress: 1,
        target: 3
    },
    // Mastery
    {
        id: "4",
        name: "Qubit Wrangler",
        description: "Simulate a total of 100 quantum circuits.",
        category: "Mastery",
        rarity: "Rare",
        xpReward: 300,
        iconName: "target",
        isUnlocked: false,
        progress: 12,
        target: 100
    },
    {
        id: "5",
        name: "Getting the Hang of It",
        description: "Run 10 simulations successfully.",
        category: "Mastery",
        rarity: "Uncommon",
        xpReward: 100,
        iconName: "target",
        isUnlocked: true,
        progress: 10,
        target: 10
    },
    {
        id: "6",
        name: "Level 5 Achieved",
        description: "Reach level 5 by earning XP.",
        category: "Mastery",
        rarity: "Uncommon",
        xpReward: 100,
        iconName: "star",
        isUnlocked: true,
        progress: 5,
        target: 5
    },
    // Algorithm
    {
        id: "7",
        name: "Grover's Guardian",
        description: "Implement Grover's search algorithm successfully.",
        category: "Algorithms",
        rarity: "Epic",
        xpReward: 400,
        iconName: "award",
        isUnlocked: false,
        progress: 0,
        target: 1
    },
    {
        id: "8",
        name: "Shor's Scholar",
        description: "Implement Shor's factoring algorithm.",
        category: "Algorithms",
        rarity: "Legendary",
        xpReward: 500,
        iconName: "award",
        isUnlocked: false,
        progress: 0,
        target: 1
    }
];

const CATEGORIES = ["All", "Getting Started", "Mastery", "Algorithms"];

export default function AchievementsPage() {
    const [activeCategory, setActiveCategory] = useState("All");

    const filteredAchievements = activeCategory === "All"
        ? MOCK_ACHIEVEMENTS
        : MOCK_ACHIEVEMENTS.filter(a => a.category === activeCategory);

    return (
        <div className="min-h-screen bg-editor-bg text-white">
            <SimpleTopBar />

            {/* Spacer to prevent topbar overlap */}
            <div className="h-20"></div>

            <div className="p-6 md:p-10">
                <div className="max-w-6xl mx-auto">
                    <header className="mb-10">
                        <h1 className="text-4xl font-bold quantum-gradient bg-clip-text text-transparent mb-2">
                            Achievements
                        </h1>
                        <p className="text-gray-400">Track your progress and mastery of quantum computing.</p>
                    </header>

                    {/* Stats Overview */}
                    <StatsOverview achievements={MOCK_ACHIEVEMENTS} />

                    {/* Category Filter */}
                    <div className="flex gap-2 overflow-x-auto pb-4 mb-6 border-b border-white/10">
                        {CATEGORIES.map(category => (
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

                    {/* Achievements Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {filteredAchievements.map(achievement => (
                            <AchievementCard key={achievement.id} achievement={achievement} />
                        ))}
                    </div>

                    {filteredAchievements.length === 0 && (
                        <div className="text-center py-20 text-gray-500">
                            No achievements found in this category yet.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
