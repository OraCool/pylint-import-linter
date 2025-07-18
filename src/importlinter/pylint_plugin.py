"""
Pylint plugin for import-linter integration.

This plugin allows pylint to enforce import contracts defined in .importlinter configuration files.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Union

from pylint import checkers
from pylint.lint import PyLinter

# Import astroid outside TYPE_CHECKING to avoid mypy version conflicts
try:
    from astroid import nodes
except ImportError:
    nodes = None

from importlinter.application.constants import (
    IMPORT_CONTRACT_ERROR,
    MESSAGES,
    format_violation_message,
    get_message_id_for_contract_type,
)
from importlinter.application.sentinels import NotSupplied
from importlinter.configuration import configure

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
        (
            "import-linter-fast-mode",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Enable fast mode for single-file analysis (skips full graph building)",
            },
        ),
        (
            "import-linter-pythonpath",
            {
                "default": (),
                "type": "csv",
                "metavar": "<paths>",
                "help": "Comma-separated list of paths to add to PYTHONPATH for import resolution",
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
        self._single_file_mode = False  # Track if we're analyzing just one file
        self._target_module_name = None  # Store the module name being analyzed

    def open(self) -> None:
        """Called when the checker is opened."""
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
        self._target_module_name = self._get_module_path_from_file(single_file)

        if self.linter.config.import_linter_verbose:
            print(f"Import-linter: Single-file mode optimized for module: "
                  f"{self._target_module_name}")

        # Additional optimizations for single-file mode
        if self.linter.config.import_linter_fast_mode:
            # Automatically enable caching for fast mode
            if not self.linter.config.import_linter_cache_dir:
                self.linter.config.import_linter_cache_dir = ".import_linter_cache"

            # Force verbose mode off unless explicitly requested to reduce I/O
            if not hasattr(self.linter.config, '_verbose_explicitly_set'):
                # Only modify if verbose wasn't explicitly set by user
                pass  # Keep current verbose setting

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
                _register_contract_types,
                create_report,
                read_user_options,
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
            # Apply optimizations for single-file mode
            if (self._single_file_mode
                    and self.linter.config.import_linter_fast_mode
                    and self._target_module_name):
                if verbose:
                    print(f"Import-linter: Fast mode enabled for {self._target_module_name}")

                # For now, fall back to standard report but with optimizations
                # TODO: Implement more targeted analysis in future versions
                report = create_report(
                    user_options=user_options,
                    limit_to_contracts=limit_to_contracts,
                    cache_dir=cache_dir,
                    show_timings=show_timings,
                    verbose=verbose,
                )
            else:
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

            # Check for specific grimp package resolution errors
            error_str = str(e)
            exception_name = type(e).__name__

            if ("NotATopLevelModule" in error_str
                    or exception_name == "NotATopLevelModule"
                    or "grimp.exceptions.NotATopLevelModule" in error_str):
                if self.linter.config.import_linter_verbose or debug:
                    print(
                        "Import-linter: Skipping analysis due to package structure issues. "
                        "This may be caused by hyphenated directory names or "
                        "non-standard package layouts."
                    )
                # Don't report this as an error since it's likely a project structure issue
                return

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

    def _get_module_path_from_file(self, file_path: str) -> str:
        """Convert file path to proper module path respecting PYTHONPATH."""
        if not file_path:
            return ""

        debug = self.linter.config.import_linter_debug
        target_folders = self.linter.config.import_linter_target_folders or ()

        # Get relative path from workspace root
        rel_path = os.path.relpath(file_path, os.getcwd())

        if debug:
            print(f"Debug: _get_module_path_from_file: file_path={file_path}")
            print(f"Debug: _get_module_path_from_file: rel_path={rel_path}")
            print(f"Debug: _get_module_path_from_file: target_folders={target_folders}")

        # Remove file extension
        if rel_path.endswith(".py"):
            rel_path = rel_path[:-3]

        # FIRST: Check for domains structure patterns to match import-linter expectations
        # Look for patterns like domains/gwpy-document/document/apps/audit/apps.py
        # Should resolve to document.apps.audit.apps to match import-linter output
        domains_pattern = "domains/"
        if debug:
            print(f"Debug: _get_module_path_from_file: checking domains pattern "
                  f"on rel_path={rel_path}")
            print(f"Debug: _get_module_path_from_file: domains_pattern={domains_pattern}")
            print(f"Debug: _get_module_path_from_file: rel_path.startswith(domains_pattern)="
                  f"{rel_path.startswith(domains_pattern)}")
        if rel_path.startswith(domains_pattern):
            # Extract the domain name and path after domains/
            after_domains = rel_path[len(domains_pattern):]
            parts = after_domains.split("/")
            
            if debug:
                print(f"Debug: _get_module_path_from_file: "
                      f"after_domains={after_domains}, parts={parts}")
            
            if len(parts) >= 2:
                # For domains/gwpy-document/document/apps/audit/apps
                # parts = ['gwpy-document', 'document', 'apps', 'audit', 'apps']
                # We want to use everything starting from the second part: document.apps.audit.apps
                domain_module_parts = parts[1:]  # Skip gwpy-document prefix
                result = ".".join(domain_module_parts)
                if debug:
                    print(f"Debug: _get_module_path_from_file: domains pattern result={result}")
                return result
            else:
                if debug:
                    print(f"Debug: _get_module_path_from_file: not enough parts in domains path")
        else:
            if debug:
                print(f"Debug: _get_module_path_from_file: rel_path does not start with domains/")

        # Get PYTHONPATH entries - combine configured entries with environment
        configured_pythonpath = self.linter.config.import_linter_pythonpath or ()
        env_pythonpath = os.environ.get("PYTHONPATH", "").split(":")
        
        # Convert configured relative paths to absolute, then back to relative for consistency
        all_pythonpath_entries = []
        for path_entry in configured_pythonpath:
            if not os.path.isabs(path_entry):
                abs_path = os.path.abspath(path_entry)
                # Convert back to relative from cwd for consistency with env entries
                rel_entry = os.path.relpath(abs_path, os.getcwd())
                all_pythonpath_entries.append(rel_entry)
            else:
                # Convert absolute path to relative from cwd
                rel_entry = os.path.relpath(path_entry, os.getcwd())
                all_pythonpath_entries.append(rel_entry)
        
        # Add environment PYTHONPATH entries (converted to relative paths)
        for path_entry in env_pythonpath:
            if path_entry:  # Skip empty entries
                if os.path.isabs(path_entry):
                    rel_entry = os.path.relpath(path_entry, os.getcwd())
                    all_pythonpath_entries.append(rel_entry)
                else:
                    all_pythonpath_entries.append(path_entry)

        if debug:
            print(f"Debug: _get_module_path_from_file: "
                  f"configured_pythonpath={configured_pythonpath}")
            print(f"Debug: _get_module_path_from_file: "
                  f"all_pythonpath_entries={all_pythonpath_entries}")

        # Try to resolve using PYTHONPATH entries (fallback)
        for pythonpath_entry in all_pythonpath_entries:
            if pythonpath_entry and rel_path.startswith(pythonpath_entry):
                if rel_path.startswith(pythonpath_entry + "/"):
                    # Remove the PYTHONPATH prefix to get module path
                    module_path = rel_path[len(pythonpath_entry) + 1:]
                    result = module_path.replace("/", ".")
                    if debug:
                        print(f"Debug: _get_module_path_from_file: PYTHONPATH result={result} "
                              f"(using entry: {pythonpath_entry})")
                    return result
                elif rel_path == pythonpath_entry:
                    # File is exactly at the PYTHONPATH root
                    if debug:
                        print(f"Debug: _get_module_path_from_file: PYTHONPATH root result='' "
                              f"(using entry: {pythonpath_entry})")
                    return ""

        # Check each target folder to find the module root (fallback)
        for target_folder in target_folders:
            if rel_path.startswith(target_folder + "/"):
                if debug:
                    print(
                        f"Debug: _get_module_path_from_file: "
                        f"checking target_folder={target_folder}"
                    )

                # If no PYTHONPATH match, use target folder logic as fallback
                module_path = rel_path[len(target_folder) + 1 :]
                # Use the last part of target folder as root module
                root_module = target_folder.split("/")[-1]
                result = f"{root_module}.{module_path}" if module_path else root_module
                result = result.replace("/", ".")

                if debug:
                    print(f"Debug: _get_module_path_from_file: target folder result={result}")
                return result
            elif rel_path == target_folder:
                # File is exactly at the target folder root
                root_module = target_folder.split("/")[-1]
                result = root_module

                if debug:
                    print(
                        f"Debug: _get_module_path_from_file: "
                        f"root target folder result={result}"
                    )
                return result

        # Fallback: convert relative path to module path
        result = rel_path.replace("/", ".")
        if debug:
            print(f"Debug: _get_module_path_from_file: fallback result={result}")
        return result

    def _check_individual_imports(self) -> None:
        """Check individual import nodes against contracts for line-specific reporting."""
        if not self._contracts_cache:
            return

        debug = self.linter.config.import_linter_debug
        import_nodes_to_check = self._import_nodes

        # Optimization for single-file mode with fast mode enabled
        if (self._single_file_mode
                and self.linter.config.import_linter_fast_mode
                and self._target_module_name):
            # Filter import nodes to only those from our target file
            import_nodes_to_check = [
                node for node in self._import_nodes
                if (hasattr(node.root(), 'file')
                    and node.root().file in self._analyzed_files)
            ]
            if debug:
                print(f"Debug: Fast mode filtered to {len(import_nodes_to_check)} "
                      f"import nodes from {len(self._import_nodes)} total")

        if debug:
            print(f"Debug: Checking {len(import_nodes_to_check)} import nodes for violations")

        for import_node in import_nodes_to_check:
            # Check if this import violates any contracts
            if self._is_import_violation(import_node):
                if debug:
                    print(f"Debug: Found violation in import node at line {import_node.lineno}")
                # Report violation at the specific import line
                self._report_import_violation(import_node)
            elif debug:
                print(f"Debug: No violation found for import at line {import_node.lineno}")

    def _is_import_violation(self, import_node) -> bool:
        """Check if an import node violates any contracts using the configured contracts."""
        try:
            # Only check if we have contracts loaded
            if not hasattr(self, "_contracts_cache") or not self._contracts_cache:
                return False

            debug = self.linter.config.import_linter_debug

            # Get the module being imported
            imported_module = None
            if hasattr(import_node, "modname") and import_node.modname:
                imported_module = import_node.modname
            elif hasattr(import_node, "names") and import_node.names:
                # For regular imports, get the first imported name
                imported_module = import_node.names[0][0]

            if not imported_module:
                return False

            # Get the current module path
            current_file = import_node.root().file if hasattr(import_node.root(), "file") else ""
            if not current_file:
                return False

            # Convert file path to module path using configuration
            current_module = self._get_module_path_from_file(current_file)

            # Handle relative imports - expand them to full module paths
            if imported_module.startswith('.'):
                # Relative import - resolve based on current module
                if current_module:
                    # Get the package part of current module
                    current_package = '.'.join(current_module.split('.')[:-1])
                    if current_package:
                        # Remove leading dots and append to current package
                        relative_part = imported_module.lstrip('.')
                        if relative_part:
                            imported_module = f"{current_package}.{relative_part}"
                        else:
                            imported_module = current_package
                    else:
                        # Current module is in root, can't resolve relative import
                        return False
            elif hasattr(import_node, "level") and import_node.level and import_node.level > 0:
                # This is a from-import with relative level (from .payments import PaymentService)
                if current_module:
                    current_package = '.'.join(current_module.split('.')[:-1])
                    if current_package:
                        imported_module = f"{current_package}.{imported_module}"
                    else:
                        return False

            if debug:
                print(f"Debug: Checking import {current_module} -> {imported_module}")

            # Check against actual contracts instead of hardcoded values
            # Check if this specific import violates any contracts by examining the violations
            for contract, contract_check in self._contracts_cache.get_contracts_and_checks():
                if not contract_check.kept:
                    if debug:
                        print(f"Debug: Contract '{contract.name}' is broken, checking violations")
                        print(f"Debug: Contract check metadata: {contract_check.metadata}")

                    # Import-linter stores violation details differently than expected
                    # Let's try a different approach - use the metadata or simple matching
                    violation_found = self._check_contract_against_import(
                        contract, contract_check, current_module, imported_module, debug
                    )
                    if violation_found:
                        if debug:
                            print(f"Debug: MATCH! {current_module} -> {imported_module}")
                        return True

            return False

        except (AttributeError, TypeError, ValueError) as e:
            debug = self.linter.config.import_linter_debug
            if debug:
                print(f"Debug: Exception in _is_import_violation: {e}")
            return False

    def _check_contract_against_import(
        self, contract, contract_check, current_module: str, imported_module: str, debug: bool
    ) -> bool:
        """Check if a specific import violates a specific contract."""
        try:
            # For forbidden contracts, check if the import matches source -> forbidden pattern
            if hasattr(contract, "forbidden_modules") and hasattr(contract, "source_modules"):
                # First, check if this specific import matches any violations in metadata
                if hasattr(contract_check, "metadata") and contract_check.metadata:
                    metadata = contract_check.metadata
                    if "invalid_chains" in metadata:
                        for chain_info in metadata["invalid_chains"]:
                            if "chains" in chain_info:
                                for chain in chain_info["chains"]:
                                    for link in chain:
                                        if "importer" in link and "imported" in link:
                                            # Check if this import matches the violation
                                            violation_importer = link["importer"]
                                            violation_imported = link["imported"]
                                            
                                            if debug:
                                                print(f"Debug: Testing violation match:")
                                                print(f"  current_module={current_module}")
                                                print(f"  imported_module={imported_module}")
                                                print(f"  violation_importer={violation_importer}")
                                                print(f"  violation_imported={violation_imported}")
                                            
                                            # Try exact match first
                                            if (current_module == violation_importer
                                                    and imported_module == violation_imported):
                                                if debug:
                                                    print(f"Debug: EXACT MATCH found! "
                                                          f"{current_module} -> {imported_module}")
                                                return True
                                            
                                            # Try partial match - check if current module is suffix
                                            if (violation_importer.endswith(current_module)
                                                    and imported_module == violation_imported):
                                                if debug:
                                                    print(f"Debug: SUFFIX MATCH found! "
                                                          f"{current_module} matches "
                                                          f"{violation_importer} -> "
                                                          f"{imported_module}")
                                                return True
                                            
                                            # Try prefix match - check if current module is prefix
                                            if (current_module.endswith(violation_importer)
                                                    and imported_module == violation_imported):
                                                if debug:
                                                    print(f"Debug: PREFIX MATCH found! "
                                                          f"{current_module} matches "
                                                          f"{violation_importer} -> "
                                                          f"{imported_module}")
                                                return True
                                            
                                            # Check if imported module starts with violation_imported
                                            # (e.g., billing_domain.apps.billing.models
                                            # starts with billing_domain)
                                            if (violation_importer.endswith(current_module)
                                                    and imported_module.startswith(
                                                        violation_imported + ".")):
                                                if debug:
                                                    print(
                                                        "Debug: IMPORTED MODULE PREFIX MATCH found! "
                                                        f"{current_module} matches "
                                                        f"{violation_importer} -> "
                                                        f"{imported_module} starts with "
                                                        f"{violation_imported}")
                                                return True

                                            # Alternative: Check if the current_module contains
                                            # the violation_importer as a suffix/imported matches
                                            if (violation_importer in current_module
                                                    and imported_module.startswith(
                                                        violation_imported)):
                                                if debug:
                                                    print(f"Debug: CONTAINS MATCH found! "
                                                          f"{current_module} contains "
                                                          f"{violation_importer} -> "
                                                          f"{imported_module} starts with "
                                                          f"{violation_imported}")
                                                return True
                                            
                                            # More flexible matching: check if violation_importer
                                            # ends with current_module and imported module matches
                                            if (violation_importer.endswith(f".{current_module}")
                                                    and imported_module.startswith(
                                                        violation_imported)):
                                                if debug:
                                                    print(f"Debug: FLEXIBLE SUFFIX MATCH found! "
                                                          f"{violation_importer} ends with "
                                                          f".{current_module} -> "
                                                          f"{imported_module} starts with "
                                                          f"{violation_imported}")
                                                return True

                # Fallback to pattern matching if no direct violation match
                source_match = any(
                    self._module_matches_pattern(current_module, source_pattern)
                    for source_pattern in contract.source_modules
                )

                # Check if imported module matches any forbidden module pattern
                forbidden_match = any(
                    self._module_matches_pattern(imported_module, forbidden_pattern)
                    for forbidden_pattern in contract.forbidden_modules
                )

                if debug:
                    print(
                        f"Debug: Forbidden contract check - source_match: {source_match}, "
                        f"forbidden_match: {forbidden_match}"
                    )

                return source_match and forbidden_match

            # For independence contracts, check if modules are supposed to be independent
            if hasattr(contract, "modules"):
                # Check if both modules are in the independence group
                current_in_group = any(
                    self._module_matches_pattern(current_module, module_pattern)
                    for module_pattern in contract.modules
                )
                imported_in_group = any(
                    self._module_matches_pattern(imported_module, module_pattern)
                    for module_pattern in contract.modules
                )

                if debug:
                    print(
                        f"Debug: Independence contract check - "
                        f"current_in_group: {current_in_group}, "
                        f"imported_in_group: {imported_in_group}"
                    )

                # Independence violation if both are in the group but different modules
                return (
                    current_in_group
                    and imported_in_group
                    and not self._modules_are_same_domain(current_module, imported_module)
                )

            # For whitelist contracts, check if the import is not in the allowed modules
            if hasattr(contract, "source_modules") and hasattr(contract, "allowed_modules"):
                # Check if the current module matches any source module pattern
                source_match = any(
                    self._module_matches_pattern(current_module, source_pattern)
                    for source_pattern in contract.source_modules
                )

                if source_match:
                    # Only flag imports that are explicitly violations detected by import-linter
                    if hasattr(contract_check, "metadata") and contract_check.metadata:
                        metadata = contract_check.metadata
                        if "invalid_chains" in metadata:
                            for chain_info in metadata["invalid_chains"]:
                                if "chains" in chain_info:
                                    for chain in chain_info["chains"]:
                                        for link in chain:
                                            if "importer" in link and "imported" in link:
                                                violation_importer = link["importer"]
                                                violation_imported = link["imported"]
                                                
                                                if debug:
                                                    print("Debug: Testing violation match:")
                                                    print(f"  current_module={current_module}")
                                                    print(f"  imported_module={imported_module}")
                                                    print(f"  violation_importer="
                                                          f"{violation_importer}")
                                                    print(f"  violation_imported="
                                                          f"{violation_imported}")
                                                
                                                # Check if this is the exact violation
                                                if (violation_importer == current_module
                                                        and imported_module.startswith(
                                                            violation_imported)):
                                                    if debug:
                                                        print("Debug: EXACT VIOLATION MATCH found!")
                                                    return True

                    # For whitelist contracts, only flag explicit violations
                    # This allows framework imports like Django that aren't in allowed_modules
                    # but aren't actual violations detected by import-linter
                    return False

            return False

        except (AttributeError, TypeError) as e:
            if debug:
                print(f"Debug: Exception in _check_contract_against_import: {e}")
            return False

    def _module_matches_pattern(self, module: str, pattern) -> bool:
        """Check if a module matches a pattern (with wildcard support)."""
        # Convert pattern to string if it's a ModuleExpression or other object
        pattern_str = str(pattern)

        # Handle wildcard patterns
        if "**" in pattern_str:
            # Recursive wildcard - replace ** with .* for regex
            regex_pattern = pattern_str.replace("**", ".*")
            import re

            return bool(re.match(f"^{regex_pattern}$", module))
        elif "*" in pattern_str:
            # Single wildcard - replace * with [^.]* (match anything except dots)
            regex_pattern = pattern_str.replace("*", "[^.]*")
            import re

            return bool(re.match(f"^{regex_pattern}$", module))
        else:
            # Exact match or prefix match
            return module == pattern_str or module.startswith(pattern_str + ".")

    def _modules_are_same_domain(self, module1: str, module2: str) -> bool:
        """Check if two modules are in the same domain (for independence contracts)."""

        # Extract domain parts (e.g., domains.document.* -> domains.document)
        def get_domain(module):
            parts = module.split(".")
            if len(parts) >= 2:
                return ".".join(parts[:2])  # e.g., domains.document
            return module

        return get_domain(module1) == get_domain(module2)

    def _import_matches_violation(
        self, current_module: str, imported_module: str, violation
    ) -> bool:
        """Check if a specific import matches a contract violation."""
        try:
            # Different contract types store violation information differently
            # We need to check if the violation involves our current import

            # For forbidden contracts, check if the import matches the violation details
            if hasattr(violation, "importer") and hasattr(violation, "imported"):
                return (
                    current_module == violation.importer and imported_module == violation.imported
                )

            # For other violation types, check various possible attributes
            if hasattr(violation, "detail"):
                detail = str(violation.detail)
                return current_module in detail and imported_module in detail

            # Fallback: check string representation
            violation_str = str(violation)
            return current_module in violation_str and imported_module in violation_str

        except (AttributeError, TypeError):
            return False

    def _report_import_violation(self, import_node) -> None:
        """Report a violation for a specific import node using contract-based logic."""
        try:
            # Only report if we have contracts loaded
            if not hasattr(self, "_contracts_cache") or not self._contracts_cache:
                return

            # Get the module being imported - use the same logic as _is_import_violation
            imported_module = None
            if hasattr(import_node, "modname") and import_node.modname:
                imported_module = import_node.modname
            elif hasattr(import_node, "names") and import_node.names:
                imported_module = import_node.names[0][0]

            if not imported_module:
                return

            # Get the current module path
            current_file = import_node.root().file if hasattr(import_node.root(), "file") else ""
            current_module = self._get_module_path_from_file(current_file)

            # Handle relative imports - expand them to full module paths
            if imported_module.startswith('.'):
                # Relative import - resolve based on current module
                if current_module:
                    # Get the package part of current module
                    current_package = '.'.join(current_module.split('.')[:-1])
                    if current_package:
                        # Remove leading dots and append to current package
                        relative_part = imported_module.lstrip('.')
                        if relative_part:
                            imported_module = f"{current_package}.{relative_part}"
                        else:
                            imported_module = current_package
                    else:
                        # Current module is in root, can't resolve relative import
                        return
            elif hasattr(import_node, "level") and import_node.level and import_node.level > 0:
                # This is a from-import with relative level (from .payments import PaymentService)
                if current_module:
                    current_package = '.'.join(current_module.split('.')[:-1])
                    if current_package:
                        imported_module = f"{current_package}.{imported_module}"
                    else:
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
                    # Use our custom contract matching logic
                    if self._check_contract_against_import(
                        contract, contract_check, current_module, imported_module, debug
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

    # We need at least one visit method for the checker to be active
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


def register(linter: PyLinter) -> None:
    """Register the plugin with pylint."""
    linter.register_checker(ImportLinterChecker(linter))
