---
name: database-setup
description: 'Set up SQLAlchemy models, migrations, and database configuration for base_project. Use for scaffolding ORM models, Alembic migrations, connection pooling, or any database layer.'
argument-hint: 'Database type and model names'
---

# Database Setup

Set up a complete database layer for `base_project` using SQLAlchemy with Alembic migrations.

## When to Use

- Adding database-backed features
- Setting up ORM models for the first time
- Creating database migrations
- Configuring connection pooling or multiple databases

## Procedure

### 1. Add Dependencies

```toml
# In pyproject.toml [project.dependencies]:
"sqlalchemy>=2.0"
"alembic>=1.13"

# In pyproject.toml [project.optional-dependencies] dev:
"asyncpg>=0.30"       # PostgreSQL driver
"aiosqlite>=0.20"    # SQLite async driver
```

```bash
uv sync
```

### 2. Configure Database Settings

Add to `config.py`:

```python
class DatabaseConfig(BaseSettings):
    """Database configuration settings."""

    model_config = SettingsConfigDict(
        env_prefix="DB_",
        case_sensitive=False,
    )

    url: str = "sqlite+aiosqlite:///./app.db"
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False
    pool_pre_ping: bool = True
```

Add to `config/app.toml`:

```toml
[database]
url = "sqlite+aiosqlite:///./app.db"
pool_size = 5
echo = false
pool_pre_ping = true
```

### 3. Create Base Model

```bash
mkdir -p src/base_project/models
touch src/base_project/models/__init__.py
```

`src/base_project/models/base.py`:

```python
"""SQLAlchemy base model."""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(DeclarativeBase, MappedAsDataclass):
    """Base class for SQLAlchemy models."""

    pass
```

### 4. Create Example Model

`src/base_project/models/user.py`:

```python
"""User model example."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from base_project.models.base import Base


class User(Base):
    """User model.

    Attributes:
        id: Primary key.
        username: Username string.
        email: Email address.
        created_at: Record creation timestamp.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow)
```

`src/base_project/models/__init__.py`:

```python
"""Database models package."""

from base_project.models.base import Base
from base_project.models.user import User

__all__ = ["Base", "User"]
```

### 5. Initialize Alembic

```bash
alembic init alembic
```

`alembic/env.py` — update `run_migrations_online`:

```python
from sqlalchemy import engine_from_config, pool
from base_project.models.base import Base
from base_project.config import DatabaseConfig

config.set_main_option("sqlalchemy.url", DatabaseConfig().url)

target_metadata = Base.metadata
```

### 6. Generate First Migration

```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### 7. Create Database Service

`src/base_project/services/database.py`:

```python
"""Database service for session management."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from base_project.config import DatabaseConfig


class DatabaseService:
    """Manages database connections and sessions.

    Args:
        config: Database configuration settings.
    """

    def __init__(self, config: DatabaseConfig) -> None:
        """Initialize the database service.

        Args:
            config: Database configuration.
        """
        self.config = config
        self.engine = create_async_engine(
            config.url,
            echo=config.echo,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
            pool_pre_ping=config.pool_pre_ping,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide a transactional session.

        Yields:
            AsyncSession instance.
        """
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with AsyncSession(self.engine) as session:
            yield session

    async def dispose(self) -> None:
        """Close the database engine."""
        await self.engine.dispose()
```

### 8. Write Tests

`tests/test_database.py`:

```python
"""Tests for database models and service."""

import pytest


class TestDatabaseConfig:
    """Test cases for DatabaseConfig."""

    def test_default_url(self) -> None:
        """Test default database URL is SQLite."""
        from base_project.config import DatabaseConfig

        config = DatabaseConfig()
        assert "sqlite" in config.url

    def test_pool_size(self) -> None:
        """Test default pool size."""
        from base_project.config import DatabaseConfig

        config = DatabaseConfig()
        assert config.pool_size == 5
```

### 9. Validate

```bash
uv run ruff check .
uv run mypy src/
uv run pytest
```

## Migration Commands Reference

| Task | Command |
|------|---------|
| Create migration | `alembic revision --autogenerate -m "description"` |
| Apply migrations | `alembic upgrade head` |
| Rollback one | `alembic downgrade -1` |
| Current version | `alembic current` |
| History | `alembic history` |
| Upgrade to specific | `alembic upgrade <revision>` |

## Anti-Patterns

- **Don't** import models at the top level — use lazy imports to avoid circular deps
- **Don't** hardcode connection strings — always use pydantic-settings
- **Don't** forget to run migrations after model changes
- **Don't** use synchronous SQLAlchemy in async code
- **Don't** commit migrations without testing them (`alembic downgrade head && alembic upgrade head`)
