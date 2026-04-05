"""
Reverse proxy to the Cirq-RAG-Code-Assistant FastAPI service.

Browser calls: {QCanvas API}/api/cirq-agent/api/v1/...
Forwarded to:  {CIRQ_AGENT_URL}/api/v1/...

Uses a long read timeout because the pipeline is synchronous and often 15–60+ seconds.
"""

from __future__ import annotations

import httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse

from app.config.settings import settings

router = APIRouter(prefix="/api/cirq-agent", tags=["cirq-agent"])

_CIRQ_TIMEOUT = httpx.Timeout(120.0, connect=15.0)

_HOP_BY_HOP = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
        "host",
        "content-length",
    }
)


def _forward_request_headers(request: Request) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, value in request.headers.items():
        lk = key.lower()
        if lk in _HOP_BY_HOP:
            continue
        out[key] = value
    return out


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"],
)
async def proxy_cirq_agent(path: str, request: Request) -> Response:
    base = settings.CIRQ_AGENT_URL.rstrip("/")
    url = f"{base}/{path}"
    q = str(request.query_params)
    if q:
        url = f"{url}?{q}"

    body = await request.body()
    headers = _forward_request_headers(request)

    async with httpx.AsyncClient(timeout=_CIRQ_TIMEOUT) as client:
        try:
            upstream = await client.request(
                request.method,
                url,
                content=body if body else None,
                headers=headers,
            )
        except httpx.ConnectError:
            return JSONResponse(
                status_code=503,
                content={
                    "detail": "Could not connect to the Cirq AI backend. "
                    "Ensure the service is running and CIRQ_AGENT_URL is correct."
                },
            )
        except httpx.TimeoutException:
            return JSONResponse(
                status_code=504,
                content={
                    "detail": "The Cirq AI pipeline timed out. Try a simpler prompt or reduce max optimization loops."
                },
            )

    ct = upstream.headers.get("content-type", "application/json")
    return Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=ct,
    )
