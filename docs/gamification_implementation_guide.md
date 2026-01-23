# QCanvas Gamification - Simple Implementation Guide

> **Start Date:** January 23, 2026  
> **Approach:** Build incrementally, test each step, ship early and often

---

## 🎯 Implementation Philosophy

**Start Simple. Ship Fast. Iterate.**

Instead of building everything at once, we'll implement gamification in small, testable increments:

1. ✅ **Each step should work independently**
2. ✅ **Ship to production after each major step**
3. ✅ **Get user feedback early**
4. ✅ **Iterate based on real usage data**

---

## 📅 4-Week Implementation Plan

### **Week 1: Core XP & Levels**
Get basic point tracking working so users see immediate value.

### **Week 2: Achievements & Badges**
Add recognition and milestone celebrations.

### **Week 3: Leaderboards**
Enable competition and ranking.

### **Week 4: Polish & Launch**
Bug fixes, performance, and public launch.

---

## 🚀 Step-by-Step Implementation

### **STEP 1: Database Models** (Day 1)

#### 1.1 Create Gamification Models File

**File:** `backend/app/models/gamification.py`

```python
"""
Gamification database models for QCanvas.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.config.database import Base


class UserGamification(Base):
    """Track user gamification stats."""
    __tablename__ = "user_gamification"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    total_xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(Date, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = relationship("User", backref="gamification_stats")


class GamificationActivity(Base):
    """Log all XP-earning activities."""
    __tablename__ = "gamification_activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # 'simulation', 'conversion', etc.
    xp_awarded = Column(Integer, nullable=False)
    metadata = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    # Relationship
    user = relationship("User", backref="gamification_activities")


class Achievement(Base):
    """Achievement catalog."""
    __tablename__ = "achievements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)
    criteria = Column(JSON, nullable=False)  # Unlock conditions
    reward_xp = Column(Integer, default=0)
    rarity = Column(String(20), default='common')  # common, uncommon, rare, epic, legendary
    icon_name = Column(String(50), nullable=True)
    is_hidden = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)


class UserAchievement(Base):
    """Track unlocked achievements per user."""
    __tablename__ = "user_achievements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    achievement_id = Column(UUID(as_uuid=True), ForeignKey("achievements.id"), nullable=False)
    progress = Column(JSON, nullable=True)  # For multi-step achievements
    unlocked_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="achievements")
    achievement = relationship("Achievement")
```

#### 1.2 Create Database Migration

**Command:**
```bash
cd backend
alembic revision -m "add_gamification_tables"
```

**Edit the generated migration file** (in `backend/alembic/versions/`):

```python
"""add_gamification_tables

Revision ID: <auto_generated>
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # UserGamification table
    op.create_table(
        'user_gamification',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('total_xp', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('current_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('longest_streak', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_activity_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )
    
    # GamificationActivity table
    op.create_table(
        'gamification_activities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('activity_type', sa.String(50), nullable=False),
        sa.Column('xp_awarded', sa.Integer(), nullable=False),
        sa.Column('metadata', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_activity_type', 'gamification_activities', ['activity_type'])
    op.create_index('idx_activity_created', 'gamification_activities', ['created_at'])
    
    # Achievement table
    op.create_table(
        'achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('criteria', postgresql.JSON(), nullable=False),
        sa.Column('reward_xp', sa.Integer(), server_default='0'),
        sa.Column('rarity', sa.String(20), server_default='common'),
        sa.Column('icon_name', sa.String(50), nullable=True),
        sa.Column('is_hidden', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # UserAchievement table
    op.create_table(
        'user_achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('achievement_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('progress', postgresql.JSON(), nullable=True),
        sa.Column('unlocked_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_achievement', 'user_achievements', ['user_id', 'achievement_id'], unique=True)


def downgrade():
    op.drop_table('user_achievements')
    op.drop_table('achievements')
    op.drop_table('gamification_activities')
    op.drop_table('user_gamification')
```

#### 1.3 Run Migration

```bash
alembic upgrade head
```

