import os
import sys
import json
from logging import config as logging_config
from typing import Optional, Tuple, Type, Union

import click

from importlinter.application.sentinels import NotSupplied
from importlinter.application.formatters import (
    format_report_as_json,
    format_report_as_json2,
    should_use_json_output,
)

from . import configuration
from .application import use_cases

configuration.configure()

EXIT_STATUS_SUCCESS = 0
EXIT_STATUS_ERROR = 1


@click.command()
@click.option("--config", default=None, help="The config file to use.")
@click.option(
    "--contract",
    default=list,
    multiple=True,
    help="Limit the check to the supplied contract identifier. May be passed multiple times.",
)
@click.option("--cache-dir", default=None, help="The directory to use for caching.")
@click.option("--no-cache", is_flag=True, help="Disable caching.")
@click.option(
    "--target-folders",
    default=None,
    help="Comma-separated list of folders to check (defaults to all analyzed files).",
)
@click.option(
    "--exclude-folders",
    default=None,
    help="Comma-separated list of folders to exclude from checking.",
)
@click.option("--debug", is_flag=True, help="Run in debug mode.")
@click.option(
    "--show-timings",
    is_flag=True,
    help="Show times taken to build the graph and to check each contract.",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Noisily output progress as we go along.",
)
@click.option(
    "--format",
    "output_format",
    default="text",
    type=click.Choice(["text", "json", "json2"], case_sensitive=False),
    help="Output format (text for human-readable, json/json2 for structured output).",
)
def lint_imports_command(
    config: Optional[str],
    contract: Tuple[str, ...],
    cache_dir: Optional[str],
    no_cache: bool,
    target_folders: Optional[str],
    exclude_folders: Optional[str],
    debug: bool,
    show_timings: bool,
    verbose: bool,
    output_format: str,
) -> int:
    """
    Check that a project adheres to a set of contracts.
    """
    # Parse folder arguments
    target_folders_list = []
    if target_folders:
        target_folders_list = [f.strip() for f in target_folders.split(",")]

    exclude_folders_list = []
    if exclude_folders:
        exclude_folders_list = [f.strip() for f in exclude_folders.split(",")]

    exit_code = lint_imports(
        config_filename=config,
        limit_to_contracts=contract,
        cache_dir=cache_dir,
        no_cache=no_cache,
        target_folders=tuple(target_folders_list),
        exclude_folders=tuple(exclude_folders_list),
        is_debug_mode=debug,
        show_timings=show_timings,
        verbose=verbose,
        output_format=output_format,
    )
    sys.exit(exit_code)


def lint_imports(
    config_filename: Optional[str] = None,
    limit_to_contracts: Tuple[str, ...] = (),
    cache_dir: Optional[str] = None,
    no_cache: bool = False,
    target_folders: Tuple[str, ...] = (),
    exclude_folders: Tuple[str, ...] = (),
    is_debug_mode: bool = False,
    show_timings: bool = False,
    verbose: bool = False,
    output_format: str = "text",
) -> int:
    """
    Check that a project adheres to a set of contracts.

    This is the main function that runs the linter.

    Args:
        config_filename:    the filename to use to parse user options.
        limit_to_contracts: if supplied, only lint the contracts with the supplied ids.
        cache_dir:          the directory to use for caching, defaults to '.import_linter_cache'.
        no_cache:           if True, disable caching.
        target_folders:     if supplied, only check files in these folders.
        exclude_folders:    if supplied, exclude files in these folders from checking.
        is_debug_mode:      whether debugging should be turned on. In debug mode, exceptions are
                            not swallowed at the top level, so the stack trace can be seen.
        show_timings:       whether to show the times taken to build the graph and to check
                            each contract.
        verbose:            if True, noisily output progress as it goes along.

    Returns:
        EXIT_STATUS_SUCCESS or EXIT_STATUS_ERROR.
    """
    # Add current directory to the path, as this doesn't happen automatically.
    sys.path.insert(0, os.getcwd())

    _configure_logging(verbose)

    combined_cache_dir = _combine_caching_arguments(cache_dir, no_cache)

    # Prepare folder info for JSON output
    folder_info = ""
    if target_folders or exclude_folders:
        folder_parts = []
        if target_folders:
            folder_parts.append(f"targeting folders: {', '.join(target_folders)}")
        if exclude_folders:
            folder_parts.append(f"excluding folders: {', '.join(exclude_folders)}")
        folder_info = f" ({'; '.join(folder_parts)})"

    if should_use_json_output(output_format):
        # For JSON output, we need the detailed report
        from importlinter.application.use_cases import (
            read_user_options,
            create_report,
            _register_contract_types,
        )

        try:
            user_options = read_user_options(config_filename=config_filename)
            _register_contract_types(user_options)

            report = create_report(
                user_options=user_options,
                limit_to_contracts=limit_to_contracts,
                cache_dir=combined_cache_dir,
                target_folders=target_folders,
                exclude_folders=exclude_folders,
                show_timings=show_timings,
                verbose=verbose,
            )

            # Output JSON format
            if output_format.lower() == "json2":
                json_output = format_report_as_json2(report, folder_info)
            else:  # json
                json_output = format_report_as_json(report, folder_info)
            click.echo(json_output)

            return EXIT_STATUS_SUCCESS if not report.contains_failures else EXIT_STATUS_ERROR

        except Exception as e:
            if is_debug_mode:
                raise
            # Output error in JSON format
            if output_format.lower() == "json2":
                error_output = {
                    "messages": [
                        {
                            "type": "fatal",
                            "symbol": "import-contract-error",
                            "message": f"Import contract error: {str(e)}",
                            "messageId": "E9002",
                            "confidence": "HIGH",
                            "module": "",
                            "obj": "",
                            "line": 1,
                            "column": 0,
                            "endLine": None,
                            "endColumn": None,
                            "path": "",
                            "absolutePath": "",
                        }
                    ],
                    "statistics": {
                        "messageTypeCount": {
                            "fatal": 1,
                            "error": 0,
                            "warning": 0,
                            "refactor": 0,
                            "convention": 0,
                            "info": 0,
                        },
                        "modulesLinted": 0,
                        "score": 0.0,
                    },
                }
            else:  # json
                error_output = {
                    "error": str(e),
                    "summary": {"has_violations": True, "error": True},
                }
            click.echo(json.dumps(error_output, indent=2))
            return EXIT_STATUS_ERROR
    else:
        # Use the existing text-based output
        passed = use_cases.lint_imports(
            config_filename=config_filename,
            limit_to_contracts=limit_to_contracts,
            cache_dir=combined_cache_dir,
            target_folders=target_folders,
            exclude_folders=exclude_folders,
            is_debug_mode=is_debug_mode,
            show_timings=show_timings,
            verbose=verbose,
        )

        return EXIT_STATUS_SUCCESS if passed else EXIT_STATUS_ERROR


def _combine_caching_arguments(
    cache_dir: Optional[str], no_cache: bool
) -> Union[str, None, Type[NotSupplied]]:
    if no_cache:
        return None
    if cache_dir is None:
        return NotSupplied
    return cache_dir


def _configure_logging(verbose: bool) -> None:
    logger_names = ("importlinter", "grimp", "_rustgrimp")
    logging_config.dictConfig(
        {
            "version": 1,
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO" if verbose else "WARNING",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                logger_name: {
                    "level": "INFO",
                    "handlers": ["console"],
                }
                for logger_name in logger_names
            },
        }
    )
