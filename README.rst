===============================
Pylint Import Linter (Enhanced)
===============================

.. image:: https://img.shields.io/pypi/v/pylint-import-linter.svg
    :target: https://pypi.org/project/pylint-import-linter

.. image:: https://img.shields.io/pypi/pyversions/pylint-import-linter.svg
    :alt: Python versions
    :target: https://pypi.org/project/pylint-import-linter/

**Enhanced Import Linter with Advanced Pylint Integration**

This is an enhanced version of Import Linter that extends the original `import-linter <https://import-linter.readthedocs.io/>`_ with advanced pylint integration, debug capabilities, and developer tools.

**Key Enhancements:**
- **Advanced Pylint Plugin**: Enhanced integration with unified parameter interface
- **Debug Mode**: Detailed error reporting with stack traces
- **Verbose Mode**: Real-time analysis progress and timing information
- **VS Code Integration**: Comprehensive tasks, launch configurations, and settings
- **Single File Analysis**: Targeted debugging support
- **Parameter Unification**: Consistent interface between CLI and plugin

Import Linter allows you to define and enforce rules for the imports within and between Python packages.

* Free software: BSD license
* Based on original import-linter with significant enhancements
* **NEW**: Enhanced Pylint plugin with debug capabilities!

## Features

- **Command Line Tool**: Standalone import linting (compatible with original import-linter)
- **Enhanced Pylint Plugin**: Advanced integration with debug and verbose modes
- **Debug Mode**: Stack traces, detailed error messages, and diagnostic information
- **Verbose Mode**: Real-time analysis progress and timing information
- **Single File Analysis**: Targeted debugging for specific files
- **VS Code Integration**: Comprehensive tasks, launch configurations, and settings
- **Folder-Specific Targeting**: Configure checking for particular folders only
- **Multiple Contract Types**: layers, forbidden imports, independence
- **Parameter Unification**: Consistent interface between CLI and plugin
- **Flexible Configuration**: TOML and INI support
- **CI/CD Ready**: Perfect for continuous integration

## Relationship to Original Import-Linter

This project extends the original `import-linter <https://import-linter.readthedocs.io/>`_ (version 2.3) with significant enhancements:

**What's New in This Version:**
- Enhanced pylint plugin with unified parameter interface
- Debug mode with stack traces and detailed error reporting
- Verbose mode with real-time analysis progress
- Single file analysis capabilities
- Comprehensive VS Code integration
- Parameter consistency between CLI and plugin
- Performance monitoring and timing information

**Compatibility:**
- Fully compatible with existing import-linter configuration files
- All original CLI commands work as before
- Seamless migration from original import-linter

## Installation

Install the enhanced Pylint Import Linter::

    pip install pylint-import-linter

## Quick Start

### Standalone Usage
Run the standalone command line tool::

    lint-imports

### Pylint Plugin Integration

Import Linter can be integrated into your pylint workflow for seamless architecture checking.

**Command Line Usage:**

.. code-block:: bash

    # Load the plugin and run pylint
    pylint --load-plugins=importlinter.pylint_plugin src/

**Permanent Integration in pyproject.toml:**

.. code-block:: toml

    [tool.pylint.main]
    load-plugins = ["importlinter.pylint_plugin"]

**Permanent Integration in .pylintrc:**

.. code-block:: ini

    [MAIN]
    load-plugins=importlinter.pylint_plugin

**Folder-Specific Checking:**

Target specific folders for large codebases or gradual adoption:

.. code-block:: bash

    # Only check core modules
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=src/core,src/api \
           src/

    # Exclude test and documentation folders
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-exclude-folders=tests,docs \
           src/

**Debug and Verbose Mode:**

For troubleshooting contract violations, use debug and verbose modes:

.. code-block:: bash

    # Full debug mode with all diagnostic information
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-config=.importlinter \
           --import-linter-debug=yes \
           --import-linter-verbose=yes \
           --import-linter-show-timings=yes \
           --disable=all \
           --enable=import-boundary-violation,import-independence-violation,import-layer-violation,import-contract-violation,import-contract-error \
           src/

    # Verbose mode shows detailed analysis progress
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-verbose=yes \
           src/

