=======================
Pylint Import-Linter Plugin
=======================

.. 
   Copyright (c) 2025 The Import Linter Contributors
   
   Licensed under the BSD 2-Clause License. See LICENSE file for details.

This plugin integrates `import-linter <https://import-linter.readthedocs.io/>`_ functionality directly into `Pylint <https://pylint.org/>`_, allowing you to enforce architectural contracts as part of your normal linting workflow.

Features
========

- **Seamless Integration**: Run import-linter checks as part of your normal pylint workflow
- **Contract Enforcement**: All import-linter contract types supported (layers, forbidden, independence)
- **Configurable**: Full support for import-linter configuration options
- **Error Reporting**: Clear error messages integrated into pylint's output
- **CI/CD Ready**: Perfect for continuous integration pipelines

Installation
============

The plugin is automatically available when you install this package::

    # Using uv (recommended)
    uv add pylint-import-linter

    # Using pip
    pip install pylint-import-linter

Usage
=====

Basic Usage
-----------

Run pylint with the plugin loaded::

    pylint --load-plugins=importlinter.pylint_plugin src/

Configuration File
------------------

Add the plugin to your ``.pylintrc`` or ``pyproject.toml``:

**.pylintrc:**

.. code-block:: ini

    [MASTER]
    load-plugins = importlinter.pylint_plugin

**pyproject.toml:**

.. code-block:: toml

    [tool.pylint.master]
    load-plugins = ["importlinter.pylint_plugin"]

Plugin Options
--------------

The plugin supports all import-linter configuration options::

    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-config=.importlinter \
           --import-linter-contracts=contract1,contract2 \
           --import-linter-target-folders=src/core,src/api \
           --import-linter-exclude-folders=tests,docs \
           --import-linter-cache-dir=.cache \
           --import-linter-no-cache=yes \
           src/

**Configuration Options:**

- ``--import-linter-config``: Path to import-linter config file (default: ``.importlinter``)
- ``--import-linter-contracts``: Comma-separated list of contract IDs to check
- ``--import-linter-target-folders``: Comma-separated list of folders to check (default: all analyzed files)
- ``--import-linter-exclude-folders``: Comma-separated list of folders to exclude from checking
- ``--import-linter-cache-dir``: Directory for caching (default: ``.import_linter_cache``)
- ``--import-linter-no-cache``: Disable caching

Folder-Based Configuration
--------------------------

The plugin supports targeting specific folders for contract checking, which is useful for:

- Large codebases where you only want to check certain components
- Gradual adoption of import-linter in existing projects  
- Different contract rules for different parts of your application

**Target Specific Folders:**

.. code-block:: bash

    # Only check contracts for core and api modules
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=src/core,src/api \
           src/

**Exclude Specific Folders:**

.. code-block:: bash

    # Check everything except tests and docs
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-exclude-folders=tests,docs \
           src/

**Combined Configuration:**

.. code-block:: bash

    # Target core modules but exclude experimental features
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=src/core \
           --import-linter-exclude-folders=src/core/experimental \
           src/

**Configuration File Example (.pylintrc):**

.. code-block:: ini

    [MASTER]
    load-plugins = importlinter.pylint_plugin

    [importlinter-plugin]
    import-linter-target-folders = src/core,src/api
    import-linter-exclude-folders = tests,docs,migrations

**Configuration File Example (pyproject.toml):**

.. code-block:: toml

    [tool.pylint.master]
    load-plugins = ["importlinter.pylint_plugin"]

    [tool.pylint.importlinter-plugin]
    import-linter-target-folders = ["src/core", "src/api"]
    import-linter-exclude-folders = ["tests", "docs", "migrations"]

Error Messages
==============

The plugin provides specific error codes for different types of architectural violations:

E9003: import-boundary-violation
--------------------------------
Triggered when an import violates a forbidden import contract (boundary violations).

E9004: import-layer-violation
-----------------------------
Triggered when an import violates a layer-based contract.

E9005: import-independence-violation
------------------------------------
Triggered when an import violates an independence contract.

