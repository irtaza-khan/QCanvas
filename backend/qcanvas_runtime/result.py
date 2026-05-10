"""
Backward-compatible shim for qcanvas_runtime.result.
Delegates to qcanvas.result.
"""

from qcanvas.result import SimulationResult, HybridExecutionResult

__all__ = [
    'SimulationResult',
    'HybridExecutionResult'
]
