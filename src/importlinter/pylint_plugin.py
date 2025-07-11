"""
Pylint plugin for import-linter integration.

This plugin allows pylint to enforce import contracts defined in .importlinter configuration files.
"""
from __future__ import annotations

import os
import sys
from typing import TYPE_CHECKING, Union

from pylint import checkers
from pylint.lint import PyLinter

from importlinter.application import use_cases
from importlinter.application.sentinels import NotSupplied
from importlinter.configuration import configure

if TYPE_CHECKING:
    from astroid import nodes

# Configure import-linter
configure()

# Plugin message definitions
IMPORT_CONTRACT_VIOLATION = "import-contract-violation"
IMPORT_CONTRACT_ERROR = "import-contract-error"

MESSAGES = {
    "E9001": (
        "Import contract violation: %s",
        IMPORT_CONTRACT_VIOLATION,
        "Import violates architecture contract defined in .importlinter configuration",
    ),
    "E9002": (
        "Import contract error: %s",
        IMPORT_CONTRACT_ERROR,
        "Error occurred while checking import contracts",
    ),
}


class ImportLinterChecker(checkers.BaseChecker):
    """Pylint checker that enforces import-linter contracts."""
    
    name = "import-linter"
    msgs = MESSAGES
    
    # Options for the checker
    options = (
        (
            "import-linter-config",
            {
                "default": None,
                "type": "string",
                "metavar": "<file>",
                "help": "Path to import-linter configuration file (defaults to .importlinter)",
            },
        ),
        (
            "import-linter-contracts",
            {
                "default": (),
                "type": "csv",
                "metavar": "<contract-ids>",
                "help": "Comma-separated list of contract IDs to check (defaults to all)",
            },
        ),
        (
            "import-linter-target-folders",
            {
                "default": (),
                "type": "csv",
                "metavar": "<folders>",
                "help": "Comma-separated list of folders to check (defaults to all analyzed files)",
            },
        ),
        (
            "import-linter-exclude-folders",
            {
                "default": (),
                "type": "csv",
                "metavar": "<folders>",
                "help": "Comma-separated list of folders to exclude from checking",
            },
        ),
        (
            "import-linter-cache-dir",
            {
                "default": None,
                "type": "string",
                "metavar": "<dir>",
                "help": "Directory for import-linter cache (defaults to .import_linter_cache)",
            },
        ),
        (
            "import-linter-no-cache",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Disable import-linter caching",
            },
        ),
    )
    
    def __init__(self, linter: PyLinter) -> None:
        super().__init__(linter)
        self._contracts_checked = False
        self._first_module_node = None
        self._analyzed_files = set()
        
    def open(self) -> None:
        """Called when the checker is opened."""
        # Add current directory to path for import resolution
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())
    
    def close(self) -> None:
        """Called when the checker is closed - this is where we run import-linter."""
        if not self._contracts_checked and self._should_check_contracts():
            self._check_import_contracts()
            self._contracts_checked = True
    
    def _should_check_contracts(self) -> bool:
        """Determine if we should check contracts based on folder configuration."""
        target_folders = self.linter.config.import_linter_target_folders or ()
        exclude_folders = self.linter.config.import_linter_exclude_folders or ()
        
        # If no specific folders are configured, check all analyzed files
        if not target_folders and not exclude_folders:
            return bool(self._analyzed_files)
        
        # Check if any analyzed files match target folders or don't match exclude folders
        for file_path in self._analyzed_files:
            # Convert to relative path for comparison
            rel_path = os.path.relpath(file_path)
            
            # Check exclusions first
            if exclude_folders:
                excluded = any(
                    rel_path.startswith(folder) or rel_path.startswith(folder + os.sep)
                    for folder in exclude_folders
                )
                if excluded:
                    continue
            
            # Check inclusions
            if target_folders:
                included = any(
                    rel_path.startswith(folder) or rel_path.startswith(folder + os.sep)
                    for folder in target_folders
                )
                if included:
                    return True
            else:
                # No target folders specified, include if not excluded
                return True
        
        return False
    
    def _check_import_contracts(self) -> None:
        """Run import-linter contract checking."""
        try:
            # Get configuration options
            config_filename = self.linter.config.import_linter_config
            limit_to_contracts = tuple(self.linter.config.import_linter_contracts or ())
            cache_dir = self._get_cache_dir()
            
            # Log which files are being analyzed for debugging
            target_folders = self.linter.config.import_linter_target_folders or ()
            exclude_folders = self.linter.config.import_linter_exclude_folders or ()
            
            if target_folders or exclude_folders:
                # Create a more specific violation message when using folder filtering
                folder_info = []
                if target_folders:
                    folder_info.append(f"targeting folders: {', '.join(target_folders)}")
                if exclude_folders:
                    folder_info.append(f"excluding folders: {', '.join(exclude_folders)}")
                folder_msg = f" ({'; '.join(folder_info)})"
            else:
                folder_msg = ""
            
            # Run import-linter
            passed = use_cases.lint_imports(
                config_filename=config_filename,
                limit_to_contracts=limit_to_contracts,
                cache_dir=cache_dir,
                is_debug_mode=False,
                show_timings=False,
                verbose=False,
            )
            
            if not passed:
                # Import-linter failed
                violation_msg = (
                    f"Contract validation failed{folder_msg}. "
                    "Run 'lint-imports --verbose' for details."
                )
                # Use the first module node we encountered, or create a dummy one
                node_for_message = self._first_module_node
                self.add_message(
                    IMPORT_CONTRACT_VIOLATION,
                    args=(violation_msg,),
                    node=node_for_message,
                )

        except (ImportError, FileNotFoundError, ValueError) as e:
            # Handle any errors in contract checking
            node_for_message = self._first_module_node
            self.add_message(
                IMPORT_CONTRACT_ERROR,
                args=(str(e),),
                node=node_for_message,
            )
    
    def _get_cache_dir(self) -> Union[str, None, type[NotSupplied]]:
        """Get the cache directory setting."""
        if self.linter.config.import_linter_no_cache:
            return None
        if self.linter.config.import_linter_cache_dir:
            return self.linter.config.import_linter_cache_dir
        return NotSupplied
    
    # We need at least one visit method for the checker to be active
    def visit_module(self, node: nodes.Module) -> None:
        """Visit module nodes - capture first one for error reporting and track analyzed files."""
        if self._first_module_node is None:
            self._first_module_node = node
        
        # Track the file path for folder-based filtering
        if hasattr(node, 'file') and node.file:
            self._analyzed_files.add(node.file)


def register(linter: PyLinter) -> None:
    """Register the plugin with pylint."""
    linter.register_checker(ImportLinterChecker(linter))
