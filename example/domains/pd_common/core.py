"""Core utilities and base classes shared across all domains."""


class BaseService:
    """Base service class for all domain services."""

    def __init__(self):
        self.logger = self._setup_logging()

    def _setup_logging(self):
        """Setup logging for the service."""
        import logging

        return logging.getLogger(self.__class__.__name__)


class ValidationError(Exception):
    """Base validation error for all domains."""

    pass


def format_currency(amount, currency_code="USD"):
    """Format currency amount."""
    return f"{currency_code} {amount: .2f}"
