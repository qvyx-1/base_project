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
