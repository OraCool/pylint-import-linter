Changelog
=========

1.1.6 (2025-07-18)
------------------

**Major Architectural Improvement and Pylint Plugin Enhancement**

**Plugin Architecture Modernization:**
- **Modular Package Structure**: Refactored pylint plugin from single module to clean package architecture
- **Improved Maintainability**: Split functionality across specialized modules (checker, config, contract_checker, module_resolver, violation_matcher)
- **Enhanced Separation of Concerns**: Each module now handles specific responsibilities for better code organization

**New Features and Improvements:**
- **Enhanced Module Resolution**: Improved file path to module name conversion with better PYTHONPATH support
- **Optimized Single-File Analysis**: Fast mode for analyzing individual files without full graph building
- **Better Error Handling**: More robust error reporting and debugging capabilities
- **Comprehensive Configuration**: All import-linter CLI options now available as pylint plugin options

**Technical Enhancements:**
- **Backward Compatibility**: Maintained API compatibility for existing users
- **Type Safety**: Improved type annotations throughout the codebase
- **Performance Optimization**: Better caching and analysis strategies for large codebases
- **Debug Mode**: Enhanced debugging capabilities with verbose output options

**Quality Assurance:**
- ✅ Core functionality verified and working
- ✅ Plugin loads correctly with pylint
- ✅ All configuration options functional
- ✅ Contract analysis working properly
- ✅ Package builds and installs successfully

This release significantly improves the plugin's architecture while maintaining full compatibility, making it more maintainable and extensible for future development.

1.1.5 (2025-07-17)
------------------

**Complete Tox Environment Fix and Final Release**

**Tox Configuration Updates:**
- **Updated all tox.ini dependencies**: Now properly uses the upgraded dependency versions from v1.1.4
- **Verified CI Compatibility**: Ensures tox check environment works correctly on all Python versions
- **Fixed Version Synchronization**: Package version properly aligned across all files

**Quality Assurance:**
- ✅ All 389 tests pass with updated tooling
- ✅ Tox environments work correctly on Python 3.9-3.13
- ✅ CI/CD pipeline fully functional
- ✅ Plugin functionality verified in production

This is the final release that combines all critical bug fixes from v1.1.3 with the modernized development environment from v1.1.4, ensuring complete compatibility and reliability.

1.1.4 (2025-07-17)
------------------

**Development Environment Modernization and CI Fixes**

**Dependency Upgrades:**
- **flake8**: Upgraded from 4.0.1 → 7.3.0 (fixes Python 3.10 CI compatibility issues)
- **black**: Upgraded from 22.3.0 → 25.1.0 (latest code formatting improvements)
- **mypy**: Upgraded from 0.730 → 1.17.0 (enhanced type checking and strictness)
- **pytest**: Upgraded from 7.4.0 → 8.4.1 (latest testing framework features)
- **pytest-cov**: Upgraded from 4.1.0 → 6.2.1 (improved coverage reporting)
- **coverage**: Upgraded from 6.3.1 → 7.9.2 (better performance and features)
- **PyYAML**: Updated from 6.0.1 → 6.0.2 (latest stable version)

**CI/CD Improvements:**
- **Fixed Python 3.10 CI Failures**: Resolved tox check environment failures caused by flake8/importlib-metadata compatibility issues
- **Enhanced Quality Assurance**: All 389 tests pass with updated dependencies
- **Improved Development Experience**: Modern tool versions provide better error messages and performance

**Quality Validation:**
- ✅ All formatting checks pass with Black 25.1.0
- ✅ All linting passes with flake8 7.3.0 
- ✅ All type checks pass with mypy 1.17.0
- ✅ All tests pass with pytest 8.4.1
- ✅ Coverage reporting works correctly

1.1.3 (2025-07-17)
------------------

**Critical Bug Fix: Remove Hardcoded Domain Names from Pylint Plugin**

