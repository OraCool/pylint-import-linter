#!/usr/bin/env bash
# Demo script for folder-specific targeting with the Import Linter Pylint plugin
#
# This script demonstrates various folder targeting scenarios using the
# example domains structure with Domain-Driven Design architecture.

set -e

echo "========================================"
echo "Import Linter Pylint Plugin Demo"
echo "========================================"
echo

# Change to the project root
cd "$(dirname "$0")"

echo "📁 Example structure:"
echo "example/domains/"
echo "├── document/           # Document domain"
echo "├── billing/           # Billing domain"  
echo "├── org_and_user/      # User management"
echo "└── pd_common/         # Shared utilities"
echo

echo "🔧 Configuration: example/importlinter.ini"
echo "- Domain boundaries (forbidden imports)"
echo "- Domain independence contracts"
echo "- Layered architecture enforcement"
echo

echo "========================================"
echo "1. Full Analysis (All Domains)"
echo "========================================"
echo "Running: pylint --load-plugins=importlinter.pylint_plugin example/domains/"
echo

uv run pylint --load-plugins=importlinter.pylint_plugin \
     --import-linter-config=example/importlinter.ini \
     example/domains/ || echo "❌ Contract violations found (expected)"

echo
echo "========================================"
echo "2. Target Document Domain Only"
echo "========================================"
echo "Running: pylint --import-linter-target-folders=example/domains/document"
echo

uv run pylint --load-plugins=importlinter.pylint_plugin \
     --import-linter-config=example/importlinter.ini \
     --import-linter-target-folders=example/domains/document \
     example/domains/ || echo "❌ Contract violations found (targeting document domain)"

echo
echo "========================================"
echo "3. Exclude Infrastructure Folders"
echo "========================================"
echo "Running: pylint --import-linter-exclude-folders=example/domains/pd_common"
echo

uv run pylint --load-plugins=importlinter.pylint_plugin \
     --import-linter-config=example/importlinter.ini \
     --import-linter-exclude-folders=example/domains/pd_common \
     example/domains/ || echo "❌ Contract violations found (excluding shared utilities)"

echo
echo "========================================"
echo "4. Target Business Domains Only"  
echo "========================================"
echo "Running: pylint --import-linter-target-folders=example/domains/document,example/domains/billing"
echo

uv run pylint --load-plugins=importlinter.pylint_plugin \
     --import-linter-config=example/importlinter.ini \
     --import-linter-target-folders=example/domains/document,example/domains/billing \
     example/domains/ || echo "❌ Contract violations found (targeting business domains)"

echo
echo "========================================"
echo "5. No Matching Folders (Should Skip)"
echo "========================================"
echo "Running: pylint --import-linter-target-folders=nonexistent"
echo

uv run pylint --load-plugins=importlinter.pylint_plugin \
     --import-linter-config=example/importlinter.ini \
     --import-linter-target-folders=nonexistent \
     example/domains/ && echo "✅ No import-linter output (no matching folders)"

echo
echo "========================================"
echo "✨ Demo Complete!"
echo "========================================"
echo
echo "Key observations:"
echo "1. Full analysis detects domain boundary violations"
echo "2. Targeting specific folders shows '(targeting folders: ...)' in output"
echo "3. Excluding folders shows '(excluding folders: ...)' in output"  
echo "4. No matching folders = no import-linter analysis"
echo "5. Pylint warnings are shown regardless of folder targeting"
echo
echo "Real-world use cases:"
echo "• Legacy migration: Start with new modules, expand gradually"
echo "• Microservices: Different rules for different services"
echo "• Performance: Focus on critical components only"
echo "• Development: Exclude test/documentation folders"
