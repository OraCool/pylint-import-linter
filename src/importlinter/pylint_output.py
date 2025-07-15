"""
Enhanced output adapter for capturing import-linter violations in pylint plugin.
"""

from __future__ import annotations

from typing import List, Tuple, Optional

from importlinter.application.ports.reporting import Report
from importlinter.adapters.printing import ClickPrinter


class PylintOutputAdapter:
    """Adapter to capture import-linter output for pylint reporting."""

    def __init__(self) -> None:
        self.violations: List[Tuple[str, str]] = []
        self.errors: List[str] = []

    def capture_report(self, report: Report) -> None:
        """Capture a report from import-linter."""
        if report.contains_failures:
            for contract, contract_check in report.get_contracts_and_checks():
                if not contract_check.kept:
                    contract_name = contract.name
                    # Use general message since ContractCheck doesn't expose violations
                    violation_msg = f"Contract '{contract_name}' failed"
                    self.violations.append((violation_msg, contract_name))

    def capture_error(self, error_msg: str) -> None:
        """Capture an error message."""
        self.errors.append(error_msg)

    def clear(self) -> None:
        """Clear captured violations and errors."""
        self.violations.clear()
        self.errors.clear()


class SilentPrinter(ClickPrinter):
    """A printer that captures output instead of printing to console."""

    def __init__(self, output_adapter: PylintOutputAdapter) -> None:
        super().__init__()
        self.output_adapter = output_adapter

    def print(
        self, text: str = "", bold: bool = False, color: Optional[str] = None, newline: bool = True
    ) -> None:
        """Override print to capture instead of printing."""
        # We don't print anything, just capture

    def print_error(self, text: str) -> None:
        """Override error printing to capture errors."""
        self.output_adapter.capture_error(text)
