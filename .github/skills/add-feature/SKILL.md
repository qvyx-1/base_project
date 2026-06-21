---
name: add-feature
description: 'Scaffold a new feature into base_project. Use for creating modules, services, CLI commands, models, or any new code following project conventions.'
argument-hint: 'Feature name and type (module/service/CLI/model)'
---

# Add Feature

Scaffold a new feature into the `base_project` project following established conventions.

## When to Use

- Adding a new module or package
- Creating a service class for business logic
- Adding CLI commands or subcommands
- Setting up database models
- Any new code that needs to follow project conventions

## Procedure

### 1. Determine Feature Type

```
What are you adding?
├── Data layer → src/base_project/models/ + config.py (DatabaseConfig)
├── Business logic → src/base_project/services/ (new service classes)
├── API layer → src/base_project/api/ (routers, schemas)
├── CLI command → extend main.py or create cli/ module
└── External integration → src/base_project/integrations/ + config section
```

### 2. Create Directory Structure

```bash
mkdir -p src/base_project/<feature>/
touch src/base_project/<feature>/__init__.py
mkdir -p tests/test_<feature>.py
```

### 3. Generate Source File

Every new file must include:

- `from __future__ import annotations` at the top
- Module-level docstring describing purpose
- Google-style docstrings on all public classes/functions
- Full type hints on every function signature and return type
- PEP 8 style (Ruff enforced, 100 char line length)

### 4. Add Configuration (if needed)

If the feature requires settings:

1. Add fields to appropriate pydantic-settings class in `config.py`
2. Add corresponding section to `config/app.toml`
3. Document env var prefix (`APP_` for app config, `DB_` for database)

### 5. Update Dependencies (if needed)

1. Add to `[project] dependencies` in `pyproject.toml` for runtime deps
2. Add to `[project.optional-dependencies] dev` for dev-only tools
3. Run `uv sync` to install

### 6. Write Tests

Create tests under `tests/` mirroring source structure:

- Class-based test organization
- Cover happy path, edge cases, and error conditions
- Docstrings on all test methods
- Test configuration loading with both file and env var sources

### 7. Validate

```bash
uv run ruff check .
uv run ruff format .
uv run mypy src/
uv run pytest
```

## Templates

### New Service Class

```python
"""<Feature> service module."""

from __future__ import annotations

from base_project.config import AppConfig


class <Feature>Service:
    """Service for <feature>.

    Args:
        config: Application configuration instance.
    """

    def __init__(self, config: AppConfig) -> None:
        """Initialize the service.

        Args:
            config: Application configuration.
        """
        self.config = config

    def do_something(self, data: str) -> str:
        """Process data.

        Args:
            data: Input data string.

        Returns:
            Processed result string.
        """
        return f"processed: {data}"
```

### New Config Section

```python
# In config.py, add:
class <Feature>Config(BaseSettings):
    """Configuration for <feature>."""

    model_config = SettingsConfigDict(
        env_prefix="<FEATURE>_",
        case_sensitive=False,
    )

    enabled: bool = False
    api_key: str = ""
```

### New CLI Subcommand

```python
# In main.py, extend parse_args:
subparsers = parser.add_subparsers(dest="command", help="Available commands")

my_cmd_parser = subparsers.add_parser("my-command", help="Description")
my_cmd_parser.add_argument("--flag", type=str, help="A flag")
```

## Anti-Patterns

- **Don't** create modules outside `src/base_project/`
- **Don't** skip type hints or docstrings — strict mypy enforced
- **Don't** hardcode configuration values — always use pydantic-settings
- **Don't** add dev dependencies to main dependencies list
- **Don't** skip validation steps (ruff, mypy, pytest) before committing
