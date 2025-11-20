import pyqasm
from qsim.core.exceptions import ParseError  # Integrate with core
from .allowed_nodes import ALLOWED_NODE_TYPES

def enforce_scope(module: pyqasm.Qasm3Module, strict: bool = True) -> None:
    """
    Enforce supported QASM constructs; raise ParseError if strict.
    """
    unsupported = []
    for stmt in module._statements:
        node_type = type(stmt).__name__
        if node_type not in ALLOWED_NODE_TYPES:
            unsupported.append(node_type)
    
    if strict and unsupported:
        raise ParseError(
            f"Unsupported QASM constructs detected: {', '.join(set(unsupported))}. "
            f"Allowed: {list(ALLOWED_NODE_TYPES)}"
        )
    elif unsupported:
        import logging
        logging.warning(f"Skipped {len(unsupported)} unsupported nodes: {unsupported}")