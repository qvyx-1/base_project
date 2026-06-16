# Base Project — Coding Guide & Setup Guide

## Inhaltsverzeichnis

1. [Setup Guide](#setup-guide)
2. [Coding Guidelines](#coding-guidelines)
3. [Projektstruktur](#projektstruktur)
4. [Konfigurationssystem](#konfigurationssystem)
5. [Testing](#testing)
6. [Code Quality](#code-quality)

---

## Setup Guide

### Voraussetzungen

- **Python 3.11+** (empfohlen: 3.12)
- **[uv](https://github.com/astral-sh/uv)** — Schneller Python-Paketmanager

### Installation

```bash
# uv installieren (falls noch nicht geschehen)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Oder mit pipx:
pipx install uv

# Oder mit Homebrew (macOS/Linux):
brew install uv
```

### Projekt einrichten

```bash
# Repository klonen
git clone https://github.com/qvyx-1/base_project.git
cd base_project

# Virtuelle Umgebung erstellen & Dependencies installieren
uv sync

# Optional: .env Datei anlegen
cp .env.example .env
# .env mit deinen Werten bearbeiten
```

### Projekt ausführen

```bash
# Direkt mit uv (venv wird automatisch aktiviert)
uv run python -m base_project.main

# Mit Konfigurationsdatei
uv run python -m base_project.main --config config/app.toml

# Oder manuell aktivieren
source .venv/bin/activate
python -m base_project.main
```

### Development Setup

```bash
# Dev-Dependencies installieren
uv sync --all-extras

# Tests ausführen
uv run pytest

# Linting & Formatting
uv run ruff check .
uv run ruff format .

# Type Checking
uv run mypy src/
```

---

## Coding Guidelines

### Allgemeine Regeln

1. **Python 3.11+** — F-Strings, Typ-Hints, Pattern Matching
2. **PEP 8** — Code-Stil (via Ruff enforced)
3. **Google-Style Docstrings** — Für alle öffentlichen Funktionen/Klassen
4. **snake_case** — Für Variablen, Funktionen, Module
5. **PascalCase** — Für Klassen
6. **TYPE HINTS** — Alle Funktionen und Methoden müssen Typ-Hints haben

### Dateistruktur

```
projekt/
├── pyproject.toml          # Projektmetadaten & Konfiguration
├── src/
│   └── paketname/
│       ├── __init__.py     # Package-Exporte
│       ├── main.py         # Entry Point
│       ├── config.py       # Konfiguration
│       └── module.py       # Fachliche Module
├── tests/
│   ├── __init__.py
│   └── test_module.py     # Tests nach Modul benannt
├── config/                 # Konfigurationsdateien
└── docs/                   # Dokumentation
```

### Dateinamen-Konventionen

| Typ | Konvention | Beispiel |
|-----|-----------|----------|
| Module | `snake_case` | `config.py`, `database.py` |
| Klassen | `PascalCase` | `DatabaseConfig` |
| Funktionen | `snake_case` | `load_config()` |
| Variablen | `snake_case` | `user_name` |
| Konstanten | `UPPER_SNAKE_CASE` | `MAX_RETRIES` |
| Private Elemente | `_prefix` | `_internal_state` |

### Docstring-Format (Google Style)

```python
def calculate_total(items: list[Item], tax_rate: float = 0.19) -> float:
    """Calculate the total price including tax.

    Args:
        items: List of items to calculate total for.
        tax_rate: Tax rate as a decimal (default: 0.19).

    Returns:
        Total price including tax.

    Raises:
        ValueError: If items list is empty.
    """
```

### Typ-Hinting-Regeln

```python
from __future__ import annotations  # Immer oben in neuen Dateien

from typing import Any, Optional
from pathlib import Path


def process_data(
    data: str,
    options: dict[str, Any] | None = None,
) -> list[str]:
    """Process input data and return results."""
    ...
```

**Regeln:**
- Immer `from __future__ import annotations` verwenden
- Union-Typen mit `|` statt `Union[]` (Python 3.10+)
- Optional mit `X | None` statt `Optional[X]`
- Generics mit `list[str]` statt `List[str]`

### Fehlerbehandlung

```python
# Eigene Exceptions definieren
class BaseProjectError(Exception):
    """Base exception for base_project."""


class ConfigError(BaseProjectError):
    """Raised when configuration is invalid."""


def load_config(path: Path) -> dict[str, Any]:
    """Load configuration from file.

    Raises:
        ConfigError: If config file is invalid or missing.
    """
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def do_something() -> None:
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

**Regeln:**
- Immer `logging.getLogger(__name__)` verwenden
- Keine `print()` in Produktionscode
- Sensible Daten niemals loggen

### Tests

```python
import pytest


class TestExampleService:
    """Test cases for ExampleService."""

    def test_process_valid_input(self) -> None:
        """Test processing valid input data."""
        service = ExampleService(name="test")
        result = service.process("hello")
        assert result == "[test] hello"

    def test_process_empty_raises_value_error(self) -> None:
        """Test that empty input raises ValueError."""
        service = ExampleService()
        with pytest.raises(ValueError, match="empty"):
            service.process("")
```

**Regeln:**
- Tests nach Modul benennen: `test_module.py`
- Test-Funktionen mit `test_` beginnen
- Beschreibende Test-Namen: `test_xxx_when_yyy_zzz`
- Arrange-Act-Assert Pattern verwenden
- Fixtures für wiederkehrende Setup-Logik

### Konfiguration

```python
# config.py — pydantic-settings verwenden
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=".env",
        case_sensitive=False,
    )

    app_name: str = "My App"
    debug: bool = False
    database_url: str = "sqlite:///./app.db"
```

**Priorität der Konfiguration:**
1. Environment Variables (`APP_` Prefix)
2. `.env` Datei
3. TOML-Konfigurationsdatei
4. Default-Werte in `config.py`

---

## Code Quality Checklist

- [ ] Alle Funktionen haben Typ-Hints
- [ ] Alle öffentlichen Funktionen haben Docstrings (Google Style)
- [ ] Code wird mit `ruff format` formatiert
- [ ] Linting passiert ohne Fehler: `ruff check .`
- [ ] Type Checking besteht: `mypy src/`
- [ ] Alle Tests bestehen: `pytest`
- [ ] Keine sensiblen Daten in Logs oder Code
- [ ] Eigene Exceptions für Fehlerfälle
- [ ] Importe sind gruppiert (stdlib → third-party → local)

---

## Häufige Befehle

```bash
# Entwicklung
uv sync                    # Dependencies installieren
uv run pytest              # Tests ausführen
uv run ruff check .        # Linting
uv run ruff format .       # Formatting
uv run mypy src/           # Type Checking
uv run python -m base_project.main  # Projekt starten

# Wartung
uv lock                    # Lock-Datei aktualisieren
uv sync --all-extras       # Dev-Dependencies mitinstallieren
uv remove <package>        # Package entfernen
uv add <package>           # Package hinzufügen
```
