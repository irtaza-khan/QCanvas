"""
Hybrid Execution API Routes.

Provides endpoints for executing Python code with quantum circuits
in a sandboxed environment with qcanvas and qsim access.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import sys
import os
from app.api.routes.auth import get_current_user
from app.models.database_models import User

# Add the project root directory to Python path
current_file = os.path.abspath(__file__)
# backend/app/api/routes/hybrid.py -> backend/
backend_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
# Also add project root (parent of backend)
project_root = os.path.dirname(backend_root)

if backend_root not in sys.path:
    sys.path.insert(0, backend_root)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import sandbox execution
try:
    from qcanvas_runtime.sandbox import execute_sandboxed, validate_code
    from qcanvas_runtime.result import HybridExecutionResult
    SANDBOX_AVAILABLE = True
    print("✓ Sandbox module imported successfully")
except ImportError as e:
    print(f"Warning: Sandbox not available: {e}")
    import traceback
    traceback.print_exc()
    SANDBOX_AVAILABLE = False
    execute_sandboxed = None
    validate_code = None

# Check if QSim is available (needed for sandbox execution)
try:
    from qsim import run_qasm
    QSIM_AVAILABLE = True
    print("✓ QSim module available for hybrid execution")
except ImportError as e:
    print(f"Warning: QSim not available for hybrid execution: {e}")
    QSIM_AVAILABLE = False

# Import config for status endpoint
try:
    from config.config import (
        HYBRID_EXECUTION_ENABLED,
        HYBRID_BLOCK_DANGEROUS_IMPORTS,
        HYBRID_BLOCK_FILE_ACCESS,
        HYBRID_BLOCK_NETWORK,
        HYBRID_BLOCK_SHELL,
        HYBRID_RESTRICT_BUILTINS,
        HYBRID_BLOCK_CODE_EXECUTION,
        HYBRID_MAX_EXECUTION_TIME,
        HYBRID_MAX_MEMORY_MB,
        HYBRID_MAX_SIMULATION_RUNS,
        HYBRID_ALLOWED_MODULES,
    )
except ImportError:
    HYBRID_EXECUTION_ENABLED = False
    HYBRID_BLOCK_DANGEROUS_IMPORTS = True
    HYBRID_BLOCK_FILE_ACCESS = True
    HYBRID_BLOCK_NETWORK = True
    HYBRID_BLOCK_SHELL = True
    HYBRID_RESTRICT_BUILTINS = True
    HYBRID_BLOCK_CODE_EXECUTION = True
    HYBRID_MAX_EXECUTION_TIME = 30
    HYBRID_MAX_MEMORY_MB = 512
    HYBRID_MAX_SIMULATION_RUNS = 100
    HYBRID_ALLOWED_MODULES = []


router = APIRouter(prefix="/api/hybrid", tags=["hybrid"])


class HybridExecuteRequest(BaseModel):
    """Request model for hybrid execution."""
    code: str = Field(..., description="Python code to execute")
    framework: Optional[str] = Field(None, description="Framework hint (cirq, qiskit, pennylane)")
    timeout: Optional[int] = Field(None, description="Execution timeout in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": """
import cirq
from qcanvas import compile
import qsim

q = cirq.LineQubit.range(2)
circuit = cirq.Circuit([
    cirq.H(q[0]),
    cirq.CNOT(q[0], q[1]),
    cirq.measure(q[0], q[1], key='result')
])

qasm = compile(circuit, framework="cirq")
print(f"Generated QASM:\\n{qasm}")

