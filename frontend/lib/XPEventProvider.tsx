/**
 * XP Event Provider
 * 
 * Provides a context for triggering XP toast notifications and 
 * achievement unlock toasts throughout the app.
 * Components can use this to show XP gains and achievement unlocks
 * after simulations, conversions, etc.
 */

"use client";

import { createContext, useContext, useState, ReactNode, useCallback, useRef } from 'react';
import XPToast from '@/components/gamification/XPToast';
import AchievementToast from '@/components/gamification/AchievementToast';
import { XPGainEvent, AchievementUnlock } from '@/lib/gamificationStore';

interface XPEventContextType {
    showXPGain: (event: XPGainEvent) => void;
}

const XPEventContext = createContext<XPEventContextType | undefined>(undefined);

export function XPEventProvider({ children }: { children: ReactNode }) {
    const [currentEvent, setCurrentEvent] = useState<XPGainEvent | null>(null);
    const [achievementQueue, setAchievementQueue] = useState<AchievementUnlock[]>([]);
    const [currentAchievement, setCurrentAchievement] = useState<AchievementUnlock | null>(null);
    const processingRef = useRef(false);

    const processAchievementQueue = useCallback(() => {
        if (processingRef.current) return;

        setAchievementQueue(prev => {
            if (prev.length === 0) return prev;
            processingRef.current = true;
            setCurrentAchievement(prev[0]);
            return prev.slice(1);
        });
    }, []);

    const showXPGain = useCallback((event: XPGainEvent) => {
        setCurrentEvent(event);

        // Queue achievement toasts if any
        if (event.new_achievements && event.new_achievements.length > 0) {
            setAchievementQueue(prev => [...prev, ...event.new_achievements!]);
            // Show first achievement after a small delay to let XP toast appear first
            setTimeout(() => {
                processAchievementQueue();
            }, 800);
        }
    }, [processAchievementQueue]);

    const handleXPClose = useCallback(() => {
        setCurrentEvent(null);
    }, []);

    const handleAchievementClose = useCallback(() => {
        setCurrentAchievement(null);
        processingRef.current = false;

        // Process next in queue after a delay
        setTimeout(() => {
            processAchievementQueue();
        }, 300);
    }, [processAchievementQueue]);

    return (
        <XPEventContext.Provider value={{ showXPGain }}>
            {children}
            <XPToast event={currentEvent} onClose={handleXPClose} />
            <AchievementToast achievement={currentAchievement} onClose={handleAchievementClose} />
        </XPEventContext.Provider>
    );
}

export function useXPEvent() {
    const context = useContext(XPEventContext);
    if (!context) {
        throw new Error('useXPEvent must be used within XPEventProvider');
    }
    return context;
}
