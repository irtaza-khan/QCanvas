"""
FastAPI server for Cirq-RAG-Code-Assistant.

This module exposes a small HTTP API that wraps the Orchestrator so the
QCanvas frontend can drive the full multi-agent pipeline.

Primary endpoints:
* POST /api/v1/generate       - run a pipeline execution (requires API key)
* GET  /api/v1/runs           - list recent runs                (requires API key)
* GET  /api/v1/runs/{run_id}  - fetch a specific run            (requires API key)
* GET  /health                - liveness probe (always open)
* GET  /readiness             - readiness probe (checks deps; always open)

Production hardening implemented here:
* CORS middleware (allowed origins from env).
* ``X-API-Key`` auth on every ``/api/v1/*`` route.
* Redis- or memory-backed run-history store.
* Bedrock throttling / timeouts mapped to HTTP 503 with ``Retry-After``.
* Fail-fast startup validation for required env vars.
* stdout-only JSON logging when ``CIRQ_RAG_LOG_MODE=stdout``.
"""

from __future__ import annotations

import os
import sys
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional, Set

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .auth import require_api_key
from .cirq_rag_code_assistant.config import get_config
from .cirq_rag_code_assistant.config.logging import get_logger, setup_logging
from .cli.commands import get_orchestrator as get_cli_orchestrator
from .orchestration.orchestrator import Orchestrator
from .run_history import RunHistoryStore, build_run_history_store


logger = get_logger(__name__)

_ENVIRONMENT = (os.getenv("ENVIRONMENT") or "development").strip().lower()


# ---------------------------------------------------------------------------
# Startup-time configuration
# ---------------------------------------------------------------------------


def _configure_logging_from_env() -> None:
    """Reconfigure loguru based on ``CIRQ_RAG_LOG_MODE`` / ``CIRQ_RAG_LOG_FORMAT``.

    In prod the container sets ``CIRQ_RAG_LOG_MODE=stdout`` (see Dockerfile)
    which disables file handlers entirely - CloudWatch picks up stdout for us.
    """
    mode = (os.getenv("CIRQ_RAG_LOG_MODE") or "").strip().lower()
    log_format = (os.getenv("CIRQ_RAG_LOG_FORMAT") or "").strip().lower() or "text"
    level = (os.getenv("LOG_LEVEL") or "INFO").upper()

    if mode == "stdout":
        setup_logging(
            log_level=level,
            log_format=log_format,
            enable_console=True,
            enable_file=False,
        )
    elif mode == "file":
        setup_logging(
            log_level=level,
            log_format=log_format,
            enable_console=False,
            enable_file=True,
        )
    elif mode == "both":
        setup_logging(
            log_level=level,
            log_format=log_format,
            enable_console=True,
            enable_file=True,
        )
    # If unset, the module-level logger.bind() is still functional and uses
    # whatever defaults the app picked up during import. No-op path keeps
    # existing behaviour for unit tests.


_REQUIRED_PROD_ENV = (
    "AWS_DEFAULT_REGION",
    "CIRQ_RAG_API_KEY",
)

_REQUIRED_PROD_ENV_WHEN_PGVECTOR = ("CIRQ_RAG_DB_URL",)
_REQUIRED_PROD_ENV_WHEN_REDIS = ("CIRQ_RAG_REDIS_URL",)


def _validate_prod_env() -> None:
    """Fail fast in prod if critical env vars are missing.

    In development we stay silent: devs iterate with partial configs all the
    time. In production we refuse to start rather than 500-ing the first
    request.
    """
    if _ENVIRONMENT != "production":
        return

    missing: List[str] = [k for k in _REQUIRED_PROD_ENV if not os.getenv(k)]

    vector_type = (os.getenv("CIRQ_RAG_VECTOR_STORE_TYPE") or "").strip().lower()
    if vector_type == "pgvector":
        missing.extend(k for k in _REQUIRED_PROD_ENV_WHEN_PGVECTOR if not os.getenv(k))

    history_backend = (os.getenv("CIRQ_RAG_RUN_HISTORY_BACKEND") or "").strip().lower()
    if history_backend == "redis":
        missing.extend(k for k in _REQUIRED_PROD_ENV_WHEN_REDIS if not os.getenv(k))

    if missing:
        logger.error(
            "Refusing to start in production - missing required env vars: %s",
            ", ".join(missing),
        )
        raise SystemExit(
            "Cirq-RAG refuses to start in production with missing env vars: "
            + ", ".join(missing)
        )


_configure_logging_from_env()
_validate_prod_env()


