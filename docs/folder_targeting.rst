====================================
Folder-Specific Configuration Examples
====================================

.. 
   Copyright (c) 2025 The Import Linter Contributors
   
   Licensed under the BSD 2-Clause License. See LICENSE file for details.

This document provides practical examples of using the folder-specific configuration options in the import-linter pylint plugin.

Basic Usage Patterns
====================

1. Target Specific Modules Only
-------------------------------

.. code-block:: bash

    # Only check import contracts for core business logic
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=src/core,src/domain \
           src/

    # Result: Only analyzes files in src/core and src/domain folders

2. Exclude Development/Test Code
-------------------------------

.. code-block:: bash

    # Exclude tests, docs, and migrations from contract checking
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-exclude-folders=tests,docs,migrations \
           src/

    # Result: Analyzes all files except those in excluded folders

3. Progressive Adoption
----------------------

.. code-block:: bash

    # Start with just the new feature modules
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=src/features/user_management \
           src/

    # Gradually expand to more modules
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=src/features,src/core \
           src/

Configuration File Examples
===========================

.pylintrc Configuration
-----------------------

.. code-block:: ini

    [MASTER]
    load-plugins = importlinter.pylint_plugin

    [importlinter-plugin]
    # Target only core business modules
    import-linter-target-folders = src/core,src/domain,src/services

    # Exclude test and infrastructure code
    import-linter-exclude-folders = tests,docs,migrations,scripts

pyproject.toml Configuration
----------------------------

.. code-block:: toml

    [tool.pylint.master]
    load-plugins = ["importlinter.pylint_plugin"]

    [tool.pylint.importlinter-plugin]
    # For microservice architecture - check each service separately
    import-linter-target-folders = ["src/user_service", "src/order_service"]
    import-linter-exclude-folders = ["tests", "docs", "shared/legacy"]

Real-World Scenarios
====================

Scenario 1: Legacy Codebase Migration
-------------------------------------

.. code-block:: bash

    # Phase 1: Only new modules follow architecture contracts
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=src/new_features \
           src/

    # Phase 2: Include refactored legacy modules
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=src/new_features,src/refactored \
           src/

    # Phase 3: Full coverage (remove folder restrictions)
    pylint --load-plugins=importlinter.pylint_plugin src/

Scenario 2: Microservice Monorepo
---------------------------------

.. code-block:: bash

    # Check each service independently
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=services/auth \
           --import-linter-contracts=auth-layers \
           services/

    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=services/billing \
           --import-linter-contracts=billing-forbidden \
           services/

Scenario 3: Performance Optimization
------------------------------------

.. code-block:: bash

    # For large codebases, only check critical paths
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=src/critical,src/core \
           --import-linter-exclude-folders=src/vendor,src/legacy \
           src/

How It Works
============

Folder Matching Logic
---------------------

The plugin uses prefix matching for folder paths:

.. code-block:: python

    # Examples of what gets matched:
    target_folders = ["src/core", "src/api"]

    # These files WILL be included:
    "src/core/models.py"           # Matches src/core
    "src/core/services/auth.py"    # Matches src/core (subdirectory)
    "src/api/views.py"             # Matches src/api

    # These files will NOT be included:
    "src/utils/helpers.py"         # Doesn't match any target
    "tests/test_core.py"           # Doesn't match any target

Exclusion Priority
------------------

Exclusions are checked before inclusions:

.. code-block:: bash

    # Even if src/core is targeted, src/core/experimental is excluded
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=src/core \
           --import-linter-exclude-folders=src/core/experimental \
           src/

Contract Scope
--------------

**Important**: When folder restrictions are active, import-linter still analyzes the entire project dependency graph. The folder configuration only determines *when* to run the contract checking, not *what* to analyze.

This means:

- ✅ Contracts will detect violations involving targeted folders
- ✅ All dependencies and imports are still analyzed  
- ✅ Layer violations between targeted and non-targeted modules are caught
- ❌ Performance improvement is minimal (full analysis still runs)

CI/CD Integration Examples
=========================

GitHub Actions with Folder Targeting
------------------------------------

.. code-block:: yaml

    name: Architecture Compliance
    on: [push, pull_request]

    jobs:
      check-core-architecture:
        runs-on: ubuntu-latest
        steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-python@v4
          with:
            python-version: '3.11'
        - run: pip install import-linter pylint
        - name: Check core modules only
          run: |
            pylint --load-plugins=importlinter.pylint_plugin \
                   --import-linter-target-folders=src/core \
                   --fail-on=E9001,E9002 \
                   src/

Progressive Adoption Script
---------------------------

.. code-block:: bash

    #!/bin/bash
    # progressive_check.sh - Gradually expand contract checking

    set -e

    echo "Phase 1: Core modules"
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=src/core \
           src/

    echo "Phase 2: Core + API modules"  
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=src/core,src/api \
           src/

    echo "Phase 3: All modules except legacy"
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-exclude-folders=src/legacy \
           src/

    echo "All phases completed successfully!"

Best Practices
==============

1. **Start Small**: Begin with a single module or feature
2. **Use Exclusions**: Exclude test/doc folders to focus on production code
3. **Document Phases**: Plan your adoption strategy in phases
4. **Test Incrementally**: Verify contracts work before expanding scope
5. **Consider Performance**: Large codebases may still benefit from smaller scopes even though full analysis runs

