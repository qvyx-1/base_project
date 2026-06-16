"""Example module demonstrating project structure."""

from __future__ import annotations


class ExampleService:
    """Example service class.

    This demonstrates the project's coding style and structure.
    """

    def __init__(self, name: str = "example") -> None:
        """Initialize the example service.

        Args:
            name: Service name identifier.
        """
        self.name = name
        self._initialized = False

    def initialize(self) -> bool:
        """Initialize the service.

        Returns:
            True if initialization was successful.
        """
        self._initialized = True
        return True

    def is_ready(self) -> bool:
        """Check if the service is ready.

        Returns:
            True if the service has been initialized.
        """
        return self._initialized

    def process(self, data: str) -> str:
        """Process input data.

        Args:
            data: Input string to process.

        Returns:
            Processed string with service name prefix.

        Raises:
            ValueError: If data is empty.
        """
        if not data:
            raise ValueError("Input data cannot be empty")

        return f"[{self.name}] {data}"
