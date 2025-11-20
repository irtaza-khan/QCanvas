# core/exceptions.py

class QSimError(Exception):
    """Base class for all qsim-related errors."""

class ParseError(QSimError):
    """Raised when a QASM file or circuit description cannot be parsed."""

class UnsupportedBackend(QSimError):
    """Raised when a requested backend is not supported or recognized."""