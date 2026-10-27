import time
from pathlib import Path
from typing import Annotated, NoReturn

import typer

from telar import __version__
from telar.build import build as build_site
from telar.devserver import DevServer
from telar.errors import SiteError
from telar.scaffold import create_site

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
def init(
    directory: Annotated[Path, typer.Argument(help="Where to create the site.")],
) -> None:
    """Create a new site with example content."""
    try:
        files = create_site(directory)
    except SiteError as exc:
        _fail(exc)
    typer.echo(f"Created {len(files)} files in {directory}\n")
    typer.echo("Next steps:")
    typer.echo(f"  cd {directory}")
    typer.echo("  telar dev")


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


@app.command()
def dev(
    site_dir: Annotated[Path, typer.Argument(help="Folder that contains site.toml.")] = Path("."),
    host: Annotated[str, typer.Option(help="Address to listen on.")] = "127.0.0.1",
    port: Annotated[int, typer.Option("--port", "-p", help="Port to listen on.")] = 8000,
    poll: Annotated[
        bool,
        typer.Option(
            "--poll",
            help="Check for changes by polling. Use it if saves aren't picked up, "
            "e.g. a repo under /mnt/c in WSL edited from Windows.",
        ),
    ] = False,
) -> None:
    """Serve the site locally and reload the browser when files change."""
    try:
        server = DevServer(site_dir, host, port, poll=poll)
    except SiteError as exc:
        _fail(exc)

    mode = "polling" if poll else "watching"
    typer.echo(f"Serving {server.output_dir} at {server.url} ({mode} for changes, Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        typer.echo("\nStopped.")
