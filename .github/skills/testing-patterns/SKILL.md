---
name: testing-patterns
description: 'Write tests for base_project following pytest conventions. Use for creating unit tests, integration tests, config testing, mocking patterns, fixtures, and test coverage.'
argument-hint: 'What to test (module/service/config)'
---

# Testing Patterns

Write comprehensive tests for `base_project` using pytest with proper fixtures, mocking, and coverage.

## When to Use

- Writing new tests for existing code
- Setting up test infrastructure (fixtures, mocks)
- Adding integration tests
- Testing configuration loading from multiple sources
- Improving test coverage

## Conventions

### Test Structure

```python
"""Tests for <module>."""

from __future__ import annotations

import pytest


class Test<ClassName>:
    """Test cases for <ClassName>."""

    def test_<scenario>(self) -> None:
        """Test description.

        Verifies that <expected behavior>.
        """
        # Arrange
        # Act
        # Assert
```

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Test file | `test_<module>.py` | `test_service.py` |
| Test class | `Test<ClassName>` | `TestExampleService` |
| Test method | `test_<scenario>` | `test_default_initialization` |
| Fixture | `fixture_name` | `mock_config` |

### File Organization

```
tests/
├── __init__.py
├── test_service.py       # Unit tests for service layer
├── test_config.py        # Config loading tests
├── test_api.py           # API endpoint tests
└── conftest.py           # Shared fixtures
```

## Procedure

### 1. Identify What to Test

| Code Type | Test Focus |
|-----------|-----------|
| Service class | Happy path, edge cases, error conditions |
| Config loading | File load, env var override, defaults, missing file |
| API endpoint | Status codes, validation errors, auth failures |
| Model/Schema | Validation, serialization, constraints |

### 2. Write Unit Tests

```python
"""Tests for base_project package."""

import pytest

from base_project.service import ExampleService


class TestExampleService:
    """Test cases for ExampleService class."""

    def test_default_initialization(self) -> None:
        """Test that service initializes with default name."""
        service = ExampleService()
        assert service.name == "example"
        assert not service.is_ready()

    def test_custom_name(self) -> None:
        """Test service initialization with custom name."""
        service = ExampleService(name="custom")
        assert service.name == "custom"

    def test_initialize(self) -> None:
        """Test service initialization."""
        service = ExampleService()
        result = service.initialize()
        assert result is True
        assert service.is_ready()

    def test_process(self) -> None:
        """Test data processing."""
        service = ExampleService(name="test")
        service.initialize()
        result = service.process("hello")
        assert result == "[test] hello"

    def test_process_empty_data(self) -> None:
        """Test that empty data raises ValueError."""
        service = ExampleService()
        with pytest.raises(ValueError, match="empty"):
            service.process("")
```

### 3. Test Configuration Loading

```python
"""Tests for configuration module."""

import tempfile
from pathlib import Path

import pytest

from base_project.config import AppConfig


class TestAppConfig:
    """Test cases for AppConfig."""

    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = AppConfig()
        assert config.app_name == "Base Project"
        assert config.version == "0.1.0"
        assert config.debug is False
        assert config.log_level == "INFO"

    def test_from_file(self, tmp_path: Path) -> None:
        """Test loading configuration from file."""
        toml_content = """
[app]
app_name = "Test App"
debug = true
log_level = "DEBUG"
"""
        config_file = tmp_path / "test_config.toml"
        config_file.write_text(toml_content)

        config = AppConfig.from_file(config_file)
        assert config.app_name == "Test App"
        assert config.debug is True

    def test_from_missing_file(self, tmp_path: Path) -> None:
        """Test loading from non-existent file returns defaults."""
        config = AppConfig.from_file(tmp_path / "nonexistent.toml")
        assert config.app_name == "Base Project"

    def test_env_var_override(self) -> None:
        """Test environment variable overrides defaults."""
        import os
        os.environ["APP_APP_NAME"] = "Env App"
        try:
            config = AppConfig()
            assert config.app_name == "Env App"
        finally:
            del os.environ["APP_APP_NAME"]
```

### 4. Use Fixtures for Repeated Setup

`tests/conftest.py`:

```python"""Shared test fixtures."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def sample_config_path(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary TOML config file.

    Yields:
        Path to the temporary config file.
    """
    config_content = """
[app]
app_name = "Test App"
version = "1.0.0"
debug = true
log_level = "DEBUG"

[database]
url = "sqlite:///./test.db"
"""
    config_file = tmp_path / "test_config.toml"
    config_file.write_text(config_content)
    yield config_file


@pytest.fixture
def example_service() -> Generator:
    """Provide an initialized ExampleService.

    Yields:
        Initialized ExampleService instance.
    """
    from base_project.service import ExampleService

    service = ExampleService(name="test")
    service.initialize()
    yield service
```

### 5. Mock External Dependencies

```python
"""Tests with mocking."""

from unittest.mock import MagicMock, patch

import pytest


class TestWithMocks:
    """Test cases using mocked dependencies."""

    def test_service_with_mocked_config(self) -> None:
        """Test service behavior with mocked config."""
        from base_project.service import ExampleService

        mock_config = MagicMock()
        mock_config.debug = True

        service = ExampleService(name="mocked")
        with patch.object(service, "initialize", return_value=True):
            result = service.process("data")
            assert result is not None
```

### 6. Test Coverage

```bash
# Run with coverage report
uv run pytest --cov=src/base_project --cov-report=term-missing

# Generate HTML report
uv run pytest --cov=src/base_project --cov-report=html
```

Target: **≥80% coverage** for production code.

## Test Patterns Reference

### Parameterized Tests

```python
@pytest.mark.parametrize("input_data,expected", [
    ("hello", "[test] hello"),
    ("world", "[test] world"),
    ("", None),  # Should raise ValueError
])
def test_process_parametrized(self, input_data: str, expected: str | None) -> None:
    """Test process with multiple inputs."""
    service = ExampleService(name="test")
    if expected is None:
        with pytest.raises(ValueError):
            service.process(input_data)
    else:
        assert service.process(input_data) == expected
```

### Async Tests

```python
import pytest_asyncio

@pytest.mark.asyncio
async def test_async_service() -> None:
    """Test async service method."""
    from base_project.service import AsyncService

    service = AsyncService()
    result = await service.do_something()
    assert result is not None
```

### Integration Test Pattern

```python
class TestIntegration:
    """Integration tests that test multiple components together."""

    def test_full_workflow(self, sample_config_path: Path) -> None:
        """Test complete workflow from config to service execution."""
        from base_project.config import AppConfig
        from base_project.service import ExampleService

        config = AppConfig.from_file(sample_config_path)
        service = ExampleService(name=config.app_name)
        service.initialize()

        result = service.process("test data")
        assert "Test App" in result
```

## Anti-Patterns

- **Don't** test implementation details — test behavior
- **Don't** skip edge cases and error conditions
- **Don't** use hardcoded paths — use `tmp_path` fixture
- **Don't** mix test classes for different components
- **Don't** forget to clean up environment variables in tests
- **Don't** assert on exact timestamps or UUIDs — use partial matching
