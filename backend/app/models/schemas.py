from pydantic import BaseModel
from typing import Optional, Literal, List
from uuid import UUID
from datetime import datetime

class ConversionRequest(BaseModel):
    code: str
    framework: Literal["qiskit", "cirq", "pennylane"]
    qasm_version: str = "3.0"
    style: Literal["classic", "compact"] = "classic"

class ConversionResponse(BaseModel):
    success: bool
    qasm_code: Optional[str] = None
    error: Optional[str] = None
    framework: str
    qasm_version: str
    conversion_stats: Optional[dict] = None


class ParsedGate(BaseModel):
    """Schema for a parsed gate in circuit visualization."""
    type: str
    qubit: int
    control: Optional[int] = None
    target: Optional[int] = None
    angle: Optional[float] = None
    timestamp: Optional[int] = None
    name: Optional[str] = None
    qubits: Optional[List[int]] = None


class ParseResponse(BaseModel):
    """Response schema for circuit parsing endpoint."""
    success: bool
    gates: Optional[List[ParsedGate]] = None
    qubits: Optional[int] = None
    error: Optional[str] = None
    framework: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str

# ============================================================================
# Authentication Schemas
# ============================================================================

class UserRegisterRequest(BaseModel):
    """Request schema for user registration."""
    email: str
    username: str
    password: str
    full_name: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "SecurePass123!",
                "full_name": "John Doe"
            }
        }


class UserLoginRequest(BaseModel):
    """Request schema for user login."""
    email: str
    password: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class UserResponse(BaseModel):
    """Response schema for user data (without sensitive info)."""
    id: str
    email: str
    username: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: str
    last_login_at: Optional[str] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "username": "johndoe",
                    "full_name": "John Doe",
                    "role": "user",
                    "is_active": True,
                    "is_verified": False,
                    "created_at": "2024-01-01T00:00:00",
                    "last_login_at": None
                }
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    detail: str


# ============================================================================
# Project & File Schemas
# ============================================================================

class FileCreate(BaseModel):
    filename: str
    content: str
    is_main: bool = False
    is_shared: bool = False
    project_id: Optional[int] = None

class FileUpdate(BaseModel):
    filename: Optional[str] = None
    content: Optional[str] = None
    is_main: Optional[bool] = None
    is_shared: Optional[bool] = None
    project_id: Optional[int] = None

class FileResponse(BaseModel):
    id: int
    user_id: Optional[UUID] = None
    project_id: Optional[int] = None
    filename: str
    content: str
    is_main: bool
    is_shared: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = False

class ProjectResponse(BaseModel):
    id: int
    user_id: UUID
    name: str
    description: Optional[str]
    is_public: bool
    created_at: datetime
    updated_at: datetime
    files: List[FileResponse] = []
    
    class Config:
        from_attributes = True
