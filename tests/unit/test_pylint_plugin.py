"""
Unit tests for the pylint plugin.

These tests ensure that the pylint plugin correctly integrates with import-linter
and properly detects contract violations at the line level.
"""

from unittest.mock import Mock, patch
import pytest

from importlinter.pylint_plugin import ImportLinterChecker, register
from importlinter.application.constants import IMPORT_BOUNDARY_VIOLATION


class TestImportLinterChecker:
    """Test the ImportLinterChecker class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_linter = Mock()
        self.mock_linter.config = Mock()
        self.mock_linter.config.import_linter_config = None
        self.mock_linter.config.import_linter_contract = ()
        self.mock_linter.config.import_linter_target_folders = ()
        self.mock_linter.config.import_linter_exclude_folders = ()
        self.mock_linter.config.import_linter_cache_dir = None
        self.mock_linter.config.import_linter_no_cache = False
        self.mock_linter.config.import_linter_verbose = False
        self.mock_linter.config.import_linter_show_timings = False
        self.mock_linter.config.import_linter_debug = False

        self.checker = ImportLinterChecker(self.mock_linter)

    def test_checker_initialization(self):
        """Test that the checker initializes correctly."""
        assert self.checker.name == "import-linter"
        assert self.checker._contracts_checked is False
        assert self.checker._first_module_node is None
        assert self.checker._analyzed_files == set()
        assert self.checker._module_nodes == {}
        assert self.checker._import_nodes == []
        assert self.checker._contracts_cache is None

    def test_register_function(self):
        """Test that the register function works correctly."""
        mock_linter = Mock()
        register(mock_linter)
        mock_linter.register_checker.assert_called_once()
        args = mock_linter.register_checker.call_args[0]
        assert isinstance(args[0], ImportLinterChecker)

    def test_open_adds_current_directory_to_path(self):
        """Test that open() adds current directory to sys.path."""
        with (
            patch("importlinter.pylint_plugin.os.getcwd") as mock_getcwd,
            patch("importlinter.pylint_plugin.sys.path") as mock_path,
        ):
            mock_getcwd.return_value = "/test/path"
            mock_path.__contains__ = Mock(return_value=False)
            mock_path.insert = Mock()

            self.checker.open()

            mock_path.insert.assert_called_once_with(0, "/test/path")

    def test_visit_module_tracks_files(self):
        """Test that visit_module correctly tracks analyzed files."""
        mock_node = Mock()
        mock_node.file = "/path/to/test.py"

        self.checker.visit_module(mock_node)

        assert "/path/to/test.py" in self.checker._analyzed_files
        assert self.checker._module_nodes["/path/to/test.py"] == mock_node
        assert self.checker._first_module_node == mock_node

    def test_visit_import_tracks_imports(self):
        """Test that visit_import tracks import nodes."""
        mock_node = Mock()

        self.checker.visit_import(mock_node)

        assert mock_node in self.checker._import_nodes

    def test_visit_importfrom_tracks_imports(self):
        """Test that visit_importfrom tracks import nodes."""
        mock_node = Mock()

        self.checker.visit_importfrom(mock_node)

        assert mock_node in self.checker._import_nodes


class TestModulePathResolution:
    """Test the critical _get_module_path_from_file method that was fixed."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_linter = Mock()
        self.mock_linter.config = Mock()
        self.mock_linter.config.import_linter_debug = False
        self.checker = ImportLinterChecker(self.mock_linter)

    def test_get_module_path_with_target_folders(self):
        """Test module path resolution with target folders - the key bug fix."""
        self.mock_linter.config.import_linter_target_folders = ("example/domains",)

        # Test the critical case that was broken before the fix
        with patch("importlinter.pylint_plugin.os.path.relpath") as mock_relpath:
            mock_relpath.return_value = "example/domains/billing/payments.py"

            file_path = "/abs/path/example/domains/billing/payments.py"
            result = self.checker._get_module_path_from_file(file_path)

            assert result == "domains.billing.payments"

    def test_get_module_path_with_nested_structure(self):
        """Test module path resolution with nested directory structure."""
        self.mock_linter.config.import_linter_target_folders = ("src/myproject",)

        with patch("importlinter.pylint_plugin.os.path.relpath") as mock_relpath:
            mock_relpath.return_value = "src/myproject/domain/user/service.py"

            file_path = "/abs/path/src/myproject/domain/user/service.py"
            result = self.checker._get_module_path_from_file(file_path)

            assert result == "myproject.domain.user.service"

    def test_get_module_path_fallback_without_target_folders(self):
        """Test fallback behavior when no target folders are configured."""
        self.mock_linter.config.import_linter_target_folders = ()

        with patch("importlinter.pylint_plugin.os.path.relpath") as mock_relpath:
            mock_relpath.return_value = "src/mymodule/test.py"

            result = self.checker._get_module_path_from_file("/abs/path/src/mymodule/test.py")

            assert result == "src.mymodule.test"

    def test_get_module_path_empty_file_path(self):
        """Test behavior with empty file path."""
        result = self.checker._get_module_path_from_file("")
        assert result == ""

    def test_get_module_path_root_module_file(self):
        """Test behavior when file is at the root of target folder."""
        self.mock_linter.config.import_linter_target_folders = ("example/domains",)

        with patch("importlinter.pylint_plugin.os.path.relpath") as mock_relpath:
            mock_relpath.return_value = "example/domains"

            result = self.checker._get_module_path_from_file("/abs/path/example/domains")

            assert result == "domains"


