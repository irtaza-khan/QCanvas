"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import {
    User,
    LogOut,
    Award,
    ChevronDown,
    Sparkles,
    CircuitBoard
} from "lucide-react";
import { useAuthStore } from "@/lib/authStore";

interface ProfileDropdownProps {
    onLogout: () => void;
}

// TODO: Replace with real data from useGamificationStore or API
const MOCK_STATS = {
    level: 5,
    badge: "Quantum Novice",
    xp: 450,
    nextLevelXp: 1000,
};

export default function ProfileDropdown({ onLogout }: ProfileDropdownProps) {
    const { user } = useAuthStore();
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    if (!user) return null;

    // Initials for avatar
    const initials = user.full_name
        ? user.full_name.split(" ").map((n) => n[0]).join("").toUpperCase().slice(0, 2)
        : user.icon_name || "U";

    // Calculate progress for mock progress bar
    const progressPercent = (MOCK_STATS.xp / MOCK_STATS.nextLevelXp) * 100;

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center space-x-2 p-1.5 rounded-lg hover:bg-quantum-blue-light/10 transition-all duration-200 group border border-transparent hover:border-quantum-blue-light/20"
            >
                {/* Avatar / Level Indicator */}
                <div className="relative">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-quantum-blue to-purple-600 flex items-center justify-center text-white text-xs font-bold shadow-lg ring-2 ring-white/10 group-hover:ring-quantum-blue-light/50 transition-all">
                        {initials}
                    </div>
                    <div className="absolute -bottom-1 -right-1 bg-editor-bg border border-quantum-blue-light rounded-full w-4 h-4 flex items-center justify-center">
                        <span className="text-[9px] font-bold text-quantum-blue-light">{MOCK_STATS.level}</span>
                    </div>
                </div>

                {/* Name & Badge (Hidden on mobile) */}
                <div className="hidden lg:flex flex-col items-start">
                    <span className="text-xs font-semibold text-editor-text group-hover:text-white transition-colors">
                        {user.username}
                    </span>
                    <span className="text-[10px] text-quantum-blue-light flex items-center gap-1">
                        <Award className="w-3 h-3" />
                        {MOCK_STATS.badge}
                    </span>
                </div>

                <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <div className="absolute right-0 top-full mt-2 w-64 quantum-glass-dark rounded-xl shadow-2xl border border-white/10 backdrop-blur-xl animate-fade-in z-50 overflow-hidden">
                    {/* Header */}
                    <div className="p-4 border-b border-white/10 bg-gradient-to-br from-quantum-blue/10 to-transparent">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-quantum-blue to-purple-600 flex items-center justify-center text-white text-lg font-bold shadow-inner">
                                {initials}
                            </div>
                            <div className="flex-1 overflow-hidden">
                                <h3 className="font-bold text-white truncate">{user.full_name}</h3>
                                <p className="text-xs text-gray-400 truncate">{user.email}</p>
                            </div>
                        </div>

                        {/* Gamification Progress */}
                        {/* TODO: Connect to real backend data */}
                        <div className="space-y-1.5">
                            <div className="flex justify-between text-xs">
                                <span className="text-gray-300 font-medium">Level {MOCK_STATS.level}</span>
                                <span className="text-quantum-blue-light">{MOCK_STATS.xp} / {MOCK_STATS.nextLevelXp} XP</span>
                            </div>
                            <div className="h-1.5 bg-editor-bg rounded-full overflow-hidden border border-white/5">
                                <div
                                    className="h-full bg-gradient-to-r from-quantum-blue to-purple-500 transition-all duration-500"
                                    style={{ width: `${progressPercent}%` }}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Menu Items */}
                    <div className="p-2 space-y-1">
                        <Link
                            href="/profile"
                            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-300 hover:bg-white/5 hover:text-white transition-colors group"
                            onClick={() => setIsOpen(false)}
                        >
                            <User className="w-4 h-4 text-gray-400 group-hover:text-quantum-blue-light" />
                            <span>View Profile</span>
                            {/* Badge placeholder */}
                            <span className="ml-auto text-[10px] bg-white/5 px-1.5 py-0.5 rounded text-gray-400">Soon</span>
                        </Link>

                        <Link
                            href="/achievements"
                            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-gray-300 hover:bg-white/5 hover:text-white transition-colors group"
                            onClick={() => setIsOpen(false)}
                        >
                            <Award className="w-4 h-4 text-gray-400 group-hover:text-yellow-400" />
                            <span>Achievements</span>
                        </Link>

                        <div className="h-px bg-white/10 my-1 mx-2"></div>

                        <button
                            onClick={() => {
                                onLogout();
                                setIsOpen(false);
                            }}
                            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors group"
                        >
                            <LogOut className="w-4 h-4 group-hover:scale-110 transition-transform" />
                            <span>Logout</span>
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
