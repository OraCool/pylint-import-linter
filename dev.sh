#!/usr/bin/env bash
# Development helper script for uv

set -e

export PATH="$HOME/.local/bin:$PATH"

case "$1" in
    "install")
        echo "Installing dependencies with uv..."
        uv sync --dev
        ;;
    "test")
        echo "Running tests with pytest..."
        uv run pytest "${@:2}"
        ;;
    "lint")
        echo "Running import linter..."
        uv run lint-imports "${@:2}"
        ;;
    "pylint")
        echo "Running pylint..."
        uv run pylint "${@:2}"
        ;;
    "plugin")
        echo "Testing pylint plugin..."
        uv run pylint --load-plugins=importlinter.pylint_plugin "${@:2}"
        ;;
    "black")
        echo "Running black formatter..."
        uv run black "${@:2}"
        ;;
    "mypy")
        echo "Running mypy type checker..."
        uv run mypy "${@:2}"
        ;;
    "shell")
        echo "Activating virtual environment..."
        echo "Run: source .venv/bin/activate"
        ;;
    *)
        echo "Usage: $0 {install|test|lint|pylint|plugin|black|mypy|shell} [args...]"
        echo ""
        echo "Commands:"
        echo "  install  - Install all dependencies"
        echo "  test     - Run pytest tests"
        echo "  lint     - Run import linter"
        echo "  pylint   - Run pylint"
        echo "  plugin   - Test pylint plugin"
        echo "  black    - Run black formatter"
        echo "  mypy     - Run mypy type checker"
        echo "  shell    - Show command to activate venv"
        exit 1
        ;;
esac
