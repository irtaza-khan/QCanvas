from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "QCanvas"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_SERVER: str = "127.0.0.1"
    POSTGRES_PORT: str = "5433"
    POSTGRES_DB: str = "qcanvas_db"
    DATABASE_URL: Optional[str] = None

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: Optional[str] = None

    # Security
    SECRET_KEY: str = "development_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Feature Flags (Sprint 3/4 Features)
    ENABLE_HYBRID_EXECUTION: bool = True
    ENABLE_PROJECT_MANAGEMENT: bool = False
    ENABLE_ADVANCED_MONITORING: bool = False
    ENABLE_CIRCUIT_VISUALIZATION: bool = False
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    def model_post_init(self, __context):
        if self.DATABASE_URL is None:
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        if self.REDIS_URL is None:
            self.REDIS_URL = f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
