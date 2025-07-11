=============
Import Linter
=============

.. image:: https://img.shields.io/pypi/v/import-linter.svg
    :target: https://pypi.org/project/import-linter

.. image:: https://img.shields.io/pypi/pyversions/import-linter.svg
    :alt: Python versions
    :target: https://pypi.org/project/import-linter/

.. image:: https://github.com/seddonym/import-linter/workflows/CI/badge.svg?branch=master
     :target: https://github.com/seddonym/import-linter/actions?workflow=CI
     :alt: CI Status

Import Linter allows you to define and enforce rules for the imports within and between Python packages.

* Free software: BSD license
* Documentation: https://import-linter.readthedocs.io.
* **NEW**: Pylint plugin for seamless integration!

## Features

- **Command Line Tool**: Standalone import linting
- **Pylint Plugin**: Integrated architecture checking within pylint workflow  
- **Folder-Specific Targeting**: Configure checking for particular folders only
- **Multiple Contract Types**: layers, forbidden imports, independence
- **Flexible Configuration**: TOML and INI support
- **CI/CD Ready**: Perfect for continuous integration

## Installation

Install Import Linter::

    pip install import-linter

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
