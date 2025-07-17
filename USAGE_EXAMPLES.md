# Usage Examples

This document provides comprehensive examples of how to use the pylint-import-linter plugin in various scenarios.

## Basic Usage

### Quick Start

```bash
# Run pylint with import-linter plugin
pylint --load-plugins=importlinter.pylint_plugin src/
```

### With Configuration File

```bash
# Specify custom configuration file
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-config=.importlinter \
       src/
```

## Debug and Verbose Mode

### Full Debug Mode (Recommended for Troubleshooting)

```bash
# Enable all diagnostic features
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-config=.importlinter \
       --import-linter-debug=yes \
       --import-linter-verbose=yes \
       --import-linter-show-timings=yes \
       --disable=all \
       --enable=import-boundary-violation,import-independence-violation,import-layer-violation,import-contract-violation,import-contract-error \
       src/
```

**Example Debug Output:**

```
Import-linter: Analyzing contracts in .importlinter
Import-linter: Debug mode enabled
Import-linter: Found 3 contracts
Import-linter: Contract 1: Document domain boundaries (type: forbidden)
Import-linter: Contract 2: Billing domain boundaries (type: forbidden)
Import-linter: Contract 3: Domain independence (type: independence)
Building import graph (cache directory is .import_linter_cache)...
Built graph in 0s.
Checking Document domain boundaries...
Searching for import chains from domains.document to domains.billing.payments...
Found 2 illegal chains in 0s.
Document domain boundaries BROKEN [0s]
```

### Verbose Mode Only

```bash
# Show detailed analysis progress
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-verbose=yes \
       src/
```

### Debug Mode Only

```bash
# Show debug information and stack traces
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-debug=yes \
       src/
```

## Single File Analysis

### Debug Specific File

```bash
# Analyze single file with full debug mode
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-config=.importlinter \
       --import-linter-target-folders=src/domains \
       --import-linter-debug=yes \
       --import-linter-verbose=yes \
       --disable=all \
       --enable=import-boundary-violation,import-independence-violation,import-layer-violation,import-contract-violation,import-contract-error \
       src/specific_file.py
```

### Quick File Check

```bash
# Basic check for single file
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-config=.importlinter \
       --import-linter-target-folders=src/domains \
       --disable=all \
       --enable=import-boundary-violation,import-independence-violation,import-layer-violation,import-contract-violation,import-contract-error \
       src/specific_file.py
```

## Folder Targeting

### Target Specific Folders

```bash
# Only check specific folders
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-target-folders=src/core,src/api \
       --import-linter-verbose=yes \
       src/
```

### Exclude Specific Folders

```bash
# Exclude tests and docs from analysis
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-exclude-folders=tests,docs,migrations \
       src/
```

### Combined Folder Configuration

```bash
# Target core modules but exclude experimental features
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-target-folders=src/core,src/api \
       --import-linter-exclude-folders=src/core/experimental,tests \
       src/
```

## Contract-Specific Analysis

### Check Specific Contracts

```bash
# Only check specific contracts
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-contract=document_domain,billing_domain \
       --import-linter-verbose=yes \
       src/
```

### Performance Optimization

```bash
# Use cache for faster analysis
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-cache-dir=.import_linter_cache \
       --import-linter-show-timings=yes \
       src/
```

```bash
# Force fresh analysis without cache
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-no-cache=yes \
       src/
```

## Error Handling and Troubleshooting

### Configuration Error Debugging

```bash
# Debug configuration file issues
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-config=nonexistent.ini \
       --import-linter-debug=yes \
       src/
```

**Example Error Output:**

```
E9002: Import contract error: Could not find nonexistent.ini.
Debug traceback:
Traceback (most recent call last):
  File "src/importlinter/pylint_plugin.py", line 220, in _check_import_contracts
    user_options = read_user_options(config_filename=config_filename)
  File "src/importlinter/application/use_cases.py", line 108, in read_user_options
    options = reader.read_options(config_filename=config_filename)
  File "src/importlinter/adapters/user_options.py", line 26, in read_options
    raise FileNotFoundError(f"Could not find {config_filename}.")
FileNotFoundError: Could not find nonexistent.ini.
```

### Contract Violation Analysis

```bash
# Detailed analysis of contract violations
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-debug=yes \
       --import-linter-verbose=yes \
       --disable=all \
       --enable=import-boundary-violation,import-independence-violation,import-layer-violation,import-contract-violation,import-contract-error \
       src/
```

