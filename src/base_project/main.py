"""Main entry point for base_project.

Demonstrates configuration loading and application startup.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console

from base_project.config import AppConfig, get_logger

console = Console()


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line arguments.

    Args:
        args: Optional list of arguments (defaults to sys.argv[1:]).

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        prog="base_project",
        description="A configurable Python base project template",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file (TOML)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )
    return parser.parse_args(args)


def main() -> int:
    """Main application entry point.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    args = parse_args()

    # Load configuration
    config_path = Path(args.config) if args.config else None
    config = AppConfig.from_file(config_path) if config_path else AppConfig()

    if args.debug:
        config.debug = True
        config.log_level = "DEBUG"

    # Setup logging
    logger = get_logger("base_project", config.log_level)
    logger.info("Starting %s v%s", config.app_name, config.version)

    # Display configuration
    console.print("[bold green]Base Project[/bold green] v" + config.version)
    console.print(f"  App: {config.app_name}")
    console.print(f"  Debug: {config.debug}")
    console.print(f"  Log level: {config.log_level}")
    console.print(f"  Database: {config.database_url}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
