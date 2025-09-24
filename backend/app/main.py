import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# Add the project root directory to Python path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
sys.path.insert(0, project_root)

from app.api.routes import converter, health, simulator

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting QCanvas Backend...")
    print(f"Project root: {project_root}")
    
    # Test imports
    try:
        from quantum_converters.converters.cirq_to_qasm import convert_cirq_to_qasm3
        from quantum_converters.converters.pennylane_to_qasm import convert_pennylane_to_qasm3
        from quantum_converters.converters.qiskit_to_qasm import convert_qiskit_to_qasm3
        print("✓ All converter modules imported successfully")
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Please ensure all converter modules are available.")
    
    yield
    
    # Shutdown
    print("Shutting down QCanvas Backend...")

# Create FastAPI app
app = FastAPI(
    title="QCanvas Backend",
    description="Backend API for QCanvas - Quantum Circuit Framework Converter",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(health.router)
app.include_router(converter.router)
app.include_router(simulator.router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "QCanvas Backend API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "converter": "/api/converter",
            "docs": "/docs"
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)