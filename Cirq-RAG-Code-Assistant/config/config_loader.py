"""
Configuration Loader Module

This module provides a JSON-based configuration loader that reads
configuration files from the config directory and provides easy access
to all configuration settings.

Author: Umer Farooq, Hussain Waseem Syed, Muhammad Irtaza Khan
Email: umerfarooqcs0891@gmail.com
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add config directory to path for imports
_config_dir = Path(__file__).parent
_project_root = _config_dir.parent
sys.path.insert(0, str(_project_root))

# Load .env early so AWS_* and other vars are set before any code uses them
try:
    from dotenv import load_dotenv

    _env_path = _project_root / ".env"
    _parent_env = _project_root.parent / ".env"

    load_dotenv(_env_path)
    if _parent_env.is_file():
        load_dotenv(_parent_env)

    def _aws_access_keys_missing() -> bool:
        aid = (os.getenv("AWS_ACCESS_KEY_ID") or "").strip()
        sec = (os.getenv("AWS_SECRET_ACCESS_KEY") or "").strip()
        return not aid or not sec

    # Docker Compose often sets AWS_*=${VAR:-} which injects empty strings; those count as
    # "set" so the default load_dotenv(override=False) will not replace them from a file.
    if _aws_access_keys_missing():
        load_dotenv(_env_path, override=True)
        if _parent_env.is_file():
            load_dotenv(_parent_env, override=True)
except ImportError:
    pass

try:
    from src.cirq_rag_code_assistant.config.logging import get_logger
    logger_available = True
except ImportError:
    # Fallback logger if logging not available
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger_available = False

if logger_available:
    logger = get_logger(__name__)
else:
    logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Loads and manages configuration from JSON files.
    
    Supports environment-specific config files and environment variable overrides.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the ConfigLoader.
        
        Args:
            config_file: Path to config file (defaults to config/config.json)
        """
        # Find project root (config folder's parent)
        self.config_dir = Path(__file__).parent
        self.project_root = self.config_dir.parent
        
        # Determine config file
        if config_file:
            self.config_path = Path(config_file)
        else:
            # Use environment-specific config if available
            env = os.getenv("ENVIRONMENT", "development")
            dev_config = self.config_dir / "config.dev.json"
            default_config = self.config_dir / "config.json"
            
            if env == "development" and dev_config.exists():
                self.config_path = dev_config
            elif default_config.exists():
                self.config_path = default_config
            else:
                # Fallback to template
                self.config_path = self.config_dir / "config.template.json"
        
        # Load configuration
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            logger.info("Using default configuration")
            self.config = self._get_default_config()
            return
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            
            # Override with environment variables
            self._apply_env_overrides()
            
            logger.info(f"✅ Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            logger.info("Using default configuration")
            self.config = self._get_default_config()
    
    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides to config."""
        # Environment
        if os.getenv("ENVIRONMENT"):
            self.config["app"]["environment"] = os.getenv("ENVIRONMENT")
        if os.getenv("DEBUG"):
            self.config["app"]["debug"] = os.getenv("DEBUG").lower() in ("true", "1", "yes")
        
        # Logging
        if os.getenv("LOG_LEVEL"):
            self.config["logging"]["log_level"] = os.getenv("LOG_LEVEL")

        # AWS (region from env; credentials come from env / .env only, never from config)
        if os.getenv("AWS_DEFAULT_REGION"):
            self.config.setdefault("aws", {})["region"] = os.getenv("AWS_DEFAULT_REGION")

        # Models (LLM)
        if os.getenv("LLM_PROVIDER"):
            self.config.setdefault("models", {}).setdefault("llm", {})["provider"] = os.getenv("LLM_PROVIDER")
        if os.getenv("LLM_MODEL"):
            self.config.setdefault("models", {}).setdefault("llm", {})["model"] = os.getenv("LLM_MODEL")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "app": {
                "name": "Cirq-RAG-Code-Assistant",
                "version": "0.1.0",
                "debug": False,
                "environment": "development"
            },
            "aws": {
                "region": "us-east-1",
                "embeddings": {"embedding_dimension": 1024}
            },
            "models": {
                "embedding": {
                    "model_name": "BAAI/bge-base-en-v1.5",
                    "device": "auto",
                    "batch_size": 16
                },
                "llm": {
                    "provider": "ollama",
                    "model": "qwen2.5-coder:14b-instruct-q4_K_M",
                    "temperature": 0.2,
                    "max_tokens": 2000
                }
            },
            "rag": {
                "knowledge_base": {"path": "data/knowledge_base"},
                "vector_store": {"type": "faiss", "index_path": "data/models/vector_index"},
                "retrieval": {"top_k_results": 5, "similarity_threshold": 0.7}
            },
            "agents": {
                "general": {"max_retries": 3, "timeout_seconds": 300},
                "designer": {"enabled": True},
                "optimizer": {"enabled": True, "level": "balanced"},
                "validator": {"enabled": True},
                "educational": {"enabled": True}
            },
            "paths": {
                "data_dir": "data",
                "outputs_dir": "outputs",
                "logs_dir": "outputs/logs"
            },
            "logging": {
                "log_level": "INFO",
                "log_file": "outputs/logs/cirq_rag.log"
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path (e.g., "models.embedding.model_name")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split(".")
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get a configuration section.
        
        Args:
            section: Section name (e.g., "models", "rag", "agents")
            
        Returns:
            Configuration section dictionary
        """
        return self.config.get(section, {})
    
    def create_directories(self) -> None:
        """Create all necessary directories from config."""
        paths = self.get_section("paths")
        
        directories = [
            paths.get("data_dir"),
            paths.get("datasets_dir"),
            paths.get("knowledge_base_dir"),
            paths.get("models_dir"),
            paths.get("outputs_dir"),
            paths.get("logs_dir"),
            paths.get("reports_dir"),
            paths.get("artifacts_dir"),
            paths.get("cache_dir"),
            paths.get("embedding_cache_dir"),
        ]
        
        # Also get vector index path
        rag = self.get_section("rag")
        vector_store = rag.get("vector_store", {})
        if "index_path" in vector_store:
            directories.append(vector_store["index_path"])
        
        for directory in directories:
            if directory:
                # Handle both absolute and relative paths
                if Path(directory).is_absolute():
                    dir_path = Path(directory)
                else:
                    dir_path = self.project_root / directory
                dir_path.mkdir(parents=True, exist_ok=True)
        
        logger.debug("Created all necessary directories")
    
    def setup_pytorch(self) -> None:
        """Setup PyTorch configuration from config."""
        pytorch_config = self.get_section("pytorch")
        
        os.environ["CUDA_VISIBLE_DEVICES"] = pytorch_config.get("cuda_visible_devices", "0")
        
        try:
            import torch
            
            if pytorch_config.get("torch_deterministic", False):
                torch.backends.cudnn.deterministic = True
                torch.backends.cudnn.benchmark = False
                torch.use_deterministic_algorithms(True)
            else:
                torch.backends.cudnn.benchmark = pytorch_config.get("torch_benchmark", True)
            
            device = pytorch_config.get("torch_device", "auto")
            if device == "auto":
                device = "cuda" if torch.cuda.is_available() else "cpu"
            
            if device.startswith("cuda") and torch.cuda.is_available():
                memory_fraction = pytorch_config.get("torch_memory_fraction", 0.8)
                if memory_fraction < 1.0:
                    torch.cuda.set_per_process_memory_fraction(memory_fraction)
                
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
                logger.info(f"PyTorch GPU: {gpu_name} ({gpu_memory:.2f} GB)")
        except ImportError:
            logger.warning("PyTorch not installed. GPU acceleration will not be available.")


# Global config loader instance
_config_loader: Optional[ConfigLoader] = None


def get_config_loader(config_file: Optional[str] = None) -> ConfigLoader:
    """
    Get or create global config loader instance.
    
    Args:
        config_file: Optional path to config file
        
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    
    if _config_loader is None:
        _config_loader = ConfigLoader(config_file)
        _config_loader.create_directories()
        if not _config_loader.get("app.debug", False):
            _config_loader.setup_pytorch()
    
    return _config_loader


def get_config() -> Dict[str, Any]:
    """
    Get the configuration dictionary.
    
    Returns:
        Configuration dictionary
    """
    return get_config_loader().config


def reload_config(config_file: Optional[str] = None) -> ConfigLoader:
    """
    Reload configuration from file.
    
    Args:
        config_file: Optional path to config file
        
    Returns:
        ConfigLoader instance
    """
    global _config_loader
    _config_loader = ConfigLoader(config_file)
    _config_loader.create_directories()
    if not _config_loader.get("app.debug", False):
        _config_loader.setup_pytorch()
    return _config_loader

