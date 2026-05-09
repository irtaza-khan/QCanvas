"""
Local configuration variables for quantum converters.
"""

VERBOSE: bool = False
INCLUDE_VARS: bool = False
INCLUDE_CONSTANTS: bool = True

def vprint(*args, **kwargs) -> None:
    """Verbose print helper (no-op unless VERBOSE is True)."""
    if VERBOSE:
        print(*args, **kwargs)