**✅ Test:** Verify tables created in PostgreSQL.

---

### **STEP 2: XP Service** (Day 2)

#### 2.1 Create Gamification Service

**File:** `backend/app/services/gamification_service.py`

```python
"""
Gamification service for XP tracking and level calculation.
"""
from sqlalchemy.orm import Session
from app.models.gamification import UserGamification, GamificationActivity
from datetime import datetime, date
import math


# XP required for each level (exponential growth)
def xp_for_level(level: int) -> int:
    """Calculate total XP required to reach a level."""
    if level <= 1:
        return 0
    # Formula: 100 * level^1.5
    return int(100 * math.pow(level, 1.5))


def calculate_level(total_xp: int) -> int:
    """Calculate level based on total XP."""
    level = 1
    while xp_for_level(level + 1) <= total_xp:
        level += 1
    return level


# XP reward mapping
XP_REWARDS = {
    'simulation_run': 10,
    'first_simulation': 50,
    'conversion': 30,
    'first_conversion': 60,
    'circuit_saved': 5,
    'project_created': 25,
}


class GamificationService:
    """Service for managing gamification features."""
    
    @staticmethod
    def get_or_create_stats(db: Session, user_id: str) -> UserGamification:
        """Get or create gamification stats for a user."""
        stats = db.query(UserGamification).filter(
            UserGamification.user_id == user_id
        ).first()
        
        if not stats:
            stats = UserGamification(user_id=user_id)
            db.add(stats)
            db.commit()
            db.refresh(stats)
        
        return stats
    
    @staticmethod
    def award_xp(
        db: Session,
        user_id: str,
        activity_type: str,
        xp_amount: int = None,
        metadata: dict = None
    ) -> dict:
        """
        Award XP to a user for an activity.
        Returns dict with xp_gained, new_total, level_up info.
        """
        # Get or create user stats
        stats = GamificationService.get_or_create_stats(db, user_id)
        
        # Determine XP amount
        if xp_amount is None:
            xp_amount = XP_REWARDS.get(activity_type, 0)
        
        if xp_amount <= 0:
            return {
                'xp_gained': 0,
                'total_xp': stats.total_xp,
                'level': stats.level,
                'level_up': False
            }
        
        # Check for first-time bonus
        is_first_time = db.query(GamificationActivity).filter(
            GamificationActivity.user_id == user_id,
            GamificationActivity.activity_type == activity_type
        ).count() == 0
        
        if is_first_time and f'first_{activity_type}' in XP_REWARDS:
            xp_amount = XP_REWARDS[f'first_{activity_type}']
        
        # Record activity
        activity = GamificationActivity(
            user_id=user_id,
            activity_type=activity_type,
            xp_awarded=xp_amount,
            metadata=metadata or {}
        )
        db.add(activity)
        
        # Update stats
        old_level = stats.level
        stats.total_xp += xp_amount
        stats.level = calculate_level(stats.total_xp)
        stats.last_activity_date = date.today()
        stats.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(stats)
        
        level_up = stats.level > old_level
        
        return {
            'xp_gained': xp_amount,
            'total_xp': stats.total_xp,
            'level': stats.level,
            'old_level': old_level,
            'level_up': level_up,
            'xp_to_next_level': xp_for_level(stats.level + 1) - stats.total_xp
        }
    
    @staticmethod
    def get_user_stats(db: Session, user_id: str) -> dict:
        """Get gamification stats for a user."""
        stats = GamificationService.get_or_create_stats(db, user_id)
        
        return {
            'user_id': str(stats.user_id),
            'total_xp': stats.total_xp,
            'level': stats.level,
            'current_streak': stats.current_streak,
            'longest_streak': stats.longest_streak,
            'xp_to_next_level': xp_for_level(stats.level + 1) - stats.total_xp,
            'xp_current_level': xp_for_level(stats.level),
            'xp_next_level': xp_for_level(stats.level + 1),
        }
```

**✅ Test:** Write unit test for XP calculation.

---

### **STEP 3: API Endpoints** (Day 3)

