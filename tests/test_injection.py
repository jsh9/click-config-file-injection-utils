from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

import click
import pytest
from click.core import ParameterSource
from click.testing import CliRunner

from click_config_file_injection_utils import (
    MissingToolSectionError,
    injectDefaultOptionsFromToml,
)


def writeToml(tmp_path: Path, body: str) -> Path:
    path = tmp_path / 'pyproject.toml'
    path.write_text(body, encoding='utf-8')
    return path


def buildCtx() -> tuple[click.Context, click.Option]:
    command = click.Command('demo')
    option = click.Option(['--config'])
    ctx = click.Context(command)
    return ctx, option


def testTomlFileInjectCanUpdateDefaultMap(tmp_path: Path) -> None:
    toml = writeToml(
        tmp_path,
        '[tool]\n[tool.demo]\nflag = true\ncount = 3\nname = "demo123"\n',
    )

    ctx, option = buildCtx()
    ctx._parameter_source[option.name] = ParameterSource.DEFAULT

    value = injectDefaultOptionsFromToml(
        ctx,
        option,
        str(toml),
        toolSectionName='demo',
    )

    assert value == str(toml)
    assert ctx.default_map == {
        'flag': True,
        'count': 3,
        'name': 'demo123',
    }


def testMissingFileIsSilentlyIgnoredForNonCliSources(tmp_path: Path) -> None:
    missing: Path = tmp_path / 'does-not-exist.toml'
    ctx, option = buildCtx()
    ctx._parameter_source[option.name] = ParameterSource.DEFAULT

    value = injectDefaultOptionsFromToml(
        ctx,
        option,
        str(missing),
        toolSectionName='demo',
    )

    assert value == str(missing)
    assert ctx.default_map == {}


def testMissingToolSectionRaisesForCliSources(tmp_path: Path) -> None:
    toml = writeToml(tmp_path, '[tool]\n[tool.other]\nflag = true\n')
    ctx, option = buildCtx()
    ctx._parameter_source[option.name] = ParameterSource.COMMANDLINE

    with pytest.raises(click.BadParameter) as excInfo:
        injectDefaultOptionsFromToml(
            ctx,
            option,
            str(toml),
            toolSectionName='demo',
        )

    assert 'does not have a [tool.demo] section' in str(excInfo.value)


def testCliRunnerReportsClickError(tmp_path: Path) -> None:
    ctxDefault = {'sample': 'value'}
    missingFilename: Path = tmp_path / 'missing.toml'

    @click.command()
    @click.option(
        '--config',
        callback=lambda ctx, param, value: injectDefaultOptionsFromToml(
            ctx,
            param,
            value,
            toolSectionName='demo',
        ),
    )
    @click.pass_context
    def cli(ctx: click.Context, _config: str | None) -> None:
        ctx.default_map = ctxDefault

    runner = CliRunner()
    result = runner.invoke(cli, ['--config', str(missingFilename)])

    assert result.exit_code != 0
    assert result.output == (
        'Usage: cli [OPTIONS]\n'
        "Try 'cli --help' for help.\n"
        '\n'
        f"Error: Invalid value for '--config': Config"
        f' file "{missingFilename}" does not exist.\n'
    )


def testMissingToolSectionErrorRepr() -> None:
    error = MissingToolSectionError('boom')
    assert str(error) == 'boom'