class TestContractFolderLogic:
    """Test the _should_check_contracts method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_linter = Mock()
        self.mock_linter.config = Mock()
        self.checker = ImportLinterChecker(self.mock_linter)

    def test_should_check_contracts_with_target_folders(self):
        """Test contract checking with target folders."""
        self.mock_linter.config.import_linter_target_folders = ("src/",)
        self.mock_linter.config.import_linter_exclude_folders = ()

        with patch("importlinter.pylint_plugin.os.path.relpath") as mock_relpath:
            mock_relpath.return_value = "src/test.py"
            self.checker._analyzed_files.add("/abs/path/src/test.py")

            result = self.checker._should_check_contracts()

            assert result is True

    def test_should_check_contracts_with_excluded_folders(self):
        """Test contract checking with excluded folders."""
        self.mock_linter.config.import_linter_target_folders = ()
        self.mock_linter.config.import_linter_exclude_folders = ("tests/",)

        with patch("importlinter.pylint_plugin.os.path.relpath") as mock_relpath:
            mock_relpath.return_value = "tests/test.py"
            self.checker._analyzed_files.add("/abs/path/tests/test.py")

            result = self.checker._should_check_contracts()

            assert result is False

    def test_should_check_contracts_no_configuration(self):
        """Test contract checking with no folder configuration."""
        self.mock_linter.config.import_linter_target_folders = ()
        self.mock_linter.config.import_linter_exclude_folders = ()

        self.checker._analyzed_files.add("/abs/path/src/test.py")

        result = self.checker._should_check_contracts()

        assert result is True

    def test_should_check_contracts_no_files(self):
        """Test contract checking with no analyzed files."""
        self.mock_linter.config.import_linter_target_folders = ()
        self.mock_linter.config.import_linter_exclude_folders = ()

        result = self.checker._should_check_contracts()

        assert result is False


class TestPatternMatching:
    """Test the _module_matches_pattern method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_linter = Mock()
        self.checker = ImportLinterChecker(self.mock_linter)

    def test_exact_pattern_match(self):
        """Test exact pattern matching."""
        result1 = self.checker._module_matches_pattern("domains.billing", "domains.billing")
        assert result1 is True

        result2 = self.checker._module_matches_pattern("domains.document", "domains.billing")
        assert result2 is False

    def test_prefix_pattern_match(self):
        """Test prefix pattern matching."""
        result1 = self.checker._module_matches_pattern(
            "domains.billing.payments", "domains.billing"
        )
        assert result1 is True

        result2 = self.checker._module_matches_pattern("domains.document.core", "domains.billing")
        assert result2 is False

    def test_single_wildcard_pattern(self):
        """Test single wildcard pattern matching."""
        result1 = self.checker._module_matches_pattern("domains.billing", "domains.*")
        assert result1 is True

        result2 = self.checker._module_matches_pattern("domains.billing.payments", "domains.*")
        assert result2 is False

    def test_recursive_wildcard_pattern(self):
        """Test recursive wildcard pattern matching."""
        result1 = self.checker._module_matches_pattern("domains.billing", "domains.**")
        assert result1 is True

        result2 = self.checker._module_matches_pattern("domains.billing.payments", "domains.**")
        assert result2 is True

        result3 = self.checker._module_matches_pattern("other.billing", "domains.**")
        assert result3 is False

    def test_pattern_with_module_expression_object(self):
        """Test pattern matching with ModuleExpression-like objects."""
        mock_pattern = Mock()
        mock_pattern.__str__ = Mock(return_value="domains.billing")

        assert self.checker._module_matches_pattern("domains.billing", mock_pattern) is True


