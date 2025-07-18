"""Module path resolution utilities for import-linter pylint plugin."""

import os
from typing import Optional


class ModulePathResolver:
    """Resolves file paths to proper module paths respecting PYTHONPATH and project structure."""
    
    def __init__(self, config=None, debug: bool = False):
        """Initialize the resolver with configuration."""
        self.config = config
        self.debug = debug
    
    def get_module_path_from_file(self, file_path: str) -> str:
        """Convert file path to proper module path respecting PYTHONPATH."""
        if not file_path:
            return ""

        target_folders = getattr(self.config, "import_linter_target_folders", ()) or ()

        # Get relative path from workspace root
        rel_path = os.path.relpath(file_path, os.getcwd())

        if self.debug:
            print(f"Debug: _get_module_path_from_file: file_path={file_path}")
            print(f"Debug: _get_module_path_from_file: rel_path={rel_path}")
            print(f"Debug: _get_module_path_from_file: target_folders={target_folders}")

        # Remove file extension
        if rel_path.endswith(".py"):
            rel_path = rel_path[:-3]

        # Try different resolution strategies in order of priority
        strategies = [
            self._try_domains_pattern,
            self._try_pythonpath_resolution,
            self._try_target_folder_resolution,
            self._fallback_resolution
        ]

        for strategy in strategies:
            result = strategy(rel_path, target_folders)
            if result is not None:
                return result

        # Final fallback
        return rel_path.replace("/", ".")

    def _try_domains_pattern(self, rel_path: str, target_folders) -> Optional[str]:
        """Try to resolve using domains pattern structure."""
        domains_pattern = "domains/"

        if self.debug:
            print(f"Debug: checking domains pattern on rel_path={rel_path}")
            print(f"Debug: domains_pattern={domains_pattern}")
            print(f"Debug: rel_path.startswith(domains_pattern)={rel_path.startswith(domains_pattern)}")

        if not rel_path.startswith(domains_pattern):
            if self.debug:
                print("Debug: rel_path does not start with domains/")
            return None

        # Extract the domain name and path after domains/
        after_domains = rel_path[len(domains_pattern):]
        parts = after_domains.split("/")

        if self.debug:
            print(f"Debug: after_domains={after_domains}, parts={parts}")

        if len(parts) >= 2:
            # For domains/gwpy-document/document/apps/audit/apps
            # parts = ['gwpy-document', 'document', 'apps', 'audit', 'apps']
            # We want to use everything starting from the second part: document.apps.audit.apps
            domain_module_parts = parts[1:]  # Skip gwpy-document prefix
            result = ".".join(domain_module_parts)
            if self.debug:
                print(f"Debug: domains pattern result={result}")
            return result
        else:
            if self.debug:
                print("Debug: not enough parts in domains path")
            return None

    def _try_pythonpath_resolution(self, rel_path: str, target_folders) -> Optional[str]:
        """Try to resolve using PYTHONPATH entries."""
        pythonpath_entries = self._get_all_pythonpath_entries()

        for pythonpath_entry in pythonpath_entries:
            result = self._resolve_with_pythonpath_entry(rel_path, pythonpath_entry)
            if result is not None:
                return result

        return None

    def _get_all_pythonpath_entries(self) -> list[str]:
        """Get all PYTHONPATH entries as relative paths."""
        configured_pythonpath = getattr(self.config, "import_linter_pythonpath", ()) or ()
        env_pythonpath = os.environ.get("PYTHONPATH", "").split(":")

        all_pythonpath_entries = []

        # Add configured entries
        for path_entry in configured_pythonpath:
            rel_entry = self._convert_to_relative_path(path_entry)
            all_pythonpath_entries.append(rel_entry)

        # Add environment entries
        for path_entry in env_pythonpath:
            if path_entry:  # Skip empty entries
                rel_entry = self._convert_to_relative_path(path_entry)
                all_pythonpath_entries.append(rel_entry)

        if self.debug:
            print(f"Debug: configured_pythonpath={configured_pythonpath}")
            print(f"Debug: all_pythonpath_entries={all_pythonpath_entries}")

        return all_pythonpath_entries

    def _convert_to_relative_path(self, path_entry: str) -> str:
        """Convert a path entry to relative path from current working directory."""
        if os.path.isabs(path_entry):
            return os.path.relpath(path_entry, os.getcwd())

        # For relative paths, convert to absolute then back to relative for consistency
        abs_path = os.path.abspath(path_entry)
        return os.path.relpath(abs_path, os.getcwd())

    def _resolve_with_pythonpath_entry(self, rel_path: str, pythonpath_entry: str) -> Optional[str]:
        """Try to resolve module path using a specific PYTHONPATH entry."""
        if not pythonpath_entry or not rel_path.startswith(pythonpath_entry):
            return None

        if rel_path.startswith(pythonpath_entry + "/"):
            # Remove the PYTHONPATH prefix to get module path
            module_path = rel_path[len(pythonpath_entry) + 1:]
            result = module_path.replace("/", ".")
            if self.debug:
                print(f"Debug: PYTHONPATH result={result} (using entry: {pythonpath_entry})")
            return result
        elif rel_path == pythonpath_entry:
            # File is exactly at the PYTHONPATH root
            if self.debug:
                print(f"Debug: PYTHONPATH root result='' (using entry: {pythonpath_entry})")
            return ""

        return None

    def _try_target_folder_resolution(self, rel_path: str, target_folders) -> Optional[str]:
        """Try to resolve using target folders."""
        for target_folder in target_folders:
            result = self._resolve_with_target_folder(rel_path, target_folder)
            if result is not None:
                return result
        return None

    def _resolve_with_target_folder(self, rel_path: str, target_folder: str) -> Optional[str]:
        """Try to resolve module path using a specific target folder."""
        if rel_path.startswith(target_folder + "/"):
            if self.debug:
                print(f"Debug: checking target_folder={target_folder}")

            # If no PYTHONPATH match, use target folder logic as fallback
            module_path = rel_path[len(target_folder) + 1:]
            # Use the last part of target folder as root module
            root_module = target_folder.split("/")[-1]
            result = f"{root_module}.{module_path}" if module_path else root_module
            result = result.replace("/", ".")

            if self.debug:
                print(f"Debug: target folder result={result}")
            return result
        elif rel_path == target_folder:
            # File is exactly at the target folder root
            root_module = target_folder.split("/")[-1]
            if self.debug:
                print(f"Debug: root target folder result={root_module}")
            return root_module

        return None

    def _fallback_resolution(self, rel_path: str, target_folders) -> str:
        """Fallback resolution strategy."""
        result = rel_path.replace("/", ".")
        if self.debug:
            print(f"Debug: fallback result={result}")
        return result
