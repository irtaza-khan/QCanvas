"use client";

import { TrendingUp } from "lucide-react";

// Mock Data
const XP_HISTORY = [
    { day: "Mon", xp: 45 },
    { day: "Tue", xp: 120 },
    { day: "Wed", xp: 80 },
    { day: "Thu", xp: 15 },
    { day: "Fri", xp: 200 },
    { day: "Sat", xp: 90 },
    { day: "Sun", xp: 60 },
];

export default function XPHistoryChart() {
    const maxXP = Math.max(...XP_HISTORY.map(d => d.xp));

    return (
        <div className="bg-quantum-glass-dark border border-white/10 rounded-xl p-6">
            <div className="flex items-center justify-between mb-6">
                <h3 className="font-bold text-lg text-white flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-quantum-blue-light" />
                    Weekly Activity
                </h3>
                <span className="text-xs text-gray-400 bg-white/5 px-2 py-1 rounded">Last 7 Days</span>
            </div>

            <div className="flex items-end justify-between h-40 gap-2">
                {XP_HISTORY.map((item, index) => {
                    const heightPercent = (item.xp / maxXP) * 100;
                    return (
                        <div key={index} className="flex flex-col items-center gap-2 flex-1 group">
                            <div className="w-full relative flex items-end justify-center h-full">
                                {/* Tooltip */}
                                <div className="absolute -top-8 bg-gray-800 text-white text-[10px] py-1 px-2 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap z-10 border border-white/10 pointer-events-none">
                                    {item.xp} XP
                                </div>

                                {/* Bar */}
                                <div
                                    className="w-full max-w-[30px] bg-gradient-to-t from-quantum-blue to-quantum-blue-light/50 rounded-t-sm hover:from-quantum-blue-light hover:to-white/80 transition-all duration-300"
                                    style={{ height: `${heightPercent}%` }}
                                />
                            </div>
                            <span className="text-[10px] text-gray-500 font-medium uppercase">{item.day}</span>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
