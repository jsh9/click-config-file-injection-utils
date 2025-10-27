# click-config-file-injection-utils

<!--TOC-->

______________________________________________________________________

**Table of Contents**

- [1. Example](#1-example)

______________________________________________________________________

<!--TOC-->

Utilities for building Click CLIs that load option defaults from user-specified
`pyproject.toml` files. The package exposes a single callback function,
`injectDefaultOptionsFromToml`, and the error `MissingToolSectionError`.

Use the helper as the callback for a `click.Option` that captures a path such
as `--config`. When the user points at a TOML file, the function parses the
`[tool.<name>]` table and merges those values into `ctx.default_map`, so the
options act as Click defaults (explicit CLI flags still override them).

## 1. Example

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