result = qsim.run(qasm, shots=100, backend="cirq")
print(f"Counts: {result.counts}")
""",
                "framework": "cirq",
                "timeout": 30
            }
        }


class HybridValidateRequest(BaseModel):
    """Request model for code validation."""
    code: str = Field(..., description="Python code to validate")


class HybridExecuteResponse(BaseModel):
    """Response model for hybrid execution."""
    success: bool
    stdout: str = ""
    stderr: str = ""
    qasm_generated: Optional[str] = None
    simulation_results: List[Dict[str, Any]] = []
    execution_time: str = ""
    error: Optional[str] = None
    error_line: Optional[int] = None
    error_type: Optional[str] = None


class HybridValidateResponse(BaseModel):
    """Response model for code validation."""
    valid: bool
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None


class HybridStatusResponse(BaseModel):
    """Response model for hybrid execution status."""
    enabled: bool
    sandbox_available: bool
    security_settings: Dict[str, Any]
    limits: Dict[str, Any]
    allowed_modules: List[str]


@router.post("/execute", response_model=HybridExecuteResponse)
async def execute_hybrid(
    request: HybridExecuteRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Execute Python code with quantum circuits in a sandboxed environment.
    
    The code has access to:
    - `from qcanvas import compile` - Compile circuits to QASM
    - `import qsim` and `qsim.run()` - Execute QASM simulations
    - `print()` - Output text (captured and returned)
    - Quantum frameworks: cirq, qiskit, pennylane
    - Safe modules: numpy, math, etc.
    
    Security restrictions are applied based on config settings.
    
    Returns:
        HybridExecuteResponse with stdout, simulation results, and errors
    """
    if not SANDBOX_AVAILABLE:
        return HybridExecuteResponse(
            success=False,
            error="Hybrid execution is not available. Sandbox module failed to load. Check backend logs for details.",
            error_type="ImportError"
        )
    
    if not HYBRID_EXECUTION_ENABLED:
        return HybridExecuteResponse(
            success=False,
            error="Hybrid execution is disabled in configuration. Set HYBRID_EXECUTION_ENABLED=True in config/config.py",
            error_type="DisabledError"
        )
    
    if not QSIM_AVAILABLE:
        return HybridExecuteResponse(
            success=False,
            error="QSim simulation backend is not available. qsim.run() will not work.",
            error_type="ImportError",
            stdout="Note: You can still use qcanvas.compile() for QASM generation."
        )
    
    try:
        # Execute in sandbox
        result = execute_sandboxed(
            code=request.code,
            timeout=request.timeout,
            framework_hint=request.framework
        )
        
        # Convert to response model
        return HybridExecuteResponse(
            success=result.success,
            stdout=result.stdout,
            stderr=result.stderr,
            qasm_generated=result.qasm_generated,
            simulation_results=result.simulation_results,
            execution_time=result.execution_time,
            error=result.error,
            error_line=result.error_line,
            error_type=result.error_type,
        )
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Hybrid execution error: {e}")
        print(error_trace)
        
        return HybridExecuteResponse(
            success=False,
            error=f"Execution failed: {str(e)}",
            error_type=type(e).__name__,
            stderr=error_trace,
        )


@router.post("/validate", response_model=HybridValidateResponse)
async def validate_hybrid(
    request: HybridValidateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Validate Python code without executing it.
    
    Checks for:
    - Syntax errors
    - Blocked imports
    - Dangerous patterns
    
    Returns:
        HybridValidateResponse with validation result
    """
    if not SANDBOX_AVAILABLE:
        return HybridValidateResponse(
            valid=False,
            errors=["Validation is not available. Sandbox module failed to load."]
        )
    
    try:
        result = validate_code(request.code)
        
        return HybridValidateResponse(
            valid=result.get('valid', False),
            errors=result.get('errors'),
            warnings=result.get('warnings'),
        )
        
    except Exception as e:
        return HybridValidateResponse(
            valid=False,
            errors=[f"Validation error: {str(e)}"]
        )


@router.get("/status", response_model=HybridStatusResponse)
async def get_hybrid_status():
    """
    Get the current status and configuration of hybrid execution.
    
    Returns security settings, limits, and available modules.
    """
    return HybridStatusResponse(
        enabled=HYBRID_EXECUTION_ENABLED and SANDBOX_AVAILABLE and QSIM_AVAILABLE,
        sandbox_available=SANDBOX_AVAILABLE,
        security_settings={
            "block_dangerous_imports": HYBRID_BLOCK_DANGEROUS_IMPORTS,
            "block_file_access": HYBRID_BLOCK_FILE_ACCESS,
            "block_network": HYBRID_BLOCK_NETWORK,
            "block_shell": HYBRID_BLOCK_SHELL,
            "restrict_builtins": HYBRID_RESTRICT_BUILTINS,
            "block_code_execution": HYBRID_BLOCK_CODE_EXECUTION,
        },
        limits={
            "max_execution_time": HYBRID_MAX_EXECUTION_TIME,
            "max_memory_mb": HYBRID_MAX_MEMORY_MB,
            "max_simulation_runs": HYBRID_MAX_SIMULATION_RUNS,
        },
        allowed_modules=list(HYBRID_ALLOWED_MODULES),
    )


@router.get("/health")
async def hybrid_health():
    """
    Health check for hybrid execution service.
    """
    issues = []
    if not SANDBOX_AVAILABLE:
        issues.append("Sandbox module not loaded")
    if not QSIM_AVAILABLE:
        issues.append("QSim module not available")
    if not HYBRID_EXECUTION_ENABLED:
        issues.append("Hybrid execution disabled in config")
    
    return {
        "status": "healthy" if not issues else "degraded",
        "sandbox_available": SANDBOX_AVAILABLE,
        "qsim_available": QSIM_AVAILABLE,
        "hybrid_enabled": HYBRID_EXECUTION_ENABLED,
        "issues": issues if issues else None,
    }

