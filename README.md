# click-config-file-injection-utils

<!--TOC-->

______________________________________________________________________

**Table of Contents**

- [1. Introduction](#1-introduction)
- [2. Installation Instruction](#2-installation-instruction)
- [3. Usage](#3-usage)

______________________________________________________________________

<!--TOC-->

## 1. Introduction

Utilities for building Click CLIs that load option defaults from user-specified
TOML files. The package exposes a single callback function,
`injectDefaultOptionsFromToml` and the exception `MissingToolSectionError`.

The config options in the TOML file are injected as the default config options,
which can be overwritten by any CLI-specified configs. If users don't specify
corresponding configs from CLI, these TOML config options will be actually
applied to the CLI tool.

## 2. Installation Instruction

```bash
pip install click-config-file-injection-utils
```

## 3. Usage

Here is how you can use it with `Click`:

```python
import click
from click_config_file_injection_utils import injectDefaultOptionsFromToml


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
@click.option('--count', default=1, show_default=True)
def cli(count: int, config: str | None) -> None:
    click.echo(f'count={count}')


if __name__ == '__main__':
    cli()
```

If the user runs `cli --config pyproject.toml` and that file contains
`[tool.demo] count = 5`, the command prints `count=5`. Passing `--count` on the
CLI still overrides the TOML value.

The helper mirrors the behavior currently used in the `pydoclint` CLI, but it
can be reused by any Click application that maintains its configuration under a
`[tool.<name>]` table.
