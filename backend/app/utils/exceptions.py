"""
QCanvas Custom Exceptions

This module defines custom exception classes for the QCanvas application,
providing detailed error handling and proper HTTP status codes for
different types of errors that can occur during quantum circuit conversion
and simulation.

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

from typing import Optional, Dict, Any


class QCanvasException(Exception):
    """
    Base exception class for QCanvas application.
    
    This is the base exception class that all other QCanvas exceptions
    inherit from. It provides common functionality for error handling
    and HTTP status code management.
    """
    
    def __init__(
        self,
        message: str,
        error_type: str = "QCanvasError",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize QCanvas exception.
        
        Args:
            message: Human-readable error message
            error_type: Type identifier for the error
            status_code: HTTP status code for the error
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.status_code = status_code
        self.details = details or {}


class ConversionError(QCanvasException):
    """
    Exception raised during quantum circuit conversion.
    
    This exception is raised when errors occur during the conversion
    process between different quantum computing frameworks.
    """
    
    def __init__(
        self,
        message: str,
        source_framework: Optional[str] = None,
        target_framework: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize conversion error.
        
        Args:
            message: Error message
            source_framework: Source framework name
            target_framework: Target framework name
            details: Additional error details
        """
        super().__init__(
            message=message,
            error_type="ConversionError",
            status_code=400,
            details=details or {}
        )
        self.source_framework = source_framework
        self.target_framework = target_framework


class FrameworkNotSupportedError(ConversionError):
    """
    Exception raised when a quantum computing framework is not supported.
    
    This exception is raised when attempting to use a framework that
    is not currently supported by the QCanvas conversion system.
    """
    
    def __init__(self, framework: str, supported_frameworks: Optional[list] = None):
        """
        Initialize framework not supported error.
        
        Args:
            framework: Unsupported framework name
            supported_frameworks: List of supported frameworks
        """
        message = f"Framework '{framework}' is not supported"
        if supported_frameworks:
            message += f". Supported frameworks: {', '.join(supported_frameworks)}"
        
        super().__init__(
            message=message,
            details={
                "unsupported_framework": framework,
                "supported_frameworks": supported_frameworks or []
            }
        )
        self.error_type = "FrameworkNotSupportedError"


class CircuitValidationError(ConversionError):
    """
    Exception raised when circuit validation fails.
    
    This exception is raised when a quantum circuit fails validation
    checks during the conversion process.
    """
    
    def __init__(self, message: str, validation_errors: Optional[list] = None):
        """
        Initialize circuit validation error.
        
        Args:
            message: Validation error message
            validation_errors: List of specific validation errors
        """
        super().__init__(
            message=message,
            details={
                "validation_errors": validation_errors or []
            }
        )
        self.error_type = "CircuitValidationError"
        self.validation_errors = validation_errors or []


