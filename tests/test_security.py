import pytest
from fastapi.testclient import TestClient
import time
from sqlalchemy.exc import OperationalError

try:
    from backend.app.main import app
    # Import DB symbols from the same module namespace used by app bootstrap
    # to avoid loading model modules twice under different package names.
    from app.models.database_models import ApiActivity
    from app.config.database import SessionLocal
except ModuleNotFoundError as e:
    pytest.skip(f"Security tests require optional deps: {e}", allow_module_level=True)

client = TestClient(app)

def test_security_headers():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
    csp = response.headers.get("Content-Security-Policy", "")
    assert "default-src 'self'" in csp

def test_audit_logging():
    # Make a request to a monitored endpoint
    # Note: /health is excluded from logging in our middleware, so use /api/frameworks
    response = client.get("/api/frameworks")
    assert response.status_code == 200
    
    # Check database for log
    db = SessionLocal()
    try:
        # Wait a moment for async write if any (though our middleware is sync)
        log = db.query(ApiActivity).order_by(ApiActivity.created_at.desc()).first()
    except OperationalError as exc:
        pytest.skip(f"PostgreSQL not available for audit log validation: {exc}")
    finally:
        db.close()

    assert log is not None
    assert log.endpoint == "/api/frameworks"
    assert log.method == "GET"
    assert log.status_code == 200

# Note: Rate limiting is hard to test with TestClient as it mocks the request
# and slowapi relies on IP address which might be consistent or mocked.
# We will skip automated rate limit testing for now and rely on manual verification if needed,
# or assume the library works as configured.
