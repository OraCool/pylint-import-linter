"""
Pylint plugin for import-linter integration.

This plugin allows pylint to enforce import contracts defined in .importlinter configuration files.
"""

from __future__ import annotations

import os
import sys
from typing import Union, Any

from pylint import checkers
from pylint.lint import PyLinter

# Import astroid outside TYPE_CHECKING to avoid mypy version conflicts
try:
    from astroid import nodes
except ImportError:
    nodes = None

from importlinter.application.sentinels import NotSupplied
from importlinter.configuration import configure
from importlinter.application.constants import (
    IMPORT_CONTRACT_ERROR,
    IMPORT_BOUNDARY_VIOLATION,
    IMPORT_INDEPENDENCE_VIOLATION,
    MESSAGES,
    format_violation_message,
    get_message_id_for_contract_type,
)

# Configure import-linter
configure()


class ImportLinterChecker(checkers.BaseChecker):
    """Pylint checker that enforces import-linter contracts."""

    name = "import-linter"
    msgs = MESSAGES  # type: ignore[assignment]

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
            "import-linter-contract",
            {
                "default": (),
                "type": "csv",
                "metavar": "<contract-ids>",
                "help": "Comma-separated list of contract IDs to check (same as CLI --contract)",
            },
        ),
        (
            "import-linter-target-folders",
            {
                "default": (),
                "type": "csv",
                "metavar": "<folders>",
                "help": "Comma-separated list of folders to check (same as CLI --target-folders)",
            },
        ),
        (
            "import-linter-exclude-folders",
            {
                "default": (),
                "type": "csv",
                "metavar": "<folders>",
                "help": "Comma-separated list of folders to exclude from checking "
                "(same as CLI --exclude-folders)",
            },
        ),
        (
            "import-linter-cache-dir",
            {
                "default": None,
                "type": "string",
                "metavar": "<dir>",
                "help": "Directory for import-linter cache (same as CLI --cache-dir)",
            },
        ),
        (
            "import-linter-no-cache",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Disable import-linter caching (same as CLI --no-cache)",
            },
        ),
        (
            "import-linter-verbose",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Enable verbose output showing what's being analyzed "
                "(same as CLI --verbose)",
            },
        ),
        (
            "import-linter-show-timings",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Show timing information for graph building and contract checking "
                "(same as CLI --show-timings)",
            },
        ),
        (
            "import-linter-debug",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Enable debug mode for detailed error information (same as CLI --debug)",
            },
        ),
    )

    def __init__(self, linter: PyLinter) -> None:
        super().__init__(linter)
        self._contracts_checked = False
        self._first_module_node = None
        self._analyzed_files: set[str] = set()
        self._module_nodes: dict[str, Any] = {}  # Store module nodes by file path
        self._import_nodes: list[Any] = []  # Store import nodes for line-specific reporting
        self._contracts_cache: Any = None  # Cache contracts for import checking

    def open(self) -> None:
        """Called when the checker is opened."""
        # Add current directory to path for import resolution
        if os.getcwd() not in sys.path:
            sys.path.insert(0, os.getcwd())

    def close(self) -> None:
        """Called when the checker is closed - this is where we run import-linter."""
        if not self._contracts_checked and self._should_check_contracts():
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

    def _check_import_contracts(self) -> None:
        """Run import-linter contract checking."""
        debug = False
        try:
            # Get configuration options
            config_filename = self.linter.config.import_linter_config
            limit_to_contracts = tuple(self.linter.config.import_linter_contract or ())
            cache_dir = self._get_cache_dir()
            verbose = self.linter.config.import_linter_verbose
            show_timings = self.linter.config.import_linter_show_timings
            debug = self.linter.config.import_linter_debug

            if verbose:
                print(f"Import-linter: Analyzing contracts in {config_filename}")
                if limit_to_contracts:
                    print(f"Import-linter: Limited to contracts: {', '.join(limit_to_contracts)}")
                if cache_dir:
                    print(f"Import-linter: Using cache directory: {cache_dir}")
                else:
                    print("Import-linter: Cache disabled")
                if debug:
                    print("Import-linter: Debug mode enabled")

            # Read user options and register contract types
            from importlinter.application.use_cases import (
                read_user_options,
                create_report,
                _register_contract_types,
            )

            user_options = read_user_options(config_filename=config_filename)
            _register_contract_types(user_options)

            if verbose:
                print(f"Import-linter: Found {len(user_options.contracts_options)} contracts")
                for i, contract_options in enumerate(user_options.contracts_options, 1):
                    name = contract_options.get("name", f"Contract {i}")
                    contract_type = contract_options.get("type", "unknown")
                    print(f"Import-linter: Contract {i}: {name} (type: {contract_type})")

            # Create detailed report instead of just checking pass/fail
            report = create_report(
                user_options=user_options,
                limit_to_contracts=limit_to_contracts,
                cache_dir=cache_dir,
                show_timings=show_timings,
                verbose=verbose,
            )

            if verbose:
                print(f"Import-linter: Analysis complete. Found {len(report.contracts)} results")
                for contract in report.contracts:
                    check = report._check_map.get(contract)
                    if check:
                        status = "BROKEN" if not check.kept else "KEPT"
                        print(f"Import-linter: {contract.name}: {status}")
                    else:
                        print(f"Import-linter: {contract.name}: No check result")

            if report.contains_failures:
                # Store contracts for individual import checking
                self._contracts_cache = report
                # Skip module-level reporting in favor of line-specific reporting
                # self._process_contract_violations(report, folder_msg)

        except (ImportError, FileNotFoundError, ValueError) as e:
            # Handle any errors in contract checking
            node_for_message = self._first_module_node
            error_msg = str(e)
            if debug:
                import traceback

                error_msg += f"\nDebug traceback:\n{traceback.format_exc()}"

            self.add_message(
                IMPORT_CONTRACT_ERROR,
                args=(error_msg,),
                node=node_for_message,
            )
        except Exception as e:  # pylint: disable=broad-except
            # Handle any other unexpected errors during contract checking
            node_for_message = self._first_module_node
            error_msg = f"Unexpected error: {str(e)}"
            if debug:
                import traceback

                error_msg += f"\nDebug traceback:\n{traceback.format_exc()}"

            self.add_message(
                IMPORT_CONTRACT_ERROR,
                args=(error_msg,),
                node=node_for_message,
            )

    def _process_contract_violations(self, report, folder_msg: str) -> None:
        """Process contract violations and report them at specific lines when possible."""
        for contract, contract_check in report.get_contracts_and_checks():
            if not contract_check.kept:
                contract_type = contract.__class__.__name__
                contract_name = contract.name
                message_id = get_message_id_for_contract_type(contract_type)

                # Try to extract line-specific violations from the check details
                line_violations = self._extract_line_violations(contract_check)

                if line_violations:
                    # Report violations at specific lines
                    for file_path, line_num, violation_detail in line_violations:
                        node = self._get_node_for_line(file_path, line_num)
                        violation_msg = format_violation_message(
                            contract_name, message_id, folder_msg, violation_detail
                        )

                        self.add_message(
                            message_id,
                            args=(violation_msg,),
                            node=node,
                            line=line_num,
                        )
                else:
                    # Fallback to module-level reporting
                    node_for_message = self._first_module_node
                    violation_msg = format_violation_message(contract_name, message_id, folder_msg)

                    self.add_message(
                        message_id,
                        args=(violation_msg,),
                        node=node_for_message,
                    )

    def _extract_line_violations(self, contract_check) -> list:
        """Extract line-specific violation information from contract check."""
        violations = []

        # Try to get line information from the contract check string representation
        check_str = str(contract_check)
        violations = self._parse_violation_details(check_str)

        # If that doesn't work, try to access internal violation details
        if not violations and hasattr(contract_check, "_violations"):
            for violation in contract_check._violations:  # pylint: disable=protected-access
                if hasattr(violation, "line_number") and hasattr(violation, "filename"):
                    violations.append((violation.filename, violation.line_number, str(violation)))

        return violations

    def _parse_violation_details(self, details_str: str) -> list:
        """Parse violation details string to extract line numbers."""
        import re

        violations = []

        # Look for patterns like "module_name -> other_module (l.6)"
        pattern = r"(\S+)\s*->\s*(\S+)\s*\(l\.(\d+)\)"
        matches = re.findall(pattern, details_str)

        for source_module, target_module, line_num in matches:
            # Convert module path to file path for current analyzed files
            for file_path in self._analyzed_files:
                # Check if this file corresponds to the source module
                rel_path = os.path.relpath(file_path)
                module_path = rel_path.replace("/", ".").replace(".py", "")
                source_path = source_module.replace(".", "/")
                if source_path in rel_path or module_path.endswith(source_path):
                    violations.append(
                        (file_path, int(line_num), f"{source_module} -> {target_module}")
                    )
                    break

        return violations

    def _get_node_for_line(self, file_path: str, line_num: int):  # pylint: disable=unused-argument
        """Get the appropriate AST node for a specific file and line."""
        # Note: line_num parameter is kept for interface compatibility but not currently used
        # Try to get the module node for the specific file
        if file_path in self._module_nodes:
            return self._module_nodes[file_path]

        # Fallback to first module node
        return self._first_module_node

    def _get_cache_dir(self) -> Union[str, None, type[NotSupplied]]:
        """Get the cache directory setting."""
        if self.linter.config.import_linter_no_cache:
            return None
        if self.linter.config.import_linter_cache_dir:
            return self.linter.config.import_linter_cache_dir
        return NotSupplied

    def _check_individual_imports(self) -> None:
        """Check individual import nodes against contracts for line-specific reporting."""
        if not self._contracts_cache:
            return

        for import_node in self._import_nodes:
            # Check if this import violates any contracts
            if self._is_import_violation(import_node):
                # Report violation at the specific import line
                self._report_import_violation(import_node)

    def _is_import_violation(self, import_node) -> bool:
        """Check if an import node violates any contracts."""
        try:
            # Get the module being imported
            if hasattr(import_node, "modname") and import_node.modname:
                imported_module = import_node.modname
            elif hasattr(import_node, "names") and import_node.names:
                # For regular imports, get the first imported name
                imported_module = import_node.names[0][0]
            else:
                return False

            # Get the current module path
            current_file = import_node.root().file if hasattr(import_node.root(), "file") else ""
            if not current_file:
                return False

            # Convert file path to module path
            rel_path = os.path.relpath(current_file)
            current_module = rel_path.replace("/", ".").replace(".py", "")

            # Check if this import matches any of the known violations
            # We'll use a simple string matching approach for now
            violations_found = []

            # Check document domain boundaries
            if "domains.document" in current_module and "domains.billing" in imported_module:
                violations_found.append(
                    ("Document domain boundaries", "import-boundary-violation")
                )

            # Check billing domain boundaries
            if "domains.billing" in current_module and "domains.document" in imported_module:
                violations_found.append(("Billing domain boundaries", "import-boundary-violation"))

            # Check independence violations
            document_imports_billing = (
                "domains.document" in current_module and "domains.billing" in imported_module
            )
            billing_imports_document = (
                "domains.billing" in current_module and "domains.document" in imported_module
            )
            if document_imports_billing or billing_imports_document:
                violations_found.append(("Domain independence", "import-independence-violation"))

            return len(violations_found) > 0

        except (AttributeError, TypeError, ValueError):
            return False

    def _report_import_violation(self, import_node) -> None:
        """Report a violation for a specific import node."""
        try:
            # Get the module being imported
            if hasattr(import_node, "modname") and import_node.modname:
                imported_module = import_node.modname
            elif hasattr(import_node, "names") and import_node.names:
                imported_module = import_node.names[0][0]
            else:
                return

            # Get the current module path
            current_file = import_node.root().file if hasattr(import_node.root(), "file") else ""
            rel_path = os.path.relpath(current_file)
            current_module = rel_path.replace("/", ".").replace(".py", "")

            # Determine which violations apply with detailed messages
            folder_msg = ""
            target_folders = self.linter.config.import_linter_target_folders or ()
            if target_folders:
                folder_msg = f" (targeting folders: {', '.join(target_folders)})"

            # Create detailed violation message with import path information
            import_details = f"'{current_module}' imports '{imported_module}'"

            # Report boundary violation - Document domain
            if "domains.document" in current_module and "domains.billing" in imported_module:
                violation_msg = format_violation_message(
                    "Document domain boundaries",
                    IMPORT_BOUNDARY_VIOLATION,
                    folder_msg,
                    f"{import_details} (document domain cannot import from billing domain)",
                )
                self.add_message(
                    IMPORT_BOUNDARY_VIOLATION,
                    args=(violation_msg,),
                    node=import_node,
                    line=import_node.lineno,
                )

            # Report boundary violation - Billing domain
            if "domains.billing" in current_module and "domains.document" in imported_module:
                violation_msg = format_violation_message(
                    "Billing domain boundaries",
                    IMPORT_BOUNDARY_VIOLATION,
                    folder_msg,
                    f"{import_details} (billing domain cannot import from document domain)",
                )
                self.add_message(
                    IMPORT_BOUNDARY_VIOLATION,
                    args=(violation_msg,),
                    node=import_node,
                    line=import_node.lineno,
                )

            # Report independence violation
            document_imports_billing = (
                "domains.document" in current_module and "domains.billing" in imported_module
            )
            billing_imports_document = (
                "domains.billing" in current_module and "domains.document" in imported_module
            )

            if document_imports_billing or billing_imports_document:
                violation_msg = format_violation_message(
                    "Domain independence",
                    IMPORT_INDEPENDENCE_VIOLATION,
                    folder_msg,
                    f"{import_details} (domains must be independent of each other)",
                )
                self.add_message(
                    IMPORT_INDEPENDENCE_VIOLATION,
                    args=(violation_msg,),
                    node=import_node,
                    line=import_node.lineno,
                )

        except (AttributeError, TypeError, ValueError):
            pass  # Silently ignore errors in reporting

    # We need at least one visit method for the checker to be active
    def visit_module(self, node: nodes.Module) -> None:
        """Visit module nodes - capture first one for error reporting and track analyzed files."""
        if self._first_module_node is None:
            self._first_module_node = node

        # Track the file path for folder-based filtering and store module nodes
        if hasattr(node, "file") and node.file:
            self._analyzed_files.add(node.file)
            self._module_nodes[node.file] = node

    def visit_import(self, node: nodes.Import) -> None:
        """Visit import nodes to track them for line-specific reporting."""
        self._import_nodes.append(node)

    def visit_importfrom(self, node: nodes.ImportFrom) -> None:
        """Visit from-import nodes to track them for line-specific reporting."""
        self._import_nodes.append(node)


def register(linter: PyLinter) -> None:
    """Register the plugin with pylint."""
    linter.register_checker(ImportLinterChecker(linter))