E9001: import-contract-violation
--------------------------------
Triggered when an import violates a defined contract (generic violations).

E9002: import-contract-error
----------------------------  
Triggered when there's an error in the plugin or import-linter configuration.

Configuration
^^^^^^^^^^^^^

In your ``.pylintrc`` configuration file:

.. code-block:: ini

   [MESSAGES CONTROL]
   # Enable specific import contract checks
   enable = import-boundary-violation,import-layer-violation,import-independence-violation,import-contract-violation,import-contract-error
   
   # Or enable specific types only
   enable = import-boundary-violation,import-layer-violation

Examples
========

Example 1: Layer Architecture
-----------------------------

**.importlinter:**

.. code-block:: ini

    [importlinter]
    root_package = myproject

    [importlinter:contract:1]
    name=Layered architecture
    type=layers
    containers=myproject
    layers=
        presentation
        business
        data

**Running pylint:**

.. code-block:: bash

    pylint --load-plugins=importlinter.pylint_plugin myproject/

**Output when violation occurs:**

.. code-block:: text

    myproject/data/models.py:1:0: E9001: Import contract violation: Contract validation failed. Run 'lint-imports --verbose' for details. (import-contract-violation)

Example 2: Forbidden Imports
-----------------------------

**.importlinter:**

.. code-block:: ini

    [importlinter]
    root_package = myproject

    [importlinter:contract:1]
    name=No database imports in presentation
    type=forbidden
    source_modules=myproject.presentation
    forbidden_modules=myproject.database

Example 3: Folder-Specific Checking
------------------------------------

For large projects, you might want to gradually adopt import-linter or only check specific components:

**.importlinter:**

.. code-block:: ini

    [importlinter]
    root_package = myproject

    [importlinter:contract:1]
    name=Core layer architecture
    type=layers
    layers=
        myproject.core.domain
        myproject.core.application  
        myproject.core.infrastructure

**Check only core modules:**

.. code-block:: bash

    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=src/core \
           src/

**Output when violation occurs:**

.. code-block:: text

    src/core/domain/models.py:1:0: E9001: Import contract violation: Contract validation failed (targeting folders: src/core). Run 'lint-imports --verbose' for details. (import-contract-violation)

This approach is particularly useful for:

- **Legacy codebases**: Start with new modules and gradually expand coverage
- **Microservice architectures**: Different rules for different services  
- **Performance**: Only check critical components in large codebases

CI/CD Integration
=================

**GitHub Actions:**

.. code-block:: yaml

    - name: Lint with pylint and import-linter
      run: |
        pylint --load-plugins=importlinter.pylint_plugin \
               --fail-on=E9001,E9002 \
               src/

**Pre-commit hook:**

.. code-block:: yaml

    repos:
      - repo: local
        hooks:
          - id: pylint-import-linter
            name: Pylint with Import Linter
            entry: pylint
            language: system
            args: [--load-plugins=importlinter.pylint_plugin]
            files: \.py$

Comparison: Plugin vs Standalone
================================

+------------------+-------------------+---------------------------+
| Feature          | Pylint Plugin     | Standalone import-linter  |
+==================+===================+===========================+
| Integration      | ✅ Part of pylint | ❌ Separate tool          |
+------------------+-------------------+---------------------------+
| CI/CD            | ✅ Single command | ❌ Two commands needed    |
+------------------+-------------------+---------------------------+
| IDE Support      | ✅ Full pylint    | ❌ Limited                |
|                  | support           |                           |
+------------------+-------------------+---------------------------+
| Error Reporting  | ✅ Integrated     | ❌ Separate output        |
+------------------+-------------------+---------------------------+
| Performance      | ✅ Single run     | ❌ Two separate runs      |
+------------------+-------------------+---------------------------+

Advanced Configuration
======================

Selective Contract Checking
----------------------------

Check only specific contracts::

    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-contracts=layers,forbidden-db \
           src/

Custom Configuration Files
---------------------------

Use different config files for different environments::

    # Development
    pylint --import-linter-config=.importlinter.dev src/

    # Production  
    pylint --import-linter-config=.importlinter.prod src/

