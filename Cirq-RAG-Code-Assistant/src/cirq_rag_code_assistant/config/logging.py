"""Logging configuration for Cirq-RAG-Code-Assistant."""

import logging
import sys
from pathlib import Path
from typing import Optional

from loguru import logger

try:
    import structlog

    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


class LoggingConfig:
    """Configuration class for logging setup."""

    def __init__(
        self,
        log_level: str = "INFO",
        log_file: Optional[str] = None,
        log_format: str = "json",
        enable_console: bool = True,
        enable_file: bool = True,
        max_file_size: str = "10 MB",
        backup_count: int = 5,
    ):
        self.log_level = log_level.upper()
        self.log_file = log_file or "outputs/logs/cirq_rag.log"
        self.log_format = log_format
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.max_file_size = max_file_size
        self.backup_count = backup_count

        # Only touch the filesystem if we actually plan to write log files.
        # In the production container we run stdout-only and filesystem writes
        # would fail (or be pointless on an ephemeral Fargate task).
        if self.enable_file:
            log_path = Path(self.log_file)
            try:
                log_path.parent.mkdir(parents=True, exist_ok=True)
            except OSError:
                # Read-only filesystem or permission denied: fall back to
                # console-only logging rather than crashing on import.
                self.enable_file = False

    def setup_loguru(self) -> None:
        logger.remove()

        if self.enable_console:
            if self.log_format == "json":
                # loguru's built-in JSON serializer keeps structured fields so
                # CloudWatch Insights can parse `level`, `message`, `extra`, etc.
                logger.add(
                    sys.stdout,
                    level=self.log_level,
                    serialize=True,
                    backtrace=True,
                    diagnose=False,
                )
            else:
                console_format = (
                    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                    "<level>{level: <8}</level> | "
                    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                    "<level>{message}</level>"
                )
                logger.add(
                    sys.stderr,
                    format=console_format,
                    level=self.log_level,
                    colorize=True,
                    backtrace=True,
                    diagnose=True,
                )

        if self.enable_file:
            file_format = (
                "{time:YYYY-MM-DD HH:mm:ss} | "
                "{level: <8} | "
                "{name}:{function}:{line} | "
                "{message}"
            )
            logger.add(
                self.log_file,
                format=file_format,
                level=self.log_level,
                rotation=self.max_file_size,
                retention=self.backup_count,
                compression="zip",
                backtrace=True,
                diagnose=True,
            )

    def setup_structlog(self) -> None:
        if not STRUCTLOG_AVAILABLE:
            return
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
                if self.log_format == "json"
                else structlog.dev.ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

    def setup_standard_logging(self) -> None:
        handlers: list = [logging.StreamHandler(sys.stdout)]
        if self.enable_file:
            try:
                handlers.append(logging.FileHandler(self.log_file))
            except OSError:
                # If the file can't be opened (read-only FS in container, etc.)
                # silently skip the file handler rather than refusing to start.
                pass

        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format=(
                "%(asctime)s - %(name)s - %(levelname)s - "
                "%(filename)s:%(lineno)d - %(message)s"
            ),
            handlers=handlers,
            force=True,
        )

        logging.getLogger("torch").setLevel(logging.WARNING)
        logging.getLogger("transformers").setLevel(logging.WARNING)
        logging.getLogger("cirq").setLevel(logging.INFO)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

    def setup_all(self) -> None:
        self.setup_loguru()
        self.setup_structlog()
        self.setup_standard_logging()

        logger.info(
            "Logging configuration completed",
            log_level=self.log_level,
            log_file=self.log_file,
            format=self.log_format,
        )


def get_logger(name: str) -> logger:
    return logger.bind(name=name)


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None, **kwargs) -> LoggingConfig:
    config = LoggingConfig(log_level=log_level, log_file=log_file, **kwargs)
    config.setup_all()
    return config


def setup_default_logging() -> None:
    setup_logging(
        log_level="INFO",
        log_file="outputs/logs/cirq_rag.log",
        enable_console=True,
        enable_file=True,
    )

