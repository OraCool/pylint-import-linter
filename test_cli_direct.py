#!/usr/bin/env python3
"""Test script to verify CLI functionality directly"""

import sys
import os

# Add src to path so we can import directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from importlinter.cli import lint_imports_command

if __name__ == "__main__":
    # Test the function with folder targeting
    result = lint_imports_command(
        config=None,
        contract=(),
        cache_dir=None,
        no_cache=False,
        target_folders="src",
        exclude_folders=None,
        debug=True,
        show_timings=False,
        verbose=True,
    )
    print(f"CLI function result: {result}")
