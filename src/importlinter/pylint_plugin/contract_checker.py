"""Contract checking and violation detection logic."""

from typing import Any, Union, Optional
from importlinter.application.sentinels import NotSupplied
from importlinter.application.constants import (
    IMPORT_CONTRACT_ERROR,
    format_violation_message,
    get_message_id_for_contract_type,
)
from .violation_matcher import ViolationMatcher


class ContractChecker:
    """Handles contract checking and violation reporting."""
    
    def __init__(self, linter_config, module_resolver, debug: bool = False):
        """Initialize the contract checker."""
        self.config = linter_config
        self.module_resolver = module_resolver
        self.debug = debug
        self.violation_matcher = ViolationMatcher(debug=debug)
    
    def check_import_contracts(self, first_module_node, single_file_mode: bool, 
                             target_module_name: Optional[str]):
        """Run import-linter contract checking."""
        debug = self.debug
        try:
            # Get configuration options
            config_filename = self.config.import_linter_config
            limit_to_contracts = tuple(self.config.import_linter_contract or ())
            cache_dir = self._get_cache_dir()
            verbose = self.config.import_linter_verbose
            show_timings = self.config.import_linter_show_timings

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

            # Create detailed report with optimizations for single-file mode
            if (single_file_mode and self.config.import_linter_fast_mode and target_module_name):
                if verbose:
                    print(f"Import-linter: Fast mode enabled for {target_module_name}")

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

            return report if report.contains_failures else None

        except (ImportError, FileNotFoundError, ValueError) as e:
            return self._handle_contract_error(e, first_module_node, debug)
        except Exception as e:  # pylint: disable=broad-except
            return self._handle_unexpected_error(e, first_module_node, debug)

    def _handle_contract_error(self, error, first_module_node, debug: bool):
        """Handle errors in contract checking."""
        error_msg = str(error)
        if debug:
            import traceback
            error_msg += f"\nDebug traceback:\n{traceback.format_exc()}"
        
        # This would need to be handled by the calling checker
        # For now, return error info
        return {"error": IMPORT_CONTRACT_ERROR, "args": (error_msg,), "node": first_module_node}

    def _handle_unexpected_error(self, error, first_module_node, debug: bool):
        """Handle unexpected errors during contract checking."""
        error_str = str(error)
        exception_name = type(error).__name__

        if ("NotATopLevelModule" in error_str
                or exception_name == "NotATopLevelModule"
                or "grimp.exceptions.NotATopLevelModule" in error_str):
            if self.config.import_linter_verbose or debug:
                print(
                    "Import-linter: Skipping analysis due to package structure issues. "
                    "This may be caused by hyphenated directory names or "
                    "non-standard package layouts."
                )
            # Don't report this as an error since it's likely a project structure issue
            return None

        error_msg = f"Unexpected error: {str(error)}"
        if debug:
            import traceback
            error_msg += f"\nDebug traceback:\n{traceback.format_exc()}"

        return {"error": IMPORT_CONTRACT_ERROR, "args": (error_msg,), "node": first_module_node}

    def _get_cache_dir(self) -> Union[str, None, type[NotSupplied]]:
        """Get the cache directory setting."""
        if self.config.import_linter_no_cache:
            return None
        if self.config.import_linter_cache_dir:
            return self.config.import_linter_cache_dir
        return NotSupplied

    def is_import_violation(self, import_node, contracts_cache) -> bool:
        """Check if an import node violates any contracts using the configured contracts."""
        try:
            if not contracts_cache:
                return False

            # Get the module being imported
            imported_module = self._extract_imported_module(import_node)
            if not imported_module:
                return False

            # Get the current module path
            current_file = import_node.root().file if hasattr(import_node.root(), "file") else ""
            if not current_file:
                return False

            current_module = self.module_resolver.get_module_path_from_file(current_file)

            # Handle relative imports
            imported_module = self._resolve_relative_import(
                imported_module, import_node, current_module
            )
            if not imported_module:
                return False

            if self.debug:
                print(f"Debug: Checking import {current_module} -> {imported_module}")

            # Check against contracts
            for contract, contract_check in contracts_cache.get_contracts_and_checks():
                if not contract_check.kept:
                    if self.debug:
                        print(f"Debug: Contract '{contract.name}' is broken, checking violations")
                        print(f"Debug: Contract check metadata: {contract_check.metadata}")

                    if self._check_contract_against_import(
                        contract, contract_check, current_module, imported_module
                    ):
                        if self.debug:
                            print(f"Debug: MATCH! {current_module} -> {imported_module}")
                        return True

            return False

        except (AttributeError, TypeError, ValueError) as e:
            if self.debug:
                print(f"Debug: Exception in is_import_violation: {e}")
            return False

    def _extract_imported_module(self, import_node) -> Optional[str]:
        """Extract the module name being imported from an import node."""
        if hasattr(import_node, "modname") and import_node.modname:
            return import_node.modname
        elif hasattr(import_node, "names") and import_node.names:
            return import_node.names[0][0]
        return None

    def _resolve_relative_import(self, imported_module: str, import_node, 
                               current_module: str) -> Optional[str]:
        """Resolve relative imports to absolute module paths."""
        if imported_module.startswith('.'):
            # Relative import - resolve based on current module
            if current_module:
                current_package = '.'.join(current_module.split('.')[:-1])
                if current_package:
                    relative_part = imported_module.lstrip('.')
                    if relative_part:
                        return f"{current_package}.{relative_part}"
                    else:
                        return current_package
                else:
                    return None
        elif hasattr(import_node, "level") and import_node.level and import_node.level > 0:
            # This is a from-import with relative level
            if current_module:
                current_package = '.'.join(current_module.split('.')[:-1])
                if current_package:
                    return f"{current_package}.{imported_module}"
                else:
                    return None
        
        return imported_module

    def _check_contract_against_import(self, contract, contract_check, 
                                     current_module: str, imported_module: str) -> bool:
        """Check if a specific import violates a specific contract."""
        try:
            if self._is_forbidden_contract(contract):
                return self._check_forbidden_contract(
                    contract, contract_check, current_module, imported_module
                )
            elif self._is_independence_contract(contract):
                return self._check_independence_contract(
                    contract, current_module, imported_module
                )
            elif self._is_whitelist_contract(contract):
                return self._check_whitelist_contract(
                    contract, contract_check, current_module, imported_module
                )
            return False

        except (AttributeError, TypeError) as e:
            if self.debug:
                print(f"Debug: Exception in _check_contract_against_import: {e}")
            return False

    def _is_forbidden_contract(self, contract) -> bool:
        """Check if contract is a forbidden contract."""
        return hasattr(contract, "forbidden_modules") and hasattr(contract, "source_modules")

    def _is_independence_contract(self, contract) -> bool:
        """Check if contract is an independence contract."""
        return hasattr(contract, "modules")

    def _is_whitelist_contract(self, contract) -> bool:
        """Check if contract is a whitelist contract."""
        return hasattr(contract, "source_modules") and hasattr(contract, "allowed_modules")

    def _check_forbidden_contract(self, contract, contract_check, 
                                current_module: str, imported_module: str) -> bool:
        """Check forbidden contract violations."""
        # First, check if this specific import matches any violations in metadata
        if self._check_metadata_violations(contract_check, current_module, imported_module):
            return True

        # Fallback to pattern matching if no direct violation match
        return self._check_forbidden_pattern_match(contract, current_module, imported_module)

    def _check_independence_contract(self, contract, current_module: str, 
                                   imported_module: str) -> bool:
        """Check independence contract violations."""
        current_in_group = any(
            self.violation_matcher.module_matches_pattern(current_module, module_pattern)
            for module_pattern in contract.modules
        )
        imported_in_group = any(
            self.violation_matcher.module_matches_pattern(imported_module, module_pattern)
            for module_pattern in contract.modules
        )

        if self.debug:
            print(f"Debug: Independence contract check - "
                  f"current_in_group: {current_in_group}, "
                  f"imported_in_group: {imported_in_group}")

        return (
            current_in_group
            and imported_in_group
            and not self.violation_matcher.modules_are_same_domain(current_module, imported_module)
        )

    def _check_whitelist_contract(self, contract, contract_check, 
                                current_module: str, imported_module: str) -> bool:
        """Check whitelist contract violations."""
        source_match = any(
            self.violation_matcher.module_matches_pattern(current_module, source_pattern)
            for source_pattern in contract.source_modules
        )

        if not source_match:
            return False

        # Only flag imports that are explicitly violations detected by import-linter
        return self._check_explicit_violations(contract_check, current_module, imported_module)

    def _check_metadata_violations(self, contract_check, current_module: str, 
                                 imported_module: str) -> bool:
        """Check if import matches any violations in contract metadata."""
        if not (hasattr(contract_check, "metadata") and contract_check.metadata):
            return False

        metadata = contract_check.metadata
        if "invalid_chains" not in metadata:
            return False

        for chain_info in metadata["invalid_chains"]:
            if "chains" in chain_info:
                for chain in chain_info["chains"]:
                    for link in chain:
                        if "importer" in link and "imported" in link:
                            if self.violation_matcher.matches_violation_link(
                                link, current_module, imported_module
                            ):
                                return True
        return False

    def _check_forbidden_pattern_match(self, contract, current_module: str, 
                                     imported_module: str) -> bool:
        """Check forbidden contract using pattern matching."""
        source_match = any(
            self.violation_matcher.module_matches_pattern(current_module, source_pattern)
            for source_pattern in contract.source_modules
        )

        forbidden_match = any(
            self.violation_matcher.module_matches_pattern(imported_module, forbidden_pattern)
            for forbidden_pattern in contract.forbidden_modules
        )

        if self.debug:
            print(f"Debug: Forbidden contract check - source_match: {source_match}, "
                  f"forbidden_match: {forbidden_match}")

        return source_match and forbidden_match

    def _check_explicit_violations(self, contract_check, current_module: str, 
                                 imported_module: str) -> bool:
        """Check only explicit violations for whitelist contracts."""
        if not (hasattr(contract_check, "metadata") and contract_check.metadata):
            return False

        metadata = contract_check.metadata
        if "invalid_chains" not in metadata:
            return False

        for chain_info in metadata["invalid_chains"]:
            if "chains" in chain_info:
                for chain in chain_info["chains"]:
                    for link in chain:
                        if "importer" in link and "imported" in link:
                            violation_importer = link["importer"]
                            violation_imported = link["imported"]

                            if self.debug:
                                print("Debug: Testing violation match:")
                                print(f"  current_module={current_module}")
                                print(f"  imported_module={imported_module}")
                                print(f"  violation_importer={violation_importer}")
                                print(f"  violation_imported={violation_imported}")

                            # Check if this is the exact violation
                            if (violation_importer == current_module
                                    and imported_module.startswith(violation_imported)):
                                if self.debug:
                                    print("Debug: EXACT VIOLATION MATCH found!")
                                return True

        # For whitelist contracts, only flag explicit violations
        return False
