---
name: extend-base-project
description: 'Extend the base_project template into a working project. Use for scaffolding new modules, adding services, configuring features, generating boilerplate code, setting up database models, API routes, or any project extension workflow.'
argument-hint: 'What feature or module to add'
---

# Extend Base Project

Transform the `base_project` template into a fully working application by following this structured extension workflow.

## When to Use

- Adding new features/modules to the base project
- Scaffolding database models, API routes, CLI commands
- Configuring third-party integrations (Redis, Celery, auth, etc.)
- Generating boilerplate code that follows the project conventions
- Extending configuration with new sections

## Project Conventions (Always Follow)

| Convention | Rule |
|------------|------|
| Python | 3.11+, Google-style docstrings, full type hints |
| Style | PEP 8 enforced by Ruff (`ruff check .` / `ruff format .`) |
| Structure | `src/base_project/` — never top-level modules |
| Config | pydantic-settings in `config.py`, TOML files in `config/` |
| Tests | Mirror source structure under `tests/`, pytest with class-based tests |
| Naming | `snake_case` for functions/vars, `PascalCase` for classes |
| Build | Hatch via `pyproject.toml` |
| Package Manager | `uv sync` / `uv run` |

## Procedure

### 1. Plan the Extension

Determine what needs to be added:

- **New module**: Create under `src/base_project/` with `__init__.py` exports
- **Config section**: Add to `config.py` (pydantic-settings class) + `config/app.toml`
- **CLI command**: Extend `main.py` argparse or create a new subcommand module
- **Database model**: Create in `src/base_project/models/` with SQLAlchemy or preferred ORM
- **API routes**: Create in `src/base_project/api/` with routers

**Decision tree:**
```
What are you adding?
├── Data layer → src/base_project/models/ + config.py (DatabaseConfig)
├── Business logic → src/base_project/services/ (new service classes)
├── API layer → src/base_project/api/ (routers, schemas)
├── CLI command → extend main.py or create cli/ module
└── External integration → src/base_project/integrations/ + config section
```

### 2. Update Configuration

If the feature requires new settings:

1. Add fields to the appropriate pydantic-settings class in `config.py`
2. Add corresponding section to `config/app.toml`
3. Document env var prefix (`APP_` for app config, `DB_` for database)

### 3. Create Source Files

Follow this directory structure for new features:

```
src/base_project/
├── models/          # Data models (SQLAlchemy, pydantic schemas)
│   ├── __init__.py
│   └── <model>.py
├── services/        # Business logic
│   ├── __init__.py
│   └── <service>.py
├── api/             # API routes
│   ├── __init__.py
│   └── <router>.py
└── integrations/    # External service clients
    ├── __init__.py
    └── <integration>.py
```

Each new file must:
- Have `from __future__ import annotations` at the top
- Include Google-style docstrings on all public classes/functions
- Have full type hints on every function signature and return type
- Follow the existing coding style (100 char line length, strict mypy)

### 4. Update Dependencies

If new packages are needed:

1. Add to `[project] dependencies` in `pyproject.toml`
2. Add to `[project.optional-dependencies] dev` if it's a dev-only tool
3. Run `uv sync` to install

### 5. Write Tests

Create tests mirroring the source structure under `tests/`:

```
tests/
├── test_<module>.py    # Unit tests for module
└── test_<service>.py   # Integration tests for service
```

Test requirements:
- Use class-based test organization (like `test_service.py`)
- Cover happy path, edge cases, and error conditions
- Include docstrings on all test methods
- Test configuration loading with both file and env var sources

### 6. Update Documentation

1. Add feature description to `README.md` under the appropriate section
2. Update `docs/coding_guide.md` if introducing new conventions
3. Document any new CLI flags or environment variables

### 7. Validate

Run all quality checks before considering the extension complete:

```bash
uv run ruff check .          # Linting
uv run ruff format --check . # Formatting
uv run mypy src/             # Type checking
uv run pytest                # Tests
```

Fix any issues before committing.

## Extension Patterns

### Adding a New Service

```python
# src/base_project/services/my_feature.py
"""My feature service module."""

from __future__ import annotations

from base_project.config import AppConfig


class MyFeatureService:
    """Service for my feature.

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

### Adding a New Config Section

```python
# In config.py, add:
class MyFeatureConfig(BaseSettings):
    """Configuration for my feature."""

    model_config = SettingsConfigDict(
        env_prefix="MY_FEATURE_",
        case_sensitive=False,
    )

    enabled: bool = False
    api_key: str = ""
```

### Adding a CLI Subcommand

```python
# In main.py, extend parse_args:
subparsers = parser.add_subparsers(dest="command", help="Available commands")

# Add subcommand parser
my_cmd_parser = subparsers.add_parser("my-command", help="Description")
my_cmd_parser.add_argument("--flag", type=str, help="A flag")
```

## Anti-Patterns to Avoid

- **Don't** create modules outside `src/base_project/`
- **Don't** skip type hints or docstrings — the project enforces strict mypy
- **Don't** hardcode configuration values — always use pydantic-settings
- **Don't** add dev dependencies to main dependencies list
- **Don't** modify `.github/skills/` files during normal development
- **Don't** skip validation steps (ruff, mypy, pytest) before committing
