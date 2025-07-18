"""Configuration options for the pylint import-linter plugin."""

# Plugin configuration options tuple
PLUGIN_OPTIONS = (
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
