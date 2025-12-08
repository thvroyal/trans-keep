"""Application configuration using Pydantic Settings"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "TransKeep"
    app_version: str = "0.1.0"
    debug: bool = False

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/transkeep"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # S3 / MinIO
    aws_access_key_id: str = "minioadmin"
    aws_secret_access_key: str = "minioadmin"
    aws_region: str = "us-east-1"
    aws_bucket_name: str = "transkeep-files"
    s3_endpoint_url: str | None = "http://localhost:9000"  # None for real AWS S3

    # Authentication
    jwt_secret: str = "dev_secret_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    google_client_id: str = ""
    google_client_secret: str = ""

    # External APIs
    deepl_api_key: str = ""
    claude_api_key: str = ""

    # OpenTelemetry
    otel_exporter_jaeger_agent_host: str = "localhost"
    otel_exporter_jaeger_agent_port: int = 6831

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance
    
    Note: This uses lru_cache to create a singleton, but the Settings
    instance is created fresh on first call (at runtime), not at import time.
    This ensures environment variables are properly loaded from .env files.
    """
    return Settings()

