from dataclasses import dataclass
from pathlib import Path

from markupsafe import Markup

from telar.collections import group_collections
from telar.config import load_config
from telar.content import load_pages
from telar.errors import SiteError
from telar.markdown import render_markdown
from telar.render import Renderer
from telar.writer import clean_dir, copy_static, list_files, write_file


@dataclass(frozen=True)
class BuildResult:
    output_dir: Path
    page_count: int


def build(site_dir: Path, output_dir: Path | None = None) -> BuildResult:
    """Build the site in site_dir.

    Everything is rendered in memory first, so if anything fails the old output is left alone.
    """
    site_dir = site_dir.resolve()
    config = load_config(site_dir)
    content_dir = site_dir / config.content_dir
    templates_dir = site_dir / config.templates_dir
    static_dir = site_dir / config.static_dir
    output_dir = (output_dir or site_dir / config.output_dir).resolve()
    _check_output_dir(output_dir, site_dir, [content_dir, templates_dir, static_dir])

    pages = load_pages(content_dir)
    for page in pages:
        # Markup tells Jinja this HTML is already safe, so templates don't need |safe.
        page.content = Markup(render_markdown(page.body))
    collections = group_collections(pages)

    renderer = Renderer(templates_dir, config, collections)
    rendered = {page.output_path: renderer.render(page) for page in pages}
    _check_static_collisions(static_dir, rendered)

    clean_dir(output_dir)
    copy_static(static_dir, output_dir)
    for relative, html in rendered.items():
        write_file(output_dir / relative, html)
    return BuildResult(output_dir=output_dir, page_count=len(pages))


def _check_output_dir(output_dir: Path, site_dir: Path, sources: list[Path]) -> None:
    # The output folder is wiped on every build, so make sure that can't eat the user's files.
    if site_dir.is_relative_to(output_dir):
        raise SiteError("output_dir can't be the site folder or one of its parents", output_dir)
    for source in sources:
        if output_dir.is_relative_to(source) or source.is_relative_to(output_dir):
            raise SiteError(f"output_dir overlaps the {source.name}/ folder", output_dir)


def _check_static_collisions(static_dir: Path, rendered: dict[Path, str]) -> None:
    for relative in list_files(static_dir):
        if relative in rendered:
            raise SiteError("has the same output path as a generated page", static_dir / relative)
