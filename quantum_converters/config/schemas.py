from typing import Dict, List, Literal
from pydantic import BaseModel, Field


Framework = Literal["qiskit", "cirq", "pennylane"]


class GateMap(BaseModel):
    """Mapping for a single canonical gate into a framework-specific representation.

    - openqasm_gate: OpenQASM 3 mnemonic (e.g., "rx")
    - target_gate: Framework-specific gate identifier (e.g., "qml.RX" or "RX")
    - param_order: Parameter names in order expected by the target gate
    - inversible: Whether an inverse exists within Iteration I scope
    - notes: Optional note for maintainers
    """

    openqasm_gate: str = Field(..., min_length=1)
    target_gate: str = Field(..., min_length=1)
    param_order: List[str] = Field(default_factory=list)
    inversible: bool = True
    notes: str = ""


class FrameworkGateRegistry(BaseModel):
    """Registry mapping canonical gate ids (e.g., "x", "rx") to GateMap."""

    framework: Framework
    mapping: Dict[str, GateMap]

    class Config:
        frozen = True  # make instances immutable


