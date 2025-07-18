"""Main pylint checker class for import-linter integration."""

from __future__ import annotations

import os
import sys
from typing import Any

from pylint import checkers
from pylint.lint import PyLinter

# Import astroid outside TYPE_CHECKING to avoid mypy version conflicts
try:
    from astroid import nodes
except ImportError:
    nodes = None

from importlinter.application.constants import (
    MESSAGES,
    format_violation_message,
    get_message_id_for_contract_type,
)
from importlinter.configuration import configure

from .config import PLUGIN_OPTIONS
from .module_resolver import ModulePathResolver
from .contract_checker import ContractChecker

# Configure import-linter
configure()


class ImportLinterChecker(checkers.BaseChecker):
    """Pylint checker that enforces import-linter contracts."""

    name = "import-linter"
    msgs = MESSAGES  # type: ignore[assignment]
    options = PLUGIN_OPTIONS  # type: ignore[assignment]

    def __init__(self, linter: PyLinter) -> None:
        super().__init__(linter)
        self._contracts_checked = False
        self._first_module_node = None
        self._analyzed_files: set[str] = set()
        self._module_nodes: dict[str, Any] = {}  # Store module nodes by file path
        self._import_nodes: list[Any] = []  # Store import nodes for line-specific reporting
        self._contracts_cache: Any = None  # Cache contracts for import checking
        self._single_file_mode = False  # Track if we're analyzing just one file
        self._target_module_name: str | None = None  # Store the module name being analyzed

        # Initialize helper components immediately with config
        debug = getattr(linter.config, "import_linter_debug", False)
        self._module_resolver = ModulePathResolver(linter.config, debug=debug)
        self._contract_checker = ContractChecker(linter.config, self._module_resolver, debug=debug)

    def open(self) -> None:
        """Called when the checker is opened."""
        self._setup_pythonpath()

    def _setup_pythonpath(self) -> None:
        """Set up PYTHONPATH for import resolution."""
        # Add current directory to path for import resolution
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())

        # Add configured PYTHONPATH entries
        pythonpath_entries = self.linter.config.import_linter_pythonpath or ()
        for path_entry in pythonpath_entries:
            # Convert relative paths to absolute paths
            if not os.path.isabs(path_entry):
                path_entry = os.path.abspath(path_entry)

            if path_entry not in sys.path:
                sys.path.insert(0, path_entry)

            # Also set in environment for import-linter
            current_pythonpath = os.environ.get("PYTHONPATH", "")
            if path_entry not in current_pythonpath.split(os.pathsep):
                if current_pythonpath:
                    os.environ["PYTHONPATH"] = f"{path_entry}{os.pathsep}{current_pythonpath}"
                else:
                    os.environ["PYTHONPATH"] = path_entry

        # Debug output for PYTHONPATH setup
        if self.linter.config.import_linter_verbose and pythonpath_entries:
            print(f"Import-linter: Added PYTHONPATH entries: {', '.join(pythonpath_entries)}")
            print(f"Import-linter: Current PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")

    def close(self) -> None:
        """Called when the checker is closed - this is where we run import-linter."""
        if not self._contracts_checked and self._should_check_contracts():
            # Detect single-file mode for optimization
            self._single_file_mode = len(self._analyzed_files) == 1
            if self._single_file_mode:
                self._optimize_for_single_file()

            self._check_import_contracts()
            self._check_individual_imports()  # Check individual imports for line-specific reporting
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

    def _optimize_for_single_file(self) -> None:
        """Optimize settings when analyzing only a single file."""
        single_file = next(iter(self._analyzed_files))

        # Convert file path to module name
        self._target_module_name = self._module_resolver.get_module_path_from_file(single_file)

        if self.linter.config.import_linter_verbose:
            print(
                f"Import-linter: Single-file mode optimized for module: "
                f"{self._target_module_name}"
            )

        # Additional optimizations for single-file mode
        if self.linter.config.import_linter_fast_mode:
            # Automatically enable caching for fast mode
            if not self.linter.config.import_linter_cache_dir:
                self.linter.config.import_linter_cache_dir = ".import_linter_cache"

    def _check_import_contracts(self) -> None:
        """Run import-linter contract checking."""
        result = self._contract_checker.check_import_contracts(
            self._first_module_node, self._single_file_mode, self._target_module_name
        )

        if result and isinstance(result, dict) and "error" in result:
            # Handle error case
            self.add_message(
                result["error"],
                args=result["args"],
                node=result["node"],
            )
        elif result:
            # Store contracts for individual import checking
            self._contracts_cache = result

    def _check_individual_imports(self) -> None:
        """Check individual import nodes against contracts for line-specific reporting."""
        if not self._contracts_cache:
            return

        debug = self.linter.config.import_linter_debug
        import_nodes_to_check = self._import_nodes

        # Optimization for single-file mode with fast mode enabled
        if (
            self._single_file_mode
            and self.linter.config.import_linter_fast_mode
            and self._target_module_name
        ):
            # Filter import nodes to only those from our target file
            import_nodes_to_check = [
                node
                for node in self._import_nodes
                if (hasattr(node.root(), "file") and node.root().file in self._analyzed_files)
            ]
            if debug:
                print(
                    f"Debug: Fast mode filtered to {len(import_nodes_to_check)} "
                    f"import nodes from {len(self._import_nodes)} total"
                )

        if debug:
            print(f"Debug: Checking {len(import_nodes_to_check)} import nodes for violations")

        for import_node in import_nodes_to_check:
            # Check if this import violates any contracts
            if self._contract_checker.is_import_violation(import_node, self._contracts_cache):
                if debug:
                    print(f"Debug: Found violation in import node at line {import_node.lineno}")
                # Report violation at the specific import line
                self._report_import_violation(import_node)
            elif debug:
                print(f"Debug: No violation found for import at line {import_node.lineno}")

    def _report_import_violation(self, import_node) -> None:
        """Report a violation for a specific import node using contract-based logic."""
        try:
            # Only report if we have contracts loaded
            if not self._contracts_cache:
                return

            # Get the module being imported
            imported_module = self._contract_checker._extract_imported_module(import_node)
            if not imported_module:
                return

            # Get the current module path
            current_file = import_node.root().file if hasattr(import_node.root(), "file") else ""
            current_module = self._module_resolver.get_module_path_from_file(current_file)

            # Handle relative imports
            imported_module = self._contract_checker._resolve_relative_import(
                imported_module, import_node, current_module
            )
            if not imported_module:
                return

            # Determine folder message for context
            folder_msg = ""
            target_folders = self.linter.config.import_linter_target_folders or ()
            if target_folders:
                folder_msg = f" (targeting folders: {', '.join(target_folders)})"

            # Create detailed violation message with import path information
            import_details = f"'{current_module}' imports '{imported_module}'"

            debug = self.linter.config.import_linter_debug

            if debug:
                print(f"Debug: _report_import_violation called for {import_details}")

            # Check against actual contracts and report violations
            for contract, contract_check in self._contracts_cache.get_contracts_and_checks():
                if not contract_check.kept:
                    # Use contract checker logic
                    if self._contract_checker._check_contract_against_import(
                        contract, contract_check, current_module, imported_module
                    ):
                        # Determine the contract type and message ID
                        contract_type = contract.__class__.__name__
                        message_id = get_message_id_for_contract_type(contract_type)

                        if debug:
                            print(f"Debug: Adding message {message_id} for {contract.name}")

                        # Create appropriate violation message
                        violation_msg = format_violation_message(
                            contract.name,
                            message_id,
                            folder_msg,
                            f"{import_details} (violates {contract.name})",
                        )

                        # Report the violation
                        self.add_message(
                            message_id,
                            args=(violation_msg,),
                            node=import_node,
                            line=import_node.lineno,
                        )

                        if debug:
                            print(
                                f"Debug: Message added successfully for line {import_node.lineno}"
                            )

                        # Only report the first matching violation per import
                        return

        except (AttributeError, TypeError, ValueError):
            pass  # Silently ignore errors in reporting

    # Visitor methods for collecting nodes
    def visit_module(self, node) -> None:
        """Visit module nodes - capture first one for error reporting and track analyzed files."""
        if self._first_module_node is None:
            self._first_module_node = node

        # Track the file path for folder-based filtering and store module nodes
        if hasattr(node, "file") and node.file:
            self._analyzed_files.add(node.file)
            self._module_nodes[node.file] = node

    def visit_import(self, node) -> None:
        """Visit import nodes to track them for line-specific reporting."""
        self._import_nodes.append(node)

    def visit_importfrom(self, node) -> None:
        """Visit from-import nodes to track them for line-specific reporting."""
        self._import_nodes.append(node)

    # Backward compatibility methods for tests
    def _get_module_path_from_file(self, file_path: str) -> str:
        """Delegate to module resolver."""
        return self._module_resolver.get_module_path_from_file(file_path)

    def _get_cache_dir(self):
        """Delegate to contract checker."""
        return self._contract_checker._get_cache_dir()

    def _module_matches_pattern(self, module_name: str, pattern) -> bool:
        """Delegate to violation matcher."""
        return self._contract_checker.violation_matcher.module_matches_pattern(
            module_name, pattern
        )

    def _check_contract_against_import(
        self,
        contract,
        contract_check,
        current_module: str,
        imported_module: str,
        fast_mode: bool = False,
    ) -> bool:
        """Delegate to contract checker."""
        return self._contract_checker._check_contract_against_import(
            contract, contract_check, current_module, imported_module
        )

    def _modules_are_same_domain(self, module1: str, module2: str) -> bool:
        """Delegate to violation matcher."""
        return self._contract_checker.violation_matcher.modules_are_same_domain(module1, module2)

    def _is_import_violation(self, import_node) -> bool:
        """Delegate to contract checker."""
        return self._contract_checker.is_import_violation(import_node, self._contracts_cache)
