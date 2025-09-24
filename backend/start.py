#!/usr/bin/env python3
"""
Startup script for QCanvas Backend
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Starting QCanvas Backend...")
    print("API Documentation will be available at: http://localhost:8000/docs")
    print("Health check: http://localhost:8000/api/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to avoid import string requirement
        log_level="info"
    )
