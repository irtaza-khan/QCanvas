"""
QCanvas Logging Configuration

This module provides comprehensive logging configuration for the QCanvas application,
including structured logging, different log levels, file and console handlers,
and proper formatting for both development and production environments.

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

import logging
import logging.config
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from app.config.settings import get_settings


def setup_logging(
    log_level: Optional[str] = None,
    log_format: Optional[str] = None,
    log_file: Optional[str] = None
) -> None:
    """
    Setup logging configuration for the QCanvas application.
    
    This function configures logging with appropriate handlers, formatters,
    and log levels based on the application settings and environment.
    
    Args:
        log_level: Override log level from settings
        log_format: Override log format from settings
        log_file: Override log file path from settings
    """
    settings = get_settings()
    
    # Use provided parameters or fall back to settings
    level = log_level or settings.LOG_LEVEL
    format_type = log_format or settings.LOG_FORMAT
    log_file_path = log_file or settings.LOG_FILE
    
    # Create logs directory if it doesn't exist
    if log_file_path:
        log_dir = Path(log_file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging based on format type
    if format_type.lower() == "json":
        config = _get_json_logging_config(level, log_file_path)
    else:
        config = _get_text_logging_config(level, log_file_path)
    
    # Apply logging configuration
    logging.config.dictConfig(config)
    
    # Set up additional loggers for specific components
    _setup_component_loggers(level)
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized", extra={
        "log_level": level,
        "log_format": format_type,
        "log_file": log_file_path,
        "environment": settings.ENVIRONMENT
    })


def _get_json_logging_config(level: str, log_file: Optional[str]) -> Dict[str, Any]:
    """
    Get JSON logging configuration.
    
    Args:
        level: Log level
        log_file: Log file path
        
    Returns:
        Dict: Logging configuration dictionary
    """
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "app.utils.logging.JsonFormatter",
                "format": "%(timestamp)s %(level)s %(name)s %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "json",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            }
        }
    }
    
    # Add file handler if log file is specified
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": "json",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
        config["loggers"][""]["handlers"].append("file")
    
    return config


def _get_text_logging_config(level: str, log_file: Optional[str]) -> Dict[str, Any]:
    """
    Get text logging configuration.
    
    Args:
        level: Log level
        log_file: Log file path
        
    Returns:
        Dict: Logging configuration dictionary
    """
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "simple": {
                "format": "%(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "": {
                "level": level,
                "handlers": ["console"],
                "propagate": False
            }
        }
    }
    
    # Add file handler if log file is specified
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": "detailed",
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
        config["loggers"][""]["handlers"].append("file")
    
    return config


def _setup_component_loggers(level: str) -> None:
    """
    Setup specific loggers for different components.
    
    Args:
        level: Log level for component loggers
    """
    # Quantum converter loggers
    logging.getLogger("quantum_converters").setLevel(level)
    logging.getLogger("quantum_converters.converters").setLevel(level)
    logging.getLogger("quantum_converters.parsers").setLevel(level)
    logging.getLogger("quantum_converters.validators").setLevel(level)
    
    # Quantum simulator loggers
    logging.getLogger("quantum_simulator").setLevel(level)
    logging.getLogger("quantum_simulator.backends").setLevel(level)
    logging.getLogger("quantum_simulator.algorithms").setLevel(level)
    
    # API loggers
    logging.getLogger("app.api").setLevel(level)
    logging.getLogger("app.api.routes").setLevel(level)
    logging.getLogger("app.services").setLevel(level)
    
    # WebSocket logger
    logging.getLogger("app.core.websocket_manager").setLevel(level)
    
    # External library loggers (set to higher level to reduce noise)
    logging.getLogger("uvicorn").setLevel("WARNING")
    logging.getLogger("fastapi").setLevel("WARNING")
    logging.getLogger("sqlalchemy").setLevel("WARNING")
    logging.getLogger("redis").setLevel("WARNING")


class JsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    
    This formatter converts log records to JSON format for better
    parsing and analysis in log aggregation systems.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            str: JSON formatted log message
        """
        import json
        
        # Create base log entry
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception information if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)
        
        # Add custom fields from record attributes
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "levelname", "levelno", "pathname", 
                          "filename", "module", "lineno", "funcName", "created", 
                          "msecs", "relativeCreated", "thread", "threadName", 
                          "processName", "process", "getMessage", "exc_info", 
                          "exc_text", "stack_info", "extra_fields"]:
                log_entry[key] = value
        
        return json.dumps(log_entry)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


