"""Production smoke test.

Hits ``/health``, ``/readiness``, and a minimal ``POST /api/v1/generate``
against a running Cirq-RAG service. Exits 0 on success, non-zero on any
failure.

Usage::

    python scripts/smoke_prod.py --base-url https://cirq-agent.example.com
    python scripts/smoke_prod.py --base-url http://localhost:8001 --api-key $CIRQ_RAG_API_KEY

Environment variable fallbacks:
    CIRQ_RAG_BASE_URL  -> --base-url
    CIRQ_RAG_API_KEY   -> --api-key
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, Optional

try:
    import httpx
except ImportError:  # pragma: no cover - fallback to stdlib
    httpx = None  # type: ignore[assignment]
    import urllib.error
    import urllib.request


def _get(url: str, api_key: Optional[str], timeout: float) -> tuple[int, Dict[str, Any]]:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key

    if httpx is not None:
        r = httpx.get(url, headers=headers, timeout=timeout)
        try:
            body = r.json()
        except ValueError:
            body = {"raw": r.text}
        return r.status_code, body

    req = urllib.request.Request(url, headers=headers)  # type: ignore[name-defined]
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # type: ignore[name-defined]
            return resp.getcode(), json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:  # type: ignore[name-defined]
        try:
            body = json.loads(exc.read().decode("utf-8") or "{}")
        except Exception:
            body = {}
        return exc.code, body


def _post(url: str, api_key: Optional[str], payload: Dict[str, Any], timeout: float):
    headers = {"Accept": "application/json", "Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key

    if httpx is not None:
        r = httpx.post(url, headers=headers, json=payload, timeout=timeout)
        try:
            body = r.json()
        except ValueError:
            body = {"raw": r.text}
        return r.status_code, body

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")  # type: ignore[name-defined]
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # type: ignore[name-defined]
            return resp.getcode(), json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:  # type: ignore[name-defined]
        try:
            body = json.loads(exc.read().decode("utf-8") or "{}")
        except Exception:
            body = {}
        return exc.code, body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=os.getenv("CIRQ_RAG_BASE_URL", "http://localhost:8001"),
        help="Base URL of the Cirq-RAG service (no trailing slash).",
    )
    parser.add_argument(
        "--api-key",
        default=os.getenv("CIRQ_RAG_API_KEY"),
        help="API key for X-API-Key header. Required in prod.",
    )
    parser.add_argument(
        "--skip-generate",
        action="store_true",
        help="Only hit /health and /readiness - skip the Bedrock round-trip.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=120.0,
        help="Per-request timeout in seconds (generate can take 60-120s).",
    )
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    failures: list[str] = []

    # 1. /health
    code, body = _get(f"{base}/health", api_key=None, timeout=10.0)
    print(f"[health] status={code} body={body}")
    if code != 200 or body.get("status") != "ok":
        failures.append("health did not return 200 ok")

    # 2. /readiness
    code, body = _get(f"{base}/readiness", api_key=None, timeout=15.0)
    print(f"[readiness] status={code} body={body}")
    if code not in (200, 503):
        failures.append(f"readiness returned unexpected status {code}")
    elif code == 503:
        failures.append(f"readiness reported degraded: {body}")

    # 3. minimal /api/v1/generate
    if not args.skip_generate:
        payload = {
            "description": "Create a simple Bell state circuit.",
            "enable_optimizer": False,
            "enable_educational": False,
            "max_optimization_loops": 1,
            "educational_depth": "low",
        }
        started = time.monotonic()
        code, body = _post(
            f"{base}/api/v1/generate",
            api_key=args.api_key,
            payload=payload,
            timeout=args.timeout,
        )
        elapsed = time.monotonic() - started
        print(f"[generate] status={code} elapsed={elapsed:.1f}s")
        if code != 200:
            failures.append(f"generate returned {code}: {body}")
        else:
            final_code = body.get("final_code")
            if not final_code or "cirq" not in str(final_code).lower():
                failures.append("generate did not return Cirq code in final_code")

    if failures:
        print("\nSMOKE FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("\nSMOKE OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
