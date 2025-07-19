# VS Code Configuration for pylint-import-linter

This document describes the VS Code configuration for the pylint-import-linter project.

## Quick Start

1. Open the project in VS Code
2. Use `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac) to open the Command Palette
3. Type "Tasks: Run Task" and select it
4. Choose one of the import linter tasks:
   - **Debug Import Violations (Full Debug Mode)** - Recommended for troubleshooting
   - **Check Import Violations (Current File)** - Quick check for current file
   - **Check Import Violations (Verbose)** - Shows detailed analysis progress

## Available Tasks

### Debug Tasks
- **Debug Import Violations (Full Debug Mode)**: Full diagnostic mode with debug, verbose, and timing information
- **Debug Import Violations (Debug Only)**: Debug mode with stack traces for errors

### Standard Tasks
- **Check Import Violations (Current File)**: Basic violation check for the current file
- **Check Import Violations (Verbose)**: Shows detailed analysis progress
- **Check Import Violations (Verbose + Timings)**: Verbose output with performance timings
- **Check Import Violations (Fast Mode)**: Uses cache for faster analysis
- **Check Import Violations (No Cache)**: Forces fresh analysis without cache
- **Check Import Violations (All Folders)**: Analyzes all domain folders

## Debug Configurations

### Launch Configurations
1. **Debug Import Linter**: Debug the CLI directly
2. **Debug Pylint Plugin**: Debug the pylint plugin
3. **Debug Pylint Plugin (Debug Mode)**: Debug the plugin with full diagnostic mode

### How to Debug
1. Open the file you want to debug
2. Press `F5` or go to Run > Start Debugging
3. Select the appropriate debug configuration
4. Set breakpoints in the code as needed

## Settings Overview

The project is configured with:

- **Automatic Linting**: Pylint runs automatically on save
- **Import Linter Integration**: Plugin loads automatically with proper configuration
- **Problem Reporting**: Import violations show up in VS Code's Problems panel
- **Enhanced Visibility**: Rulers, breadcrumbs, and minimap enabled
- **Terminal Integration**: PYTHONPATH set correctly for terminal commands

## Task Usage Examples

### For Development
```bash
# Quick check while coding
Tasks: Run Task > Check Import Violations (Current File)

# Detailed analysis
Tasks: Run Task > Check Import Violations (Verbose)
```

### For Debugging
```bash
# Full diagnostic information
Tasks: Run Task > Debug Import Violations (Full Debug Mode)

# Debug configuration errors
Tasks: Run Task > Debug Import Violations (Debug Only)
```

### For CI/CD Testing
```bash
# Analyze all domains
Tasks: Run Task > Check Import Violations (All Folders)

# Performance testing
Tasks: Run Task > Check Import Violations (Verbose + Timings)
```

## Problem Matcher

The tasks use custom problem matchers to:
- Parse pylint output and show violations in the Problems panel
- Enable quick navigation to violation locations
- Display error codes and messages clearly

## Keyboard Shortcuts

- `F5`: Start debugging
- `Ctrl+Shift+P`: Command palette
- `Ctrl+Shift+B`: Run build task
- `Ctrl+\``: Toggle terminal

## Tips

1. **Use Debug Mode**: When troubleshooting violations, always use "Debug Import Violations (Full Debug Mode)"
2. **Check Problems Panel**: All violations appear in the Problems panel (View > Problems)
3. **Cache Management**: Use "No Cache" tasks when configuration changes
4. **Performance**: Use "Fast Mode" for quick checks during development

## Configuration Files

- `.vscode/tasks.json`: Task definitions
- `.vscode/launch.json`: Debug configurations  
- `.vscode/settings.json`: Editor and linting settings
- `.vscode/extensions.json`: Recommended extensions

## Troubleshooting

### Environment Setup
For best results, set up PYTHONPATH before using VS Code tasks:
```bash
export PYTHONPATH=$PWD/src:$PWD/example:$PYTHONPATH
```

### Common Issues
1. **"Module not found"**: Ensure PYTHONPATH includes src/ and example/ directories
2. **"Config not found"**: Verify config path in task arguments
3. **"No violations shown"**: Check if correct folders are targeted
4. **Module resolution errors**: Set PYTHONPATH environment variable

### Debug Steps
1. Set PYTHONPATH: `export PYTHONPATH=$PWD/src:$PWD/example:$PYTHONPATH`
2. Run "Debug Import Violations (Full Debug Mode)" task
3. Check the terminal output for detailed error messages
4. Verify configuration file paths and content
5. Use the debugger to step through plugin code if needed
