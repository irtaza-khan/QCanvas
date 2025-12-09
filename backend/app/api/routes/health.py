from fastapi import APIRouter
from app.models.schemas import HealthResponse
from datetime import datetime

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for the QCanvas backend
    
    Returns:
        HealthResponse with status, timestamp, and version
    """
    from app.config.settings import settings

    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        features={
            "hybrid_execution": settings.ENABLE_HYBRID_EXECUTION,
            "project_management": settings.ENABLE_PROJECT_MANAGEMENT,
            "advanced_monitoring": settings.ENABLE_ADVANCED_MONITORING,
            "circuit_visualization": settings.ENABLE_CIRCUIT_VISUALIZATION
        }
    )
