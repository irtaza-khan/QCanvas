"""
Gamification database models for QCanvas.

This module defines the database schema for the gamification system,
including user stats, activities, achievements, and progression tracking.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, ForeignKey, JSON, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.config.database import Base


class UserGamification(Base):
    """Track user gamification stats and progression."""
    __tablename__ = "user_gamification"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    total_xp = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(Date, nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship
    user = relationship("User", backref="gamification_stats")


class GamificationActivity(Base):
    """Log all XP-earning activities for tracking and analytics."""
    __tablename__ = "gamification_activities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    activity_type = Column(String(50), nullable=False)  # 'simulation', 'conversion', etc.
    xp_awarded = Column(Integer, nullable=False)
    activity_metadata = Column(JSON, nullable=True)  # Additional context (backend, shots, qubits, etc.)
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    # Relationship
    user = relationship("User", backref="gamification_activities")


class Achievement(Base):
    """Achievement catalog - defines all available achievements."""
    __tablename__ = "achievements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=False)
    category = Column(String(50), nullable=False)  # 'getting_started', 'mastery', 'progression', etc.
    criteria = Column(JSON, nullable=False)  # Unlock conditions as JSON
    reward_xp = Column(Integer, default=0, nullable=False)
    rarity = Column(String(20), default='common', nullable=False)  # common, uncommon, rare, epic, legendary
    icon_name = Column(String(50), nullable=True)  # Icon identifier for frontend
    is_hidden = Column(Boolean, default=False, nullable=False)  # Hidden achievements
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)


class UserAchievement(Base):
    """Track unlocked achievements per user with progress."""
    __tablename__ = "user_achievements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(UUID(as_uuid=True), ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    progress = Column(JSON, nullable=True)  # For multi-step achievements (e.g., {"current": 5, "target": 10})
    unlocked_at = Column(TIMESTAMP, nullable=True)  # NULL if in progress, timestamp when unlocked
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", backref="achievements")
    achievement = relationship("Achievement")
