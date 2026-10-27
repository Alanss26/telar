from typing import Annotated

import typer

from telar import __version__

app = typer.Typer(
    help="Turn a folder of Markdown files into a static website.",
    no_args_is_help=True,
)


def _print_version(value: bool) -> None:
    if value:
        typer.echo(f"telar {__version__}")
        raise typer.Exit()


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
