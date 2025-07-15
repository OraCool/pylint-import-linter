"""
Output formatters for import-linter CLI.

Provides different output formats including text and JSON for better integration
with CI/CD systems and automated tooling.
"""

import json
from typing import Any

from importlinter.application.constants import (
    get_message_id_for_contract_type,
    format_violation_message,
)


def format_report_as_json(report: Any, folder_info: str = "") -> str:
    """
    Format an import-linter report as JSON output.

    This provides structured output compatible with the pylint plugin format
    for consistent tooling integration.
    """
    result: dict[str, Any] = {
        "summary": {
            "analyzed_files": getattr(report, "number_of_modules", 0),
            "dependencies": getattr(report, "number_of_dependencies", 0),
            "contracts_total": len(list(report.get_contracts_and_checks())),
            "contracts_kept": 0,
            "contracts_broken": 0,
            "has_violations": report.contains_failures,
        },
        "violations": [],
        "contracts": [],
    }

    # Process contracts and violations
    for contract, contract_check in report.get_contracts_and_checks():
        contract_info = {
            "name": contract.name,
            "type": contract.__class__.__name__,
            "kept": contract_check.kept,
        }

        if contract_check.kept:
            result["summary"]["contracts_kept"] += 1
        else:
            result["summary"]["contracts_broken"] += 1

            # Get the appropriate message ID for this contract type
            contract_type = contract.__class__.__name__
            message_id = get_message_id_for_contract_type(contract_type)

            # Create violation entry compatible with pylint plugin format
            violation = {
                "symbol": message_id,
                "contract_name": contract.name,
                "contract_type": contract_type,
                "message": format_violation_message(contract.name, contract_type, folder_info),
                "details": [],
            }

            # Add specific violation details if available
            if hasattr(contract_check, "metadata") and contract_check.metadata:
                if "invalid_chains" in contract_check.metadata:
                    for chain in contract_check.metadata["invalid_chains"]:
                        violation["details"].append(
                            {
                                "import_chain": str(chain),
                                "line_number": getattr(chain, "line_number", None),
                            }
                        )

            result["violations"].append(violation)
            contract_info["violation"] = violation

        result["contracts"].append(contract_info)

    return json.dumps(result, indent=2)


def format_report_as_json2(report: Any, folder_info: str = "") -> str:
    """
    Format an import-linter report as JSON2 output (improved format with statistics).

    This provides structured output compatible with pylint's json2 format,
    including statistics and enhanced message structure.
    """
    messages: list[dict[str, Any]] = []
    statistics: dict[str, Any] = {
        "messageTypeCount": {
            "fatal": 0,
            "error": 0,
            "warning": 0,
            "refactor": 0,
            "convention": 0,
            "info": 0,
        },
        "modulesLinted": getattr(report, "number_of_modules", 0),
        "score": 10.0 if report.passed else 0.0,
    }

    # Process contracts and violations
    for contract, contract_check in report.get_contracts_and_checks():
        if not contract_check.kept:
            # Get the appropriate message ID for this contract type
            contract_type = contract.__class__.__name__
            message_id = get_message_id_for_contract_type(contract_type)

            # Create message entry compatible with pylint json2 format
            message = {
                "type": "error",
                "symbol": message_id,
                "message": format_violation_message(contract.name, message_id, folder_info),
                "messageId": "E9001",  # Generic import contract violation
                "confidence": "HIGH",
                "module": contract.name,
                "obj": "",
                "line": 1,
                "column": 0,
                "endLine": None,
                "endColumn": None,
                "path": contract.name,
                "absolutePath": contract.name,
            }

            # Map specific contract types to appropriate message IDs
            if message_id == "import-boundary-violation":
                message["messageId"] = "E9003"
            elif message_id == "import-layer-violation":
                message["messageId"] = "E9004"
            elif message_id == "import-independence-violation":
                message["messageId"] = "E9005"

            messages.append(message)
            statistics["messageTypeCount"]["error"] += 1

    result = {"messages": messages, "statistics": statistics}

    return json.dumps(result, indent=2)


def should_use_json_output(format_type: str) -> bool:
    """Check if JSON output format should be used."""
    return format_type.lower() in ["json", "json2"]
