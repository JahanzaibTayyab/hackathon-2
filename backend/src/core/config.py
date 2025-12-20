"""Application configuration settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str

    # Authentication
    better_auth_secret: str
    better_auth_url: str = "http://localhost:3000"
    jwt_algorithm: str = "HS256"
    jwt_expiration_days: int = 7

    # API
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Environment
    python_env: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
