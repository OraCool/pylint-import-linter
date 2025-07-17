# Parameter Mapping: CLI vs Plugin

This document shows the unified parameter mapping between the `lint-imports` CLI command and the pylint plugin.

## Unified Parameter Names

| CLI Parameter | Plugin Parameter | Description |
|---------------|------------------|-------------|
| `--config` | `--import-linter-config` | Path to import-linter configuration file |
| `--contract` | `--import-linter-contract` | Comma-separated list of contract IDs to check |
| `--target-folders` | `--import-linter-target-folders` | Comma-separated list of folders to check |
| `--exclude-folders` | `--import-linter-exclude-folders` | Comma-separated list of folders to exclude |
| `--cache-dir` | `--import-linter-cache-dir` | Directory for caching |
| `--no-cache` | `--import-linter-no-cache` | Disable caching |
| `--verbose` | `--import-linter-verbose` | Enable verbose output |
| `--show-timings` | `--import-linter-show-timings` | Show timing information |
| `--debug` | `--import-linter-debug` | Enable debug mode |

## Usage Examples

### CLI Usage
```bash
# Basic usage
lint-imports --config .importlinter --verbose

# With specific contracts
lint-imports --contract document_domain --contract billing_domain --verbose

# With folder targeting
lint-imports --target-folders src/domains --cache-dir /tmp/cache --show-timings
```

### Plugin Usage
```bash
# Basic usage
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-config=.importlinter \
       --import-linter-verbose=yes \
       src/

# With debug and verbose mode (recommended for troubleshooting)
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-config=importlinter.ini \
       --import-linter-verbose=yes \
       --import-linter-debug=yes \
       --import-linter-show-timings=yes \
       src/

# Debug mode for single file analysis
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-config=importlinter.ini \
       --import-linter-target-folders=src/domains \
       --import-linter-debug=yes \
       --import-linter-verbose=yes \
       --disable=all \
       --enable=import-boundary-violation,import-independence-violation,import-layer-violation,import-contract-violation,import-contract-error \
       src/specific_file.py

# With specific contracts
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-contract=document_domain,billing_domain \
       --import-linter-verbose=yes \
       src/

# With folder targeting
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-target-folders=src/domains \
       --import-linter-cache-dir=/tmp/cache \
       --import-linter-show-timings=yes \
       src/
```

## Key Differences

1. **Parameter Names**: Plugin parameters have the `--import-linter-` prefix to avoid conflicts with pylint's own parameters
2. **Boolean Values**: Plugin boolean parameters use `=yes/no` format instead of flags
3. **Multiple Values**: Both support comma-separated values, but plugin uses single parameter while CLI allows multiple parameter usage

## Debug and Verbose Mode Configuration

### For Troubleshooting Import Violations

When you need to debug import contract violations, use both debug and verbose modes:

```bash
# Full debug mode with all diagnostic information
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-config=importlinter.ini \
       --import-linter-debug=yes \
       --import-linter-verbose=yes \
       --import-linter-show-timings=yes \
       --disable=all \
       --enable=import-boundary-violation,import-independence-violation,import-layer-violation,import-contract-violation,import-contract-error \
       your_file.py
```

### What Debug Mode Shows:
- **Stack traces** for configuration errors
- **Detailed error messages** with file paths and line numbers
- **Cache usage information**
- **Contract analysis progress**

### What Verbose Mode Shows:
- **Real-time analysis progress** ("Analyzing contracts in config.ini")
- **Contract details** ("Found 3 contracts", "Contract 1: Document domain boundaries")
- **Import chain analysis** ("Searching for import chains from A to B")
- **Timing information** for each operation
- **Final results summary**

### VS Code Task Configuration

You can also configure VS Code tasks for debug mode:

```json
{
    "label": "Debug Import Violations",
    "type": "shell",
    "command": "uv",
    "args": [
        "run",
        "pylint",
        "--load-plugins=importlinter.pylint_plugin",
        "--import-linter-config=importlinter.ini",
        "--import-linter-debug=yes",
        "--import-linter-verbose=yes",
        "--import-linter-show-timings=yes",
        "--disable=all",
        "--enable=import-boundary-violation,import-independence-violation,import-layer-violation,import-contract-violation,import-contract-error",
        "${file}"
    ],
    "group": "test"
}
```

## Migration Guide

If you're migrating from using the CLI to the plugin, simply:

1. Add `--import-linter-` prefix to all parameters
2. Convert boolean flags to `=yes` format
3. Combine multiple `--contract` parameters into a single comma-separated `--import-linter-contract` parameter
