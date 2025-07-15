# Development Guide

This project uses [uv](https://github.com/astral-sh/uv) for fast Python package management.

## Quick Start

### Prerequisites

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup Development Environment

1. Clone the repository
2. Install dependencies:
```bash
uv sync --dev
```

3. Activate the virtual environment:
```bash
source .venv/bin/activate
```

## Available Commands

We provide a development script for common tasks:

```bash
# Install all dependencies
./dev.sh install

# Run import linter
./dev.sh lint

# Run tests
./dev.sh test

# Run pylint
./dev.sh pylint src/

# Format code with black
./dev.sh black src/

# Type check with mypy
./dev.sh mypy src/

# Show how to activate shell
./dev.sh shell
```

## Direct uv Commands

You can also use uv directly:

```bash
# Install dependencies
uv sync --dev

# Run scripts
uv run lint-imports
uv run pytest
uv run pylint src/
uv run black src/
uv run mypy src/

# Add new dependencies
uv add package-name

# Add development dependencies
uv add --dev package-name

# Update lock file
uv lock

# Create/update virtual environment
uv venv
```

## Why uv?

- **Fast**: Much faster than pip and Poetry
- **Reliable**: Uses a lockfile for reproducible builds
- **Simple**: Easy to use and understand
- **Modern**: Built for the current Python ecosystem

## Migration from Poetry

This project was migrated from Poetry to uv. The main changes:

- Removed `poetry.lock` and added `uv.lock`
- Added `[tool.uv]` section in `pyproject.toml`
- Created `dev.sh` helper script for common tasks
- All dependencies are now managed through uv

## Project Structure

```
├── src/importlinter/          # Main package source
├── tests/                     # Test files
├── .venv/                     # Virtual environment (created by uv)
├── uv.lock                    # Dependency lock file
├── pyproject.toml             # Project configuration
└── dev.sh                     # Development helper script
```
