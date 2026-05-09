"""
Backward-compatible shim for qcanvas_runtime.sandbox.
Delegates to qcanvas.sandbox.
"""

from qcanvas.sandbox import execute_sandboxed, validate_code

__all__ = [
    'execute_sandboxed',
    'validate_code'
]
