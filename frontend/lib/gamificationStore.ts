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
    new_achievements?: AchievementUnlock[];
    message?: string;
}

export interface AchievementData {
    id: string;
    name: string;
    description: string;
    category: string;
    rarity: string;
    xp_reward: number;
    icon_name: string;
    is_hidden: boolean;
    is_unlocked: boolean;
    progress: number;
    target: number;
    unlocked_at: string | null;
}

export interface AchievementUnlock {
    id: string;
    name: string;
    description: string;
    category: string;
    rarity: string;
    xp_reward: number;
    icon_name: string;
    unlocked_at: string;
}

interface GamificationState {
    // XP & Level
    stats: UserStats | null;
    recentActivities: Activity[];
    isLoading: boolean;
    error: string | null;
    lastFetched: number | null;

    // Achievements
    achievements: AchievementData[];
    achievementsLoading: boolean;
    achievementsLastFetched: number | null;

    // Actions
    fetchStats: (token: string, forceRefresh?: boolean) => Promise<void>;
    fetchRecentActivities: (token: string, limit?: number) => Promise<void>;
    fetchAchievements: (token: string, forceRefresh?: boolean) => Promise<void>;
    updateStatsFromXPGain: (xpGainEvent: XPGainEvent) => void;
    clearGamification: () => void;
    shouldRefetch: () => boolean;
    shouldRefetchAchievements: () => boolean;
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

            // Achievements
            achievements: [],
            achievementsLoading: false,
            achievementsLastFetched: null,

            // Fetch user stats from backend
            fetchStats: async (token: string, forceRefresh: boolean = false) => {
                const state = get();

                // Skip if loading or cache is fresh
                if (state.isLoading) return;
                if (!forceRefresh && !state.shouldRefetch()) return;

                set({ isLoading: true, error: null });

                try {
                    const response = await gamificationApi.getStats(token);

                    if (response.success && response.data?.stats) {
                        set({
                            stats: response.data.stats as UserStats,
                            isLoading: false,
                            lastFetched: Date.now(),
                        });
                    } else {
                        throw new Error(response.error || response.data?.error || 'Failed to fetch gamification stats');
                    }
                } catch (error) {
                    console.error('Error fetching gamification stats:', error);
                    set({ isLoading: false, error: String(error) });
                }
            },

            // Fetch recent activities
            fetchRecentActivities: async (token: string, limit = 10) => {
                try {
                    const response = await gamificationApi.getRecentActivities(token, limit);
                    if (response.success && response.data?.activities) {
                        set({ recentActivities: response.data.activities as Activity[] });
                    }
                } catch (error) {
                    console.error('Error fetching recent activities:', error);
                }
            },

            // Fetch achievements from backend
            fetchAchievements: async (token: string, forceRefresh: boolean = false) => {
                const state = get();

                if (state.achievementsLoading) return;
                if (!forceRefresh && !state.shouldRefetchAchievements()) return;

                set({ achievementsLoading: true });

                try {
                    const response = await gamificationApi.getAchievements(token);

                    if (response.success && response.data?.achievements) {
                        set({
                            achievements: response.data.achievements as AchievementData[],
                            achievementsLoading: false,
                            achievementsLastFetched: Date.now(),
                        });
                    } else {
                        throw new Error(response.error || 'Failed to fetch achievements');
                    }
                } catch (error) {
                    console.error('Error fetching achievements:', error);
                    set({ achievementsLoading: false });
                }
            },

            // Update stats from XP gain event (optimistic update)
            updateStatsFromXPGain: (xpGainEvent: XPGainEvent) => {
                const state = get();
                if (state.stats) {
                    set({
                        stats: {
                            ...state.stats,
                            total_xp: xpGainEvent.total_xp,
                            level: xpGainEvent.level,
                            xp_to_next_level: xpGainEvent.xp_to_next_level,
                            current_streak: xpGainEvent.current_streak,
                        },
                        // Force refetch on next access to get accurate data
                        lastFetched: null,
                    });
                }

                // If achievements were unlocked, force refetch achievements
                if (xpGainEvent.new_achievements && xpGainEvent.new_achievements.length > 0) {
                    set({ achievementsLastFetched: null });
                }
            },

