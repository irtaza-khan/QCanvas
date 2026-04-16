"""API-key authentication for the Cirq-RAG HTTP API.

The production deployment sits behind an ALB with no native auth. To keep the
service from being an open door to our Bedrock bill we require every request
to ``/api/v1/*`` to present an ``X-API-Key`` header whose value matches
``CIRQ_RAG_API_KEY``.

Behaviour:
* If ``CIRQ_RAG_API_KEY`` is unset AND ``app.environment`` is not ``production``,
  the dependency is a no-op. This keeps local dev friction-free.
* If ``CIRQ_RAG_API_KEY`` is set (any environment), the key is required on every
  ``/api/v1/*`` request.
* Comparison uses ``hmac.compare_digest`` to avoid trivial timing side-channels.
"""

from __future__ import annotations

import hmac
import os
from typing import Optional

from fastapi import Header, HTTPException, status


def _expected_key() -> Optional[str]:
    key = os.getenv("CIRQ_RAG_API_KEY")
    if key is None:
        return None
    key = key.strip()
    return key or None


def _environment() -> str:
    return (os.getenv("ENVIRONMENT") or "development").strip().lower()


def require_api_key(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
) -> None:
    """FastAPI dependency - raises 401 when the API key is missing or wrong."""
    expected = _expected_key()

    if expected is None:
        if _environment() == "production":
            # Fail closed: refuse to serve traffic in prod without a key set.
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "error": {
                        "code": "api_key_not_configured",
                        "message": (
                            "CIRQ_RAG_API_KEY is not set on the server. "
                            "Refusing to accept requests in production."
                        ),
                        "retryable": False,
                    }
                },
            )
        # Dev: no key configured, let every request through.
        return

    presented = (x_api_key or "").strip()
    if not presented or not hmac.compare_digest(presented, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "invalid_api_key",
                    "message": "Missing or invalid X-API-Key header.",
                    "retryable": False,
                }
            },
            headers={"WWW-Authenticate": "ApiKey"},
        )
