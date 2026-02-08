"use client";

import Link from "next/link";
import { ChevronRight, Trophy } from "lucide-react";
import AchievementCard, { Achievement } from "@/components/gamification/AchievementCard";

// Mock data matching what we used in Main Achievements page
const PREVIEW_ACHIEVEMENTS: Achievement[] = [
    {
        id: "7",
        name: "Grover's Guardian",
        description: "Implement Grover's search algorithm successfully.",
        category: "Algorithms",
        rarity: "Epic", // Showing off a cool locked one
        xpReward: 400,
        iconName: "award",
        isUnlocked: false,
        progress: 0,
        target: 1
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
    }
];

export default function AchievementsPreview() {
    return (
        <div className="bg-quantum-glass-dark border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold text-lg text-white flex items-center gap-2">
                    <Trophy className="w-5 h-5 text-yellow-400" />
                    Achievements
                </h3>
                <Link
                    href="/achievements"
                    className="text-xs text-quantum-blue-light hover:text-white flex items-center gap-1 transition-colors"
                >
                    View All <ChevronRight className="w-3 h-3" />
                </Link>
            </div>

            <div className="grid grid-cols-1 gap-3">
                {PREVIEW_ACHIEVEMENTS.filter(a => a.isUnlocked).map(achievement => (
                    <AchievementCard key={achievement.id} achievement={achievement} />
                ))}
            </div>
        </div>
    );
}