**Major Bug Fixes:**
- **Removed Hardcoded Values**: Eliminated hardcoded "domains.document" and "domains.billing" strings from pylint plugin that prevented it from working with other domain structures
- **Dynamic Module Path Resolution**: Implemented proper module path resolution based on target folder configuration instead of hardcoded prefixes
- **Configuration-Driven Contract Matching**: Plugin now properly uses contracts from .importlinter configuration files instead of hardcoded patterns
- **Contract-Based Violation Detection**: Implemented proper contract violation matching using import-linter's contract system with forbidden and independence contract support
- **Wildcard Pattern Support**: Added support for single (*) and recursive (**) wildcard patterns in contract matching

**Technical Improvements:**
- **Generic Plugin Architecture**: Plugin now works with any domain structure defined in configuration files, not just hardcoded "domains.*" patterns
- **Proper Import Resolution**: Fixed module path calculation to respect Python import structure and target folder configuration
- **Line-Specific Error Reporting**: Violations are now reported at the exact import lines with proper pylint message IDs
- **Enhanced Debug Output**: Added comprehensive debug logging for troubleshooting contract matching and module resolution

**Verification:**
- Plugin now correctly detects violations: went from always reporting 10.00/10 (false negative) to properly flagging violations (1.67/10 for test file)
- Successfully tested with document domain violations: 3 violations detected on lines 4, 7, and 8
- Plugin works with any import-linter configuration, not just the hardcoded example domains

1.1.2 (2025-07-17)
------------------

**Enhanced Documentation and Wildcard Pattern Support**

**New Features:**
- **Comprehensive Wildcard Documentation**: Detailed explanations of `*` (single) vs `**` (recursive) wildcard patterns
- **Enhanced Usage Examples**: Complete guide with practical examples for `ignore_imports` configuration
- **Improved Contract Types Documentation**: Expanded wildcards section with real-world use cases
- **Author Recognition**: Updated AUTHORS.rst and LICENSE to properly recognize all contributors

**Documentation Improvements:**
- **Wildcard Pattern Guide**: Clear distinction between single and recursive wildcards
- **Practical Examples**: Real-world scenarios for test utilities, cross-domain imports, and migration patterns
- **Configuration Examples**: Complete .importlinter configuration examples with wildcard patterns
- **Command Line Testing**: Instructions for testing wildcard patterns with verbose output

**Bug Fixes:**
- **License Attribution**: Added proper copyright notice for all contributors
- **Documentation Cross-References**: Improved linking between documentation sections

1.1.1 (2025-07-17)
------------------

**CI/CD and Build Fixes**

**Bug Fixes:**
- **CI/CD Pipeline**: Fixed Black code formatting issues in pylint_plugin.py
- **Type Dependencies**: Added types-PyYAML dependency for proper type checking
- **Package Building**: Resolved build issues and dependency conflicts
- **Quality Checks**: All linting, formatting, and type checking now pass

**Improvements:**
- **Code Quality**: Consistent code formatting with Black
- **Type Safety**: Complete type checking with proper stub dependencies
- **Build Process**: Streamlined build and release workflow
- **Documentation**: Updated with proper version references

1.1.0 (2025-07-17)
------------------

**Enhanced Debug and Verbose Features**

**New Features:**
- **Debug Mode**: Enhanced error reporting with stack traces and detailed diagnostic information
- **Verbose Mode**: Real-time analysis progress with contract details and timing information
- **Single File Analysis**: Targeted debugging support for specific files with full diagnostic mode
- **VS Code Integration**: Comprehensive tasks, launch configurations, and debug settings
- **Parameter Unification**: Unified parameter names between CLI and plugin (--import-linter- prefix)
- **Performance Monitoring**: Timing information and cache management options
- **Enhanced Error Handling**: Detailed diagnostic messages with file paths and line numbers

**Improvements:**
- **Parameter Consistency**: All plugin parameters now use consistent --import-linter- prefix
- **Documentation**: Comprehensive documentation with debug mode examples and VS Code setup
- **Error Messages**: Enhanced error reporting with full context and stack traces
- **Developer Experience**: Improved debugging workflow with VS Code integration

