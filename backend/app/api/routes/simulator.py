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
            return JSONResponse(
                content={"success": False, "error": "qasm_input is required"},
                status_code=400
            )
        
        # Execute with QSim - wrap in try-except to catch any unexpected exceptions
        try:
            result = simulation_service.execute_qasm_with_qsim(
                qasm_code=qasm_input,
                backend=backend,
                shots=shots
            )
        except Exception as service_error:
            # If service itself raises an exception (shouldn't happen, but safety check)
            import traceback
            error_trace = traceback.format_exc()
            print(f"Unexpected exception in simulation_service.execute_qasm_with_qsim: {service_error}")
            print(error_trace)
            return JSONResponse(
                content={
                    "success": False,
                    "error": f"Service error: {str(service_error)}"
                },
                status_code=500
            )
        
        # Check if simulation failed and return appropriate status code
        if not result.get("success", False):
            return JSONResponse(
                content=result,
                status_code=400  # Use 400 for simulation failures (bad input/execution)
            )
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the full error for debugging
        import traceback
        error_trace = traceback.format_exc()
        print(f"QSim execution error in route handler: {e}")
        print(error_trace)
        
        # Return error response instead of raising HTTPException to ensure proper format
        error_detail = str(e)
        # Try to extract more specific error message
        if hasattr(e, '__cause__') and e.__cause__:
            error_detail = str(e.__cause__)
        elif hasattr(e, 'args') and e.args:
            error_detail = str(e.args[0])
        
        return JSONResponse(
            content={
                "success": False,
                "error": f"QSim simulation failed: {error_detail}"
            },
            status_code=500
        )

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
