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

        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    def setup_loguru(self) -> None:
        logger.remove()

        if self.enable_console:
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
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format=(
                "%(asctime)s - %(name)s - %(levelname)s - "
                "%(filename)s:%(lineno)d - %(message)s"
            ),
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(self.log_file)
                if self.enable_file
                else logging.NullHandler(),
            ],
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

