"""
FastAPI server for Cirq-RAG-Code-Assistant.

This module exposes a simple HTTP API that wraps the Orchestrator
so the React frontend can drive the full multi-agent pipeline.

Primary endpoints:
- POST /api/v1/generate  -> run a pipeline execution
- GET  /api/v1/runs      -> list recent runs (in-memory history)
- GET  /api/v1/runs/{id} -> fetch a specific run
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Set

from .cirq_rag_code_assistant.config.logging import get_logger
from .orchestration.orchestrator import Orchestrator
from .cli.commands import get_orchestrator as get_cli_orchestrator


logger = get_logger(__name__)

app = FastAPI(
    title="Cirq-RAG-Code-Assistant API",
    version="0.1.0",
    description="HTTP API for the Cirq RAG Code Assistant multi-agent pipeline.",
)


def _json_safe(value: Any, _seen: Optional[Set[int]] = None) -> Any:
    """
    Convert arbitrary python objects into JSON-serializable values.

    FastAPI/Pydantic will otherwise error on unknown runtime types (e.g. `cirq.Circuit`).
    """
    if _seen is None:
        _seen = set()

    # Basic primitives
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    # Prevent infinite recursion on self-referential objects
    obj_id = id(value)
    if obj_id in _seen:
        return str(value)
    _seen.add(obj_id)

    # Collections
    if isinstance(value, dict):
        return {str(k): _json_safe(v, _seen) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v, _seen) for v in value]

    # Cirq objects (not JSON-serializable by default)
    try:
        import cirq  # type: ignore

        if isinstance(value, cirq.Circuit):
            return repr(value)
    except Exception:
        # If cirq isn't available or type check fails, fall back to string.
        pass

    # Fallback: string representation
    return str(value)


class GenerateRequest(BaseModel):
    description: str = Field(..., description="Natural language description of the desired quantum program.")
    algorithm: Optional[str] = Field(
        default=None,
        description="Optional algorithm hint (e.g., 'vqe', 'qaoa', 'grover').",
    )
    enable_designer: bool = Field(default=True, description="Whether to run the Designer stage.")
    enable_validator: bool = Field(default=True, description="Whether to run the Validator stages.")
    enable_optimizer: bool = Field(default=True, description="Whether to run the Optimizer stage.")
    enable_final_validator: bool = Field(default=True, description="Whether to run the Final Validator stage.")
    enable_educational: bool = Field(default=True, description="Whether to run the Educational agent.")
    max_optimization_loops: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum optimizer/validator loop iterations.",
    )
    educational_depth: Optional[
        Literal["low", "intermediate", "high", "very_high"]
    ] = Field(
        default="intermediate",
        description="How detailed the educational explanation should be.",
    )


class AgentStep(BaseModel):
    name: str
    status: str
    summary: Optional[str] = None
    code: Optional[str] = None
    logs: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class GenerateResponse(BaseModel):
    run_id: str
    status: str
    created_at: datetime
    prompt: str
    algorithm: Optional[str]
    agents: List[AgentStep]
    final_code: Optional[str]
    explanation: Optional[Dict[str, Any]] = None
    raw_result: Dict[str, Any]


class RunSummary(BaseModel):
    run_id: str
    created_at: datetime
    prompt_preview: str
    status: str
    enable_validator: bool
    enable_optimizer: bool
    enable_educational: bool


class RunDetail(GenerateResponse):
    pass


_RUN_HISTORY: Dict[str, GenerateResponse] = {}
_MAX_HISTORY = 50


def _get_orchestrator(req: GenerateRequest) -> Orchestrator:
    """
    Get the shared Orchestrator instance used by the CLI.
    This reuses the same RAG stack (EmbeddingModel, VectorStore, KnowledgeBase)
    and agent wiring (Designer, Optimizer, Validator, Educational).
    """
    orchestrator = get_cli_orchestrator()
    return orchestrator


def _build_agent_steps(orchestrator_result: Dict[str, Any]) -> List[AgentStep]:
    """
    Adapt the orchestrator's result dictionary into a list of AgentStep
    entries that the frontend can render in a pipeline timeline.
    """
    stages: List[str] = orchestrator_result.get("stages", [])
    steps: List[AgentStep] = []

    # Designer
    if "designer" in stages:
        steps.append(
            AgentStep(
                name="designer",
                status="success",
                summary="Initial Cirq code generated from prompt.",
                code=orchestrator_result.get("code"),
            )
        )

    # Initial validator
    if "validator" in stages:
        validation = orchestrator_result.get("validation") or {}
        steps.append(
            AgentStep(
                name="validator",
                status="success" if validation.get("validation_passed") else "warning",
                summary="Initial validation of generated code.",
                metrics={
                    "validation_passed": validation.get("validation_passed"),
                    "details": validation.get("details"),
                },
            )
        )

    # Optimizer
    if "optimizer" in stages:
        optimization_metrics = orchestrator_result.get("optimization_metrics") or {}
        steps.append(
            AgentStep(
                name="optimizer",
                status="success" if optimization_metrics else "info",
                summary="Circuit optimization and resource reduction.",
                code=orchestrator_result.get("optimized_code") or orchestrator_result.get("code"),
                metrics=optimization_metrics,
            )
        )

    # Final validator
    if "final_validator" in stages:
        final_validation = orchestrator_result.get("final_validation") or {}
        steps.append(
            AgentStep(
                name="final_validator",
                status="success" if final_validation.get("validation_passed") else "warning",
                summary="Final validation of the (possibly optimized) circuit.",
                metrics={
                    "validation_passed": final_validation.get("validation_passed"),
                    "details": final_validation.get("details"),
                },
            )
        )

    # Educational
    if "educational" in stages:
        explanation = orchestrator_result.get("explanation") or {}
        steps.append(
            AgentStep(
                name="educational",
                status="success" if explanation else "info",
                summary="Educational explanations and learning materials.",
                metrics={"has_explanations": bool(explanation)},
            )
        )

    return steps


@app.post("/api/v1/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest) -> GenerateResponse:
    """
    Run the full multi-agent pipeline for a single prompt.
    """
    logger.info(
        "Received generate request (algorithm=%s, validator=%s, optimizer=%s, educational=%s, educational_depth=%s)",
        req.algorithm,
        req.enable_validator,
        req.enable_optimizer,
        req.enable_educational,
        req.educational_depth,
    )

    orchestrator = _get_orchestrator(req)

    result = orchestrator.generate_code(
        query=req.description,
        algorithm=req.algorithm,
        designer=req.enable_designer,
        optimize=req.enable_optimizer,
        validate=req.enable_validator,
        final_validate=req.enable_final_validator,
        explain=req.enable_educational,
        max_optimization_loops=req.max_optimization_loops,
        educational_depth=req.educational_depth,
    )

    # Ensure raw_result is fully JSON-serializable for FastAPI/Pydantic.
    # Validator currently includes a `cirq.Circuit` object inside `validation.compilation`,
    # which otherwise causes `PydanticSerializationError` (HTTP 500).
    serializable_result = _json_safe(result)

    status = "completed" if result.get("success") else "error"
    run_id = str(uuid.uuid4())
    created_at = datetime.utcnow()

    agents = _build_agent_steps(result)
    final_code = result.get("optimized_code") or result.get("code")

    response = GenerateResponse(
        run_id=run_id,
        status=status,
        created_at=created_at,
        prompt=req.description,
        algorithm=req.algorithm,
        agents=agents,
        final_code=final_code,
        explanation=result.get("explanation"),
        raw_result=serializable_result,
    )

    _RUN_HISTORY[run_id] = response
    if len(_RUN_HISTORY) > _MAX_HISTORY:
        # Drop oldest entry
        oldest_id = sorted(_RUN_HISTORY.values(), key=lambda r: r.created_at)[0].run_id
        _RUN_HISTORY.pop(oldest_id, None)

    return response


@app.get("/api/v1/runs", response_model=List[RunSummary])
def list_runs() -> List[RunSummary]:
    """
    List recent runs in reverse chronological order.
    """
    runs = sorted(_RUN_HISTORY.values(), key=lambda r: r.created_at, reverse=True)
    summaries: List[RunSummary] = []
    for r in runs:
        summaries.append(
            RunSummary(
                run_id=r.run_id,
                created_at=r.created_at,
                prompt_preview=(r.prompt[:120] + "...") if len(r.prompt) > 120 else r.prompt,
                status=r.status,
                enable_validator=bool(
                    any(step.name.startswith("validator") for step in r.agents)
                ),
                enable_optimizer=bool(
                    any(step.name == "optimizer" for step in r.agents)
                ),
                enable_educational=bool(
                    any(step.name == "educational" for step in r.agents)
                ),
            )
        )
    return summaries


@app.get("/api/v1/runs/{run_id}", response_model=RunDetail)
def get_run(run_id: str) -> RunDetail:
    """
    Fetch details for a specific run.
    """
    run = _RUN_HISTORY.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunDetail(**run.dict())


def get_app() -> FastAPI:
    """
    Uvicorn entrypoint helper:
    `uvicorn src.server:get_app` (with appropriate PYTHONPATH).
    """
    return app

