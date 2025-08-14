"""
QCanvas Backend Main Application

This module serves as the main entry point for the QCanvas backend API.
It sets up the FastAPI application with all necessary middleware, routes,
and WebSocket support for the quantum computing platform.

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api.routes import converter, simulator, health
from app.core.websocket_manager import WebSocketManager
from app.config.settings import get_settings
from app.utils.logging import setup_logging
from app.utils.exceptions import QCanvasException

# Initialize settings
settings = get_settings()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global WebSocket manager
websocket_manager = WebSocketManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    Initializes database connections, WebSocket manager, and other resources.
    """
    # Startup
    logger.info("Starting QCanvas Backend...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    
    # Initialize WebSocket manager
    await websocket_manager.startup()
    
    # Initialize database connections (if needed)
    # await init_database()
    
    logger.info("QCanvas Backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down QCanvas Backend...")
    
    # Cleanup WebSocket connections
    await websocket_manager.shutdown()
    
    # Close database connections (if needed)
    # await close_database()
    
    logger.info("QCanvas Backend shutdown complete")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="""
        QCanvas - Quantum Unified Simulator API
        
        A comprehensive quantum computing platform that provides unified simulation,
        circuit conversion, and visualization capabilities across multiple quantum frameworks.
        
        ## Features
        
        * **Circuit Conversion**: Convert between Cirq, Qiskit, and PennyLane
        * **Quantum Simulation**: Execute circuits with multiple backend options
        * **Real-time Visualization**: WebSocket-based real-time updates
        * **RESTful API**: Comprehensive API for programmatic access
        
        ## Frameworks Supported
        
        * **Cirq**: Google's quantum computing framework
        * **Qiskit**: IBM's quantum computing framework  
        * **PennyLane**: Xanadu's quantum machine learning framework
        * **OpenQASM 3.0**: Standard quantum assembly language
        """,
        version=settings.APP_VERSION,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS.split(","),
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Add trusted host middleware for security
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS.split(",")
    )
    
    # Add custom exception handler
    @app.exception_handler(QCanvasException)
    async def qcanvas_exception_handler(request: Request, exc: QCanvasException):
        """Handle custom QCanvas exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_type,
                "message": exc.message,
                "details": exc.details
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "InternalServerError",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.DEBUG else "Internal server error"
            }
        )
    
    # Include API routes
    app.include_router(
        health.router,
        prefix="/api/health",
        tags=["Health"]
    )
    
    app.include_router(
        converter.router,
        prefix="/api/convert",
        tags=["Circuit Conversion"]
    )
    
    app.include_router(
        simulator.router,
        prefix="/api/simulate",
        tags=["Quantum Simulation"]
    )
    
    # Add WebSocket endpoint
    @app.websocket("/ws")
    async def websocket_endpoint(websocket):
        """WebSocket endpoint for real-time communication."""
        await websocket_manager.connect(websocket)
        try:
            while True:
                # Handle WebSocket messages
                data = await websocket.receive_text()
                await websocket_manager.handle_message(websocket, data)
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
        finally:
            await websocket_manager.disconnect(websocket)
    
    # Add static files serving (for documentation, etc.)
    if os.path.exists("static"):
        app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root() -> Dict[str, Any]:
        """
        Root endpoint providing basic API information.
        
        Returns:
            Dict containing API information and available endpoints
        """
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "description": "Quantum Unified Simulator API",
            "docs": "/docs" if settings.DEBUG else None,
            "health": "/api/health",
            "endpoints": {
                "conversion": "/api/convert",
                "simulation": "/api/simulate",
                "websocket": "/ws"
            }
        }
    
    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    """
    Run the application directly when this file is executed.
    
    This is useful for development. For production, use uvicorn directly.
    """
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=settings.WORKERS if not settings.RELOAD else 1,
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True
    )