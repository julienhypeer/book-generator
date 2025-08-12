"""Application configuration and settings."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Database
    database_url: str = "sqlite:///./storage/book_generator.db"

    # Storage paths
    storage_path: str = str(Path(__file__).parent.parent.parent / "storage")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # WeasyPrint
    weasyprint_dpi: int = 300
    weasyprint_optimize_images: bool = True

    # Redis (for Celery)
    redis_url: str = "redis://localhost:6379/0"

    # Application
    debug: bool = False
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    @property
    def storage_root(self) -> Path:
        """Get storage root path as Path object."""
        return Path(self.storage_path)

    @property
    def projects_dir(self) -> Path:
        """Get projects directory path."""
        return self.storage_root / "projects"

    @property
    def templates_dir(self) -> Path:
        """Get templates directory path."""
        return self.storage_root / "templates"

    @property
    def exports_dir(self) -> Path:
        """Get exports directory path."""
        return self.storage_root / "exports"

    @property
    def temp_dir(self) -> Path:
        """Get temporary files directory path."""
        return self.storage_root / "temp"


# Create singleton instance
settings = Settings()
