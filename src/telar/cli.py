import time
from pathlib import Path
from typing import Annotated, NoReturn

import typer

from telar import __version__
from telar.build import build as build_site
from telar.errors import SiteError

app = typer.Typer(
    help="Turn a folder of Markdown files into a static website.",
    no_args_is_help=True,
)


def _print_version(value: bool) -> None:
    if value:
        typer.echo(f"telar {__version__}")
        raise typer.Exit()


def _fail(exc: SiteError) -> NoReturn:
    typer.secho(f"error: {exc}", fg=typer.colors.RED, err=True)
    raise typer.Exit(1)


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            callback=_print_version,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = False,
) -> None:
    """Telar: Markdown in, HTML out."""


@app.command()
def build(
    site_dir: Annotated[Path, typer.Argument(help="Folder that contains site.toml.")] = Path("."),
    out: Annotated[
        Path | None,
        typer.Option("--out", "-o", help="Write here instead of output_dir from site.toml."),
    ] = None,
) -> None:
    """Build the site into its output folder."""
    started = time.perf_counter()
    try:
        result = build_site(site_dir, out)
    except SiteError as exc:
        _fail(exc)
    elapsed = time.perf_counter() - started
    typer.echo(f"Built {result.page_count} pages in {elapsed:.2f}s -> {result.output_dir}")