#### 3.1 Create Gamification Routes

**File:** `backend/app/api/routes/gamification.py`

```python
"""
Gamification API routes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.config.database import get_db
from app.services.gamification_service import GamificationService
from app.api.dependencies import get_current_user
from app.models.database_models import User

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


@router.get("/stats")
async def get_gamification_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current user's gamification stats."""
    stats = GamificationService.get_user_stats(db, str(current_user.id))
    return {
        "success": True,
        "stats": stats
    }


@router.post("/activity")
async def log_activity(
    activity_type: str,
    metadata: Dict[str, Any] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Log an activity and award XP.
    This endpoint is called by other services (simulation, conversion, etc.)
    """
    result = GamificationService.award_xp(
        db=db,
        user_id=str(current_user.id),
        activity_type=activity_type,
        metadata=metadata
    )
    
    return {
        "success": True,
        **result
    }


@router.get("/stats/{user_id}")
async def get_user_stats(
    user_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get any user's public gamification stats (for leaderboards)."""
    stats = GamificationService.get_user_stats(db, user_id)
    return {
        "success": True,
        "stats": stats
    }
```

#### 3.2 Register Router

**File:** `backend/app/main.py` (or wherever routes are registered)

Add:
```python
from app.api.routes import gamification

app.include_router(gamification.router)
```

**✅ Test:** Call API endpoints with Postman/curl.

---

### **STEP 4: Integrate XP Tracking** (Day 4)

#### 4.1 Add XP Tracking to Existing Endpoints

**Modify:** `backend/app/api/routes/simulator.py`

```python
from app.services.gamification_service import GamificationService

# In the simulation endpoint, after successful simulation:
@router.post("/execute")
async def execute_simulation(...):
    # ... existing simulation code ...
    
    if result["success"]:
        # Award XP for simulation
        GamificationService.award_xp(
            db=db,
            user_id=str(current_user.id),
            activity_type="simulation_run",
            metadata={
                "backend": backend,
                "shots": shots,
                "qubits": result.get("num_qubits", 0)
            }
        )
    
    return result
```

**Modify:** `backend/app/api/routes/converter.py`

```python
from app.services.gamification_service import GamificationService

# In the conversion endpoint:
@router.post("/convert")
async def convert_circuit(...):
    # ... existing conversion code ...
    
    if result["success"]:
        # Award XP for conversion
        GamificationService.award_xp(
            db=db,
            user_id=str(current_user.id),
            activity_type="conversion",
            metadata={
                "source_framework": source_framework,
                "target_framework": "qasm"
            }
        )
    
    return result
```

**✅ Test:** Run simulation/conversion and verify XP is awarded.

---

### **STEP 5: Frontend Components** (Day 5-6)

#### 5.1 Create XP Display Component

**File:** `frontend/components/gamification/XPProgress.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, Award } from 'lucide-react';

interface GamificationStats {
  total_xp: number;
  level: number;
  xp_to_next_level: number;
  xp_current_level: number;
  xp_next_level: number;
}

export default function XPProgress() {
  const [stats, setStats] = useState<GamificationStats | null>(null);
  const [showLevelUp, setShowLevelUp] = useState(false);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/gamification/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const data = await response.json();
      if (data.success) {
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Failed to fetch gamification stats:', error);
    }
  };

  if (!stats) return null;

  const progress = ((stats.total_xp - stats.xp_current_level) / 
                   (stats.xp_next_level - stats.xp_current_level)) * 100;

  return (
    <div className="flex items-center gap-3 bg-gradient-to-r from-purple-500/10 to-blue-500/10 rounded-lg px-4 py-2 border border-purple-500/20">
      {/* Level Badge */}
      <div className="flex items-center gap-2">
        <Award className="w-5 h-5 text-purple-400" />
        <span className="text-sm font-bold text-purple-300">
          Level {stats.level}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="flex-1 min-w-[150px]">
        <div className="relative h-2 bg-gray-700 rounded-full overflow-hidden">
          <div 
            className="absolute h-full bg-gradient-to-r from-purple-500 to-blue-500 transition-all duration-500"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="mt-1 text-xs text-gray-400 flex justify-between">
          <span>{stats.total_xp.toLocaleString()} XP</span>
          <span>{stats.xp_to_next_level} to next level</span>
        </div>
      </div>

      {/* XP Icon */}
      <TrendingUp className="w-4 h-4 text-green-400" />
    </div>
  );
}
```

