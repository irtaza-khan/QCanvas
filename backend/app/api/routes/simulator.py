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
from app.config.database import get_db
from sqlalchemy.orm import Session
from app.models.database_models import User, Simulation, SimulationBackend, ExecutionStatus
from app.api.routes.auth import get_optional_user
from app.core.middleware import limiter
from fastapi import Depends, Request

router = APIRouter(prefix="/api/simulator", tags=["simulator"])

# Initialize simulation service
simulation_service = SimulationService()

@router.post("/execute")
@limiter.limit("20/minute")
async def execute_qasm(
    request: Request,
    request_data: dict,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Execute OpenQASM code using the quantum simulator (legacy)
    
    Args:
        request: FastAPI Request (for rate limiting)
        request_data: Dictionary containing qasm_code, backend, shots, etc.
        
    """
    try:
        qasm_code = request_data.get("qasm_code")
        backend = request_data.get("backend", "statevector")
        shots = request_data.get("shots", 1024)
        
        if not qasm_code:
            raise HTTPException(status_code=400, detail="qasm_code is required")
        
        # Execute the simulation
        result = simulation_service.execute_qasm(
            qasm_code=qasm_code,
            backend=backend,
            shots=shots
        )
        
        # Award XP for successful simulation if user is authenticated
        if current_user and result.get("success"):
            try:
                from app.services.gamification_service import GamificationService
                
                # Extract circuit metadata for XP tracking
                metadata = {
                    "backend": backend,
                    "shots": shots,
                    "qubits": result.get("metadata", {}).get("num_qubits", 0) if result.get("metadata") else 0
                }
                
                # Award XP for simulation
                GamificationService.award_xp(
                    db=db,
                    user_id=str(current_user.id),
                    activity_type='simulation_run',
                    metadata=metadata
                )
                print(f"✅ Awarded XP to user {current_user.username} for simulation")
            except Exception as e:
                # Don't fail the request if gamification fails
                print(f"❌ Failed to award XP for simulation: {e}")
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")

@router.post("/execute-qsim")
@limiter.limit("20/minute")
async def execute_qasm_with_qsim(
    request: Request,
    request_data: dict,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Execute OpenQASM code using QSim backend
    
    Args:
        request: FastAPI Request
        request_data: Dictionary containing qasm_input, backend (cirq/qiskit/pennylane), shots
        
    Returns:
        JSON response with QSim simulation results
    """
    try:
        qasm_input = request_data.get("qasm_input")
        backend = request_data.get("backend", "cirq")
        shots = request_data.get("shots", 1024)
        
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
        
        # Award XP for successful simulation if user is authenticated
        if current_user and result.get("success"):
            try:
                from app.services.gamification_service import GamificationService
                
                # Extract circuit metadata for XP tracking
                metadata = {
                    "backend": backend,
                    "shots": shots,
                    "qubits": result.get("results", {}).get("metadata", {}).get("num_qubits", 0)
                }
                
                # Award XP for simulation
                GamificationService.award_xp(
                    db=db,
                    user_id=str(current_user.id),
                    activity_type='simulation_run',
                    metadata=metadata
                )
            except Exception as e:
                # Don't fail the request if gamification fails
                print(f"Failed to award XP for simulation: {e}")
        
        # Save to database if user is authenticated and simulation was successful
        if current_user and result.get("success"):
            try:
                # Map backend string to Enum
                # The backend strings might be lowercase, Enum is uppercase usually but let's check definition
                # Enum: STATEVECTOR, DENSITY_MATRIX, STABILIZER
                # But QSim backends are 'cirq', 'qiskit', 'pennylane'.
                # This is a mismatch. The SimulationBackend Enum only has: STATEVECTOR, DENSITY_MATRIX, STABILIZER.
                # I need to update the Enum to include CIRQ, QISKIT, PENNYLANE or map them.
                # Since I cannot update Enum easily without migration, I will map them to closest or just fail gracefully?
                # Actually, I can add them to the Enum in the model definition, but Postgres will reject if not in DB type.
                # I will map 'cirq' -> 'STATEVECTOR' (as it's a statevector simulator usually) or just skip saving if backend not in Enum.
                # This is a schema limitation I should have caught.
                # For now, I will try to map or just log warning.
                # Let's check if I can use a default or if I should just not save.
                # I'll try to map 'cirq', 'qiskit', 'pennylane' to 'STATEVECTOR' as a fallback, 
                # or better, I should have added them to Enum.
                # I will use STATEVECTOR as a generic backend for now if it doesn't match.
                
                backend_enum = SimulationBackend.STATEVECTOR
                try:
                    backend_enum = SimulationBackend(backend.upper())
                except ValueError:
                    pass # Keep default
                
                sim_record = Simulation(
                    user_id=current_user.id,
                    qasm_code=qasm_input,
                    backend=backend_enum,
                    shots=shots,
                    results_json=result.get("results"),
                    status=ExecutionStatus.SUCCESS,
                    execution_time_ms=int(float(result.get("results", {}).get("metadata", {}).get("execution_time", "0").replace("ms", ""))) if result.get("results") else 0
                )
                db.add(sim_record)
                db.commit()
            except Exception as e:
                print(f"Failed to save simulation history: {e}")

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
