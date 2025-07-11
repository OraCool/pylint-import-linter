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
        "Import violates domain boundaries (forbidden contract)",
    ),
    "E9004": (
        "Layer violation: %s",
        IMPORT_LAYER_VIOLATION,
        "Import violates layer architecture (layers contract)",
    ),
    "E9005": (
        "Independence violation: %s",
        IMPORT_INDEPENDENCE_VIOLATION,
        "Import violates module independence (independence contract)",
    ),
}