#### 5.2 Add to Navigation Bar

**File:** `frontend/components/Navbar.tsx` (or your header component)

```typescript
import XPProgress from './gamification/XPProgress';

// Inside your navbar/header component:
<div className="flex items-center gap-4">
  <XPProgress />
  {/* ... other navbar items ... */}
</div>
```

#### 5.3 Create XP Notification Toast

**File:** `frontend/components/gamification/XPToast.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import { Sparkles } from 'lucide-react';

interface XPGainEvent {
  xp_gained: number;
  level_up: boolean;
  new_level?: number;
}

export default function XPToast() {
  const [notification, setNotification] = useState<XPGainEvent | null>(null);

  useEffect(() => {
    // Listen for XP gain events
    window.addEventListener('xp-gained', handleXPGain);
    return () => window.removeEventListener('xp-gained', handleXPGain);
  }, []);

  const handleXPGain = (event: CustomEvent<XPGainEvent>) => {
    setNotification(event.detail);
    setTimeout(() => setNotification(null), 3000);
  };

  if (!notification) return null;

  return (
    <div className="fixed top-20 right-4 z-50 animate-slide-in-right">
      <div className="bg-gradient-to-r from-green-500 to-emerald-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center gap-3">
        <Sparkles className="w-5 h-5" />
        <div>
          <p className="font-bold">+{notification.xp_gained} XP</p>
          {notification.level_up && (
            <p className="text-sm">Level up! Now level {notification.new_level}</p>
          )}
        </div>
      </div>
    </div>
  );
}
```

**Add to your main layout:**
```typescript
import XPToast from './gamification/XPToast';

<XPToast />
```

#### 5.4 Trigger XP Notifications

After successful simulation/conversion, dispatch event:

```typescript
// In your simulation/conversion success handler:
window.dispatchEvent(new CustomEvent('xp-gained', {
  detail: {
    xp_gained: 10,
    level_up: false
  }
}));
```

**✅ Test:** Verify XP bar updates and toast shows.

---

### **STEP 6: Basic Achievement System** (Week 2, Day 1-2)

#### 6.1 Seed Initial Achievements

**File:** `backend/scripts/seed_achievements.py`

```python
"""Seed initial achievements into database."""
from app.config.database import SessionLocal
from app.models.gamification import Achievement
import uuid

achievements_data = [
    {
        "name": "First Steps",
        "description": "Create your first quantum circuit",
        "category": "getting_started",
        "criteria": {"activity_type": "simulation_run", "count": 1},
        "reward_xp": 50,
        "rarity": "common",
        "icon_name": "rocket"
    },
    {
        "name": "Getting the Hang of It",
        "description": "Run 10 simulations",
        "category": "mastery",
        "criteria": {"activity_type": "simulation_run", "count": 10},
        "reward_xp": 100,
        "rarity": "uncommon",
        "icon_name": "target"
    },
    {
        "name": "Framework Explorer",
        "description": "Convert your first circuit",
        "category": "getting_started",
        "criteria": {"activity_type": "conversion", "count": 1},
        "reward_xp": 75,
        "rarity": "common",
        "icon_name": "compass"
    },
    {
        "name": "Conversion Expert",
        "description": "Convert 25 circuits",
        "category": "mastery",
        "criteria": {"activity_type": "conversion", "count": 25},
        "reward_xp": 250,
        "rarity": "rare",
        "icon_name": "award"
    },
    {
        "name": "Level 5 Achieved",
        "description": "Reach level 5",
        "category": "progression",
        "criteria": {"level": 5},
        "reward_xp": 100,
        "rarity": "uncommon",
        "icon_name": "star"
    },
]

def seed_achievements():
    db = SessionLocal()
    try:
        for achievement_data in achievements_data:
            # Check if exists
            existing = db.query(Achievement).filter(
                Achievement.name == achievement_data["name"]
            ).first()
            
            if not existing:
                achievement = Achievement(**achievement_data)
                db.add(achievement)
        
        db.commit()
        print(f"✅ Seeded {len(achievements_data)} achievements")
    finally:
        db.close()

if __name__ == "__main__":
    seed_achievements()
```

