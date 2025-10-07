"""
Typed, validated, read-only configuration registries for quantum converters.

This package centralizes domain configuration such as framework-to-OpenQASM
gate mappings. Keep runtime/environment flags in `config/config.py` and
domain-specific registries here alongside the conversion layer.
"""

from .schemas import Framework, GateMap, FrameworkGateRegistry  # re-export types
from .mappings import (
    PENNYLANE_TO_QASM_REGISTRY,
    get_pl_to_qasm_mapping,
    get_pl_inverse_qasm_map,
    QISKIT_TO_QASM_REGISTRY,
    get_qiskit_inverse_qasm_map,
    CIRQ_TO_QASM_REGISTRY,
    get_cirq_inverse_qasm_map,
)

__all__ = [
    "Framework",
    "GateMap",
    "FrameworkGateRegistry",
    "PENNYLANE_TO_QASM_REGISTRY",
    "get_pl_to_qasm_mapping",
    "get_pl_inverse_qasm_map",
    "QISKIT_TO_QASM_REGISTRY",
    "get_qiskit_inverse_qasm_map",
    "CIRQ_TO_QASM_REGISTRY",
    "get_cirq_inverse_qasm_map",
]


