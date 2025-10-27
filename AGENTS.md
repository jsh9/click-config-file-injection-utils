# AGENTS

## 1. Project overview

- `click_config_file_injection_utils` ships a single helper,
  `injectDefaultOptionsFromToml`, plus the `MissingToolSectionError` exception.
- The helper is meant to be wired to a Click option (typically `--config`) so a
  CLI can pull defaults from a `[tool.<name>]` table in a user supplied
  `pyproject.toml`.
- The repository targets Python 3.10+ (see `pyproject.toml`) and mirrors the
  behavior presently used by the `pydoclint` CLI.

## 2. Key files

- `click_config_file_injection_utils/injection.py`: Core logic for parsing the
  TOML file, validating the target `[tool.<name>]` table, and updating
  `ctx.default_map` without mutating inputs.
- `tests/test_injection.py`: Pytest coverage for the happy path, missing file
  handling, Click CLI error surfacing, and exception string behavior.
- `tests/conftest.py`: Extends `sys.path` so tests import the local package.
- `pyproject.toml`: Declares dependencies, pytest defaults, and packaging
  metadata.
- `tox.ini`: Defines Python, mypy, muff (ruff-based) lint/format, and
  pre-commit environments.
- `muff.toml` & `.pre-commit-config.yaml`: Enforce formatting, lint selection,
  and auxiliary Markdown/TOML tooling.

## 3. Development setup

1. Use Python 3.10+.
2. Create an isolated environment and install the package plus dev tooling:
   ```
   pip install -e .
   pip install -r requirements.dev
   ```
3. Optionally install `tox` or `muff` globally if you plan to run the full
   automation locally.

## 4. Test & quality commands

- Fast unit pass: `pytest -q`.
- Full matrix: `tox` (see `envlist` in `tox.ini`).
- Static typing: `tox -e mypy`.
- Formatting & linting: `tox -e muff-format` and `tox -e muff-lint`.
- All hooks: `tox -e pre-commit` (skips muff inside the hook to avoid duplicate
  work).

## 5. Implementation notes

- `_parseOneTomlFile` gracefully downgrades missing files or malformed sections
  unless the value originated from the command line, in which case it raises to
  signal a Click `BadParameter`.
- `ctx.default_map` is copied and updated, never mutated in place, to preserve
  Click’s expectations.
- TOML parsing relies on `tomllib` (or `tomli` on \<3.11). When returning data,
  hyphens in option names become underscores to match Click’s option naming.
- Logging is intentionally informative but not verbose; reuse `logger` instead
  of printing.

## 6. Contribution checklist

1. Add or update tests that demonstrate the behavior change.
2. Run `pytest` and relevant `tox` environments.
3. Apply `muff format` and ensure `muff check` passes.
4. Run `pre-commit run -a` before raising a pull request.
5. Update `README.md` and `CHANGELOG.md` if the public surface or workflow
   changes.
