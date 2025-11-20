from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import sys
import os

# Add the project root directory to Python path
current_file = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
sys.path.insert(0, project_root)

from app.models.schemas import ConversionRequest
from app.services.simulation_service import SimulationService

router = APIRouter(prefix="/api/simulator", tags=["simulator"])

# Initialize simulation service
simulation_service = SimulationService()

@router.post("/execute")
async def execute_qasm(request: dict):
    """
    Execute OpenQASM code using the quantum simulator (legacy)
    
    Args:
        request: Dictionary containing qasm_code, backend, shots, etc.
        
    Returns:
        JSON response with simulation results
    """
    try:
        qasm_code = request.get("qasm_code")
        backend = request.get("backend", "statevector")
        shots = request.get("shots", 1024)
        
        if not qasm_code:
            raise HTTPException(status_code=400, detail="qasm_code is required")
        
        # Execute the simulation
        result = simulation_service.execute_qasm(
            qasm_code=qasm_code,
            backend=backend,
            shots=shots
        )
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@router.post("/execute-qsim")
async def execute_qasm_with_qsim(request: dict):
    """
    Execute OpenQASM code using QSim backend
    
    Args:
        request: Dictionary containing qasm_input, backend (cirq/qiskit/pennylane), shots
        
    Returns:
        JSON response with QSim simulation results
    """
    try:
        qasm_input = request.get("qasm_input")
        backend = request.get("backend", "cirq")
        shots = request.get("shots", 1024)
        
        if not qasm_input:
            raise HTTPException(status_code=400, detail="qasm_input is required")
        
        # Execute with QSim
        result = simulation_service.execute_qasm_with_qsim(
            qasm_code=qasm_input,
            backend=backend,
            shots=shots
        )
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"QSim simulation failed: {str(e)}")

@router.get("/backends")
async def get_available_backends():
    """
    Get list of available simulation backends
    
    Returns:
        List of available backend names
    """
    try:
        backends = simulation_service.get_available_backends()
        return {"backends": backends}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get backends: {str(e)}")

@router.get("/health")
async def simulator_health():
    """
    Health check for the simulator service
    
    Returns:
        Health status of the simulator service
    """
    try:
        status = simulation_service.health_check()
        return status
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
