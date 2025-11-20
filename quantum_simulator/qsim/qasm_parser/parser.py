import logging
from typing import Union
from pathlib import Path
import pyqasm

from .scope import enforce_scope
from .allowed_nodes import ALLOWED_NODE_TYPES  # For docs/error msgs
from qsim.core.exceptions import ParseError

logger = logging.getLogger(__name__)

def parse_openqasm3(qasm_code: Union[str, Path], unroll: bool = False, strict_scope: bool = True) -> pyqasm.Qasm3Module:
    """
    Parses OpenQASM 3 code, enforces QSim scope, and returns the AST.

    Args:
        qasm_code: QASM3 string or .qasm file path.
        unroll: If True, unroll loops in the AST (via pyqasm).
        strict_scope: If True, raise ParseError on unsupported nodes; else, warn.

    Returns:
        pyqasm.Qasm3Module: The parsed AST.

    Raises:
        ParseError: On syntax errors or (if strict) unsupported constructs.
    """
    # Handle file input
    if isinstance(qasm_code, Path):
        if not qasm_code.exists():
            raise ParseError(f"QASM file not found: {qasm_code}")
        qasm_code = qasm_code.read_text(encoding='utf-8')
    
    if not qasm_code.strip():
        raise ParseError("Empty QASM input provided.")

    try:
        module = pyqasm.loads(qasm_code)
        logger.info(f"Successfully parsed QASM3 with {len(module._statements)} statements.")
    except Exception as e:
        raise ParseError(f"Failed to parse OpenQASM 3 code: {e}") from e

    # Scope enforcement (modular call)
    enforce_scope(module, strict=strict_scope)

    # Optional loop unrolling
    if unroll:
        module.unroll()
        logger.debug("Loops unrolled in AST.")

    return module