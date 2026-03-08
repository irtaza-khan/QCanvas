"""
Gamification API routes for QCanvas.

Handles XP tracking, level progression, achievements, and leaderboards.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from app.config.database import get_db
from app.services.gamification_service import GamificationService
from app.api.routes.auth import get_current_user
from app.models.database_models import User

router = APIRouter(prefix="/api/gamification", tags=["Gamification"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ActivityRequest(BaseModel):
    """Request model for logging an activity."""
    activity_type: str = Field(..., description="Type of activity (e.g., 'simulation_run', 'conversion')")
    xp_amount: Optional[int] = Field(None, description="Custom XP amount (optional, uses default if not provided)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional activity metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "activity_type": "simulation_run",
                "metadata": {
                    "backend": "statevector",
                    "shots": 1024,
                    "qubits": 3
                }
            }
        }


class XPAwardResponse(BaseModel):
    """Response model for XP award."""
    success: bool
    xp_gained: int
    total_xp: int
    level: int
    old_level: int
    level_up: bool
    xp_to_next_level: int
    is_first_time: bool
    current_streak: int
    new_achievements: List[Dict[str, Any]] = []
    message: Optional[str] = None


class UserStatsResponse(BaseModel):
    """Response model for user stats."""
    success: bool
    stats: Dict[str, Any]


class RecentActivitiesResponse(BaseModel):
    """Response model for recent activities."""
    success: bool
    activities: List[Dict[str, Any]]
    count: int


class ActivitySummaryResponse(BaseModel):
    """Response model for activity summary."""
    success: bool
    summary: Dict[str, Any]


class AchievementsResponse(BaseModel):
    """Response model for achievements."""
    success: bool
    achievements: List[Dict[str, Any]]
    total: int
    unlocked: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get(
    "/stats",
    response_model=UserStatsResponse,
    summary="Get Current User's Gamification Stats",
    description="Retrieve comprehensive gamification statistics for the authenticated user including XP, level, streaks, and progress."
)
async def get_gamification_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserStatsResponse:
    """
    Get current user's gamification stats.
    
    Returns:
    - Total XP
    - Current level
    - Progress to next level (percentage)
    - Current and longest streaks
    - XP thresholds for current and next level
    """
    try:
        stats = GamificationService.get_user_stats(db, str(current_user.id))
        return UserStatsResponse(
            success=True,
            stats=stats
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve gamification stats: {str(e)}"
        )


@router.post(
    "/activity",
    response_model=XPAwardResponse,
    summary="Log Activity and Award XP",
    description="Log a user activity and award XP. Automatically applies first-time bonuses, updates level progression, and checks for achievements.",
    status_code=status.HTTP_201_CREATED
)
async def log_activity(
    request: ActivityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> XPAwardResponse:
    """
    Log an activity and award XP.
    
    This endpoint is called by other services (simulation, conversion, etc.)
    to award XP when users complete activities.
    
    Features:
    - Automatic first-time bonuses
    - Level-up detection
    - Streak tracking
    - Activity logging for analytics
    - Achievement checking and unlocking
    """
    try:
        result = GamificationService.award_xp(
            db=db,
            user_id=str(current_user.id),
            activity_type=request.activity_type,
            xp_amount=request.xp_amount,
            metadata=request.metadata
        )
        
        # Generate appropriate message
        message = f"Earned {result['xp_gained']} XP"
        if result['level_up']:
            message += f" and leveled up to Level {result['level']}! 🎉"
        elif result['is_first_time']:
            message += " (First time bonus!) 🆕"
        
        # Add achievement info to message
        new_achievements = result.get('new_achievements', [])
        if new_achievements:
            names = [a['name'] for a in new_achievements]
            message += f" | 🏆 Unlocked: {', '.join(names)}"
        
        return XPAwardResponse(
            success=True,
            message=message,
            **result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to award XP: {str(e)}"
        )


@router.get(
    "/stats/{user_id}",
    response_model=UserStatsResponse,
    summary="Get Any User's Public Stats",
    description="Retrieve public gamification stats for any user (for leaderboards and profiles)."
)
async def get_user_stats(
    user_id: str,
    db: Session = Depends(get_db)
) -> UserStatsResponse:
    """
    Get any user's public gamification stats.
    
    This endpoint is public and can be used for:
    - Leaderboards
    - User profiles
    - Comparing stats
    
    Note: Only returns public information (no private metadata).
    """
    try:
        stats = GamificationService.get_user_stats(db, user_id)
        return UserStatsResponse(
            success=True,
            stats=stats
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User stats not found: {str(e)}"
        )


@router.get(
    "/activities/recent",
    response_model=RecentActivitiesResponse,
    summary="Get Recent Activities",
    description="Retrieve the user's recent XP-earning activities."
)
async def get_recent_activities(
    limit: int = Query(default=10, ge=1, le=50, description="Number of activities to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> RecentActivitiesResponse:
    """
    Get user's recent activities.
    
    Returns a list of recent XP-earning activities with:
    - Activity type
    - XP awarded
    - Timestamp
    - Metadata
    """
    try:
        activities = GamificationService.get_recent_activities(
            db=db,
            user_id=str(current_user.id),
            limit=limit
        )
        return RecentActivitiesResponse(
            success=True,
            activities=activities,
            count=len(activities)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve activities: {str(e)}"
        )


@router.get(
    "/activities/summary",
    response_model=ActivitySummaryResponse,
    summary="Get Activity Summary",
    description="Get aggregated statistics of user activities grouped by type."
)
async def get_activity_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ActivitySummaryResponse:
    """
    Get activity summary statistics.
    
    Returns aggregated data showing:
    - Count of each activity type
    - Total XP earned from each activity type
    - Overall activity breakdown
    """
    try:
        summary = GamificationService.get_activity_summary(
            db=db,
            user_id=str(current_user.id)
        )
        return ActivitySummaryResponse(
            success=True,
            summary=summary
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve activity summary: {str(e)}"
        )


# ============================================================================
# ACHIEVEMENT ENDPOINTS
# ============================================================================

@router.get(
    "/achievements",
    response_model=AchievementsResponse,
    summary="Get All Achievements with User Progress",
    description="Retrieve all achievements with the current user's progress and unlock status."
)
async def get_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AchievementsResponse:
    """
    Get all achievements with user's progress.
    
    Returns all achievements including:
    - Achievement details (name, description, rarity, XP reward)
    - Whether the user has unlocked it
    - Current progress towards unlocking
    - Unlock date if unlocked
    
    Hidden achievements show "???" for description until unlocked.
    """
    try:
        achievements = GamificationService.get_user_achievements(
            db=db,
            user_id=str(current_user.id),
            include_locked=True
        )
        
        unlocked_count = sum(1 for a in achievements if a['is_unlocked'])
        
        return AchievementsResponse(
            success=True,
            achievements=achievements,
            total=len(achievements),
            unlocked=unlocked_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve achievements: {str(e)}"
        )


@router.get(
    "/achievements/unlocked",
    response_model=AchievementsResponse,
    summary="Get User's Unlocked Achievements",
    description="Retrieve only the achievements the current user has unlocked."
)
async def get_unlocked_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AchievementsResponse:
    """
    Get only unlocked achievements.
    
    Returns achievements the user has earned, sorted by unlock date.
    """
    try:
        achievements = GamificationService.get_user_achievements(
            db=db,
            user_id=str(current_user.id),
            include_locked=False
        )
        
        return AchievementsResponse(
            success=True,
            achievements=achievements,
            total=len(achievements),
            unlocked=len(achievements)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve unlocked achievements: {str(e)}"
        )


@router.post(
    "/achievements/check",
    response_model=AchievementsResponse,
    summary="Manually Check Achievements",
    description="Trigger a manual achievement check for the current user."
)
async def check_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> AchievementsResponse:
    """
    Manually trigger achievement check.
    
    Evaluates all achievement criteria against the user's current stats
    and unlocks any newly earned achievements. Useful for retroactive
    achievement grants.
    """
    try:
        new_achievements = GamificationService.check_achievements(
            db=db,
            user_id=str(current_user.id),
            activity_type='manual_check'
        )
        
        # Return all achievements after the check
        all_achievements = GamificationService.get_user_achievements(
            db=db,
            user_id=str(current_user.id),
            include_locked=True
        )
        
        unlocked_count = sum(1 for a in all_achievements if a['is_unlocked'])
        
        return AchievementsResponse(
            success=True,
            achievements=all_achievements,
            total=len(all_achievements),
            unlocked=unlocked_count
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check achievements: {str(e)}"
        )


# ============================================================================
# LEADERBOARD
# ============================================================================

@router.get(
    "/leaderboard",
    summary="Get Leaderboard",
    description="Get top users by total XP (leaderboard)."
)
async def get_leaderboard(
    limit: int = Query(default=10, ge=1, le=100, description="Number of top users to return"),
    db: Session = Depends(get_db)
):
    """
    Get leaderboard of top users by XP.
    
    Returns top users ranked by total XP with:
    - Rank
    - User info (username, level)
    - Total XP
    """
    try:
        from app.models.gamification import UserGamification
        from sqlalchemy import desc
        
        # Get top users by XP
        top_users = db.query(
            UserGamification,
            User
        ).join(
            User, UserGamification.user_id == User.id
        ).filter(
            User.is_active == True,
            User.deleted_at == None
        ).order_by(
            desc(UserGamification.total_xp)
        ).limit(limit).all()
        
        leaderboard = []
        for rank, (stats, user) in enumerate(top_users, start=1):
            leaderboard.append({
                'rank': rank,
                'user_id': str(user.id),
                'username': user.username,
                'level': stats.level,
                'total_xp': stats.total_xp,
                'current_streak': stats.current_streak
            })
        
        return {
            'success': True,
            'leaderboard': leaderboard,
            'count': len(leaderboard)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve leaderboard: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health Check",
    description="Check if the gamification service is operational."
)
async def health_check():
    """Simple health check endpoint."""
    return {
        "status": "healthy",
        "service": "gamification",
        "version": "2.0.0"
    }
