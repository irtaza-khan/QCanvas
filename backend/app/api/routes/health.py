"""
QCanvas Health Check API Routes

This module provides health check endpoints for monitoring the QCanvas backend
system status, including database connectivity, quantum simulator status,
and overall system health.

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.config.settings import get_settings
from app.core.websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)
router = APIRouter()

# Global WebSocket manager reference (will be set by main app)
websocket_manager: WebSocketManager = None


class HealthStatus(BaseModel):
    """Health status model for API responses."""
    
    status: str = Field(..., description="Overall health status (healthy/unhealthy)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    version: str = Field(..., description="Application version")
    uptime: float = Field(..., description="Application uptime in seconds")
    components: Dict[str, Any] = Field(..., description="Individual component health status")


class ComponentHealth(BaseModel):
    """Individual component health model."""
    
    status: str = Field(..., description="Component status (healthy/unhealthy/unknown)")
    response_time: Optional[float] = Field(default=None, description="Response time in milliseconds")
    error: Optional[str] = Field(default=None, description="Error message if unhealthy")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional component details")


# Application startup time for uptime calculation
startup_time = time.time()


def get_uptime() -> float:
    """Get application uptime in seconds."""
    return time.time() - startup_time


async def check_database_health() -> ComponentHealth:
    """
    Check database connectivity and health.
    
    Returns:
        ComponentHealth: Database health status
    """
    start_time = time.time()
    
    try:
        # TODO: Implement actual database health check
        # For now, return a mock healthy status
        response_time = (time.time() - start_time) * 1000
        
        return ComponentHealth(
            status="healthy",
            response_time=response_time,
            details={
                "type": "postgresql",
                "pool_size": 10,
                "active_connections": 0
            }
        )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"Database health check failed: {str(e)}")
        
        return ComponentHealth(
            status="unhealthy",
            response_time=response_time,
            error=str(e)
        )


async def check_redis_health() -> ComponentHealth:
    """
    Check Redis connectivity and health.
    
    Returns:
        ComponentHealth: Redis health status
    """
    start_time = time.time()
    
    try:
        # TODO: Implement actual Redis health check
        # For now, return a mock healthy status
        response_time = (time.time() - start_time) * 1000
        
        return ComponentHealth(
            status="healthy",
            response_time=response_time,
            details={
                "type": "redis",
                "memory_usage": "2.5MB",
                "connected_clients": 1
            }
        )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"Redis health check failed: {str(e)}")
        
        return ComponentHealth(
            status="unhealthy",
            response_time=response_time,
            error=str(e)
        )


async def check_quantum_simulator_health() -> ComponentHealth:
    """
    Check quantum simulator availability and health.
    
    Returns:
        ComponentHealth: Quantum simulator health status
    """
    start_time = time.time()
    
    try:
        # TODO: Implement actual quantum simulator health check
        # For now, return a mock healthy status
        response_time = (time.time() - start_time) * 1000
        
        return ComponentHealth(
            status="healthy",
            response_time=response_time,
            details={
                "available_backends": ["statevector", "density_matrix", "stabilizer"],
                "max_qubits": 32,
                "supported_frameworks": ["cirq", "qiskit", "pennylane"]
            }
        )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"Quantum simulator health check failed: {str(e)}")
        
        return ComponentHealth(
            status="unhealthy",
            response_time=response_time,
            error=str(e)
        )


async def check_websocket_health() -> ComponentHealth:
    """
    Check WebSocket manager health.
    
    Returns:
        ComponentHealth: WebSocket manager health status
    """
    start_time = time.time()
    
    try:
        if websocket_manager is None:
            return ComponentHealth(
                status="unknown",
                response_time=(time.time() - start_time) * 1000,
                error="WebSocket manager not initialized"
            )
        
        stats = websocket_manager.get_connection_stats()
        response_time = (time.time() - start_time) * 1000
        
        return ComponentHealth(
            status="healthy",
            response_time=response_time,
            details=stats
        )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"WebSocket health check failed: {str(e)}")
        
        return ComponentHealth(
            status="unhealthy",
            response_time=response_time,
            error=str(e)
        )


async def check_external_services_health() -> ComponentHealth:
    """
    Check external services health (AWS, email, etc.).
    
    Returns:
        ComponentHealth: External services health status
    """
    start_time = time.time()
    
    try:
        settings = get_settings()
        
        # Check if external services are configured
        external_services = []
        
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            external_services.append("aws")
        
        if settings.SMTP_HOST and settings.SMTP_USERNAME:
            external_services.append("email")
        
        response_time = (time.time() - start_time) * 1000
        
        return ComponentHealth(
            status="healthy" if external_services else "unknown",
            response_time=response_time,
            details={
                "configured_services": external_services,
                "aws_configured": bool(settings.AWS_ACCESS_KEY_ID),
                "email_configured": bool(settings.SMTP_HOST)
            }
        )
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        logger.error(f"External services health check failed: {str(e)}")
        
        return ComponentHealth(
            status="unhealthy",
            response_time=response_time,
            error=str(e)
        )


@router.get("/", response_model=HealthStatus)
async def health_check():
    """
    Perform a comprehensive health check of the QCanvas backend.
    
    This endpoint checks the health of all major system components:
    - Database connectivity
    - Redis connectivity
    - Quantum simulator availability
    - WebSocket manager status
    - External services configuration
    
    Returns:
        HealthStatus: Comprehensive health status of all components
    """
    logger.debug("Performing health check")
    
    # Get settings
    settings = get_settings()
    
    # Check all components
    components = {}
    
    # Database health
    components["database"] = await check_database_health()
    
    # Redis health
    components["redis"] = await check_redis_health()
    
    # Quantum simulator health
    components["quantum_simulator"] = await check_quantum_simulator_health()
    
    # WebSocket health
    components["websocket"] = await check_websocket_health()
    
    # External services health
    components["external_services"] = await check_external_services_health()
    
    # Determine overall status
    unhealthy_components = [
        name for name, health in components.items()
        if health.status == "unhealthy"
    ]
    
    overall_status = "unhealthy" if unhealthy_components else "healthy"
    
    # Create response
    health_status = HealthStatus(
        status=overall_status,
        version=settings.APP_VERSION,
        uptime=get_uptime(),
        components=components
    )
    
    logger.info(f"Health check completed: {overall_status}")
    
    return health_status


@router.get("/simple")
async def simple_health_check():
    """
    Perform a simple health check.
    
    This endpoint provides a quick health check without detailed
    component information, useful for load balancers and basic monitoring.
    
    Returns:
        Dict: Simple health status
    """
    settings = get_settings()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.APP_VERSION,
        "uptime": get_uptime()
    }


@router.get("/ready")
async def readiness_check():
    """
    Perform a readiness check for Kubernetes/container orchestration.
    
    This endpoint checks if the application is ready to receive traffic.
    It performs minimal checks to ensure the application can handle requests.
    
    Returns:
        Dict: Readiness status
    """
    try:
        # Quick checks for readiness
        settings = get_settings()
        
        # Check if WebSocket manager is available
        websocket_ready = websocket_manager is not None
        
        # Basic readiness criteria
        ready = websocket_ready
        
        if ready:
            return {
                "status": "ready",
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            raise HTTPException(
                status_code=503,
                detail="Application not ready"
            )
            
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Application not ready: {str(e)}"
        )


@router.get("/live")
async def liveness_check():
    """
    Perform a liveness check for Kubernetes/container orchestration.
    
    This endpoint checks if the application is alive and running.
    It performs minimal checks that don't depend on external services.
    
    Returns:
        Dict: Liveness status
    """
    try:
        settings = get_settings()
        
        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.APP_VERSION,
            "uptime": get_uptime()
        }
    except Exception as e:
        logger.error(f"Liveness check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Application not alive: {str(e)}"
        )


@router.get("/info")
async def system_info():
    """
    Get detailed system information.
    
    This endpoint provides comprehensive system information including
    configuration details, component status, and system metrics.
    
    Returns:
        Dict: Detailed system information
    """
    settings = get_settings()
    
    # Get component health
    components = {}
    components["database"] = await check_database_health()
    components["redis"] = await check_redis_health()
    components["quantum_simulator"] = await check_quantum_simulator_health()
    components["websocket"] = await check_websocket_health()
    components["external_services"] = await check_external_services_health()
    
    return {
        "application": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "uptime": get_uptime()
        },
        "server": {
            "host": settings.HOST,
            "port": settings.PORT,
            "workers": settings.WORKERS
        },
        "quantum": {
            "max_qubits": settings.MAX_QUBITS,
            "max_shots": settings.MAX_SHOTS,
            "default_backend": settings.DEFAULT_BACKEND,
            "enable_noise_models": settings.ENABLE_NOISE_MODELS
        },
        "components": components,
        "timestamp": datetime.utcnow().isoformat()
    }
