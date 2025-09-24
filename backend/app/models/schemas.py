from pydantic import BaseModel
from typing import Optional, Literal

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

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
