"""
Pylint plugin for import-linter integration.

This plugin allows pylint to enforce import contracts defined in .importlinter configuration files.

Note: This module has been refactored into a package structure for better maintainability.
The main functionality is now split across multiple modules:
- config.py: Plugin configuration options
- module_resolver.py: Module path resolution logic
- violation_matcher.py: Violation detection and matching
- contract_checker.py: Contract checking logic
- checker.py: Main checker class
"""

# Import from the new modular structure
from importlinter.pylint_plugin.checker import ImportLinterChecker


def register(linter):
    """Register the plugin with pylint."""
    linter.register_checker(ImportLinterChecker(linter))


# For backward compatibility, expose the checker class at the module level
__all__ = ["ImportLinterChecker", "register"]