**Run:** `python backend/scripts/seed_achievements.py`

#### 6.2 Achievement Detection Service

**Add to:** `backend/app/services/gamification_service.py`

```python
from app.models.gamification import Achievement, UserAchievement

class GamificationService:
    # ... existing methods ...
    
    @staticmethod
    def check_achievements(db: Session, user_id: str) -> list:
        """
        Check if user unlocked any new achievements.
        Returns list of newly unlocked achievements.
        """
        newly_unlocked = []
        
        # Get all achievements
        all_achievements = db.query(Achievement).all()
        
        # Get already unlocked
        unlocked_ids = {
            ua.achievement_id for ua in
            db.query(UserAchievement).filter(
                UserAchievement.user_id == user_id,
                UserAchievement.unlocked_at.isnot(None)
            ).all()
        }
        
        stats = GamificationService.get_or_create_stats(db, user_id)
        
        for achievement in all_achievements:
            if achievement.id in unlocked_ids:
                continue  # Already unlocked
            
            criteria = achievement.criteria
            unlocked = False
            
            # Check activity count criteria
            if 'activity_type' in criteria:
                count = db.query(GamificationActivity).filter(
                    GamificationActivity.user_id == user_id,
                    GamificationActivity.activity_type == criteria['activity_type']
                ).count()
                
                if count >= criteria.get('count', 1):
                    unlocked = True
            
            # Check level criteria
            elif 'level' in criteria:
                if stats.level >= criteria['level']:
                    unlocked = True
            
            if unlocked:
                # Create user achievement
                user_achievement = UserAchievement(
                    user_id=user_id,
                    achievement_id=achievement.id,
                    unlocked_at=datetime.utcnow()
                )
                db.add(user_achievement)
                
                # Award XP
                if achievement.reward_xp > 0:
                    stats.total_xp += achievement.reward_xp
                    stats.level = calculate_level(stats.total_xp)
                
                newly_unlocked.append({
                    'id': str(achievement.id),
                    'name': achievement.name,
                    'description': achievement.description,
                    'rarity': achievement.rarity,
                    'reward_xp': achievement.reward_xp
                })
        
        if newly_unlocked:
            db.commit()
        
        return newly_unlocked
```

**Modify award_xp to check achievements:**

```python
@staticmethod
def award_xp(...) -> dict:
    # ... existing code ...
    
    # Check for new achievements
    new_achievements = GamificationService.check_achievements(db, user_id)
    
    return {
        'xp_gained': xp_amount,
        'total_xp': stats.total_xp,
        'level': stats.level,
        'old_level': old_level,
        'level_up': level_up,
        'xp_to_next_level': xp_for_level(stats.level + 1) - stats.total_xp,
        'new_achievements': new_achievements  # NEW
    }
```

**✅ Test:** Verify achievements unlock after activities.

---

### **STEP 7: Achievement UI** (Week 2, Day 3)

#### 7.1 Achievement Display Component

**File:** `frontend/components/gamification/AchievementBadge.tsx`

