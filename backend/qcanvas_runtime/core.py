"""
Backward-compatible shim for qcanvas_runtime.core.
Delegates to qcanvas.core.
"""

from qcanvas.core import compile, compile_and_execute

__all__ = [
    'compile',
    'compile_and_execute',
]
