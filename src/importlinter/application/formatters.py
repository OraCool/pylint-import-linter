"""
Output formatters for import-linter CLI.

Provides different output formats including text and JSON for better integration
with CI/CD systems and automated tooling.
"""
import json

from importlinter.application.constants import (
    CONTRACT_TYPE_TO_MESSAGE_ID,
    DEFAULT_CONTRACT_MESSAGE_ID,
)


def format_report_as_json(report, folder_info: str = "") -> str:
    """
    Format an import-linter report as JSON output.
    
    This provides structured output compatible with the pylint plugin format
    for consistent tooling integration.
    """
    result = {
        "summary": {
            "analyzed_files": getattr(report, 'number_of_modules', 0),
            "dependencies": getattr(report, 'number_of_dependencies', 0),
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
            message_id = CONTRACT_TYPE_TO_MESSAGE_ID.get(
                contract_type, DEFAULT_CONTRACT_MESSAGE_ID
            )
            
            # Create violation entry compatible with pylint plugin format
            violation = {
                "symbol": message_id,
                "contract_name": contract.name,
                "contract_type": contract_type,
                "message": _get_violation_message(contract, message_id, folder_info),
                "details": [],
            }
            
            # Add specific violation details if available
            if hasattr(contract_check, 'metadata') and contract_check.metadata:
                if 'invalid_chains' in contract_check.metadata:
                    for chain in contract_check.metadata['invalid_chains']:
                        violation["details"].append({
                            "import_chain": str(chain),
                            "line_number": getattr(chain, 'line_number', None),
                        })
            
            result["violations"].append(violation)
            contract_info["violation"] = violation
        
        result["contracts"].append(contract_info)
    
    return json.dumps(result, indent=2)


def _get_violation_message(contract, message_id: str, folder_info: str) -> str:
    """Generate a violation message consistent with the pylint plugin."""
    contract_name = contract.name
    
    if message_id == "import-boundary-violation":
        return (
            f"Forbidden import detected in '{contract_name}'{folder_info}. "
            "Run 'lint-imports --verbose' for details."
        )
    elif message_id == "import-layer-violation":
        return (
            f"Layer boundary violated in '{contract_name}'{folder_info}. "
            "Run 'lint-imports --verbose' for details."
        )
    elif message_id == "import-independence-violation":
        return (
            f"Module independence violated in '{contract_name}'{folder_info}. "
            "Run 'lint-imports --verbose' for details."
        )
    else:
        return (
            f"Contract validation failed for '{contract_name}'{folder_info}. "
            "Run 'lint-imports --verbose' for details."
        )


def should_use_json_output(format_type: str) -> bool:
    """Check if JSON output format should be used."""
    return format_type.lower() == "json"