class TestContractChecking:
    """Test contract violation detection logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_linter = Mock()
        self.mock_linter.config = Mock()
        self.mock_linter.config.import_linter_debug = False
        self.checker = ImportLinterChecker(self.mock_linter)

    def test_check_forbidden_contract_violation(self):
        """Test detection of forbidden contract violations."""
        # Mock forbidden contract
        mock_contract = Mock()
        mock_contract.source_modules = ["domains.document"]
        mock_contract.forbidden_modules = ["domains.billing.*"]

        mock_contract_check = Mock()

        # Test violation case
        result = self.checker._check_contract_against_import(
            mock_contract,
            mock_contract_check,
            "domains.document.core",
            "domains.billing.payments",
            False,
        )
        assert result is True

        # Test non-violation case
        result = self.checker._check_contract_against_import(
            mock_contract,
            mock_contract_check,
            "domains.document.core",
            "domains.shared.utils",
            False,
        )
        assert result is False

    def test_check_independence_contract_violation(self):
        """Test detection of independence contract violations."""
        # Mock independence contract
        mock_contract = Mock()
        mock_contract.modules = ["domains.document", "domains.billing"]
        delattr(mock_contract, "source_modules")  # Ensure it's not a forbidden contract
        delattr(mock_contract, "forbidden_modules")

        mock_contract_check = Mock()

        # Test violation case (different domains)
        result = self.checker._check_contract_against_import(
            mock_contract,
            mock_contract_check,
            "domains.document.core",
            "domains.billing.payments",
            False,
        )
        assert result is True

        # Test non-violation case (same domain)
        result = self.checker._check_contract_against_import(
            mock_contract,
            mock_contract_check,
            "domains.document.core",
            "domains.document.utils",
            False,
        )
        assert result is False

    def test_modules_are_same_domain(self):
        """Test the domain comparison logic."""
        # Same domain
        result1 = self.checker._modules_are_same_domain(
            "domains.document.core", "domains.document.utils"
        )
        assert result1 is True

        # Different domains
        result2 = self.checker._modules_are_same_domain(
            "domains.document.core", "domains.billing.payments"
        )
        assert result2 is False

        # Edge case: single part modules
        result3 = self.checker._modules_are_same_domain("document", "billing")
        assert result3 is False


class TestImportViolationDetection:
    """Test the _is_import_violation method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_linter = Mock()
        self.mock_linter.config = Mock()
        self.mock_linter.config.import_linter_debug = False
        self.mock_linter.config.import_linter_target_folders = ("example/domains",)
        self.checker = ImportLinterChecker(self.mock_linter)

    def test_is_import_violation_with_contracts_cache(self):
        """Test import violation detection with contracts loaded."""
        # Setup mock import node
        mock_import_node = Mock()
        mock_import_node.modname = "domains.billing.payments"
        mock_root = Mock()
        mock_root.file = "/abs/path/example/domains/document/core.py"
        mock_import_node.root.return_value = mock_root

        # Setup mock contracts cache
        mock_contract = Mock()
        mock_contract.source_modules = ["domains.document"]
        mock_contract.forbidden_modules = ["domains.billing.*"]

        mock_contract_check = Mock()
        mock_contract_check.kept = False

        mock_contracts_cache = Mock()
        mock_contracts_cache.get_contracts_and_checks.return_value = [
            (mock_contract, mock_contract_check)
        ]

        self.checker._contracts_cache = mock_contracts_cache

        with patch.object(
            self.checker, "_get_module_path_from_file", return_value="domains.document.core"
        ):
            result = self.checker._is_import_violation(mock_import_node)

        assert result is True

    def test_is_import_violation_no_contracts_cache(self):
        """Test import violation detection without contracts loaded."""
        mock_import_node = Mock()

        result = self.checker._is_import_violation(mock_import_node)

        assert result is False

    def test_is_import_violation_with_names_attribute(self):
        """Test import violation detection with 'names' attribute (regular imports)."""
        # Setup mock import node with names instead of modname
        mock_import_node = Mock()
        delattr(mock_import_node, "modname")  # Remove modname
        mock_import_node.names = [("domains.billing.payments", None)]
        mock_root = Mock()
        mock_root.file = "/abs/path/example/domains/document/core.py"
        mock_import_node.root.return_value = mock_root

        # Setup mock contracts cache
        mock_contract = Mock()
        mock_contract.source_modules = ["domains.document"]
        mock_contract.forbidden_modules = ["domains.billing.*"]

        mock_contract_check = Mock()
        mock_contract_check.kept = False

        mock_contracts_cache = Mock()
        mock_contracts_cache.get_contracts_and_checks.return_value = [
            (mock_contract, mock_contract_check)
        ]

        self.checker._contracts_cache = mock_contracts_cache

        with patch.object(
            self.checker, "_get_module_path_from_file", return_value="domains.document.core"
        ):
            result = self.checker._is_import_violation(mock_import_node)

        assert result is True


