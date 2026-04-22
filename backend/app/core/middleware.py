import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from app.config.database import SessionLocal
from app.models.database_models import ApiActivity
from app.utils.jwt_auth import get_user_id_from_token
import hashlib

# Initialize Limiter
limiter = Limiter(key_func=get_remote_address)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Add your API domain to the connect-src so the browser allows the fetch
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "connect-src 'self' https://api.qcanvas.codes https://www.qcanvas.codes; " 
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://fastapi.tiangolo.com"
        )
        return response

class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        process_time = (time.time() - start_time) * 1000
        
        # Don't log OPTIONS requests or health checks to reduce noise
        if request.method == "OPTIONS" or request.url.path in ["/health", "/api/health"]:
            return response

        # Extract user info if available
        user_id = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            user_id = get_user_id_from_token(token)

        # Log to database
        db = SessionLocal()
        try:
            activity = ApiActivity(
                user_id=user_id,
                endpoint=request.url.path,
                method=request.method,
                status_code=response.status_code,
                ip_address=request.client.host,
                user_agent=request.headers.get("user-agent", "unknown"),
                response_time_ms=int(process_time)
            )
            db.add(activity)
            db.commit()
        except Exception as e:
            print(f"Failed to write audit log: {e}")
        finally:
            db.close()
            
        return response