def log_function_call(func):
    """
    Decorator to log function calls with parameters and execution time.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function
    """
    import functools
    import time
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        # Log function entry
        logger.debug(f"Entering {func.__name__}", extra={
            "function": func.__name__,
            "module": func.__module__,
            "args_count": len(args),
            "kwargs_count": len(kwargs)
        })
        
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            
            # Log successful completion
            execution_time = time.time() - start_time
            logger.debug(f"Completed {func.__name__}", extra={
                "function": func.__name__,
                "execution_time": execution_time,
                "status": "success"
            })
            
            return result
            
        except Exception as e:
            # Log error
            execution_time = time.time() - start_time
            logger.error(f"Error in {func.__name__}: {str(e)}", extra={
                "function": func.__name__,
                "execution_time": execution_time,
                "status": "error",
                "error_type": type(e).__name__,
                "error_message": str(e)
            }, exc_info=True)
            raise
    
    return wrapper


def log_async_function_call(func):
    """
    Decorator to log async function calls with parameters and execution time.
    
    Args:
        func: Async function to decorate
        
    Returns:
        Decorated async function
    """
    import functools
    import time
    import asyncio
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        
        # Log function entry
        logger.debug(f"Entering async {func.__name__}", extra={
            "function": func.__name__,
            "module": func.__module__,
            "args_count": len(args),
            "kwargs_count": len(kwargs),
            "async": True
        })
        
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            
            # Log successful completion
            execution_time = time.time() - start_time
            logger.debug(f"Completed async {func.__name__}", extra={
                "function": func.__name__,
                "execution_time": execution_time,
                "status": "success",
                "async": True
            })
            
            return result
            
        except Exception as e:
            # Log error
            execution_time = time.time() - start_time
            logger.error(f"Error in async {func.__name__}: {str(e)}", extra={
                "function": func.__name__,
                "execution_time": execution_time,
                "status": "error",
                "error_type": type(e).__name__,
                "error_message": str(e),
                "async": True
            }, exc_info=True)
            raise
    
    return wrapper


def log_performance_metrics(operation: str, **metrics):
    """
    Log performance metrics for monitoring and analysis.
    
    Args:
        operation: Name of the operation being measured
        **metrics: Key-value pairs of metrics to log
    """
    logger = logging.getLogger("performance")
    
    log_entry = {
        "operation": operation,
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics
    }
    
    logger.info(f"Performance metrics for {operation}", extra={
        "performance_metrics": log_entry
    })


def log_api_request(method: str, path: str, status_code: int, duration: float, **kwargs):
    """
    Log API request details for monitoring and analysis.
    
    Args:
        method: HTTP method
        path: Request path
        status_code: HTTP status code
        duration: Request duration in seconds
        **kwargs: Additional request details
    """
    logger = logging.getLogger("api")
    
    log_entry = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration": duration,
        "timestamp": datetime.utcnow().isoformat(),
        **kwargs
    }
    
    # Determine log level based on status code
    if status_code >= 500:
        log_level = logging.ERROR
    elif status_code >= 400:
        log_level = logging.WARNING
    else:
        log_level = logging.INFO
    
    logger.log(log_level, f"API Request: {method} {path} - {status_code}", extra={
        "api_request": log_entry
    })


def log_quantum_operation(operation: str, framework: str, backend: str, **details):
    """
    Log quantum computing operations for monitoring and analysis.
    
    Args:
        operation: Type of quantum operation
        framework: Quantum framework used
        backend: Simulation backend used
        **details: Additional operation details
    """
    logger = logging.getLogger("quantum")
    
    log_entry = {
        "operation": operation,
        "framework": framework,
        "backend": backend,
        "timestamp": datetime.utcnow().isoformat(),
        **details
    }
    
    logger.info(f"Quantum operation: {operation} using {framework} on {backend}", extra={
        "quantum_operation": log_entry
    })


# Initialize logging when module is imported
if not logging.getLogger().handlers:
    setup_logging()
