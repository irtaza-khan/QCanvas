"""
Top-level QCanvas Python API for Hybrid CPU–QPU execution.

This module is intentionally lightweight and acts as a friendly import shim
so that user code can simply write:

    from qcanvas import compile
    import qsim

without worrying about the internal package layout.
"""

import sys
import os

# Ensure backend package is importable when running from project root
_CURRENT_FILE = os.path.abspath(__file__)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_CURRENT_FILE))
_BACKEND_ROOT = os.path.join(_PROJECT_ROOT, "backend")

if _BACKEND_ROOT not in sys.path:
    sys.path.insert(0, _BACKEND_ROOT)

from qcanvas_runtime.core import compile, compile_and_execute  # type: ignore[attr-defined]
from qcanvas_runtime.result import SimulationResult, HybridExecutionResult  # type: ignore[attr-defined]

__all__ = [
    "compile",
    "compile_and_execute",
    "SimulationResult",
    "HybridExecutionResult",
]


