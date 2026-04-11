"""Compatibility package for legacy quantum_simulator imports."""

from .core import BaseBackend, DensityMatrixBackend, StabilizerBackend, StatevectorBackend

__all__ = [
    "BaseBackend",
    "DensityMatrixBackend",
    "StabilizerBackend",
    "StatevectorBackend",
]