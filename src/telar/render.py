import traceback
from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    TemplateNotFound,
    TemplateSyntaxError,
    select_autoescape,
)

from telar.config import SiteConfig
from telar.content import Page
from telar.errors import SiteError


def layout_for(page: Page) -> str:
    name = page.layout or ("list" if page.is_listing else "page")
    return f"layouts/{name}.html"


class Renderer:
    """Renders pages with the Jinja2 templates of one site."""

    def __init__(
        self,
        templates_dir: Path,
        site: SiteConfig,
        collections: dict[str, list[Page]],
    ) -> None:
        if not templates_dir.is_dir():
            raise SiteError("templates folder not found", templates_dir)
        self.templates_dir = templates_dir
        self.site = site
        self.collections = collections
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(),
            # Fail loudly on typos like {{ page.titel }} instead of rendering nothing.
            undefined=StrictUndefined,
        )

    def render(self, page: Page) -> str:
        try:
            template = self.env.get_template(layout_for(page))
            return template.render(page=page, site=self.site, collections=self.collections)
        except TemplateSyntaxError as exc:
            path = Path(exc.filename) if exc.filename else None
            raise SiteError(f"template syntax error: {exc.message}", path, exc.lineno) from exc
        except TemplateNotFound as exc:
            raise self._error(f"template not found: {exc.name}", exc, page) from exc
        except Exception as exc:
            # Anything else that blows up inside a template is a template problem too.
            raise self._error(str(exc), exc, page) from exc

    def _error(self, message: str, exc: Exception, page: Page) -> SiteError:
        # Jinja rewrites tracebacks so template frames point at the .html file and line.
        for frame in reversed(traceback.extract_tb(exc.__traceback__)):
            path = Path(frame.filename)
            if path.is_relative_to(self.templates_dir):
                return SiteError(f"{message} (rendering {page.source})", path, frame.lineno)
        return SiteError(message, page.source)
