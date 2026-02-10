# Gamification Implementation Guide

## ✅ Implementation Status: CORE COMPLETE

This document provides a comprehensive guide to the QCanvas gamification system implementation.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Backend Implementation](#backend-implementation)
3. [Frontend Implementation](#frontend-implementation)
4. [Integration Guide](#integration-guide)
5. [Testing](#testing)
6. [Next Steps](#next-steps)

---

## Overview

The gamification system adds XP, levels, achievements, and leaderboards to QCanvas to enhance user engagement and learning.

### Core Features Implemented:
- ✅ XP and leveling system
- ✅ Activity tracking
- ✅ Streak system (daily engagement)
- ✅ First-time bonuses
- ✅ Real-time stats display
- ✅ Profile and achievements pages
- ✅ XP toast notifications
- ⏳ Achievements system (backend ready, needs frontend completion)
- ⏳ Leaderboard (API ready, needs frontend page)

---

## Backend Implementation

### 1. Database Models (`backend/app/models/gamification.py`)

#### UserGamification
Tracks user stats:
- `total_xp`: Total XP earned
- `level`: Current level
- `current_streak`: Consecutive days active
- `longest_streak`: Best streak record
- `last_activity_date`: Last activity timestamp

#### GamificationActivity
Logs all XP-earning events:
- `activity_type`: Type of activity
- `xp_awarded`: XP amount
- `metadata`: Additional context (JSON)
- `created_at`: Timestamp

#### Achievement
Defines available achievements:
- `name`, `description`, `category`
- `criteria`: Unlock requirements (JSON)
- `xp_reward`, `badge_icon`

#### UserAchievement
Tracks user achievement progress:
- `progress`: Current progress
- `unlocked_at`: Unlock timestamp

### 2. Gamification Service (`backend/app/services/gamification_service.py`)

#### Level Progression Formula
```python
xp_for_level(level) = 500 * (level - 1)
```

Example progression:
- Level 1 → 2: 500 XP (Total: 500)
- Level 2 → 3: 500 XP (Total: 1000)
- Level 5 → 6: 500 XP (Total: 2500)
- Level 10 → 11: 500 XP (Total: 5000)

#### XP Rewards
| Activity | Base XP | First Time Bonus | Total (First) |
|----------|---------|------------------|---------------|
| Simulation | 10 XP | +40 XP | 50 XP |
| Conversion | 30 XP | +30 XP | 60 XP |
| Circuit Saved | 5 XP | - | 5 XP |
| Project Created | 25 XP | - | 25 XP |

#### Key Methods
- `award_xp()`: Award XP and update stats
- `get_user_stats()`: Retrieve user gamification data
- `get_recent_activities()`: Fetch activity history
- `get_activity_summary()`: Get aggregated stats

### 3. API Endpoints (`backend/app/api/routes/gamification.py`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/gamification/health` | Health check | No |
| GET | `/api/gamification/stats` | Get current user stats | Yes |
| POST | `/api/gamification/activity` | Log activity & award XP | Yes |
| GET | `/api/gamification/stats/{user_id}` | Get public user stats | No |
| GET | `/api/gamification/activities/recent` | Get recent activities | Yes |
| GET | `/api/gamification/activities/summary` | Get activity summary | Yes |
| GET | `/api/gamification/leaderboard` | Get top users by XP | No |

### 4. Integration Points

#### Simulator (`backend/app/api/routes/simulator.py`)
- Awards XP after successful simulation
- Tracks: backend, shots, qubits
- First simulation bonus: 50 XP

#### Converter (`backend/app/api/routes/converter.py`)
- Awards XP after successful conversion
- Tracks: frameworks, qubits, gates
- First conversion bonus: 60 XP

---

## Frontend Implementation

### 1. Gamification Store (`frontend/lib/gamificationStore.ts`)

Zustand store with persistence:
```typescript
interface UserStats {
    total_xp: number;
    level: number;
    current_streak: number;
    longest_streak: number;
    progress_percentage: number;
    // ... more fields
}
```

**Key Features:**
- 5-minute caching
- Optimistic updates
- Auto-fetch on mount
- Helper functions for formatting

**Helper Functions:**
- `getLevelBadge(level)`: Get badge title
- `formatXP(xp)`: Format with commas
- `getActivityDisplayName(type)`: Human-readable names
- `getActivityIcon(type)`: Icon mapping

### 2. Components

#### ProfileDropdown (`components/ProfileDropdown.tsx`)
- ✅ Real-time level and XP display
- ✅ Progress bar
- ✅ Dynamic badge
- ✅ Links to profile and achievements

#### ProfileHeader (`components/profile/ProfileHeader.tsx`)
- ✅ User info with level badge
- ✅ Dynamic badge based on level
- ✅ Join date formatting

#### RecentActivityList (`components/profile/RecentActivityList.tsx`)
- ✅ Fetches from `/api/gamification/activities/recent`
- ✅ Displays activity type, XP, and timestamp
- ✅ Highlights first-time bonuses
- ✅ Relative time formatting

#### XPToast (`components/gamification/XPToast.tsx`)
- ✅ Three styles: regular, first-time, level-up
- ✅ Auto-dismiss (3s/5s)
- ✅ Smooth animations
- ✅ Progress bar

#### Profile Page (`app/profile/page.tsx`)
- ✅ Real stats: Total XP, Current Streak, Longest Streak
- ✅ Integrated components
- ✅ Responsive layout

### 3. XP Event System (`lib/XPEventProvider.tsx`)

Context provider for XP notifications:
```typescript
const { showXPGain } = useXPEvent();

// Show XP gain
showXPGain({
    xp_gained: 50,
    total_xp: 450,
    level: 5,
    level_up: true,
    // ... more fields
});
```

---

## Integration Guide

### Adding XP to New Features

#### Step 1: Backend Integration

In your API endpoint:
```python
from app.services.gamification_service import GamificationService

# After successful operation
if current_user:
    try:
        GamificationService.award_xp(
            db=db,
            user_id=str(current_user.id),
            activity_type='your_activity_type',
            metadata={'key': 'value'}
        )
    except Exception as e:
        print(f"Failed to award XP: {e}")
```

#### Step 2: Add Activity Type

1. Add to `XP_REWARDS` in `gamification_service.py`:
```python
XP_REWARDS = {
    'your_activity': 20,
    'first_your_activity': 50,  # Optional first-time bonus
}
```

2. Add display name in `gamificationStore.ts`:
```typescript
const names: Record<string, string> = {
    'your_activity': 'Your Activity Name',
};
```

3. Add icon mapping:
```typescript
const icons: Record<string, string> = {
    'your_activity': 'icon-name',
};
```

#### Step 3: Frontend Notification (Optional)

Wrap your app with `XPEventProvider` and use:
```typescript
const { showXPGain } = useXPEvent();

// After API call that awards XP
if (response.success) {
    showXPGain(response.xp_event);
}
```

---

## Testing

### Backend Testing

1. **Health Check**:
```bash
curl http://localhost:8000/api/gamification/health
```

2. **Get Stats** (requires auth):
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/gamification/stats
```

3. **Award XP**:
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"activity_type": "simulation_run", "metadata": {}}' \
     http://localhost:8000/api/gamification/activity
```

### Frontend Testing

1. **Login** to the application
2. **Check ProfileDropdown** - Should show real level and XP
3. **Run a simulation** - XP should be awarded
4. **Visit `/profile`** - Should show real stats
5. **Check recent activities** - Should list your actions

---

## Level Badge System

| Level Range | Badge Title |
|-------------|-------------|
| 50+ | Quantum Master |
| 40-49 | Quantum Expert |
| 30-39 | Quantum Specialist |
| 20-29 | Quantum Adept |
| 10-19 | Quantum Apprentice |
| 5-9 | Quantum Novice |
| 1-4 | Quantum Beginner |

---

## Next Steps

### Immediate (Required for Full Functionality)

1. **Wrap App with XPEventProvider**
   - Add to `app/layout.tsx` or main layout
   - Enable XP toast notifications

2. **Test XP Flow**
   - Run simulation → Check XP awarded
   - Run conversion → Check XP awarded
   - Verify toast appears (after provider added)

### Short-term Enhancements

1. **Achievements Backend Endpoint**
   - Create `/api/gamification/achievements`
   - Return achievement list with progress

2. **Update Achievements Page**
   - Fetch real achievements
   - Display actual progress
   - Remove mock data

3. **XP History Chart**
   - Create endpoint for historical XP data
   - Implement chart visualization

4. **Leaderboard Page**
   - Create `/leaderboard` page
   - Fetch from `/api/gamification/leaderboard`
   - Display top users

### Long-term Features

1. **Achievement Notifications**
   - Toast when achievement unlocked
   - Celebration animations

2. **Weekly Challenges**
   - Time-limited objectives
   - Bonus XP rewards

3. **Social Features**
   - Compare stats with friends
   - Share achievements

4. **Customization**
   - Profile badges
   - Avatar frames
   - Custom themes

---

## File Structure

```
backend/
├── app/
│   ├── models/
│   │   └── gamification.py          # Database models
│   ├── services/
│   │   └── gamification_service.py  # Business logic
│   └── api/
│       └── routes/
│           ├── gamification.py      # API endpoints
│           ├── simulator.py         # XP integration
│           └── converter.py         # XP integration

frontend/
├── lib/
│   ├── gamificationStore.ts         # State management
│   └── XPEventProvider.tsx          # Event system
├── components/
│   ├── ProfileDropdown.tsx          # Topbar dropdown
│   ├── gamification/
│   │   ├── XPToast.tsx             # Toast notifications
│   │   ├── AchievementCard.tsx     # Achievement display
│   │   └── StatsOverview.tsx       # Stats summary
│   └── profile/
│       ├── ProfileHeader.tsx        # Profile header
│       ├── RecentActivityList.tsx   # Activity feed
│       ├── XPHistoryChart.tsx       # XP chart
│       └── AchievementsPreview.tsx  # Achievement preview
└── app/
    ├── profile/
    │   └── page.tsx                 # Profile page
    └── achievements/
        └── page.tsx                 # Achievements page
```

---

## API Documentation

Full API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Support

For issues or questions:
1. Check this guide
2. Review API documentation
3. Check backend logs: `python backend/start.py`
4. Check frontend console: Browser DevTools

---

**Last Updated**: February 10, 2026
**Version**: 1.0.0
**Status**: Core Implementation Complete ✅
