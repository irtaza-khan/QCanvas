"""
Gamification service for XP tracking and level calculation.

This service handles:
- XP awarding and tracking
- Level calculation and progression
- Activity logging
- User stats retrieval
"""
from sqlalchemy.orm import Session
from app.models.gamification import UserGamification, GamificationActivity
from datetime import datetime, date
from typing import Dict, Any, Optional
import math
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# LEVEL PROGRESSION FORMULAS
# ============================================================================

def xp_for_level(level: int) -> int:
    """
    Calculate total XP required to reach a specific level.
    
    Formula: 100 * level^1.5
    This creates exponential growth that feels rewarding but not overwhelming.
    
    Examples:
    - Level 1: 0 XP
    - Level 2: 283 XP
    - Level 5: 1,118 XP
    - Level 10: 3,162 XP
    - Level 20: 8,944 XP
    
    Args:
        level: Target level (1-based)
        
    Returns:
        Total XP required to reach that level
    """
    if level <= 1:
        return 0
    return int(100 * math.pow(level, 1.5))


def calculate_level(total_xp: int) -> int:
    """
    Calculate current level based on total XP.
    
    Uses binary search for efficiency with large XP values.
    
    Args:
        total_xp: Total XP accumulated
        
    Returns:
        Current level (minimum 1)
    """
    if total_xp <= 0:
        return 1
    
    level = 1
    while xp_for_level(level + 1) <= total_xp:
        level += 1
    
    return level


# ============================================================================
# XP REWARD CONFIGURATION
# ============================================================================

# Base XP rewards for different activities
XP_REWARDS = {
    # Simulation activities
    'simulation_run': 10,
    'first_simulation': 50,  # First-time bonus
    
    # Conversion activities
    'conversion': 30,
    'first_conversion': 60,  # First-time bonus
    
    # Circuit management
    'circuit_saved': 5,
    'project_created': 25,
    
    # Learning activities
    'tutorial_completed': 100,
    'challenge_completed': 150,
    
    # Social activities
    'circuit_shared': 25,
    'helped_user': 50,
}


# ============================================================================
# GAMIFICATION SERVICE
# ============================================================================