**Usage Examples:**
- Full debug mode: `--import-linter-debug=yes --import-linter-verbose=yes --import-linter-show-timings=yes`
- Single file analysis with debug information
- VS Code tasks for quick debugging and analysis
- Enhanced error reporting for configuration issues

1.0.0 (2025-07-17)
------------------

**Initial Release of pylint-import-linter**

This is a new project that extends the original import-linter with enhanced pylint integration and debugging capabilities.

**New Features:**
- **Enhanced Pylint Plugin**: Unified parameter interface with --import-linter- prefix
- **Debug Mode**: Detailed error reporting with stack traces and diagnostic information
- **Verbose Mode**: Real-time analysis progress with contract details and timing
- **Single File Analysis**: Targeted debugging support for specific files
- **VS Code Integration**: Comprehensive tasks, launch configurations, and settings
- **Parameter Unification**: Consistent interface between CLI and plugin
- **Performance Monitoring**: Timing information and cache management
- **Enhanced Error Handling**: Detailed diagnostic messages with file paths and line numbers

**Based on import-linter 2.3 with additional features:**

Original import-linter Changelog
=================================

The following versions are from the original import-linter project that this tool extends:

2.3 (2025-03-11) - Original import-linter
-----------------------------------------

* Add as_packages field to forbidden contracts.
* Improve performance of parsing module / import expressions.

2.2 (2025-02-07)
----------------

* Add support for wildcards in layers contract containers.
* Improve performance of `helpers.pop_imports`.

2.1 (2024-10-8)
---------------

* Add support for wildcards in forbidden and independence contracts.
* Formally support Python 3.13.
* Drop support for Python 3.8.

2.0 (2024-1-9)
--------------

* Add support for non-independent sibling modules in layer contracts.
* In `importlinter.contracts.layers`, `Layer` and `LayerField` 
  have changed their API slightly. This could impact custom
  contract types depending on these classes. 

1.12.1 (2023-10-30)
-------------------

* Add ability to exclude imports made in type checking guards via ``exclude_type_checking_imports`` setting.
* Update to Grimp 3.1.

1.12.0 (2023-09-24)
-------------------