Troubleshooting
===============

No Import-Linter Output
-----------------------

If you don't see import-linter results, it means none of the analyzed files matched your folder criteria:

.. code-block:: bash

    # Debug: Check which files are being analyzed
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=wrong/path \
           src/

    # Result: Only pylint output, no import-linter section

Contracts Still Failing Outside Target Folders
----------------------------------------------

This is expected behavior. Import-linter analyzes the entire project graph and may detect violations involving non-targeted files:

.. code-block:: bash

    # Even targeting only src/api, violations in src/core affecting src/api will be reported
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-target-folders=src/api \
           src/

This is actually beneficial - it ensures architectural integrity across the entire codebase.

Practical Example
=================

The project includes a complete example demonstrating folder-specific targeting with a Domain-Driven Design architecture.

Example Structure
-----------------

.. code-block:: text

    example/
    ├── domains/
    │   ├── document/           # Document domain
    │   ├── billing/           # Billing domain  
    │   ├── org_and_user/      # User management
    │   └── pd_common/         # Shared utilities
    └── importlinter.ini       # DDD configuration

Running the Example
-------------------

.. code-block:: bash

    # Full analysis - all domains
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-config=example/importlinter.ini \
           example/domains/

    # Target only document domain
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-config=example/importlinter.ini \
           --import-linter-target-folders=example/domains/document \
           example/domains/

    # Exclude shared utilities
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-config=example/importlinter.ini \
           --import-linter-exclude-folders=example/domains/pd_common \
           example/domains/

Interactive Demo
----------------

Run the included demo script to see all scenarios::

    ./demo_folder_targeting.sh

This demonstrates:

- ✅ Full domain analysis with boundary violations
- ✅ Selective domain targeting 
- ✅ Infrastructure folder exclusion
- ✅ Business domain focus
- ✅ No-match scenarios (skips analysis)

IDE Integration and JSON Output
===============================

The pylint plugin supports all standard pylint output formats, enabling seamless integration with IDEs and development tools that rely on structured output for syntax highlighting and error reporting.

JSON Output Support
-------------------

The plugin works perfectly with pylint's JSON output formats, providing structured data for automated processing:

.. code-block:: bash

    # Standard JSON format
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-config=example/importlinter.ini \
           --output-format=json \
           example/domains/

    # Improved JSON format (recommended)
    pylint --load-plugins=importlinter.pylint_plugin \
           --import-linter-config=example/importlinter.ini \
           --output-format=json2 \
           example/domains/

JSON Output Structure
--------------------

Import contract violations appear as standard pylint error messages in JSON output:

.. code-block:: json

    {
        "type": "error",
        "module": "example.domains",
        "obj": "",
        "line": 1,
        "column": 0,
        "endLine": null,
        "endColumn": null,
        "path": "example/domains/__init__.py",
        "symbol": "import-contract-violation",
        "message": "Import contract violation: Contract validation failed (targeting folders: example/domains/document). Run 'lint-imports --verbose' for details.",
        "message-id": "E9001"
    }

The folder targeting information is included in the message field, enabling tools to understand which folders are being analyzed.

GitHub Actions Integration
--------------------------

For GitHub Actions workflows, use the GitHub-specific output format:

.. code-block:: yaml

    name: Architecture Compliance
    on: [push, pull_request]

    jobs:
      check-architecture:
        runs-on: ubuntu-latest
        steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-python@v4
          with:
            python-version: '3.11'
        - run: pip install import-linter pylint
        - name: Check import contracts with folder targeting
          run: |
            pylint --load-plugins=importlinter.pylint_plugin \
                   --import-linter-target-folders=src/core \
                   --output-format=github \
                   src/

This produces GitHub-compatible annotations:

.. code-block:: text

    ::error file=src/__init__.py,line=1,col=0,title=E9001::Import contract violation: Contract validation failed (targeting folders: src/core)

IDE Configuration Examples
--------------------------

VS Code with Python Extension
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configure in ``.vscode/settings.json``:

.. code-block:: json

    {
        "python.linting.enabled": true,
        "python.linting.pylintEnabled": true,
        "python.linting.pylintArgs": [
            "--load-plugins=importlinter.pylint_plugin",
            "--import-linter-target-folders=src/core,src/api"
        ]
    }

PyCharm Configuration
~~~~~~~~~~~~~~~~~~~~

1. Go to **Settings** → **Tools** → **External Tools**
2. Add new tool with:
   - **Program**: ``pylint``
   - **Arguments**: ``--load-plugins=importlinter.pylint_plugin --import-linter-target-folders=src/core $FilePath$``
   - **Working Directory**: ``$ProjectFileDir$``

Vim/Neovim with ALE
~~~~~~~~~~~~~~~~~~

Configure in your ``.vimrc`` or ``init.vim``:

.. code-block:: vim

    let g:ale_python_pylint_options = '--load-plugins=importlinter.pylint_plugin --import-linter-target-folders=src/core'

Output Format Compatibility
---------------------------

The plugin supports all pylint output formats:

- **text** (default): Human-readable output
- **parseable**: Machine-readable format
- **colorized**: Colored terminal output  
- **json**: Standard JSON format
- **json2**: Improved JSON format with statistics
- **github**: GitHub Actions annotations
- **msvs**: Visual Studio format

Each format preserves folder targeting information in the appropriate structure, ensuring compatibility with any tool that processes pylint output.