class GamificationService:
    """Service for managing gamification features."""
    
    @staticmethod
    def get_or_create_stats(db: Session, user_id: str) -> UserGamification:
        """
        Get or create gamification stats for a user.
        
        Args:
            db: Database session
            user_id: User UUID as string
            
        Returns:
            UserGamification object
        """
        stats = db.query(UserGamification).filter(
            UserGamification.user_id == user_id
        ).first()
        
        if not stats:
            logger.info(f"Creating new gamification stats for user {user_id}")
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
        xp_amount: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Award XP to a user for an activity.
        
        This is the core method for gamification. It:
        1. Determines XP amount (with first-time bonuses)
        2. Records the activity
        3. Updates user stats
        4. Calculates level progression
        5. Updates streaks
        
        Args:
            db: Database session
            user_id: User UUID as string
            activity_type: Type of activity (e.g., 'simulation_run')
            xp_amount: Optional custom XP amount (overrides default)
            metadata: Optional additional data about the activity
            
        Returns:
            Dictionary with:
            - xp_gained: Amount of XP awarded
            - total_xp: New total XP
            - level: Current level
            - old_level: Previous level
            - level_up: Whether user leveled up
            - xp_to_next_level: XP needed for next level
        """
        try:
            # Get or create user stats
            stats = GamificationService.get_or_create_stats(db, user_id)
            
            # Determine XP amount
            if xp_amount is None:
                xp_amount = XP_REWARDS.get(activity_type, 0)
            
            # If no XP for this activity, return early
            if xp_amount <= 0:
                logger.warning(f"No XP defined for activity type: {activity_type}")
                return {
                    'xp_gained': 0,
                    'total_xp': stats.total_xp,
                    'level': stats.level,
                    'old_level': stats.level,
                    'level_up': False,
                    'xp_to_next_level': xp_for_level(stats.level + 1) - stats.total_xp
                }
            
            # Check for first-time bonus
            is_first_time = db.query(GamificationActivity).filter(
                GamificationActivity.user_id == user_id,
                GamificationActivity.activity_type == activity_type
            ).count() == 0
            
            # Apply first-time bonus if available
            if is_first_time:
                first_time_key = f'first_{activity_type}'
                if first_time_key in XP_REWARDS:
                    xp_amount = XP_REWARDS[first_time_key]
                    logger.info(f"First-time bonus applied for {activity_type}: {xp_amount} XP")
            
            # Record the activity
            activity = GamificationActivity(
                user_id=user_id,
                activity_type=activity_type,
                xp_awarded=xp_amount,
                activity_metadata=metadata or {}
            )
            db.add(activity)
            
            # Update user stats
            old_level = stats.level
            stats.total_xp += xp_amount
            stats.level = calculate_level(stats.total_xp)
            
            # Update streak
            today = date.today()
            if stats.last_activity_date:
                days_diff = (today - stats.last_activity_date).days
                if days_diff == 1:
                    # Consecutive day - increment streak
                    stats.current_streak += 1
                    if stats.current_streak > stats.longest_streak:
                        stats.longest_streak = stats.current_streak
                elif days_diff > 1:
                    # Streak broken - reset
                    stats.current_streak = 1
                # If days_diff == 0, same day - don't change streak
            else:
                # First activity ever
                stats.current_streak = 1
                stats.longest_streak = 1
            
            stats.last_activity_date = today
            stats.updated_at = datetime.utcnow()
            
            # Commit all changes
            db.commit()
            db.refresh(stats)
            
            level_up = stats.level > old_level
            
            if level_up:
                logger.info(f"User {user_id} leveled up: {old_level} -> {stats.level}")
            
            result = {
                'xp_gained': xp_amount,
                'total_xp': stats.total_xp,
                'level': stats.level,
                'old_level': old_level,
                'level_up': level_up,
                'xp_to_next_level': xp_for_level(stats.level + 1) - stats.total_xp,
                'is_first_time': is_first_time,
                'current_streak': stats.current_streak
            }
            
            logger.info(f"Awarded {xp_amount} XP to user {user_id} for {activity_type}")
            return result
            
        except Exception as e:
            logger.error(f"Error awarding XP to user {user_id}: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def get_user_stats(db: Session, user_id: str) -> Dict[str, Any]:
        """
        Get comprehensive gamification stats for a user.
        
        Args:
            db: Database session
            user_id: User UUID as string
            
        Returns:
            Dictionary with all user stats including:
            - user_id
            - total_xp
            - level
            - current_streak
            - longest_streak
            - xp_to_next_level
            - xp_current_level (XP threshold for current level)
            - xp_next_level (XP threshold for next level)
            - progress_percentage (% progress to next level)
        """
        stats = GamificationService.get_or_create_stats(db, user_id)
        
        xp_current_level = xp_for_level(stats.level)
        xp_next_level = xp_for_level(stats.level + 1)
        xp_to_next = xp_next_level - stats.total_xp
        
        # Calculate progress percentage within current level
        level_xp_range = xp_next_level - xp_current_level
        xp_in_current_level = stats.total_xp - xp_current_level
        progress_percentage = (xp_in_current_level / level_xp_range * 100) if level_xp_range > 0 else 0
        
        return {
            'user_id': str(stats.user_id),
            'total_xp': stats.total_xp,
            'level': stats.level,
            'current_streak': stats.current_streak,
            'longest_streak': stats.longest_streak,
            'last_activity_date': stats.last_activity_date.isoformat() if stats.last_activity_date else None,
            'xp_to_next_level': xp_to_next,
            'xp_current_level': xp_current_level,
            'xp_next_level': xp_next_level,
            'progress_percentage': round(progress_percentage, 1)
        }
    
    @staticmethod
    def get_recent_activities(
        db: Session,
        user_id: str,
        limit: int = 10
    ) -> list[Dict[str, Any]]:
        """
        Get recent activities for a user.
        
        Args:
            db: Database session
            user_id: User UUID as string
            limit: Maximum number of activities to return
            
        Returns:
            List of activity dictionaries
        """
        activities = db.query(GamificationActivity).filter(
            GamificationActivity.user_id == user_id
        ).order_by(
            GamificationActivity.created_at.desc()
        ).limit(limit).all()
        
        return [
            {
                'id': str(activity.id),
                'activity_type': activity.activity_type,
                'xp_awarded': activity.xp_awarded,
                'metadata': activity.activity_metadata,
                'created_at': f"{activity.created_at.isoformat()}Z"
            }
            for activity in activities
        ]
    
    @staticmethod
    def get_activity_summary(db: Session, user_id: str) -> Dict[str, Any]:
        """
        Get summary statistics of user activities.
        
        Args:
            db: Database session
            user_id: User UUID as string
            
        Returns:
            Dictionary with activity counts by type
        """
        from sqlalchemy import func
        
        results = db.query(
            GamificationActivity.activity_type,
            func.count(GamificationActivity.id).label('count'),
            func.sum(GamificationActivity.xp_awarded).label('total_xp')
        ).filter(
            GamificationActivity.user_id == user_id
        ).group_by(
            GamificationActivity.activity_type
        ).all()
        
        summary = {}
        for activity_type, count, total_xp in results:
            summary[activity_type] = {
                'count': count,
                'total_xp': total_xp or 0
            }
        
        return summary
