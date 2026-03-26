"use client";

import { useState } from "react";
import { useAuthStore } from "@/lib/authStore";
import { useGamificationStore, getLevelBadge } from "@/lib/gamificationStore";
import { Edit2, MapPin, Calendar, Shield, Sparkles } from 'lucide-react';;
import { useEffect } from "react";
import EditProfileModal from "@/components/profile/EditProfileModal";

export default function ProfileHeader() {
    const { user, token } = useAuthStore();
    const { stats, fetchStats } = useGamificationStore();
    const [editOpen, setEditOpen] = useState(false);

    useEffect(() => {
        if (user && token) {
            fetchStats(token);
        }
    }, [user, token, fetchStats]);

    const displayUser = user || {
        username: "QuantumUser",
        full_name: "Quantum Explorer",
        email: "explorer@qcanvas.com",
        created_at: new Date().toISOString(),
        bio: undefined,
    };

    const initials = displayUser.full_name
        ? displayUser.full_name.split(" ").map((n: string) => n[0]).join("").toUpperCase().slice(0, 2)
        : "QU";

    const level = stats?.level || 1;
    const badge = getLevelBadge(level);
    const xpProgress = stats?.progress_percentage || 0;

    const joinDate = new Date(displayUser.created_at).toLocaleDateString("en-US", {
        month: "long",
        year: "numeric",
    });

    const bio = (displayUser as typeof displayUser & { bio?: string }).bio ||
        "No bio provided yet. Click 'Edit Profile' to add one!";

    return (
        <>
            <div className="bg-quantum-glass-dark border border-white/10 rounded-xl overflow-hidden relative group">
                {/* Cover Banner */}
                <div className="h-28 relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-r from-[#0f2050] via-[#1a3a7c] to-[#2d1b69]" />
                    {/* Animated shimmer lines */}
                    <div className="absolute inset-0 opacity-20"
                        style={{
                            backgroundImage: "repeating-linear-gradient(135deg, transparent, transparent 20px, rgba(255,255,255,0.03) 20px, rgba(255,255,255,0.03) 40px)",
                        }}
                    />
                    {/* Floating sparkle dots */}
                    <div className="absolute top-3 right-4 flex gap-3 opacity-30">
                        {[...Array(6)].map((_, i) => (
                            <div
                                key={i}
                                className="w-1 h-1 rounded-full bg-blue-300"
                                style={{ animationDelay: `${i * 0.4}s` }}
                            />
                        ))}
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 h-8 bg-gradient-to-t from-black/30 to-transparent" />
                </div>

                <div className="px-5 pb-5 relative">
                    {/* Avatar + Edit Row */}
                    <div className="flex items-start justify-between">
                        {/* Avatar */}
                        <div className="absolute -top-12 left-5">
                            <div className="w-[88px] h-[88px] rounded-full bg-[#141622] p-[3px] shadow-xl">
                                <div className="w-full h-full rounded-full bg-gradient-to-br from-quantum-blue to-purple-600 flex items-center justify-center text-3xl font-bold text-white select-none">
                                    {initials}
                                </div>
                            </div>
                            {/* Online dot */}
                            <div className="absolute bottom-1.5 right-1.5 w-4 h-4 bg-green-500 rounded-full border-[3px] border-[#141622] shadow" title="Online" />
                        </div>

                        {/* Edit button */}
                        <div className="flex justify-end pt-3 w-full mb-3">
                            <button
                                id="open-edit-profile-btn"
                                onClick={() => setEditOpen(true)}
                                className="flex items-center gap-2 px-3.5 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-quantum-blue/40 rounded-lg text-sm font-medium text-black dark:text-gray-300 hover:text-white transition-all group/btn"
                            >
                                <Edit2 className="w-3.5 h-3.5 group-hover/btn:text-quantum-blue-light transition-colors" />
                                Edit Profile
                            </button>
                        </div>
                    </div>

                    {/* User Info */}
                    <div className="mt-2">
                        <div className="flex items-center gap-2 flex-wrap">
                            <h1 className="text-xl font-bold text-white">{displayUser.full_name}</h1>
                            <span className="inline-flex items-center gap-1 text-[11px] bg-quantum-blue/20 text-quantum-blue-light px-2 py-0.5 rounded border border-quantum-blue/30 font-mono font-medium">
                                <Sparkles className="w-3 h-3" />
                                Lv.{level}
                            </span>
                        </div>
                        <p className="text-black dark:text-gray-400 text-sm mt-0.5">@{displayUser.username}</p>
                    </div>

                    {/* Bio */}
                    <p className="mt-3 text-black dark:text-gray-300 text-sm leading-relaxed">
                        {bio}
                    </p>



                    {/* Metadata row */}
                    <div className="mt-4 flex flex-wrap gap-x-4 gap-y-2 text-xs text-black dark:text-gray-500">
                        <div className="flex items-center gap-1.5">
                            <Shield className="w-3.5 h-3.5 text-black dark:text-gray-500" />
                            <span>{badge}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <MapPin className="w-3.5 h-3.5 text-black dark:text-gray-500" />
                            <span>Quantum Realm</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <Calendar className="w-3.5 h-3.5 text-black dark:text-gray-500" />
                            <span>Joined {joinDate}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Edit Modal */}
            <EditProfileModal isOpen={editOpen} onClose={() => setEditOpen(false)} />
        </>
    );
}