**Debug Mode Features:**

- Stack traces for configuration errors
- Detailed error messages with file paths and line numbers
- Cache usage information
- Contract analysis progress

**Verbose Mode Features:**

- Real-time analysis progress
- Contract details and import chain analysis
- Timing information for each operation
- Final results summary

**IDE Integration:**
Most IDEs that support pylint will automatically pick up the plugin when configured in your project settings.

See the `documentation <https://import-linter.readthedocs.io/>`_ for complete plugin documentation and advanced configuration options.

For folder-specific configuration and advanced targeting examples, see the documentation.

Overview
--------

Import Linter is a command line tool and pylint plugin to check that you are following a self-imposed
architecture within your Python project. It does this by analysing the imports between all the modules in one
or more Python packages, and compares this against a set of rules that you provide in a configuration file.

The tool can be used in two ways:

1. **Standalone CLI tool**: Run ``lint-imports`` as a separate command
2. **Pylint plugin**: Integrate architecture checking into your existing pylint workflow

The configuration file contains one or more 'contracts'. Each contract has a specific
type, which determines the sort of rules it will apply. For example, the ``forbidden``
contract type allows you to check that certain modules or packages are not imported by
parts of your project.

Import Linter is particularly useful if you are working on a complex codebase within a team,
when you want to enforce a particular architectural style. In this case you can add
Import Linter to your deployment pipeline, so that any code that does not follow
the architecture will fail tests.

If there isn't a built in contract type that fits your desired architecture, you can define
a custom one.

Quick start
-----------

Install Import Linter::

    pip install import-linter

Decide on the dependency flows you wish to check. In this example, we have
decided to make sure that ``myproject.foo`` has dependencies on neither
``myproject.bar`` nor ``myproject.baz``, so we will use the ``forbidden`` contract type.

Create an ``.importlinter`` file in the root of your project to define your contract(s). In this case:

.. code-block:: ini

    [importlinter]
    root_package = myproject

    [importlinter:contract:1]
    name=Foo doesn't import bar or baz
    type=forbidden
    source_modules=
        myproject.foo
    forbidden_modules=
        myproject.bar
        myproject.baz

**Option 1: Standalone Usage**

From your project root, run::

    lint-imports

**Option 2: Pylint Plugin Usage**

Run with pylint to integrate into your existing linting workflow::

    pylint --load-plugins=importlinter.pylint_plugin src/

Or configure permanently in your project (see Installation section above).

If your code violates the contract, you will see an error message something like this:

.. code-block:: text

    =============
    Import Linter
    =============

    ---------
    Contracts
    ---------

    Analyzed 23 files, 44 dependencies.
    -----------------------------------

    Foo doesn't import bar or baz BROKEN

    Contracts: 1 broken.


    ----------------
    Broken contracts
    ----------------

    Foo doesn't import bar or baz
    -----------------------------

    myproject.foo is not allowed to import myproject.bar:

    -   myproject.foo.blue -> myproject.utils.red (l.16)
        myproject.utils.red -> myproject.utils.green (l.1)
        myproject.utils.green -> myproject.bar.yellow (l.3)


CI/CD Integration
-----------------

**GitHub Actions Example:**

.. code-block:: yaml

    name: Lint
    on: [push, pull_request]
    jobs:
      lint:
        runs-on: ubuntu-latest
        steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-python@v4
          with:
            python-version: '3.11'
        - run: pip install import-linter pylint
        - run: pylint --load-plugins=importlinter.pylint_plugin src/

**Pre-commit Hook:**

.. code-block:: yaml

    repos:
    - repo: local
      hooks:
      - id: import-linter-pylint
        name: Import Linter (Pylint Plugin)
        entry: pylint
        args: [--load-plugins=importlinter.pylint_plugin]
        language: system
        types: [python]

**Makefile Integration:**

.. code-block:: make

    lint:
    	pylint --load-plugins=importlinter.pylint_plugin src/
    
    lint-standalone:
    	lint-imports
