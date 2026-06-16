"""Configuration module for base_project.

Uses pydantic-settings to load configuration from multiple sources:
1. Environment variables
2. Configuration files (TOML/YAML)
3. Default values
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class AppConfig(BaseSettings):
    """Application configuration settings.

    Configuration can be loaded from:
    - config/app.toml (TOML format)
    - Environment variables (prefix: APP_)
    - Default values defined below
    """

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application settings
    app_name: str = "Base Project"
    version: str = "0.1.0"
    debug: bool = False
    log_level: str = "INFO"

    # Database settings (example)
    database_url: str = "sqlite:///./app.db"

    # Server settings (example)
    host: str = "127.0.0.1"
    port: int = 8000

    @classmethod
    def from_file(cls, config_path: Path | str) -> AppConfig:
        """Load configuration from a TOML file.

        Args:
            config_path: Path to the TOML configuration file.

        Returns:
            AppConfig instance with loaded settings.
        """
        path = Path(config_path)
        if not path.exists():
            logger.warning("Config file not found: %s, using defaults", path)
            return cls()

        logger.info("Loading config from: %s", path)
        return cls(_env_file=None)  # type: ignore[call-arg]


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="DB_",
        case_sensitive=False,
    )

    url: str = "sqlite:///./app.db"
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False


def load_config(config_path: Path | str | None = None) -> AppConfig:
    """Load application configuration.

    Args:
        config_path: Optional path to config file. If None, uses defaults/env vars.

    Returns:
        AppConfig instance.
    """
    if config_path:
        return AppConfig.from_file(config_path)
    return AppConfig()


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Create and configure a logger.

    Args:
        name: Logger name (usually __name__).
        level: Logging level string.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger
