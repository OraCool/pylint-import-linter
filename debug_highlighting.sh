#!/usr/bin/env bash
# Diagnostic script for pylint import-linter highlighting issues

set -e

echo "🔧 Diagnosing pylint import-linter highlighting issues..."
echo ""

# Check if we're in VS Code integrated terminal
if [ -n "$VSCODE_PID" ]; then
    echo "✅ Running in VS Code integrated terminal"
else
    echo "⚠️  Not running in VS Code integrated terminal"
    echo "   Try running this from VS Code's integrated terminal"
fi
echo ""

# Check Python environment
echo "🐍 Python Environment:"
which python
python --version
echo ""

# Check pylint availability and plugins
echo "🔍 Pylint Configuration:"
uv run pylint --version
echo ""

# Test plugin loading
echo "📦 Testing Plugin Loading:"
uv run pylint --load-plugins=importlinter.pylint_plugin --help | head -5
echo ""

# Test on the specific file
echo "🎯 Testing Import Violations Detection:"
FILE="example/domains/document/documents_core.py"
echo "File: $FILE"
echo ""

echo "📊 JSON Output (for IDE integration):"
uv run pylint \
    --load-plugins=importlinter.pylint_plugin \
    --import-linter-config=example/importlinter.ini \
    --import-linter-target-folders=example/domains \
    --output-format=json \
    --disable=all \
    --enable=import-boundary-violation,import-independence-violation \
    "$FILE" || echo "Exit code: $?"
echo ""

echo "💡 Troubleshooting Steps:"
echo "1. Restart VS Code completely"
echo "2. Check Python interpreter is set to project .venv"
echo "3. Ensure Python extension is installed and enabled"
echo "4. Check VS Code settings for pylint configuration"
echo "5. Try running the 'Python: Clear Cache and Reload Window' command"
echo ""

echo "🔧 VS Code Commands to try:"
echo "- Ctrl/Cmd + Shift + P → 'Python: Select Interpreter'"
echo "- Ctrl/Cmd + Shift + P → 'Python: Clear Cache and Reload Window'"
echo "- Ctrl/Cmd + Shift + P → 'Python: Refresh Linting'"
echo "- Check Problems panel (Ctrl/Cmd + Shift + M)"
