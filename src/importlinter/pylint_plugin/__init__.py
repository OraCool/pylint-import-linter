"""
Pylint plugin for import-linter integration.

This plugin allows pylint to enforce import contracts defined in .importlinter configuration files.
"""

import os  # For test compatibility
import sys  # For test compatibility

from .checker import ImportLinterChecker


def register(linter):
    """Register the plugin with pylint."""
    linter.register_checker(ImportLinterChecker(linter))


__all__ = ["register", "ImportLinterChecker", "os", "sys"]
