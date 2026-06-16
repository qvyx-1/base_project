# Base Project — Python Template mit uv

Ein konfigurierbares Python-Projekttemplate mit:

- **uv** für schnelle Paketinstallation und venv-Management
- **pydantic-settings** für Konfiguration über Dateien + Environment Variables
- **Hatch** als Build-System
- **Ruff** für Linting/Formatting
- **mypy** für Type Checking
- **pytest** für Tests
- **src layout** für saubere Paketstruktur

## Schnellstart

```bash
# 1. uv installieren (falls nicht vorhanden)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. In das Projektverzeichnis wechseln
cd base_project

# 3. Virtuelle Umgebung mit uv erstellen und Dependencies installieren
uv sync

# 4. Aktivierung (optional — uv run macht das automatisch)
source .venv/bin/activate

# 5. Projekt ausführen
uv run python -m base_project.main

# Mit Konfigurationsdatei:
uv run python -m base_project.main --config config/app.toml

# 6. Tests ausführen
uv run pytest

# 7. Linting
uv run ruff check .

# 8. Type Checking
uv run mypy src/
```

## Projektstruktur

```
base_project/
├── pyproject.toml          # Projektmetadaten + Tools (Hatch, Ruff, MyPy, Pytest)
├── requirements.txt        # Pip-kompatible Requirements (optional)
├── .gitignore              # Python .gitignore
├── .env.example            # Beispiel Environment Variables
├── config/
│   └── app.toml            # TOML-Konfiguration
├── src/
│   └── base_project/
│       ├── __init__.py
│       ├── main.py         # Entry Point
│       ├── config.py       # Konfiguration (pydantic-settings)
│       └── service.py      # Beispiel-Service
├── tests/
│   ├── __init__.py
│   └── test_service.py     # Tests
└── docs/
    └── coding_guide.md     # Coding & Setup Guide
```

## Konfiguration

Die Konfiguration wird über **pydantic-settings** geladen mit folgender Priorität:

1. **Environment Variables** (Prefix: `APP_`)
2. **.env Datei**
3. **TOML-Konfigurationsdatei** (`--config config/app.toml`)
4. **Default-Werte** in `config.py`

### Environment Variables Beispiel

```bash
export APP_APP_NAME="Meine App"
export APP_DEBUG=true
export APP_LOG_LEVEL=DEBUG
export APP_DATABASE_URL="postgresql://user:pass@localhost/db"
```

### TOML Konfiguration (`config/app.toml`)

```toml
[app]
app_name = "Meine App"
debug = true
log_level = "DEBUG"

[database]
url = "postgresql://user:pass@localhost/db"
```

## Tools

| Tool | Befehl | Beschreibung |
|------|--------|-------------|
| **Tests** | `uv run pytest` | Alle Tests ausführen |
| **Linting** | `uv run ruff check .` | Code prüfen |
| **Formatting** | `uv run ruff format .` | Code formatieren |
| **Type Check** | `uv run mypy src/` | Typen prüfen |
| **Run** | `uv run python -m base_project.main` | Projekt starten |

## Anpassung

1. **Projektname ändern**: `pyproject.toml` → `[project] name`
2. **Dependencies**: `pyproject.toml` → `[project] dependencies`
3. **Konfiguration**: `src/base_project/config.py` anpassen
4. **Config-Dateien**: `config/app.toml` bearbeiten

## Lizenz

MIT