## IDE Integration

### VS Code Task Configuration

Add to `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Debug Import Violations",
            "type": "shell",
            "command": "uv",
            "args": [
                "run",
                "pylint",
                "--load-plugins=importlinter.pylint_plugin",
                "--import-linter-config=.importlinter",
                "--import-linter-debug=yes",
                "--import-linter-verbose=yes",
                "--import-linter-show-timings=yes",
                "--disable=all",
                "--enable=import-boundary-violation,import-independence-violation,import-layer-violation,import-contract-violation,import-contract-error",
                "${file}"
            ],
            "group": "test"
        }
    ]
}
```

### VS Code Launch Configuration

Add to `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Pylint Plugin",
            "type": "debugpy",
            "request": "launch",
            "module": "pylint",
            "args": [
                "--load-plugins=importlinter.pylint_plugin",
                "--import-linter-config=.importlinter",
                "--import-linter-debug=yes",
                "--import-linter-verbose=yes",
                "--disable=all",
                "--enable=import-boundary-violation,import-independence-violation,import-layer-violation,import-contract-violation,import-contract-error",
                "${file}"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Import Linter
on: [push, pull_request]

jobs:
  check-imports:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install uv
          uv pip install pylint-import-linter
      - name: Check import contracts
        run: |
          uv run pylint --load-plugins=importlinter.pylint_plugin \
                        --import-linter-verbose=yes \
                        --disable=all \
                        --enable=import-boundary-violation,import-independence-violation,import-layer-violation,import-contract-violation,import-contract-error \
                        src/
```

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: import-linter
        name: Import Linter
        entry: pylint
        language: system
        args:
          - --load-plugins=importlinter.pylint_plugin
          - --import-linter-config=.importlinter
          - --disable=all
          - --enable=import-boundary-violation,import-independence-violation,import-layer-violation,import-contract-violation,import-contract-error
        files: \.py$
```

## Parameter Reference

### CLI vs Plugin Parameter Mapping

| CLI Parameter | Plugin Parameter | Description |
|---------------|------------------|-------------|
| `--config` | `--import-linter-config` | Path to configuration file |
| `--contract` | `--import-linter-contract` | Specific contracts to check |
| `--target-folders` | `--import-linter-target-folders` | Folders to analyze |
| `--exclude-folders` | `--import-linter-exclude-folders` | Folders to exclude |
| `--cache-dir` | `--import-linter-cache-dir` | Cache directory |
| `--no-cache` | `--import-linter-no-cache` | Disable caching |
| `--verbose` | `--import-linter-verbose` | Verbose output |
| `--show-timings` | `--import-linter-show-timings` | Show timing info |
| `--debug` | `--import-linter-debug` | Debug mode |

### Boolean Parameter Format

Plugin boolean parameters use `=yes/no` format:

```bash
# Correct
--import-linter-verbose=yes
--import-linter-debug=yes
--import-linter-no-cache=yes

# Incorrect
--import-linter-verbose
--import-linter-debug
--import-linter-no-cache
```

## Common Use Cases

### Development Workflow

```bash
# During development - quick checks
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-target-folders=src/current_feature \
       src/current_feature/

# Before commit - full analysis
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-verbose=yes \
       src/

# Troubleshooting violations
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-debug=yes \
       --import-linter-verbose=yes \
       --disable=all \
       --enable=import-boundary-violation,import-independence-violation,import-layer-violation,import-contract-violation,import-contract-error \
       src/problematic_file.py
```

### Large Codebase Analysis

```bash
# Analyze specific domains
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-target-folders=src/core,src/api,src/shared \
       --import-linter-exclude-folders=src/legacy,tests \
       --import-linter-cache-dir=.import_linter_cache \
       --import-linter-show-timings=yes \
       src/

# Progressive adoption
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-target-folders=src/new_modules \
       --import-linter-contract=new_architecture_contracts \
       src/
```

### Performance Optimization

```bash
# Fast development checks
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-cache-dir=.import_linter_cache \
       --import-linter-target-folders=src/current_work \
       src/current_work/

# Full CI analysis with timing
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-verbose=yes \
       --import-linter-show-timings=yes \
       --import-linter-no-cache=yes \
       src/
```