Disable Specific Messages
--------------------------

Disable import-linter checks for specific files:

.. code-block:: python

    # pylint: disable=import-contract-violation
    from restricted_module import something

Troubleshooting
===============

Common Issues
-------------

1. **Plugin not found**: Ensure the package is installed in the same environment as pylint
2. **Config file not found**: Specify the config file path with ``--import-linter-config``
3. **No violations reported**: Check that your ``.importlinter`` file is valid

Debug Mode
----------

Run with verbose output for debugging::

    pylint --load-plugins=importlinter.pylint_plugin --verbose src/

Performance Tuning
-------------------

For large projects, use caching::

    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-cache-dir=.cache \
           src/

Integration Examples
====================

VS Code
-------

Add to your VS Code settings:

.. code-block:: json

    {
        "pylint.args": ["--load-plugins=importlinter.pylint_plugin"]
    }

PyCharm
-------

1. Go to Settings → Tools → External Tools
2. Add new tool with command: ``pylint --load-plugins=importlinter.pylint_plugin $FilePath$``

Development Workflow
--------------------

.. code-block:: bash

    # Format code
    uv run black src/

    # Type check  
    uv run mypy src/

    # Lint with architecture checks
    uv run pylint --load-plugins=importlinter.pylint_plugin src/

    # Run tests
    uv run pytest

Migration from Standalone
=========================

If you're currently using standalone import-linter:

1. **Keep your ``.importlinter`` config** - no changes needed
2. **Update CI/CD scripts** - replace separate tools with single pylint command
3. **Update pre-commit hooks** - use pylint instead of import-linter
4. **Configure IDE** - set up pylint with the plugin loaded

Performance
===========

The plugin is designed to be efficient:

- **Single analysis**: Import graph built once for both pylint and import-linter
- **Caching**: Full support for import-linter's caching system
- **Lazy evaluation**: Contracts only checked when necessary
- **Memory efficient**: Minimal memory overhead

For more advanced folder targeting examples and use cases, see :doc:`folder_targeting`.

Example Project
===============

The repository includes a complete Domain-Driven Design example in the ``example/`` folder:

.. code-block:: bash

    # Test with the included DDD example
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-config=example/importlinter.ini \
           --import-linter-target-folders=example/domains/document \
           example/domains/

    # Run the interactive demo
    ./demo_folder_targeting.sh

This demonstrates real-world usage with domain boundaries, layered architecture, and selective targeting.

JSON Output and Tool Integration
=================================

The pylint plugin provides full compatibility with pylint's output formats, enabling seamless integration with development tools, IDEs, and CI/CD pipelines.

JSON Output Examples
-------------------

Standard JSON format with import contract violations:

.. code-block:: bash

    pylint --load-plugins=importlinter.pylint_plugin \
           --output-format=json \
           src/

Example JSON output:

.. code-block:: json

    [
        {
            "type": "error",
            "module": "myproject.core",
            "obj": "",
            "line": 1,
            "column": 0,
            "path": "src/core/__init__.py",
            "symbol": "import-contract-violation",
            "message": "Import contract violation: Layer 'high' must not import 'low'",
            "message-id": "E9001"
        }
    ]

The improved JSON2 format includes additional statistics:

.. code-block:: bash

    pylint --load-plugins=importlinter.pylint_plugin \
           --output-format=json2 \
           src/

Tool Integration Benefits
------------------------

**Structured Error Reporting**: Import contract violations appear as standard pylint errors with:
- Consistent error codes (E9001, E9002)  
- File location information
- Clear violation messages
- Machine-readable format

**IDE Compatibility**: Works with any IDE that supports pylint:
- VS Code Python extension
- PyCharm/IntelliJ IDEA
- Vim/Neovim with ALE
- Emacs with flycheck

**CI/CD Integration**: Compatible with all pylint-based workflows:
- GitHub Actions annotations
- Jenkins pipeline reporting
- GitLab CI integration
- Azure DevOps builds
