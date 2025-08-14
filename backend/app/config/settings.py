"""
QCanvas Application Settings

This module provides centralized configuration management for the QCanvas application.
It uses Pydantic settings for type-safe environment variable handling and validation.

Author: QCanvas Team
Date: 2024
Version: 1.0.0
"""

import os
from typing import List, Optional
from functools import lru_cache

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    This class defines all configuration parameters for the QCanvas application,
    with automatic loading from environment variables and validation.
    """
    
    # Application Settings
    APP_NAME: str = Field(default="QCanvas", description="Application name")
    APP_VERSION: str = Field(default="1.0.0", description="Application version")
    DEBUG: bool = Field(default=False, description="Enable debug mode")
    ENVIRONMENT: str = Field(default="production", description="Environment (development/production)")
    
    # Server Configuration
    HOST: str = Field(default="0.0.0.0", description="Server host address")
    PORT: int = Field(default=8000, description="Server port")
    WORKERS: int = Field(default=4, description="Number of worker processes")
    RELOAD: bool = Field(default=False, description="Enable auto-reload for development")
    
    # Security Settings
    SECRET_KEY: str = Field(..., description="Secret key for JWT tokens and encryption")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="JWT token expiration time")
    
    # Database Configuration
    DATABASE_URL: str = Field(..., description="Database connection string")
    DATABASE_POOL_SIZE: int = Field(default=10, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, description="Database connection pool max overflow")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, description="Redis password")
    REDIS_DB: int = Field(default=0, description="Redis database number")
    
    # CORS Settings
    ALLOWED_HOSTS: str = Field(default="localhost,127.0.0.1", description="Comma-separated allowed hosts")
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000", description="Comma-separated allowed origins")
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True, description="Allow credentials in CORS")
    
    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json/text)")
    LOG_FILE: Optional[str] = Field(default=None, description="Log file path")
    
    # Quantum Simulation Settings
    MAX_QUBITS: int = Field(default=32, description="Maximum number of qubits for simulation")
    MAX_SHOTS: int = Field(default=10000, description="Maximum number of shots for simulation")
    DEFAULT_BACKEND: str = Field(default="statevector", description="Default simulation backend")
    ENABLE_NOISE_MODELS: bool = Field(default=True, description="Enable noise models in simulation")
    
    # File Upload Settings
    MAX_FILE_SIZE: int = Field(default=10485760, description="Maximum file upload size in bytes")
    UPLOAD_DIR: str = Field(default="uploads", description="Upload directory path")
    ALLOWED_EXTENSIONS: str = Field(default="py,qasm,json", description="Comma-separated allowed file extensions")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, description="Rate limit per minute")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, description="Rate limit per hour")
    
    # Monitoring and Metrics
    ENABLE_METRICS: bool = Field(default=True, description="Enable metrics collection")
    METRICS_PORT: int = Field(default=9090, description="Metrics server port")
    PROMETHEUS_ENABLED: bool = Field(default=True, description="Enable Prometheus metrics")
    
    # External Services (Optional)
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, description="AWS access key ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, description="AWS secret access key")
    AWS_REGION: str = Field(default="us-east-1", description="AWS region")
    AWS_S3_BUCKET: Optional[str] = Field(default=None, description="AWS S3 bucket name")
    
    # Email Configuration (Optional)
    SMTP_HOST: Optional[str] = Field(default=None, description="SMTP server host")
    SMTP_PORT: int = Field(default=587, description="SMTP server port")
    SMTP_USERNAME: Optional[str] = Field(default=None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(default=None, description="SMTP password")
    FROM_EMAIL: Optional[str] = Field(default=None, description="From email address")
    
    # Frontend Configuration
    FRONTEND_URL: str = Field(default="http://localhost:3000", description="Frontend URL")
    API_BASE_URL: str = Field(default="http://localhost:8000", description="API base URL")
    
    @validator("ALLOWED_HOSTS", "ALLOWED_ORIGINS")
    def parse_comma_separated(cls, v):
        """Parse comma-separated string values."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v
    
    @validator("ALLOWED_EXTENSIONS")
    def parse_extensions(cls, v):
        """Parse allowed file extensions."""
        if isinstance(v, str):
            return [ext.strip().lower() for ext in v.split(",") if ext.strip()]
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment setting."""
        valid_environments = ["development", "staging", "production"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Environment must be one of {valid_environments}")
        return v.lower()
    
    @validator("DEFAULT_BACKEND")
    def validate_backend(cls, v):
        """Validate default simulation backend."""
        valid_backends = ["statevector", "density_matrix", "stabilizer"]
        if v.lower() not in valid_backends:
            raise ValueError(f"Backend must be one of {valid_backends}")
        return v.lower()
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Allow environment variables to override defaults
        env_prefix = ""
        
        # Example environment variable mapping
        fields = {
            "SECRET_KEY": {"env": "SECRET_KEY"},
            "DATABASE_URL": {"env": "DATABASE_URL"},
            "REDIS_URL": {"env": "REDIS_URL"},
        }


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.
    
    This function caches the settings to avoid repeated environment variable
    parsing and validation on each access.
    
    Returns:
        Settings: Application settings instance
    """
    return Settings()


# Convenience functions for common settings access
def get_database_url() -> str:
    """Get database URL from settings."""
    return get_settings().DATABASE_URL


def get_redis_url() -> str:
    """Get Redis URL from settings."""
    return get_settings().REDIS_URL


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return get_settings().DEBUG


def get_allowed_origins() -> List[str]:
    """Get list of allowed CORS origins."""
    settings = get_settings()
    if isinstance(settings.ALLOWED_ORIGINS, str):
        return [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]
    return settings.ALLOWED_ORIGINS


def get_allowed_hosts() -> List[str]:
    """Get list of allowed hosts."""
    settings = get_settings()
    if isinstance(settings.ALLOWED_HOSTS, str):
        return [host.strip() for host in settings.ALLOWED_HOSTS.split(",")]
    return settings.ALLOWED_HOSTS


def get_quantum_settings() -> dict:
    """Get quantum simulation specific settings."""
    settings = get_settings()
    return {
        "max_qubits": settings.MAX_QUBITS,
        "max_shots": settings.MAX_SHOTS,
        "default_backend": settings.DEFAULT_BACKEND,
        "enable_noise_models": settings.ENABLE_NOISE_MODELS,
    }


def get_file_upload_settings() -> dict:
    """Get file upload specific settings."""
    settings = get_settings()
    return {
        "max_file_size": settings.MAX_FILE_SIZE,
        "upload_dir": settings.UPLOAD_DIR,
        "allowed_extensions": settings.ALLOWED_EXTENSIONS,
    }
