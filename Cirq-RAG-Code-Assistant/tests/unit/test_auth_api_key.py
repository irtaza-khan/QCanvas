"""Unit tests for the API-key auth dependency."""

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI, HTTPException
from fastapi.testclient import TestClient

from src.auth import require_api_key


def _app() -> FastAPI:
    app = FastAPI()

    @app.get("/protected", dependencies=[Depends(require_api_key)])
    def _protected() -> dict:
        return {"ok": True}

    @app.get("/open")
    def _open() -> dict:
        return {"ok": True}

    return app


# ---------------------------------------------------------------------------
# Dev mode: no key configured -> protected routes remain accessible.
# ---------------------------------------------------------------------------


def test_dev_without_key_allows_request(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CIRQ_RAG_API_KEY", raising=False)
    monkeypatch.setenv("ENVIRONMENT", "development")

    client = TestClient(_app())
    resp = client.get("/protected")

    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


# ---------------------------------------------------------------------------
# Prod mode: missing key config -> fail closed with 503.
# ---------------------------------------------------------------------------


def test_prod_without_key_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CIRQ_RAG_API_KEY", raising=False)
    monkeypatch.setenv("ENVIRONMENT", "production")

    client = TestClient(_app())
    resp = client.get("/protected")

    assert resp.status_code == 503
    body = resp.json()
    assert body["detail"]["error"]["code"] == "api_key_not_configured"


# ---------------------------------------------------------------------------
# Key configured: header must match.
# ---------------------------------------------------------------------------


def test_missing_header_returns_401(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CIRQ_RAG_API_KEY", "s3cret")
    monkeypatch.setenv("ENVIRONMENT", "development")

    client = TestClient(_app())
    resp = client.get("/protected")

    assert resp.status_code == 401
    assert resp.headers["WWW-Authenticate"] == "ApiKey"


def test_wrong_header_returns_401(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CIRQ_RAG_API_KEY", "s3cret")
    monkeypatch.setenv("ENVIRONMENT", "development")

    client = TestClient(_app())
    resp = client.get("/protected", headers={"X-API-Key": "wrong"})

    assert resp.status_code == 401


def test_correct_header_is_allowed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CIRQ_RAG_API_KEY", "s3cret")
    monkeypatch.setenv("ENVIRONMENT", "development")

    client = TestClient(_app())
    resp = client.get("/protected", headers={"X-API-Key": "s3cret"})

    assert resp.status_code == 200
    assert resp.json() == {"ok": True}


def test_auth_does_not_apply_to_unprotected_routes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CIRQ_RAG_API_KEY", "s3cret")
    monkeypatch.setenv("ENVIRONMENT", "development")

    client = TestClient(_app())
    resp = client.get("/open")

    assert resp.status_code == 200