class SimulationError(QCanvasException):
    """
    Exception raised during quantum circuit simulation.
    
    This exception is raised when errors occur during the simulation
    process of quantum circuits.
    """
    
    def __init__(
        self,
        message: str,
        backend: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize simulation error.
        
        Args:
            message: Error message
            backend: Simulation backend name
            details: Additional error details
        """
        super().__init__(
            message=message,
            error_type="SimulationError",
            status_code=400,
            details=details or {}
        )
        self.backend = backend


class BackendNotAvailableError(SimulationError):
    """
    Exception raised when a simulation backend is not available.
    
    This exception is raised when attempting to use a simulation backend
    that is not currently available or properly configured.
    """
    
    def __init__(self, backend: str, available_backends: Optional[list] = None):
        """
        Initialize backend not available error.
        
        Args:
            backend: Unavailable backend name
            available_backends: List of available backends
        """
        message = f"Backend '{backend}' is not available"
        if available_backends:
            message += f". Available backends: {', '.join(available_backends)}"
        
        super().__init__(
            message=message,
            backend=backend,
            details={
                "unavailable_backend": backend,
                "available_backends": available_backends or []
            }
        )
        self.error_type = "BackendNotAvailableError"


class CircuitTooLargeError(SimulationError):
    """
    Exception raised when a circuit exceeds size limits.
    
    This exception is raised when attempting to simulate a circuit
    that exceeds the maximum allowed size for the selected backend.
    """
    
    def __init__(self, circuit_qubits: int, max_qubits: int, backend: Optional[str] = None):
        """
        Initialize circuit too large error.
        
        Args:
            circuit_qubits: Number of qubits in the circuit
            max_qubits: Maximum allowed qubits
            backend: Simulation backend name
        """
        message = f"Circuit has {circuit_qubits} qubits, but maximum allowed is {max_qubits}"
        if backend:
            message += f" for backend '{backend}'"
        
        super().__init__(
            message=message,
            backend=backend,
            details={
                "circuit_qubits": circuit_qubits,
                "max_qubits": max_qubits,
                "backend": backend
            }
        )
        self.error_type = "CircuitTooLargeError"


class ResourceLimitError(QCanvasException):
    """
    Exception raised when resource limits are exceeded.
    
    This exception is raised when the application exceeds configured
    resource limits such as memory, CPU, or concurrent operations.
    """
    
    def __init__(
        self,
        message: str,
        resource_type: str,
        current_usage: Optional[Any] = None,
        limit: Optional[Any] = None
    ):
        """
        Initialize resource limit error.
        
        Args:
            message: Error message
            resource_type: Type of resource that exceeded limit
            current_usage: Current resource usage
            limit: Resource limit
        """
        super().__init__(
            message=message,
            error_type="ResourceLimitError",
            status_code=429,
            details={
                "resource_type": resource_type,
                "current_usage": current_usage,
                "limit": limit
            }
        )
        self.resource_type = resource_type
        self.current_usage = current_usage
        self.limit = limit


class ConfigurationError(QCanvasException):
    """
    Exception raised when there are configuration issues.
    
    This exception is raised when there are problems with the
    application configuration or environment setup.
    """
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
        """
        super().__init__(
            message=message,
            error_type="ConfigurationError",
            status_code=500,
            details={
                "config_key": config_key
            }
        )
        self.config_key = config_key


class DependencyError(QCanvasException):
    """
    Exception raised when required dependencies are missing.
    
    This exception is raised when required quantum computing
    frameworks or other dependencies are not properly installed.
    """
    
    def __init__(self, message: str, missing_dependency: Optional[str] = None):
        """
        Initialize dependency error.
        
        Args:
            message: Error message
            missing_dependency: Name of missing dependency
        """
        super().__init__(
            message=message,
            error_type="DependencyError",
            status_code=500,
            details={
                "missing_dependency": missing_dependency
            }
        )
        self.missing_dependency = missing_dependency


class ValidationError(QCanvasException):
    """
    Exception raised when input validation fails.
    
    This exception is raised when user input fails validation
    checks for API endpoints.
    """
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
            value: Value that failed validation
        """
        super().__init__(
            message=message,
            error_type="ValidationError",
            status_code=400,
            details={
                "field": field,
                "value": value
            }
        )
        self.field = field
        self.value = value


class RateLimitError(QCanvasException):
    """
    Exception raised when rate limits are exceeded.
    
    This exception is raised when the application exceeds configured
    rate limits for API endpoints.
    """
    
    def __init__(self, message: str, retry_after: Optional[int] = None):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message
            retry_after: Seconds to wait before retrying
        """
        super().__init__(
            message=message,
            error_type="RateLimitError",
            status_code=429,
            details={
                "retry_after": retry_after
            }
        )
        self.retry_after = retry_after


class TimeoutError(QCanvasException):
    """
    Exception raised when operations timeout.
    
    This exception is raised when operations take longer than
    the configured timeout period.
    """
    
    def __init__(self, message: str, operation: Optional[str] = None, timeout: Optional[float] = None):
        """
        Initialize timeout error.
        
        Args:
            message: Error message
            operation: Operation that timed out
            timeout: Timeout period in seconds
        """
        super().__init__(
            message=message,
            error_type="TimeoutError",
            status_code=408,
            details={
                "operation": operation,
                "timeout": timeout
            }
        )
        self.operation = operation
        self.timeout = timeout


# Convenience functions for common error scenarios
def raise_framework_error(framework: str, operation: str, details: Optional[Dict[str, Any]] = None):
    """Raise a framework-related error with standard formatting."""
    message = f"Error during {operation} with framework '{framework}'"
    if details:
        message += f": {details.get('reason', 'Unknown error')}"
    
    raise FrameworkNotSupportedError(framework) if "not supported" in message.lower() else ConversionError(
        message=message,
        source_framework=framework,
        details=details
    )


def raise_simulation_error(backend: str, operation: str, details: Optional[Dict[str, Any]] = None):
    """Raise a simulation-related error with standard formatting."""
    message = f"Error during {operation} with backend '{backend}'"
    if details:
        message += f": {details.get('reason', 'Unknown error')}"
    
    raise BackendNotAvailableError(backend) if "not available" in message.lower() else SimulationError(
        message=message,
        backend=backend,
        details=details
    )


def raise_validation_error(field: str, value: Any, expected: str):
    """Raise a validation error with standard formatting."""
    message = f"Invalid value for field '{field}': {value}. Expected: {expected}"
    raise ValidationError(message=message, field=field, value=value)