class TestErrorHandling:
    """Test error handling in the plugin."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_linter = Mock()
        self.mock_linter.config = Mock()
        self.mock_linter.config.import_linter_config = None
        self.mock_linter.config.import_linter_contract = ()
        self.mock_linter.config.import_linter_cache_dir = None
        self.mock_linter.config.import_linter_no_cache = False
        self.mock_linter.config.import_linter_verbose = False
        self.mock_linter.config.import_linter_show_timings = False
        self.mock_linter.config.import_linter_debug = False

        self.checker = ImportLinterChecker(self.mock_linter)
        self.checker._first_module_node = Mock()
        self.checker.add_message = Mock()  # type: ignore[assignment]

    @patch("importlinter.application.use_cases.read_user_options")
    def test_check_import_contracts_import_error(self, mock_read_user_options):
        """Test error handling when ImportError occurs."""
        mock_read_user_options.side_effect = ImportError("Test import error")

        self.checker._check_import_contracts()

        self.checker.add_message.assert_called_once()
        args = self.checker.add_message.call_args
        assert args[1]["args"][0] == "Test import error"

    @patch("importlinter.application.use_cases.read_user_options")
    def test_check_import_contracts_file_not_found_error(self, mock_read_user_options):
        """Test error handling when FileNotFoundError occurs."""
        mock_read_user_options.side_effect = FileNotFoundError("Config file not found")

        self.checker._check_import_contracts()

        self.checker.add_message.assert_called_once()
        args = self.checker.add_message.call_args
        assert args[1]["args"][0] == "Config file not found"

    @patch("importlinter.application.use_cases.read_user_options")
    def test_check_import_contracts_unexpected_error(self, mock_read_user_options):
        """Test error handling for unexpected exceptions."""
        mock_read_user_options.side_effect = RuntimeError("Unexpected error")

        self.checker._check_import_contracts()

        self.checker.add_message.assert_called_once()
        args = self.checker.add_message.call_args
        assert "Unexpected error: Unexpected error" in args[1]["args"][0]


class TestCacheConfiguration:
    """Test cache directory configuration logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_linter = Mock()
        self.mock_linter.config = Mock()
        self.checker = ImportLinterChecker(self.mock_linter)

    def test_get_cache_dir_disabled(self):
        """Test cache directory when caching is disabled."""
        self.mock_linter.config.import_linter_no_cache = True
        self.mock_linter.config.import_linter_cache_dir = "/some/cache/dir"

        result = self.checker._get_cache_dir()

        assert result is None

    def test_get_cache_dir_custom_directory(self):
        """Test cache directory with custom cache dir."""
        self.mock_linter.config.import_linter_no_cache = False
        self.mock_linter.config.import_linter_cache_dir = "/custom/cache/dir"

        result = self.checker._get_cache_dir()

        assert result == "/custom/cache/dir"

    def test_get_cache_dir_default(self):
        """Test cache directory with default settings."""
        from importlinter.application.sentinels import NotSupplied

        self.mock_linter.config.import_linter_no_cache = False
        self.mock_linter.config.import_linter_cache_dir = None

        result = self.checker._get_cache_dir()

        assert result is NotSupplied


