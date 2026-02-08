"use client";

import { Activity, Code, Award, Zap, GitCommit } from "lucide-react";
import { useState, useEffect } from "react";

// Mock Component
const RECENT_ACTIVITY = [
    {
        id: 1,
        type: "simulation",
        title: "Simulated 'Bell State' Circuit",
        time: "2 hours ago",
        xp: 50,
        icon: Activity,
        color: "text-blue-400",
        bgColor: "bg-blue-500/10"
    },
    {
        id: 2,
        type: "badge",
        title: "Unlocked 'Quantum Novice' Badge",
        time: "1 day ago",
        xp: 200,
        icon: Award,
        color: "text-yellow-400",
        bgColor: "bg-yellow-500/10"
    },
    {
        id: 3,
        type: "conversion",
        title: "Converted Qiskit to Cirq",
        time: "2 days ago",
        xp: 25,
        icon: Code,
        color: "text-purple-400",
        bgColor: "bg-purple-500/10"
    },
    {
        id: 4,
        type: "streak",
        title: "Reached 7-Day Streak",
        time: "3 days ago",
        xp: 150,
        icon: Zap,
        color: "text-orange-400",
        bgColor: "bg-orange-500/10"
    },
    {
        id: 5,
        type: "contribution",
        title: "Shared circuit with community",
        time: "4 days ago",
        xp: 30,
        icon: GitCommit,
        color: "text-green-400",
        bgColor: "bg-green-500/10"
    }
];

export default function RecentActivityList() {
    const [isDark, setIsDark] = useState(true); // Default to dark

    useEffect(() => {
        // Check initial theme
        const checkTheme = () => {
            setIsDark(document.documentElement.classList.contains('dark'));
        };

        checkTheme();

        // Watch for theme changes
        const observer = new MutationObserver(checkTheme);
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['class']
        });

        return () => observer.disconnect();
    }, []);

    return (
        <div
            className="rounded-xl p-6 shadow-sm dark:shadow-none"
            style={{
                backgroundColor: isDark ? 'rgba(0, 0, 0, 0.3)' : '#ffffff',
                backdropFilter: isDark ? 'blur(16px)' : 'none',
                border: isDark ? '1px solid rgba(255, 255, 255, 0.1)' : '1px solid #e5e7eb'
            }}
        >
            <h3
                className="font-bold text-lg mb-4 flex items-center gap-2"
                style={{ color: isDark ? '#ffffff' : '#111827' }}
            >
                <Activity
                    className="w-5 h-5"
                    style={{ color: isDark ? '#60a5fa' : '#1e3c72' }}
                />
                Recent Activity
            </h3>

            <div className="space-y-4">
                {RECENT_ACTIVITY.map((activity) => (
                    <div key={activity.id} className="flex items-center gap-4 group">
                        {/* Icon */}
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${activity.bgColor} ${activity.color}`}>
                            <activity.icon className="w-5 h-5" />
                        </div>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                            <h4
                                className="text-sm font-medium truncate group-hover:transition-colors"
                                style={{
                                    color: isDark ? '#e5e7eb' : '#374151'
                                }}
                            >
                                {activity.title}
                            </h4>
                            <p
                                className="text-xs"
                                style={{ color: isDark ? '#9ca3af' : '#6b7280' }}
                            >
                                {activity.time}
                            </p>
                        </div>

                        {/* XP Badge */}
                        <div
                            className="px-2 py-1 rounded text-xs font-bold border"
                            style={{
                                backgroundColor: isDark ? 'rgba(0, 0, 0, 0.2)' : '#f3f4f6',
                                color: isDark ? '#60a5fa' : '#1e3c72',
                                borderColor: isDark ? 'rgba(255, 255, 255, 0.05)' : '#e5e7eb'
                            }}
                        >
                            +{activity.xp} XP
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
