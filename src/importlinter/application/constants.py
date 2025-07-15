"""
Shared constants for import-linter messages and error codes.

These constants are used across both CLI and pylint plugin modes to ensure
consistent error reporting and message IDs.
"""

# Message IDs for different types of contract violations
# These follow the pattern: import-<violation-type>-violation
IMPORT_BOUNDARY_VIOLATION = "import-boundary-violation"
IMPORT_LAYER_VIOLATION = "import-layer-violation"
IMPORT_INDEPENDENCE_VIOLATION = "import-independence-violation"
IMPORT_CONTRACT_VIOLATION = "import-contract-violation"
IMPORT_CONTRACT_ERROR = "import-contract-error"

# Mapping of contract types to their specific message IDs
CONTRACT_TYPE_TO_MESSAGE_ID = {
    "ForbiddenContract": IMPORT_BOUNDARY_VIOLATION,
    "LayersContract": IMPORT_LAYER_VIOLATION,
    "IndependenceContract": IMPORT_INDEPENDENCE_VIOLATION,
}

# Default message ID for unknown contract types
DEFAULT_CONTRACT_MESSAGE_ID = IMPORT_CONTRACT_VIOLATION

# Pylint message definitions for import-linter violations
MESSAGES = {
    "E9001": (
        "Import contract violation: %s",
        IMPORT_CONTRACT_VIOLATION,
        "Import violates architecture contract defined in .importlinter configuration",
    ),
    "E9002": (
        "Import contract error: %s",
        IMPORT_CONTRACT_ERROR,
        "Error occurred while checking import contracts",
    ),
    "E9003": (
        "Domain boundary violation: %s",
        IMPORT_BOUNDARY_VIOLATION,
        "Import violates domain boundaries defined by forbidden contract rules",
    ),
    "E9004": (
        "Layer violation: %s",
        IMPORT_LAYER_VIOLATION,
        "Import violates layer architecture defined by layers contract rules",
    ),
    "E9005": (
        "Independence violation: %s",
        IMPORT_INDEPENDENCE_VIOLATION,
        "Import violates module independence defined by independence contract rules",
    ),
}


def format_violation_message(
    contract_name: str, message_id: str, folder_info: str = "", violation_details: str = ""
) -> str:
    """
    Generate a standardized violation message for both CLI and pylint plugin.

    This ensures consistent messaging across all import-linter tools.

    Args:
        contract_name: The name of the violated contract
        message_id: The specific violation type (import-boundary-violation, etc.)
        folder_info: Optional folder targeting information
        violation_details: Specific details about the violation (e.g., import path)

    Returns:
        A formatted violation message string
    """
    base_messages = {
        IMPORT_BOUNDARY_VIOLATION: f"Forbidden import detected - violates '{contract_name}' rule",
        IMPORT_LAYER_VIOLATION: f"Layer boundary violated - violates '{contract_name}' rule",
        IMPORT_INDEPENDENCE_VIOLATION: (
            f"Module independence violated - violates '{contract_name}' rule"
        ),
        IMPORT_CONTRACT_VIOLATION: f"Contract validation failed for '{contract_name}' rule",
    }

    base_msg = base_messages.get(
        message_id, f"Contract validation failed for '{contract_name}' rule"
    )

    # Add specific violation details if provided
    if violation_details:
        base_msg += f": {violation_details}"

    # Add folder information if provided
    if folder_info:
        base_msg += folder_info

    return f"{base_msg}. Run 'lint-imports --verbose' for details."


def get_message_id_for_contract_type(contract_type: str) -> str:
    """
    Get the appropriate message ID for a given contract type.

    Args:
        contract_type: The contract class name (e.g., "ForbiddenContract")

    Returns:
        The corresponding message ID
    """
    return CONTRACT_TYPE_TO_MESSAGE_ID.get(contract_type, DEFAULT_CONTRACT_MESSAGE_ID)