class TestIntegrationScenarios:
    """Test integration scenarios that simulate real-world usage."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_linter = Mock()
        self.mock_linter.config = Mock()
        self.mock_linter.config.import_linter_config = "test.ini"
        self.mock_linter.config.import_linter_contract = ()
        self.mock_linter.config.import_linter_target_folders = ("example/domains",)
        self.mock_linter.config.import_linter_exclude_folders = ()
        self.mock_linter.config.import_linter_cache_dir = None
        self.mock_linter.config.import_linter_no_cache = False
        self.mock_linter.config.import_linter_verbose = False
        self.mock_linter.config.import_linter_show_timings = False
        self.mock_linter.config.import_linter_debug = False

        self.checker = ImportLinterChecker(self.mock_linter)
        self.checker.add_message = Mock()  # type: ignore[assignment]

    def test_complete_workflow_with_violations(self):
        """Test complete workflow from file analysis to violation reporting."""
        # Setup: Add analyzed files
        mock_module_node = Mock()
        mock_module_node.file = "/abs/path/example/domains/document/core.py"
        self.checker.visit_module(mock_module_node)

        # Setup: Add import nodes
        mock_import_node = Mock()
        mock_import_node.modname = "domains.billing.payments"
        mock_import_node.lineno = 5
        mock_root = Mock()
        mock_root.file = "/abs/path/example/domains/document/core.py"
        mock_import_node.root.return_value = mock_root
        self.checker.visit_import(mock_import_node)

        # Mock the contracts and report
        mock_contract = Mock()
        mock_contract.__class__.__name__ = "ForbiddenContract"
        mock_contract.name = "Test Contract"
        mock_contract.source_modules = ["domains.document"]
        mock_contract.forbidden_modules = ["domains.billing.*"]

        mock_contract_check = Mock()
        mock_contract_check.kept = False

        mock_report = Mock()
        mock_report.contains_failures = True
        mock_report.get_contracts_and_checks.return_value = [(mock_contract, mock_contract_check)]

        # Mock the import-linter integration
        with (
            patch("importlinter.application.use_cases.read_user_options") as mock_read_options,
            patch("importlinter.application.use_cases._register_contract_types"),
            patch("importlinter.application.use_cases.create_report") as mock_create_report,
            patch("importlinter.pylint_plugin.os.path.relpath") as mock_relpath,
            patch(
                "importlinter.application.constants.get_message_id_for_contract_type"
            ) as mock_get_msg_id,
            patch(
                "importlinter.application.constants.format_violation_message"
            ) as mock_format_msg,
        ):

            mock_read_options.return_value = Mock(contracts_options=[])
            mock_create_report.return_value = mock_report
            mock_relpath.return_value = "example/domains/document/core.py"
            mock_get_msg_id.return_value = IMPORT_BOUNDARY_VIOLATION
            mock_format_msg.return_value = "Test violation message"

            # Execute the complete workflow
            self.checker.close()

            # Verify that violations were reported
            self.checker.add_message.assert_called()
            call_args = self.checker.add_message.call_args
            assert call_args[0][0] == IMPORT_BOUNDARY_VIOLATION

    def test_no_violations_scenario(self):
        """Test scenario where no violations are found."""
        # Setup: Add analyzed files that should pass
        mock_module_node = Mock()
        mock_module_node.file = "/abs/path/example/domains/document/core.py"
        self.checker.visit_module(mock_module_node)

        # Mock clean report
        mock_report = Mock()
        mock_report.contains_failures = False

        with (
            patch("importlinter.application.use_cases.read_user_options") as mock_read_options,
            patch("importlinter.application.use_cases._register_contract_types"),
            patch("importlinter.application.use_cases.create_report") as mock_create_report,
        ):

            mock_read_options.return_value = Mock(contracts_options=[])
            mock_create_report.return_value = mock_report

            # Execute the workflow
            self.checker.close()

            # Verify no violations were reported
            self.checker.add_message.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__])
