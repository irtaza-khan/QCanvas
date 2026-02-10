/**
 * XP Event Provider
 * 
 * Provides a context for triggering XP toast notifications throughout the app.
 * Components can use this to show XP gains after simulations, conversions, etc.
 */

"use client";

import { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import XPToast from '@/components/gamification/XPToast';
import { XPGainEvent } from '@/lib/gamificationStore';

interface XPEventContextType {
    showXPGain: (event: XPGainEvent) => void;
}

const XPEventContext = createContext<XPEventContextType | undefined>(undefined);

export function XPEventProvider({ children }: { children: ReactNode }) {
    const [currentEvent, setCurrentEvent] = useState<XPGainEvent | null>(null);

    const showXPGain = useCallback((event: XPGainEvent) => {
        setCurrentEvent(event);
    }, []);

    const handleClose = useCallback(() => {
        setCurrentEvent(null);
    }, []);

    return (
        <XPEventContext.Provider value={{ showXPGain }}>
            {children}
            <XPToast event={currentEvent} onClose={handleClose} />
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