_ALLOWED_ORIGINS: List[str] = [
    o.strip()
    for o in (
        os.getenv("CIRQ_RAG_ALLOWED_ORIGINS")
        if os.getenv("CIRQ_RAG_ALLOWED_ORIGINS") is not None
        else ("*" if _ENVIRONMENT != "production" else "")
    ).split(",")
    if o.strip()
]
_DISABLE_DOCS = (os.getenv("CIRQ_RAG_DISABLE_DOCS") or "").strip().lower() in (
    "1",
    "true",
    "yes",
)


app = FastAPI(
    title="Cirq-RAG-Code-Assistant API",
    version="0.2.0",
    description="HTTP API for the Cirq RAG Code Assistant multi-agent pipeline.",
    docs_url=None if _DISABLE_DOCS else "/docs",
    redoc_url=None if _DISABLE_DOCS else "/redoc",
    openapi_url=None if _DISABLE_DOCS else "/openapi.json",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-API-Key"],
    allow_credentials=False,
)


_RUN_HISTORY: RunHistoryStore = build_run_history_store()


@app.on_event("startup")
async def _log_startup_banner() -> None:
    cfg = get_config()
    logger.info(
        "Cirq-RAG starting | env=%s vector_store=%s embedding_provider=%s "
        "run_history=%s docs=%s allowed_origins=%s",
        cfg.get("app", {}).get("environment"),
        cfg.get("rag", {}).get("vector_store", {}).get("type"),
        cfg.get("models", {}).get("embedding", {}).get("provider"),
        type(_RUN_HISTORY).__name__,
        "disabled" if _DISABLE_DOCS else "enabled",
        _ALLOWED_ORIGINS,
    )


# ---------------------------------------------------------------------------
# JSON safety helper (preserved from the previous implementation)
# ---------------------------------------------------------------------------


def _json_safe(value: Any, _seen: Optional[Set[int]] = None) -> Any:
    """
    Convert arbitrary python objects into JSON-serializable values.

    FastAPI/Pydantic will otherwise error on unknown runtime types (e.g.
    ``cirq.Circuit``).
    """
    if _seen is None:
        _seen = set()

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    obj_id = id(value)
    if obj_id in _seen:
        return str(value)
    _seen.add(obj_id)

    if isinstance(value, dict):
        return {str(k): _json_safe(v, _seen) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(v, _seen) for v in value]

    try:
        import cirq  # type: ignore

        if isinstance(value, cirq.Circuit):
            return repr(value)
    except Exception:
        pass

    return str(value)


# ---------------------------------------------------------------------------
# Schemas (unchanged public shape)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Orchestrator factory (unchanged - reuses the CLI's singleton)
# ---------------------------------------------------------------------------


def _get_orchestrator(req: GenerateRequest) -> Orchestrator:
    return get_cli_orchestrator()


def _build_agent_steps(orchestrator_result: Dict[str, Any]) -> List[AgentStep]:
    stages: List[str] = orchestrator_result.get("stages", [])
    steps: List[AgentStep] = []

    if "designer" in stages:
        steps.append(
            AgentStep(
                name="designer",
                status="success",
                summary="Initial Cirq code generated from prompt.",
                code=orchestrator_result.get("code"),
            )
        )

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


# ---------------------------------------------------------------------------
# Error translation - wrap Bedrock throttling / timeouts into HTTP 503
# ---------------------------------------------------------------------------


def _classify_error(exc: BaseException) -> Optional[Dict[str, Any]]:
    """
    Decide whether an exception is a known transient AWS/Bedrock failure and,
    if so, produce a structured envelope. Returns None if the error is not
    recognised as retryable - the caller should re-raise or 500.
    """
    name = type(exc).__name__
    message = str(exc)

    # boto/botocore ClientError instances carry a dict response with Error.Code.
    err_code = None
    response = getattr(exc, "response", None)
    if isinstance(response, dict):
        err_code = (response.get("Error") or {}).get("Code")

    retryable_codes = {
        "ThrottlingException",
        "TooManyRequestsException",
        "ServiceUnavailableException",
        "ModelTimeoutException",
        "RequestTimeout",
        "RequestTimeoutException",
    }

    if err_code in retryable_codes or name in retryable_codes or "Throttling" in name:
        return {
            "error": {
                "code": err_code or name or "throttled",
                "message": message or "Upstream model provider throttled the request.",
                "retryable": True,
            }
        }

    if "ReadTimeout" in name or "ConnectTimeout" in name or "Timeout" in name:
        return {
            "error": {
                "code": "upstream_timeout",
                "message": message or "Upstream model provider timed out.",
                "retryable": True,
            }
        }

    return None


