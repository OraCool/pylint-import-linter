# Release Preparation Checklist for v1.1.0

## Version Update Status ✅

- [x] Updated version in `pyproject.toml` to `1.1.0`
- [x] Updated `__version__` in `src/importlinter/__init__.py` to `1.1.0`
- [x] Updated `CHANGELOG.rst` with new version entry
- [x] Added comprehensive release notes for v1.1.0

## Pre-Release Checklist

### 1. Code Quality Checks
- [ ] Run linting: `uv run pylint --load-plugins=importlinter.pylint_plugin src/`
- [ ] Run tests: `uv run pytest`
- [ ] Run import-linter on itself: `uv run lint-imports`
- [ ] Test plugin functionality: `uv run pylint --load-plugins=importlinter.pylint_plugin --import-linter-debug=yes --import-linter-verbose=yes example/domains/document/document_operations_violations.py`

### 2. Documentation Verification
- [ ] Verify all documentation files are updated
- [ ] Check README.rst renders correctly
- [ ] Verify CHANGELOG.rst is properly formatted
- [ ] Test VS Code configuration examples

### 3. Package Building
- [ ] Clean build directory: `rm -rf dist/ build/`
- [ ] Build package: `uv build`
- [ ] Verify package contents: `tar -tzf dist/pylint-import-linter-1.1.0.tar.gz`

### 4. Testing
- [ ] Install in clean environment: `pip install dist/pylint-import-linter-1.1.0.tar.gz`
- [ ] Test basic functionality
- [ ] Test debug mode features
- [ ] Test VS Code integration

### 5. Git Operations
- [ ] Commit all changes: `git add . && git commit -m "Release v1.1.0"`
- [ ] Create release tag: `git tag -a v1.1.0 -m "Release v1.1.0"`
- [ ] Push changes: `git push origin master`
- [ ] Push tags: `git push origin v1.1.0`

### 6. Publishing
- [ ] Upload to PyPI: `uv publish`
- [ ] Verify package on PyPI: https://pypi.org/project/pylint-import-linter/
- [ ] Test installation from PyPI: `pip install pylint-import-linter==1.1.0`

## Release Commands

```bash
# 1. Clean and test
rm -rf dist/ build/
uv run pytest
uv run pylint --load-plugins=importlinter.pylint_plugin src/

# 2. Build package
uv build

# 3. Test installation
pip install dist/pylint-import-linter-1.1.0.tar.gz

# 4. Git operations
git add .
git commit -m "Release v1.1.0: Enhanced debug and verbose features"
git tag -a v1.1.0 -m "Release v1.1.0: Enhanced debug and verbose features"
git push origin master
git push origin v1.1.0

# 5. Publish to PyPI
uv publish
```

## New Features in v1.1.0

### Debug Mode Enhancements
- Stack traces for configuration errors
- Detailed error messages with file paths and line numbers
- Cache usage information
- Contract analysis progress

### Verbose Mode Features
- Real-time analysis progress ("Analyzing contracts in config.ini")
- Contract details ("Found 3 contracts", "Contract 1: Document domain boundaries")
- Import chain analysis ("Searching for import chains from A to B")
- Timing information for each operation
- Final results summary

### VS Code Integration
- Comprehensive task configurations
- Debug launch configurations
- Enhanced settings for automatic linting
- Problem matcher for error reporting

### Parameter Unification
- Consistent `--import-linter-` prefix for all plugin parameters
- Boolean parameters use `=yes/no` format
- Full compatibility with CLI parameter names

### Single File Analysis
- Targeted debugging for specific files
- Full diagnostic mode for troubleshooting
- Performance optimization for development workflow

## Breaking Changes
None. This release is fully backward compatible.

## Migration Guide
No migration required. All existing configurations continue to work.

## Testing Commands for Release

```bash
# Test debug mode
uv run pylint --load-plugins=importlinter.pylint_plugin \
             --import-linter-config=example/importlinter.ini \
             --import-linter-debug=yes \
             --import-linter-verbose=yes \
             --import-linter-show-timings=yes \
             example/domains/document/document_operations_violations.py

# Test verbose mode
uv run pylint --load-plugins=importlinter.pylint_plugin \
             --import-linter-config=example/importlinter.ini \
             --import-linter-verbose=yes \
             example/domains/

# Test single file analysis
uv run pylint --load-plugins=importlinter.pylint_plugin \
             --import-linter-config=example/importlinter.ini \
             --import-linter-target-folders=example/domains \
             --disable=all \
             --enable=import-boundary-violation,import-independence-violation,import-layer-violation,import-contract-violation,import-contract-error \
             example/domains/document/document_operations_violations.py
```
