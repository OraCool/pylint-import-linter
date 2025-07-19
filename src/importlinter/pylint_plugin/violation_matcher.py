"""Contract violation detection and matching utilities."""

from typing import Dict, Any


class ViolationMatcher:
    """Handles matching imports against contract violations."""

    def __init__(self, debug: bool = False):
        """Initialize the matcher."""
        self.debug = debug

    def matches_violation_link(
        self, link: Dict[str, Any], current_module: str, imported_module: str
    ) -> bool:
        """Check if an import matches a specific violation link."""
        violation_importer = link["importer"]
        violation_imported = link["imported"]

        if self.debug:
            print("Debug: Testing violation match:")
            print(f"  current_module={current_module}")
            print(f"  imported_module={imported_module}")
            print(f"  violation_importer={violation_importer}")
            print(f"  violation_imported={violation_imported}")

        # Try multiple matching strategies
        return (
            self._exact_match(
                current_module, imported_module, violation_importer, violation_imported
            )
            or self._suffix_match(
                current_module, imported_module, violation_importer, violation_imported
            )
            or self._prefix_match(
                current_module, imported_module, violation_importer, violation_imported
            )
            or self._module_prefix_match(
                current_module, imported_module, violation_importer, violation_imported
            )
            or self._contains_match(
                current_module, imported_module, violation_importer, violation_imported
            )
            or self._flexible_suffix_match(
                current_module, imported_module, violation_importer, violation_imported
            )
        )

    def _exact_match(
        self,
        current_module: str,
        imported_module: str,
        violation_importer: str,
        violation_imported: str,
    ) -> bool:
        """Check exact match between modules."""
        if current_module == violation_importer and imported_module == violation_imported:
            if self.debug:
                print(f"Debug: EXACT MATCH found! {current_module} -> {imported_module}")
            return True
        return False

    def _suffix_match(
        self,
        current_module: str,
        imported_module: str,
        violation_importer: str,
        violation_imported: str,
    ) -> bool:
        """Check if current module is suffix of violation importer."""
        if violation_importer.endswith(current_module) and imported_module == violation_imported:
            if self.debug:
                print(
                    f"Debug: SUFFIX MATCH found! {current_module} "
                    f"matches {violation_importer} -> {imported_module}"
                )
            return True
        return False

    def _prefix_match(
        self,
        current_module: str,
        imported_module: str,
        violation_importer: str,
        violation_imported: str,
    ) -> bool:
        """Check if current module is prefix of violation importer."""
        if current_module.endswith(violation_importer) and imported_module == violation_imported:
            if self.debug:
                print(
                    f"Debug: PREFIX MATCH found! {current_module} "
                    f"matches {violation_importer} -> {imported_module}"
                )
            return True
        return False

    def _module_prefix_match(
        self,
        current_module: str,
        imported_module: str,
        violation_importer: str,
        violation_imported: str,
    ) -> bool:
        """Check if imported module starts with violation imported."""
        if violation_importer.endswith(current_module) and imported_module.startswith(
            violation_imported + "."
        ):
            if self.debug:
                print(
                    f"Debug: IMPORTED MODULE PREFIX MATCH found! "
                    f"{current_module} matches {violation_importer} -> "
                    f"{imported_module} starts with {violation_imported}"
                )
            return True
        return False

    def _contains_match(
        self,
        current_module: str,
        imported_module: str,
        violation_importer: str,
        violation_imported: str,
    ) -> bool:
        """Check if current module contains violation importer."""
        if violation_importer in current_module and imported_module.startswith(violation_imported):
            if self.debug:
                print(
                    f"Debug: CONTAINS MATCH found! {current_module} "
                    f"contains {violation_importer} -> {imported_module} "
                    f"starts with {violation_imported}"
                )
            return True
        return False

    def _flexible_suffix_match(
        self,
        current_module: str,
        imported_module: str,
        violation_importer: str,
        violation_imported: str,
    ) -> bool:
        """Check flexible suffix match with dot separator."""
        if violation_importer.endswith(f".{current_module}") and imported_module.startswith(
            violation_imported
        ):
            if self.debug:
                print(
                    f"Debug: FLEXIBLE SUFFIX MATCH found! {violation_importer} ends with "
                    f".{current_module} -> {imported_module} starts with {violation_imported}"
                )
            return True
        return False

    def module_matches_pattern(self, module: str, pattern) -> bool:
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

    def modules_are_same_domain(self, module1: str, module2: str) -> bool:
        """Check if two modules are in the same domain (for independence contracts)."""

        # Extract domain parts (e.g., domains.document.* -> domains.document)
        def get_domain(module):
            parts = module.split(".")
            if len(parts) >= 2:
                return ".".join(parts[:2])  # e.g., domains.document
            return module

        return get_domain(module1) == get_domain(module2)
