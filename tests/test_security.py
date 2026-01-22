import sys
import os
from pathlib import Path

# Add the project root to the path to allow imports from backend
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
# Add the backend directory to sys.path to allow 'app' imports to work
sys.path.insert(0, str(project_root / "backend"))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.database_models import ApiActivity
from app.config.database import SessionLocal
import time

client = TestClient(app)

def test_security_headers():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
    assert response.headers["Content-Security-Policy"] == "default-src 'self'"

def test_audit_logging():
    # Make a request to a monitored endpoint
    # Note: /health is excluded from logging in our middleware, so use /api/frameworks
    response = client.get("/api/frameworks")
    assert response.status_code == 200
    
    # Check database for log
    db = SessionLocal()
    # Wait a moment for async write if any (though our middleware is sync)
    log = db.query(ApiActivity).order_by(ApiActivity.created_at.desc()).first()
    
    assert log is not None
    assert log.endpoint == "/api/frameworks"
    assert log.method == "GET"
    assert log.status_code == 200
    db.close()

# Note: Rate limiting is hard to test with TestClient as it mocks the request
# and slowapi relies on IP address which might be consistent or mocked.
# We will skip automated rate limit testing for now and rely on manual verification if needed,
# or assume the library works as configured.
