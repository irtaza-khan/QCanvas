"""
Backward-compatible shim for qcanvas_runtime.qsim.
Delegates to qcanvas.qsim.
"""

from qcanvas.qsim import (
    run,
    run_batch,
    get_simulation_results,
    clear_simulation_results,
    execute,
    simulate
)

__all__ = [
    'run',
    'run_batch',
    'get_simulation_results',
    'clear_simulation_results',
    'execute',
    'simulate'
]