```typescript
import { Trophy, Lock } from 'lucide-react';

interface Achievement {
  id: string;
  name: string;
  description: string;
  rarity: string;
  unlocked_at: string | null;
}

const rarityColors = {
  common: 'from-gray-400 to-gray-600',
  uncommon: 'from-green-400 to-green-600',
  rare: 'from-blue-400 to-blue-600',
  epic: 'from-purple-400 to-purple-600',
  legendary: 'from-yellow-400 to-orange-600',
};

export default function AchievementBadge({ achievement }: { achievement: Achievement }) {
  const isUnlocked = !!achievement.unlocked_at;
  const gradient = rarityColors[achievement.rarity as keyof typeof rarityColors];

  return (
    <div className={`
      relative p-4 rounded-lg border-2 transition-all hover:scale-105
      ${isUnlocked 
        ? `bg-gradient-to-br ${gradient} border-transparent` 
        : 'bg-gray-800 border-gray-700 opacity-60'
      }
    `}>
      {!isUnlocked && (
        <div className="absolute inset-0 flex items-center justify-center">
          <Lock className="w-8 h-8 text-gray-600" />
        </div>
      )}
      
      <div className={!isUnlocked ? 'blur-sm' : ''}>
        <Trophy className="w-8 h-8 mb-2 text-white" />
        <h3 className="font-bold text-white">{achievement.name}</h3>
        <p className="text-sm text-gray-200 mt-1">{achievement.description}</p>
        {isUnlocked && (
          <p className="text-xs text-gray-300 mt-2">
            Unlocked {new Date(achievement.unlocked_at!).toLocaleDateString()}
          </p>
        )}
      </div>
    </div>
  );
}
```

#### 7.2 Achievements Page

**File:** `frontend/app/achievements/page.tsx`

```typescript
'use client';

import { useEffect, useState } from 'react';
import AchievementBadge from '@/components/gamification/AchievementBadge';

export default function AchievementsPage() {
  const [achievements, setAchievements] = useState([]);

  useEffect(() => {
    fetchAchievements();
  }, []);

  const fetchAchievements = async () => {
    const response = await fetch('/api/gamification/achievements', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    });
    const data = await response.json();
    setAchievements(data.achievements);
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-8">Achievements</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {achievements.map((achievement) => (
          <AchievementBadge key={achievement.id} achievement={achievement} />
        ))}
      </div>
    </div>
  );
}
```

**✅ Test:** Navigate to `/achievements` and see badges.

---

### **STEP 8: Simple Leaderboard** (Week 3)

I'll spare you the full code, but here's the approach:

1. **API Endpoint:** `/api/gamification/leaderboard`
2. **Query:** Top 100 users by total_xp
3. **Frontend:** Simple table with rank, username, level, XP
4. **Update:** Cached query that updates every 5 minutes

---

## ✅ Testing Checklist

After each step:

- [ ] Manual testing in UI
- [ ] API endpoint works (Postman/curl)
- [ ] Database updated correctly
- [ ] No console errors
- [ ] XP values feel rewarding (not too easy, not too hard)

---

## 🚢 Shipping Strategy

### After Week 1
- ✅ Deploy XP & Levels to production
- 📣 Announce: "Earn XP for every simulation!"
- 📊 Monitor: Are users engaging more?

### After Week 2
- ✅ Deploy Achievements
- 📣 Announce: "Unlock badges for milestones!"
- 📊 Monitor: Achievement unlock rate

### After Week 3
- ✅ Deploy Leaderboard
- 📣 Announce: "See where you rank!"
- 📊 Monitor: Competitive engagement

---

## 🔄 Iteration Based on Data

### Metrics to Track
1. **XP per activity** - Are values balanced?
2. **Level distribution** - Are users progressing?
3. **Achievement unlock rate** - Too easy/hard?
4. **User retention** - More engaged after gamification?

### Adjust As Needed
- If users level too fast → Increase XP requirements
- If achievements rarely unlock → Reduce criteria
- If leaderboard dominated by few → Add weekly/monthly boards

---

## 🎉 Future Enhancements

Once core is working:
- Daily challenges
- Streak system
- Social features (share circuits)
- Seasonal events
- Custom badges for special users

---

## 🙋 Need Help?

### Common Issues

**Q: Database migration fails?**  
A: Check PostgreSQL is running, verify connection string

**Q: XP not showing in UI?**  
A: Check API call in browser console, verify JWT token

**Q: Achievements not unlocking?**  
A: Check criteria logic, verify activity is logged

---

**Ready to Start? Begin with Step 1! 🚀**
