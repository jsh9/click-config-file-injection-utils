"""Core logic for injecting Click defaults from TOML config files."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import click
from click.core import ParameterSource

logger = logging.getLogger(__name__)

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


class MissingToolSectionError(RuntimeError):
    """Raised when the `[tool.<name>]` section is missing in a config file."""


def injectDefaultOptionsFromToml(
        ctx: click.Context,
        param: click.Parameter,
        value: str | None,
        *,
        toolSectionName: str,
) -> str | None:
    """
    Inject Click defaults from a user-supplied TOML file path.

    The function is designed to be used as the callback for a ``click.Option``
    that captures the ``--config`` flag. When ``value`` is defined, the
    function parses the referenced TOML file, converts the `[tool.<name>]`
    table into a dictionary, and merges the result into ``ctx.default_map``.
    Because the data flows through ``ctx.default_map`` it behaves like any
    other Click default: explicit CLI flags still win, while options the user
    leaves unspecified inherit the TOML value.

    Examples
    --------
    ::

        @click.command()
        @click.option(
            '--config',
            callback=lambda ctx, param, value: injectDefaultOptionsFromToml(
                ctx,
                param,
                value,
                toolSectionName='mytool',
            ),
        )
        @click.option('--count', default=1, show_default=True)
        def cli(count: int, config: str | None) -> None:
            click.echo(f'count={count}')

    Parameters
    ----------
    ctx : click.Context
        The "click" context
    param : click.Parameter
        The "click" parameter; not used in this function; just a placeholder
    value : str | None
        The full path of the TOML file. (It needs to be named ``value`` so that
        ``click`` can correctly use it as a callback function.)
    toolSectionName : str
        The name of the tool section in the TOML file. For example, if your
        tool is name "pytool", the expected TOML section should be
        ``[tool.pytool]``, so this parameter should be set to "pytool".

    Returns
    -------
    str | None
        The full path of the TOML file

    Raises
    ------
    click.BadParameter
        If the path supplied doesn't exist or lacks a [tool.<toolSectionName>]
        section
    """
    if not value:
        return None

    logger.info('Loading config from user-specified .toml file: %s', value)

    assert param.name is not None  # Give mypy confidence
    enforceToolSection = (
        ctx.get_parameter_source(param.name) == ParameterSource.COMMANDLINE
    )

    try:
        config = _parseOneTomlFile(
            tomlFilename=Path(value),
            enforceToolSection=enforceToolSection,
            toolSectionName=toolSectionName,
        )
    except FileNotFoundError as exc:
        raise click.BadParameter(str(exc), ctx=ctx, param=param) from exc
    except MissingToolSectionError as exc:
        raise click.BadParameter(str(exc), ctx=ctx, param=param) from exc

    _updateCtxDefaultMap(ctx=ctx, config=config)
    return value


def _parseOneTomlFile(
        tomlFilename: Path,
        *,
        enforceToolSection: bool = False,
        toolSectionName: str,
) -> dict[str, Any]:
    """Parse a TOML file and return the `[tool.<name>]` table as a dict."""
    if not tomlFilename.exists():
        message = f'Config file "{tomlFilename}" does not exist.'
        logger.info('%s Nothing to load.', message)
        if enforceToolSection:
            raise FileNotFoundError(message)

        return {}

    try:
        with Path(tomlFilename).open('rb') as fp:
            rawConfig = tomllib.load(fp)
    except Exception as exc:
        logger.info(
            'Failed to load "%s": %s; ignoring this', tomlFilename, exc
        )
        if enforceToolSection:
            raise

        return {}

    toolSection = rawConfig.get('tool')
    if not isinstance(toolSection, dict) or toolSectionName not in toolSection:
        message = (
            f'Config file "{tomlFilename}" does not have'
            f' a [tool.{toolSectionName}] section.'
        )
        logger.info(message)
        if enforceToolSection:
            raise MissingToolSectionError(message)

        finalConfig: dict[str, Any] = {}
    else:
        targetSection = toolSection[toolSectionName]
        if not isinstance(targetSection, dict):
            message = (
                f'Config file "{tomlFilename}" has a non-table'
                f' [tool.{toolSectionName}] section.'
            )
            logger.info(message)
            if enforceToolSection:
                raise MissingToolSectionError(message)

            finalConfig = {}
        else:
            finalConfig = {
                k.replace('-', '_'): v for k, v in targetSection.items()
            }

    if finalConfig:
        logger.info('Found options defined in %s:', tomlFilename)
        logger.info(finalConfig)
    else:
        logger.info('No config found in %s.', tomlFilename)

    return finalConfig


def _updateCtxDefaultMap(ctx: click.Context, config: dict[str, Any]) -> None:
    """Merge ``config`` into ``ctx.default_map`` without mutating inputs."""
    default_map: dict[str, Any] = {}
    if ctx.default_map:
        default_map.update(ctx.default_map)

    default_map.update(config)
    ctx.default_map = default_map
