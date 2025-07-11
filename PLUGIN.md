# Pylint Import-Linter Plugin

This plugin integrates [import-linter](https://import-linter.readthedocs.io/) functionality directly into [Pylint](https://pylint.org/), allowing you to enforce architectural contracts as part of your normal linting workflow.

## Features

- **Seamless Integration**: Run import-linter checks as part of your normal pylint workflow
- **Contract Enforcement**: All import-linter contract types supported (layers, forbidden, independence)
- **Configurable**: Full support for import-linter configuration options
- **Error Reporting**: Clear error messages integrated into pylint's output
- **CI/CD Ready**: Perfect for continuous integration pipelines

## Installation

The plugin is automatically available when you install this package:

```bash
# Using uv (recommended)
uv add pylint-import-linter

# Using pip
pip install pylint-import-linter
```

## Usage

### Basic Usage

Run pylint with the plugin loaded:

```bash
pylint --load-plugins=importlinter.pylint_plugin src/
```

### Configuration File

Add the plugin to your `.pylintrc` or `pyproject.toml`:

**.pylintrc:**
```ini
[MASTER]
load-plugins = importlinter.pylint_plugin
```

**pyproject.toml:**
```toml
[tool.pylint.master]
load-plugins = ["importlinter.pylint_plugin"]
```

### Plugin Options

The plugin supports all import-linter configuration options:

```bash
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-config=.importlinter \
       --import-linter-contracts=contract1,contract2 \
       --import-linter-cache-dir=.cache \
       --import-linter-no-cache=yes \
       src/
```

Available options:

- `--import-linter-config`: Path to import-linter config file (default: `.importlinter`)
- `--import-linter-contracts`: Comma-separated list of contract IDs to check
- `--import-linter-cache-dir`: Directory for caching (default: `.import_linter_cache`)
- `--import-linter-no-cache`: Disable caching

## Error Messages

The plugin provides two types of error messages:

### E9001: import-contract-violation
Triggered when an import violates a defined contract (e.g., layer violations, forbidden imports).

### E9002: import-contract-error  
Triggered when there's an error in the plugin or import-linter configuration.

## Examples

### Example 1: Layer Architecture

**.importlinter:**
```ini
[importlinter]
root_package = myproject

[importlinter:contract:1]
name=Layered architecture
type=layers
containers=myproject
layers=
    presentation
    business
    data
```

**Running pylint:**
```bash
pylint --load-plugins=importlinter.pylint_plugin myproject/
```

**Output when violation occurs:**
```
myproject/data/models.py:1:0: E9001: Import contract violation: Contract validation failed. Run 'lint-imports --verbose' for details. (import-contract-violation)
```

### Example 2: Forbidden Imports

**.importlinter:**
```ini
[importlinter]
root_package = myproject

[importlinter:contract:1]
name=No database imports in presentation
type=forbidden
source_modules=myproject.presentation
forbidden_modules=myproject.database
```

### Example 3: CI/CD Integration

**GitHub Actions:**
```yaml
- name: Lint with pylint and import-linter
  run: |
    pylint --load-plugins=importlinter.pylint_plugin \
           --fail-on=E9001,E9002 \
           src/
```

**Pre-commit hook:**
```yaml
repos:
  - repo: local
    hooks:
      - id: pylint-import-linter
        name: Pylint with Import Linter
        entry: pylint
        language: system
        args: [--load-plugins=importlinter.pylint_plugin]
        files: \.py$
```

## Comparison: Plugin vs Standalone

| Feature | Pylint Plugin | Standalone import-linter |
|---------|---------------|--------------------------|
| Integration | ✅ Part of pylint | ❌ Separate tool |
| CI/CD | ✅ Single command | ❌ Two commands needed |
| IDE Support | ✅ Full pylint support | ❌ Limited |
| Error Reporting | ✅ Integrated | ❌ Separate output |
| Performance | ✅ Single run | ❌ Two separate runs |

## Advanced Configuration

### Selective Contract Checking

Check only specific contracts:
```bash
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-contracts=layers,forbidden-db \
       src/
```

### Custom Configuration Files

Use different config files for different environments:
```bash
# Development
pylint --import-linter-config=.importlinter.dev src/

# Production  
pylint --import-linter-config=.importlinter.prod src/
```

### Disable Specific Messages

Disable import-linter checks for specific files:
```python
# pylint: disable=import-contract-violation
from restricted_module import something
```

## Troubleshooting

### Common Issues

1. **Plugin not found**: Ensure the package is installed in the same environment as pylint
2. **Config file not found**: Specify the config file path with `--import-linter-config`
3. **No violations reported**: Check that your `.importlinter` file is valid

### Debug Mode

Run with verbose output for debugging:
```bash
pylint --load-plugins=importlinter.pylint_plugin --verbose src/
```

### Performance Tuning

For large projects, use caching:
```bash
pylint --load-plugins=importlinter.pylint_plugin \
       --import-linter-cache-dir=.cache \
       src/
```

## Integration Examples

### VS Code

Add to your VS Code settings:
```json
{
    "pylint.args": ["--load-plugins=importlinter.pylint_plugin"]
}
```

### PyCharm

1. Go to Settings → Tools → External Tools
2. Add new tool with command: `pylint --load-plugins=importlinter.pylint_plugin $FilePath$`

### Development Workflow

```bash
# Format code
uv run black src/

# Type check  
uv run mypy src/

# Lint with architecture checks
uv run pylint --load-plugins=importlinter.pylint_plugin src/

# Run tests
uv run pytest
```

## Migration from Standalone

If you're currently using standalone import-linter:

1. **Keep your `.importlinter` config** - no changes needed
2. **Update CI/CD scripts** - replace separate tools with single pylint command
3. **Update pre-commit hooks** - use pylint instead of import-linter
4. **Configure IDE** - set up pylint with the plugin loaded

## Performance

The plugin is designed to be efficient:

- **Single analysis**: Import graph built once for both pylint and import-linter
- **Caching**: Full support for import-linter's caching system
- **Lazy evaluation**: Contracts only checked when necessary
- **Memory efficient**: Minimal memory overhead

## Contributing

The plugin is part of the pylint-import-linter project. See [DEVELOPMENT.md](DEVELOPMENT.md) for contribution guidelines.

## License

BSD 2-Clause License - same as the main project.
