#!/usr/bin/env bash
# Test script for the pylint import-linter plugin

set -e

echo "🔧 Testing pylint import-linter plugin..."
echo ""

# Test 1: Run on a clean file (should pass)
echo "✅ Test 1: Clean file (should pass)"
uv run pylint --load-plugins=importlinter.pylint_plugin --disable=all --enable=import-contract-violation,import-contract-error src/importlinter/__init__.py
echo ""

# Test 2: Show plugin options
echo "📋 Test 2: Plugin options available"
uv run pylint --load-plugins=importlinter.pylint_plugin --help | grep -A5 "import-linter"
echo ""

# Test 3: Show plugin messages
echo "💬 Test 3: Plugin messages"
uv run pylint --load-plugins=importlinter.pylint_plugin --help-msg=import-contract-violation
uv run pylint --load-plugins=importlinter.pylint_plugin --help-msg=import-contract-error
echo ""

echo "🎉 All tests completed!"
echo ""
echo "To use the plugin in your projects:"
echo "  pylint --load-plugins=importlinter.pylint_plugin [files...]"
echo ""
echo "Or add to your pylintrc:"
echo "  [MASTER]"
echo "  load-plugins = importlinter.pylint_plugin"
