import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import frontmatter
import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from telar.errors import SiteError, describe_validation_error


class FrontMatter(BaseModel):
    # Extra keys are allowed and end up in page.extra for templates to use.
    model_config = ConfigDict(extra="allow", coerce_numbers_to_str=True)

    title: str
    date: datetime.date | None = None
    draft: bool = False
    tags: list[str] = Field(default_factory=list)
    layout: str | None = None

    @field_validator("date", mode="before")
    @classmethod
    def _drop_time(cls, value: Any) -> Any:
        # YAML turns "2024-05-01 10:00" into a datetime; we only care about the day.
        if isinstance(value, datetime.datetime):
            return value.date()
        return value


@dataclass
class Page:
    source: Path
    url: str
    output_path: Path  # relative to the output dir
    title: str
    date: datetime.date | None
    draft: bool
    tags: list[str]
    layout: str | None
    extra: dict[str, Any]
    body: str  # raw Markdown, without the front matter
    collection: str | None
    is_listing: bool  # an _index.md that lists its collection


def route_for(relative: Path) -> tuple[str, Path]:
    """Map a path inside content/ to its URL and output file.

    blog/hola.md   -> /blog/hola/  and  blog/hola/index.html
    blog/_index.md -> /blog/       and  blog/index.html
    index.md       -> /            and  index.html
    """
    parts = list(relative.with_suffix("").parts)
    if parts[-1] in ("index", "_index"):
        parts.pop()
    url = "/" + "".join(f"{part}/" for part in parts)
    return url, Path(*parts, "index.html")


def load_pages(content_dir: Path) -> list[Page]:
    """Load every published page under content_dir. Drafts are skipped."""
    if not content_dir.is_dir():
        raise SiteError("content folder not found", content_dir)

    pages: list[Page] = []
    seen_urls: dict[str, Path] = {}
    for path in sorted(content_dir.rglob("*.md")):
        relative = path.relative_to(content_dir)
        if any(part.startswith(".") for part in relative.parts):
            continue

        page = load_page(path, relative)
        if page.draft:
            continue
        if page.url in seen_urls:
            raise SiteError(f"URL {page.url} is already used by {seen_urls[page.url]}", path)
        seen_urls[page.url] = path
        pages.append(page)
    return pages


def load_page(path: Path, relative: Path) -> Page:
    text = _read_text(path)

    try:
        post = frontmatter.loads(text)
    except yaml.YAMLError as exc:
        raise SiteError(
            f"invalid front matter: {_yaml_problem(exc)}", path, _yaml_line(exc)
        ) from exc

    try:
        meta = FrontMatter.model_validate(post.metadata)
    except ValidationError as exc:
        first_field = str(exc.errors()[0]["loc"][0])
        message = describe_validation_error("invalid front matter:", exc)
        raise SiteError(message, path, _line_of_key(text, first_field)) from exc

    url, output_path = route_for(relative)
    return Page(
        source=path,
        url=url,
        output_path=output_path,
        title=meta.title,
        date=meta.date,
        draft=meta.draft,
        tags=meta.tags,
        layout=meta.layout,
        extra=meta.model_extra or {},
        body=post.content,
        collection=relative.parts[0] if len(relative.parts) > 1 else None,
        is_listing=relative.stem == "_index",
    )


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise SiteError("file is not valid UTF-8", path) from exc


def _yaml_problem(exc: yaml.YAMLError) -> str:
    if isinstance(exc, yaml.MarkedYAMLError) and exc.problem:
        return exc.problem
    return str(exc)


def _yaml_line(exc: yaml.YAMLError) -> int | None:
    if isinstance(exc, yaml.MarkedYAMLError) and exc.problem_mark is not None:
        # The YAML text starts right after "---" (with its newline), so line 0 is the
        # "---" line itself and the 0-based mark only needs +1.
        return exc.problem_mark.line + 1
    return None


def _line_of_key(text: str, key: str) -> int | None:
    for number, line in enumerate(text.splitlines(), start=1):
        if line.startswith(f"{key}:"):
            return number
    return None
