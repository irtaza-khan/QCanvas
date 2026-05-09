"""
Backward-compatible shim for qcanvas_runtime package.
Delegates everything to the installed qcanvas package.
"""

from qcanvas import compile, compile_and_execute, SimulationResult, HybridExecutionResult

__all__ = [
    'compile',
    'compile_and_execute', 
    'SimulationResult',
    'HybridExecutionResult',
]