@app.exception_handler(Exception)
async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Translate known transient failures into 503 with Retry-After."""
    envelope = _classify_error(exc)
    if envelope is not None:
        logger.warning("Upstream transient failure: %s", exc)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=envelope,
            headers={"Retry-After": "15"},
        )

    logger.exception("Unhandled server error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "internal_error",
                "message": "An unexpected server error occurred.",
                "retryable": False,
            }
        },
    )


# ---------------------------------------------------------------------------
# Public endpoints
# ---------------------------------------------------------------------------


@app.get("/health", include_in_schema=False)
def health() -> Dict[str, str]:
    """Liveness probe: proves the process is up. Always open."""
    return {"status": "ok"}


@app.get("/readiness", include_in_schema=False)
def readiness() -> Dict[str, Any]:
    """Readiness probe: checks that deps the request path needs are reachable.

    Kept deliberately cheap - used by ECS/ALB health checks every 30s.
    """
    checks: Dict[str, Any] = {"status": "ok", "components": {}}

    # Run-history store.
    try:
        _RUN_HISTORY.list(limit=1)
        checks["components"]["run_history"] = "ok"
    except Exception as exc:
        checks["status"] = "degraded"
        checks["components"]["run_history"] = f"error: {exc}"

    # Postgres/pgvector, if configured.
    if (os.getenv("CIRQ_RAG_VECTOR_STORE_TYPE") or "").strip().lower() == "pgvector":
        dsn = os.getenv("CIRQ_RAG_DB_URL")
        if not dsn:
            checks["status"] = "degraded"
            checks["components"]["postgres"] = "CIRQ_RAG_DB_URL not set"
        else:
            try:
                import psycopg

                with psycopg.connect(dsn, connect_timeout=3) as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1")
                        cur.fetchone()
                checks["components"]["postgres"] = "ok"
            except Exception as exc:
                checks["status"] = "degraded"
                checks["components"]["postgres"] = f"error: {exc}"

    if checks["status"] != "ok":
        return JSONResponse(status_code=503, content=checks)  # type: ignore[return-value]
    return checks


@app.post(
    "/api/v1/generate",
    response_model=GenerateResponse,
    dependencies=[Depends(require_api_key)],
)
def generate(req: GenerateRequest) -> GenerateResponse:
    """Run the full multi-agent pipeline for a single prompt."""
    started = time.monotonic()
    logger.info(
        "Received generate request (algorithm=%s, validator=%s, optimizer=%s, "
        "educational=%s, educational_depth=%s)",
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

    serializable_result = _json_safe(result)

    status_text = "completed" if result.get("success") else "error"
    run_id = str(uuid.uuid4())
    created_at = datetime.utcnow()

    agents = _build_agent_steps(result)
    final_code = result.get("optimized_code") or result.get("code")

    response = GenerateResponse(
        run_id=run_id,
        status=status_text,
        created_at=created_at,
        prompt=req.description,
        algorithm=req.algorithm,
        agents=agents,
        final_code=final_code,
        explanation=result.get("explanation"),
        raw_result=serializable_result,
    )

    try:
        # Store a JSON-safe dict; Pydantic's model_dump gives us exactly that.
        _RUN_HISTORY.put(run_id, _json_safe(response.model_dump(mode="json")))
    except Exception as exc:
        # Persisting run history is best-effort; never fail the request for it.
        logger.warning("Failed to persist run history for %s: %s", run_id, exc)

    elapsed = time.monotonic() - started
    logger.info("Completed run %s in %.2fs (status=%s)", run_id, elapsed, status_text)
    return response


@app.get(
    "/api/v1/runs",
    response_model=List[RunSummary],
    dependencies=[Depends(require_api_key)],
)
def list_runs() -> List[RunSummary]:
    """List recent runs in reverse chronological order."""
    summaries: List[RunSummary] = []
    for r in _RUN_HISTORY.list(limit=50):
        prompt = r.get("prompt", "") or ""
        prompt_preview = (prompt[:120] + "...") if len(prompt) > 120 else prompt
        agents = r.get("agents") or []
        agent_names = {(a.get("name") or "") for a in agents if isinstance(a, dict)}
        summaries.append(
            RunSummary(
                run_id=r.get("run_id", ""),
                created_at=r.get("created_at") or datetime.utcnow(),
                prompt_preview=prompt_preview,
                status=r.get("status", "unknown"),
                enable_validator=any(n.startswith("validator") for n in agent_names),
                enable_optimizer="optimizer" in agent_names,
                enable_educational="educational" in agent_names,
            )
        )
    return summaries


@app.get(
    "/api/v1/runs/{run_id}",
    response_model=RunDetail,
    dependencies=[Depends(require_api_key)],
)
def get_run(run_id: str) -> RunDetail:
    """Fetch details for a specific run."""
    run = _RUN_HISTORY.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunDetail(**run)


def get_app() -> FastAPI:
    """
    Uvicorn entrypoint helper:
    ``uvicorn src.server:get_app`` (with appropriate PYTHONPATH).
    """
    return app
