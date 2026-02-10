"use client";

import { useAuthStore } from "@/lib/authStore";
import { useGamificationStore, getLevelBadge } from "@/lib/gamificationStore";
import { Edit2, MapPin, Calendar, Shield } from "lucide-react";
import { useEffect } from "react";

export default function ProfileHeader() {
    const { user, token } = useAuthStore();
    const { stats, fetchStats } = useGamificationStore();

    // Fetch stats when component mounts
    useEffect(() => {
        if (user && token) {
            fetchStats(token);
        }
    }, [user, token, fetchStats]);

    // Fallback if user is not loaded
    const displayUser = user || {
        username: "QuantumUser",
        full_name: "Quantum Explorer",
        email: "explorer@qcanvas.com",
        created_at: new Date().toISOString()
    };

    const initials = displayUser.full_name
        ? displayUser.full_name.split(" ").map((n: string) => n[0]).join("").toUpperCase().slice(0, 2)
        : "QU";

    // Use real stats
    const level = stats?.level || 1;
    const badge = getLevelBadge(level);

    // Format join date
    const joinDate = new Date(displayUser.created_at).toLocaleDateString('en-US', {
        month: 'long',
        year: 'numeric'
    });

    return (
        <div className="bg-quantum-glass-dark border border-white/10 rounded-xl overflow-hidden relative group">
            {/* Cover Image Placeholder */}
            <div className="h-32 bg-gradient-to-r from-quantum-blue to-purple-800 opacity-80 group-hover:opacity-100 transition-opacity"></div>

            <div className="px-6 pb-6 relative">
                {/* Avatar */}
                <div className="absolute -top-12 left-6">
                    <div className="w-24 h-24 rounded-full bg-editor-bg p-1.5">
                        <div className="w-full h-full rounded-full bg-gradient-to-br from-quantum-blue to-purple-600 flex items-center justify-center text-3xl font-bold text-white shadow-xl">
                            {initials}
                        </div>
                    </div>
                    {/* Online Status */}
                    <div className="absolute bottom-2 right-2 w-5 h-5 bg-green-500 rounded-full border-4 border-editor-bg" title="Online"></div>
                </div>

                {/* Action Button */}
                <div className="flex justify-end pt-4 mb-4">
                    <button className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm font-medium text-white transition-all flex items-center gap-2">
                        <Edit2 className="w-4 h-4" /> Edit Profile
                    </button>
                </div>

                {/* User Info */}
                <div className="mt-2">
                    <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                        {displayUser.full_name}
                        <span className="text-xs bg-quantum-blue/20 text-quantum-blue-light px-2 py-0.5 rounded border border-quantum-blue/30 font-mono">
                            Level {level}
                        </span>
                    </h1>
                    <p className="text-gray-400 text-sm">@{displayUser.username}</p>
                </div>

                {/* Bio Placeholder */}
                <p className="mt-4 text-gray-300 text-sm leading-relaxed max-w-lg">
                    Quantum computing enthusiast diving deep into algorithms. Currently exploring Shor's Algorithm and error correction codes.
                </p>

                {/* Metadata */}
                <div className="mt-6 flex flex-wrap gap-4 text-xs text-gray-500">
                    <div className="flex items-center gap-1.5">
                        <Shield className="w-4 h-4 text-gray-400" />
                        <span>{badge}</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <MapPin className="w-4 h-4 text-gray-400" />
                        <span>Quantum Realm</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                        <Calendar className="w-4 h-4 text-gray-400" />
                        <span>Joined {joinDate}</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
