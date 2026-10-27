# ADR 0001: Python, uv and the tooling around them

- **Status:** Accepted
- **Date:** 2026-10-27

## Context

Telar is a personal project that should be easy to read, change and explain line by line. It
has to install as a single command, run on Linux, macOS and WSL, and need as little setup as
possible from contributors.

## Decision

- **Python 3.11+.** `tomllib` is in the standard library from 3.11, and the modern typing syntax
  (`X | None`, `list[str]`) is available. Python also has mature libraries for exactly what an
  SSG needs: Markdown, YAML and templates.
- **uv** manages the project: dependencies, the lockfile (`uv.lock`), the Python version and
  the virtualenv. Users install the CLI with `uv tool install .` or `pipx install .`.
- **hatchling** as the build backend and a **`src/` layout**, so tests run against the
  installed package and not against whatever happens to be in the working directory.
- **Typer** for the CLI: commands and options come from type hints, and `--help` is free.
- **Pydantic v2** to validate `site.toml` and front matter, with readable error messages.
- **Ruff** for linting and formatting, **mypy** in strict mode, **pytest** for tests.
- **pre-commit** runs Ruff and mypy through `uv run`, so the hooks use the exact versions from
  `uv.lock` instead of a second list of versions.

Runtime dependencies are kept to six well-known packages: typer, markdown-it-py,
python-frontmatter, jinja2, pydantic and watchfiles.

## Alternatives considered

- **Go or Rust:** a single static binary and faster builds, but slower to iterate on, and speed
  isn't the bottleneck for personal sites.
- **Poetry or pip-tools:** both work, but are slower than uv and don't manage Python itself.
- **argparse or click:** argparse needs a lot of boilerplate; Typer is built on click and
  removes most of it.
- **black + isort + flake8:** three tools and three configs where Ruff does it all.
- **dataclasses + hand-written validation for config:** no dependency, but we'd be
  rewriting Pydantic's error messages badly.

## Consequences

- Users need Python 3.11+ and either uv or pipx.
- Builds are fast enough for sites with hundreds of pages; that's the target.
- mypy strict means every function has types. It slows down the first draft a bit but keeps
  the code honest. Libraries without good types (markdown-it-py's `render()` returns `Any`)
  need an explicit annotation.
