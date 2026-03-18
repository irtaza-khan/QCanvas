/**
 * XP Toast Component
 * 
 * Displays animated toast notifications when users earn XP or level up.
 */

"use client";

import { useEffect, useState } from 'react';
import { Zap, TrendingUp, Award } from '@/components/Icons';
import { Sparkles } from 'lucide-react';
import { XPGainEvent } from '@/lib/gamificationStore';

interface XPToastProps {
    event: XPGainEvent | null;
    onClose: () => void;
}

export default function XPToast({ event, onClose }: XPToastProps) {
    const [isVisible, setIsVisible] = useState(false);
    const [isExiting, setIsExiting] = useState(false);

    useEffect(() => {
        if (event) {
            setIsVisible(true);
            setIsExiting(false);

            // Auto-hide after duration
            const duration = event.level_up ? 5000 : 3000;
            const timer = setTimeout(() => {
                handleClose();
            }, duration);

            return () => clearTimeout(timer);
        }
    }, [event]);

    const handleClose = () => {
        setIsExiting(true);
        setTimeout(() => {
            setIsVisible(false);
            onClose();
        }, 300);
    };

    if (!event || !isVisible) return null;

    const isLevelUp = event.level_up;
    const isFirstTime = event.is_first_time;

    return (
        <div
            className={`fixed bottom-6 right-6 z-[9999] transition-all duration-300 ${isExiting ? 'opacity-0 translate-y-4' : 'opacity-100 translate-y-0'
                }`}
            onClick={handleClose}
        >
            {isLevelUp ? (
                // Level Up Toast
                <div className="relative overflow-hidden rounded-2xl border-2 border-yellow-400/50 bg-gradient-to-br from-yellow-500/20 via-purple-500/20 to-blue-500/20 backdrop-blur-xl shadow-2xl shadow-yellow-500/20 min-w-[320px] max-w-md">
                    {/* Animated background */}
                    <div className="absolute inset-0 bg-gradient-to-r from-yellow-400/10 via-purple-400/10 to-blue-400/10 animate-pulse" />

                    {/* Sparkle effects */}
                    <div className="absolute top-2 right-2 animate-bounce">
                        <Sparkles className="w-4 h-4 text-yellow-400" />
                    </div>
                    <div className="absolute bottom-2 left-2 animate-bounce delay-150">
                        <Sparkles className="w-3 h-3 text-purple-400" />
                    </div>

                    <div className="relative p-5">
                        <div className="flex items-start gap-4">
                            {/* Icon */}
                            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-yellow-400 to-orange-500 flex items-center justify-center shadow-lg shadow-yellow-500/50 animate-bounce">
                                <TrendingUp className="w-7 h-7 text-white" />
                            </div>

                            {/* Content */}
                            <div className="flex-1">
                                <h3 className="text-xl font-bold text-white mb-1 flex items-center gap-2">
                                    Level Up! 🎉
                                </h3>
                                <p className="text-yellow-200 text-sm mb-2">
                                    You've reached <span className="font-bold text-yellow-400">Level {event.level}</span>!
                                </p>
                                <div className="flex items-center gap-2 text-xs text-white/80">
                                    <Zap className="w-3 h-3" />
                                    <span>+{event.xp_gained} XP earned</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                // Regular XP Toast
                <div className={`relative overflow-hidden rounded-xl border backdrop-blur-xl shadow-xl min-w-[280px] max-w-sm ${isFirstTime
                        ? 'border-purple-400/50 bg-gradient-to-br from-purple-500/20 to-blue-500/20 shadow-purple-500/20'
                        : 'border-blue-400/30 bg-gradient-to-br from-blue-500/10 to-cyan-500/10 shadow-blue-500/10'
                    }`}>
                    {/* Animated background */}
                    <div className={`absolute inset-0 animate-pulse ${isFirstTime ? 'bg-gradient-to-r from-purple-400/5 to-blue-400/5' : 'bg-gradient-to-r from-blue-400/5 to-cyan-400/5'
                        }`} />

                    {isFirstTime && (
                        <div className="absolute top-2 right-2">
                            <Sparkles className="w-4 h-4 text-purple-400 animate-pulse" />
                        </div>
                    )}

                    <div className="relative p-4">
                        <div className="flex items-center gap-3">
                            {/* Icon */}
                            <div className={`w-10 h-10 rounded-lg flex items-center justify-center shadow-lg ${isFirstTime
                                    ? 'bg-gradient-to-br from-purple-500 to-blue-500 shadow-purple-500/50'
                                    : 'bg-gradient-to-br from-blue-500 to-cyan-500 shadow-blue-500/30'
                                }`}>
                                {isFirstTime ? (
                                    <Award className="w-5 h-5 text-white" />
                                ) : (
                                    <Zap className="w-5 h-5 text-white" />
                                )}
                            </div>

                            {/* Content */}
                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                    <span className={`text-lg font-bold ${isFirstTime ? 'text-purple-300' : 'text-blue-300'
                                        }`}>
                                        +{event.xp_gained} XP
                                    </span>
                                    {isFirstTime && (
                                        <span className="text-[10px] bg-purple-500/30 text-purple-200 px-1.5 py-0.5 rounded-full font-medium">
                                            FIRST TIME!
                                        </span>
                                    )}
                                </div>
                                <p className="text-xs text-white/70">
                                    {event.message || `${event.xp_to_next_level} XP to next level`}
                                </p>
                            </div>

                            {/* Level badge */}
                            <div className="text-right">
                                <div className="text-[10px] text-white/50 mb-0.5">Level</div>
                                <div className="text-lg font-bold text-white">{event.level}</div>
                            </div>
                        </div>

                        {/* Progress bar */}
                        <div className="mt-3 h-1 bg-white/10 rounded-full overflow-hidden">
                            <div
                                className={`h-full transition-all duration-500 ${isFirstTime
                                        ? 'bg-gradient-to-r from-purple-500 to-blue-500'
                                        : 'bg-gradient-to-r from-blue-500 to-cyan-500'
                                    }`}
                                style={{
                                    width: `${Math.min(100, ((event.total_xp - (event.total_xp - event.xp_gained)) / event.xp_to_next_level) * 100)}%`
                                }}
                            />
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
