"use client";

import { useEffect } from "react";
import { useRequireAuth } from "@/lib/auth";
import { useAuthStore } from "@/lib/authStore";
import { useGamificationStore, formatXP } from "@/lib/gamificationStore";
import ProfileHeader from "@/components/profile/ProfileHeader";
import XPHistoryChart from "@/components/profile/XPHistoryChart";
import RecentActivityList from "@/components/profile/RecentActivityList";
import AchievementsPreview from "@/components/profile/AchievementsPreview";
import SimpleTopBar from "@/components/SimpleTopBar";
import { Zap, Flame, Award } from "lucide-react";

export default function ProfilePage() {
    const { isAuthenticated, loading } = useRequireAuth();
    const { token } = useAuthStore();
    const { stats, fetchStats } = useGamificationStore();

    // Fetch stats when page loads
    useEffect(() => {
        if (isAuthenticated && token) {
            fetchStats(token);
        }
    }, [isAuthenticated, token, fetchStats]);

    if (loading) {
        return <div className="min-h-screen flex items-center justify-center text-quantum-blue-light">Loading profile...</div>;
    }

    if (!isAuthenticated) return null;

    // Use real stats or defaults
    const totalXP = stats?.total_xp || 0;
    const currentStreak = stats?.current_streak || 0;
    const longestStreak = stats?.longest_streak || 0;

    return (
        <div className="min-h-screen bg-editor-bg text-white">
            <SimpleTopBar />

            {/* Spacer to prevent topbar overlap */}
            <div className="h-20"></div>

            <div className="p-4 md:p-8">
                <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left Column: User Info & Main Stats */}
                    <div className="lg:col-span-1 space-y-6">
                        <ProfileHeader />

                        {/* Quick Stats Grid */}
                        <div className="grid grid-cols-3 gap-3">
                            <div className="bg-quantum-glass-dark border border-white/10 rounded-xl p-3 flex flex-col items-center justify-center text-center hover:border-yellow-400/30 transition-all group">
                                <Zap className="w-5 h-5 text-yellow-400 mb-1 group-hover:scale-110 transition-transform" />
                                <span className="text-xl font-bold text-white">{formatXP(totalXP)}</span>
                                <span className="text-[10px] text-gray-400 uppercase">Total XP</span>
                            </div>
                            <div className="bg-quantum-glass-dark border border-white/10 rounded-xl p-3 flex flex-col items-center justify-center text-center hover:border-orange-400/30 transition-all group">
                                <Flame className="w-5 h-5 text-orange-500 mb-1 group-hover:scale-110 transition-transform" />
                                <span className="text-xl font-bold text-white">{currentStreak}</span>
                                <span className="text-[10px] text-gray-400 uppercase">Day Streak</span>
                            </div>
                            <div className="bg-quantum-glass-dark border border-white/10 rounded-xl p-3 flex flex-col items-center justify-center text-center hover:border-purple-400/30 transition-all group">
                                <Award className="w-5 h-5 text-purple-400 mb-1 group-hover:scale-110 transition-transform" />
                                <span className="text-xl font-bold text-white">{longestStreak}</span>
                                <span className="text-[10px] text-gray-400 uppercase">Best Streak</span>
                            </div>
                        </div>

                        <AchievementsPreview />
                    </div>

                    {/* Right Column: Activity & Charts */}
                    <div className="lg:col-span-2 space-y-6">
                        <XPHistoryChart />
                        <RecentActivityList />
                    </div>
                </div>
            </div>
        </div>
    );
}