            // Clear gamification data (on logout)
            clearGamification: () => {
                set({
                    stats: null,
                    recentActivities: [],
                    achievements: [],
                    isLoading: false,
                    error: null,
                    lastFetched: null,
                    achievementsLoading: false,
                    achievementsLastFetched: null,
                });
            },

            // Check if we should refetch data
            shouldRefetch: () => {
                const state = get();
                if (!state.lastFetched) return true;
                return Date.now() - state.lastFetched > CACHE_DURATION;
            },

            // Check if we should refetch achievements
            shouldRefetchAchievements: () => {
                const state = get();
                if (!state.achievementsLastFetched) return true;
                return Date.now() - state.achievementsLastFetched > CACHE_DURATION;
            },
        }),
        {
            name: 'gamification-storage',
            partialize: (state) => ({
                stats: state.stats,
                achievements: state.achievements,
                lastFetched: state.lastFetched,
                achievementsLastFetched: state.achievementsLastFetched,
            }),
        }
    )
);

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

// Get level badge/title based on level
export function getLevelBadge(level: number): string {
    if (level >= 51) return 'Quantum Guru';
    if (level >= 41) return 'Quantum Master';
    if (level >= 31) return 'Quantum Engineer';
    if (level >= 21) return 'Algorithm Designer';
    if (level >= 11) return 'Quantum Explorer';
    if (level >= 6) return 'Circuit Builder';
    return 'Quantum Novice';
}

// Format XP number with commas
export function formatXP(xp: number): string {
    return xp.toLocaleString();
}

// Get activity type display name
export function getActivityDisplayName(activityType: string): string {
    const displayNames: Record<string, string> = {
        'simulation_run': 'Simulation Run',
        'conversion': 'Circuit Conversion',
        'circuit_saved': 'Circuit Saved',
        'project_created': 'Project Created',
        'tutorial_completed': 'Tutorial Completed',
        'challenge_completed': 'Challenge Completed',
        'circuit_shared': 'Circuit Shared',
        'helped_user': 'Helped User',
        'achievement_unlocked': 'Achievement Unlocked',
    };
    return displayNames[activityType] || activityType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Get activity icon name for Lucide icons
export function getActivityIcon(activityType: string): string {
    const iconMap: Record<string, string> = {
        'simulation_run': 'Play',
        'conversion': 'ArrowLeftRight',
        'circuit_saved': 'Save',
        'project_created': 'FolderPlus',
        'tutorial_completed': 'GraduationCap',
        'challenge_completed': 'Target',
        'circuit_shared': 'Share2',
        'helped_user': 'HandHelping',
        'achievement_unlocked': 'Trophy',
    };
    return iconMap[activityType] || 'Activity';
}

// Get category display name
export function getCategoryDisplayName(category: string): string {
    const displayNames: Record<string, string> = {
        'getting_started': 'Getting Started',
        'algorithms': 'Algorithms',
        'mastery': 'Mastery',
        'learning': 'Learning',
        'streak': 'Streak',
        'social': 'Social',
        'specialization': 'Specialization',
        'progression': 'Progression',
        'hidden': 'Hidden',
    };
    return displayNames[category] || category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Get rarity color class
export function getRarityColor(rarity: string): string {
    const colors: Record<string, string> = {
        'common': 'text-gray-500 dark:text-gray-400',
        'uncommon': 'text-green-600 dark:text-green-400',
        'rare': 'text-blue-600 dark:text-blue-400',
        'epic': 'text-purple-600 dark:text-purple-400',
        'legendary': 'text-yellow-500 dark:text-yellow-400',
    };
    return colors[rarity] || colors['common'];
}
