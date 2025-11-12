"""
Gate Mapping Schema Definitions

WHAT THIS FILE DOES:
    Defines Pydantic data models for gate mapping structures. Provides type-safe
    schemas for FrameworkGateRegistry and GateMap, ensuring consistent gate mapping
    definitions across the codebase. Used by mappings.py to define framework gate
    registries.

HOW IT LINKS TO OTHER FILES:
    - Used by: mappings.py (defines FrameworkGateRegistry and GateMap structures)
    - Part of: Config module providing data schemas

INPUT:
    - Gate mapping data: Gate names, OpenQASM mnemonics, parameter orders
    - Used in: FrameworkGateRegistry and GateMap constructors

OUTPUT:
    - GateMap: Schema for individual gate mappings
    - FrameworkGateRegistry: Schema for framework gate registries
    - Returned by: Pydantic model constructors

STAGE OF USE:
    - Configuration Stage: Used when defining gate mappings
    - Validation Stage: Pydantic validates mapping data structure
    - Used throughout: Gate mapping access and validation

TOOLS USED:
    - pydantic.BaseModel: Data validation and serialization
    - pydantic.Field: Field definitions with constraints
    - typing: Type hints (Dict, List, Literal)

SCHEMA STRUCTURE:
    - GateMap: Individual gate mapping with openqasm_gate, target_gate, param_order, etc.
    - FrameworkGateRegistry: Container for framework gate mappings (frozen/immutable)

ARCHITECTURE ROLE:
    Provides type-safe data structures for gate mappings. Ensures data integrity
    and consistency through Pydantic validation. Foundation for the gate mapping
    configuration system.

Author: QCanvas Team
Date: 2025-08-07
Version: 1.0.0
"""

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


