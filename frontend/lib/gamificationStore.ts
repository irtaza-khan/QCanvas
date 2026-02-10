/**
 * Gamification Store
 * 
 * Manages gamification state including XP, levels, achievements, and activities.
 * Provides methods to fetch and update gamification data from the backend.
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { gamificationApi } from '@/lib/api'; // Import gamificationApi

// ============================================================================
// TYPES
// ============================================================================

export interface UserStats {
    user_id: string;
    total_xp: number;
    level: number;
    current_streak: number;
    longest_streak: number;
    last_activity_date: string | null;
    xp_to_next_level: number;
    xp_current_level: number;
    xp_next_level: number;
    progress_percentage: number;
}

export interface Activity {
    id: string;
    activity_type: string;
    xp_awarded: number;
    metadata: Record<string, any>;
    created_at: string;
}

export interface XPGainEvent {
    xp_gained: number;
    total_xp: number;
    level: number;
    old_level: number;
    level_up: boolean;
    xp_to_next_level: number;
    is_first_time: boolean;
    current_streak: number;
    message?: string;
}

interface GamificationState {
    // State
    stats: UserStats | null;
    recentActivities: Activity[];
    isLoading: boolean;
    error: string | null;
    lastFetched: number | null;

    // Actions
    fetchStats: (token: string, forceRefresh?: boolean) => Promise<void>;
    fetchRecentActivities: (token: string, limit?: number) => Promise<void>;
    updateStatsFromXPGain: (xpGainEvent: XPGainEvent) => void;
    clearGamification: () => void;

    // Helpers
    shouldRefetch: () => boolean;
}

// Cache duration: 30 seconds (reduced for better real-time updates)
const CACHE_DURATION = 30 * 1000;

// ============================================================================
// STORE
// ============================================================================

export const useGamificationStore = create<GamificationState>()(
    persist(
        (set, get) => ({
            // Initial state
            stats: null,
            recentActivities: [],
            isLoading: false,
            error: null,
            lastFetched: null,

            // Fetch user stats from backend
            fetchStats: async (token: string, forceRefresh: boolean = false) => {
                // Check if we should refetch
                if (!forceRefresh && !get().shouldRefetch() && get().stats) {
                    return;
                }

                set({ isLoading: true, error: null });

                try {
                    const response = await gamificationApi.getStats(token);

                    if (response.success && response.data?.stats) {
                        set({
                            stats: response.data.stats,
                            isLoading: false,
                            lastFetched: Date.now(),
                        });
                    } else {
                        // If no stats yet, just clear loading
                        if (response.success && response.data?.success && !response.data?.stats) {
                            set({ isLoading: false, lastFetched: Date.now() });
                            return;
                        }

                        throw new Error(response.error || response.data?.error || 'Failed to fetch gamification stats');
                    }
                } catch (error) {
                    console.error('Error fetching gamification stats:', error);
                    set({
                        error: error instanceof Error ? error.message : 'Unknown error',
                        isLoading: false,
                    });
                }
            },

            // Fetch recent activities
            fetchRecentActivities: async (token: string, limit = 10) => {
                try {
                    const response = await gamificationApi.getRecentActivities(token, limit);

                    if (response.success && response.data?.activities) {
                        set({ recentActivities: response.data.activities });
                    } else {
                        console.warn('Failed to fetch recent activities:', response.error);
                    }
                } catch (error) {
                    console.error('Error fetching recent activities:', error);
                }
            },

            // Update stats from XP gain event (optimistic update)
            updateStatsFromXPGain: (xpGainEvent: XPGainEvent) => {
                const currentStats = get().stats;

                if (!currentStats) return;

                // Update stats optimistically
                set({
                    stats: {
                        ...currentStats,
                        total_xp: xpGainEvent.total_xp,
                        level: xpGainEvent.level,
                        current_streak: xpGainEvent.current_streak,
                        xp_to_next_level: xpGainEvent.xp_to_next_level,
                        // Recalculate progress percentage
                        progress_percentage: Math.round(
                            ((xpGainEvent.total_xp - currentStats.xp_current_level) /
                                (currentStats.xp_next_level - currentStats.xp_current_level)) *
                            100
                        ),
                    },
                });
            },

            // Clear gamification data (on logout)
            clearGamification: () => {
                set({
                    stats: null,
                    recentActivities: [],
                    isLoading: false,
                    error: null,
                    lastFetched: null,
                });
            },

            // Check if we should refetch data
            shouldRefetch: () => {
                const lastFetched = get().lastFetched;
                if (!lastFetched) return true;
                return Date.now() - lastFetched > CACHE_DURATION;
            },
        }),
        {
            name: 'gamification-storage',
            partialize: (state) => ({
                stats: state.stats,
                recentActivities: state.recentActivities,
                lastFetched: state.lastFetched,
            }),
        }
    )
);

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

/**
 * Get level badge/title based on level
 */
export function getLevelBadge(level: number): string {
    if (level >= 50) return 'Quantum Master';
    if (level >= 40) return 'Quantum Expert';
    if (level >= 30) return 'Quantum Specialist';
    if (level >= 20) return 'Quantum Adept';
    if (level >= 10) return 'Quantum Apprentice';
    if (level >= 5) return 'Quantum Novice';
    return 'Quantum Beginner';
}

/**
 * Format XP number with commas
 */
export function formatXP(xp: number): string {
    return xp.toLocaleString();
}

/**
 * Get activity type display name
 */
export function getActivityDisplayName(activityType: string): string {
    const names: Record<string, string> = {
        'simulation_run': 'Simulation Run',
        'first_simulation': 'First Simulation',
        'conversion': 'Circuit Conversion',
        'first_conversion': 'First Conversion',
        'circuit_saved': 'Circuit Saved',
        'project_created': 'Project Created',
        'tutorial_completed': 'Tutorial Completed',
        'challenge_completed': 'Challenge Completed',
        'circuit_shared': 'Circuit Shared',
        'helped_user': 'Helped User',
    };
    return names[activityType] || activityType;
}

/**
 * Get activity icon name for Lucide icons
 */
export function getActivityIcon(activityType: string): string {
    const icons: Record<string, string> = {
        'simulation_run': 'play',
        'first_simulation': 'rocket',
        'conversion': 'repeat',
        'first_conversion': 'sparkles',
        'circuit_saved': 'save',
        'project_created': 'folder-plus',
        'tutorial_completed': 'book-check',
        'challenge_completed': 'trophy',
        'circuit_shared': 'share-2',
        'helped_user': 'users',
    };
    return icons[activityType] || 'zap';
}