* Officially support Python 3.12.
* Fix error when using `click` version 6.0 and 7.0 (#191).
* Allow extra whitespace around the module names in import expressions.
* Ignore blank lines in multiple value fields.
* Fix bug with allow_indirect_imports in forbidden contracts.
  Prior to this fix, forbidden contracts with allow_indirect_imports
  only checked imports between the source/forbidden modules specified,
  not the descendants of those modules.

1.11.1 (2023-08-21)
-------------------

* Fix bug that was preventing sibling layers being used in a containerless contract.

1.11.0 (2023-08-18)
-------------------

* Update to Grimp 3.0.

1.11b1 (2023-08-17)
-------------------

* Update to Grimp 3.0b3.
* Use Grimp's find_illegal_dependencies_for_layers method in independence contracts.
* Add ability to define independent siblings in layers contracts.

1.10.0 (2023-07-06)
-------------------

* Recursive wildcard support for ignored imports.
* Drop support for Python 3.7.
* Use grimp.ImportGraph instead of importlinter.domain.ports.graph.ImportGraph.
* Use Grimp's find_illegal_dependencies_for_layers method in layers contracts.

1.9.0 (2023-05-13)
------------------

* Update to Grimp 2.4.
* Forbidden contracts: when include_external_packages is true, error if an external subpackage is
  a forbidden module.

1.8.0 (2023-03-03)
------------------

* Add caching.

1.7.0 (2023-01-27)
------------------

* Switch from optional dependency of ``toml`` to required dependency of ``tomli`` for Python versions < 3.11.
* Use DetailedImport type hinting made available in Grimp 2.2.
* Allow limiting by contract.

1.6.0 (2022-12-7)
-----------------

* Add exhaustiveness option to layers contracts.

1.5.0 (2022-12-2)
-----------------

* Officially support Python 3.11.

1.4.0 (2022-10-04)
------------------

* Include py.typed file in package data to support type checking
* Remove upper bounds on dependencies. This allows usage of Grimp 2.0, which should significantly speed up checking of
  layers contracts.
* Add --verbose flag to lint-imports command.
* Improve algorithm for independence contracts, in the following ways:
    - It is significantly faster.
    - As with layers contracts, reports of illegal indirect imports reports now include multiple start
      and end points (if they exist).
    - Illegal indirect imports that are via other modules listed in the contract are no longer listed.

1.3.0 (2022-08-22)
------------------

* Add Python API for reading configuration.
* Add support for namespace packages.

1.2.7 (2022-04-04)
------------------

* Officially support Python 3.10.
* Drop support for Python 3.6.
* Add support for default Field values.
* Add EnumField.
* Support warnings in contract checks.
* Add unmatched_ignore_imports_alerting option for each contract.
* Add command line argument for showing timings.

1.2.6 (2021-09-24)
------------------

* Fix bug with ignoring external imports that occur multiple times in the same module.

1.2.5 (2021-09-21)
------------------

* Wildcard support for ignored imports.
* Convert TOML booleans to strings in UserOptions, to make consistent with INI file parsing.

1.2.4 (2021-08-09)
------------------

* Fix TOML installation bug.

1.2.3 (2021-07-29)
------------------

* Add support for TOML configuration files.

1.2.2 (2021-07-13)
------------------

* Support Click version 8.

1.2.1 (2021-01-22)
------------------

* Add allow_indirect_imports to Forbidden Contract type
* Upgrade Grimp to 1.2.3.
* Officially support Python 3.9.

1.2 (2020-09-23)
----------------

* Upgrade Grimp to 1.2.2.
* Add SetField.
* Use a SetField for ignore_imports options.
* Add support for non `\w` characters in import exceptions.

1.1 (2020-06-29)
----------------

* Bring 1.1 out of beta.

1.1b2 (2019-11-27)
------------------

* Update to Grimp v1.2, significantly increasing speed of building the graph.

1.1b1 (2019-11-24)
------------------

* Provide debug mode.
* Allow contracts to mutate the graph without affecting other contracts.
* Update to Grimp v1.1.
* Change the rendering of broken layers contracts by combining any shared chain beginning or endings.
* Speed up and make more comprehensive the algorithm for finding illegal chains in layer contracts. Prior to this,
  layers contracts used Grimp's find_shortest_chains method for each pairing of layers. This found the shortest chain
  between each pair of modules across the two layers. The algorithm was very slow and not comprehensive. With this
  release, for each pair of layers, a copy of the graph is made. All other layers are removed from the graph, any
  direct imports between the two layers are stored. Next, the two layers in question are 'squashed', the shortest
  chain is repeatedly popped from the graph until no more chains remain. This results in more comprehensive results,
  and at significantly increased speed.

1.0 (2019-17-10)
----------------

* Officially support Python 3.8.

1.0b5 (2019-10-05)
------------------

* Allow multiple root packages.
* Make containers optional in Layers contracts.

1.0b4 (2019-07-03)
------------------

* Add https://pre-commit.com configuration.
* Use find_shortest_chains instead of find_shortest_chain on the Grimp import graph.
* Add Forbidden Modules contract type.

1.0b3 (2019-05-15)
------------------

* Update to Grimp v1.0b10, fixing Windows incompatibility.

1.0b2 (2019-04-16)
------------------

* Update to Grimp v1.0b9, fixing error with using importlib.util.find_spec.

1.0b1 (2019-04-06)
------------------

* Improve error handling of modules/containers not in the graph.
* Return the exit code correctly.
* Run lint-imports on Import Linter itself.
* Allow single values in ListField.

1.0a3 (2019-03-27)
------------------

* Include the ability to build the graph with external packages.

1.0a2 (2019-03-26)
------------------

* First usable alpha release.

1.0a1 (2019-01-27)
------------------

* Release blank project on PyPI.
