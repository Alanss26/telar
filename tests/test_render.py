from pathlib import Path

import pytest
from markupsafe import Markup

from telar.config import SiteConfig
from telar.content import Page, load_page
from telar.errors import SiteError
from telar.render import Renderer


def make_renderer(
    tmp_path: Path,
    templates: dict[str, str],
    collections: dict[str, list[Page]] | None = None,
) -> Renderer:
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()
    for name, text in templates.items():
        path = templates_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return Renderer(templates_dir, SiteConfig(title="Demo"), collections or {})


def make_page(tmp_path: Path, relative: str, text: str) -> Page:
    path = tmp_path / "content" / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return load_page(path, Path(relative))


def test_page_layout_by_default(tmp_path: Path) -> None:
    renderer = make_renderer(tmp_path, {"layouts/page.html": "{{ page.title }}|{{ page.content }}"})
    page = make_page(tmp_path, "a.md", '---\ntitle: "<b>A</b>"\n---\n')
    page.content = Markup("<p>hi</p>")
    # The title is escaped, the already-rendered content isn't.
    assert renderer.render(page) == "&lt;b&gt;A&lt;/b&gt;|<p>hi</p>"


def test_listing_page_uses_list_layout_and_sees_collections(tmp_path: Path) -> None:
    post = make_page(tmp_path, "blog/post.md", "---\ntitle: Post\n---\n")
    template = "{% for p in collections[page.collection] %}{{ p.title }}{% endfor %}"
    renderer = make_renderer(tmp_path, {"layouts/list.html": template}, {"blog": [post]})
    listing = make_page(tmp_path, "blog/_index.md", "---\ntitle: Blog\n---\n")
    assert renderer.render(listing) == "Post"


def test_layout_from_front_matter(tmp_path: Path) -> None:
    renderer = make_renderer(tmp_path, {"layouts/home.html": "home of {{ site.title }}"})
    page = make_page(tmp_path, "index.md", "---\ntitle: Home\nlayout: home\n---\n")
    assert renderer.render(page) == "home of Demo"


def test_missing_layout_points_to_the_page(tmp_path: Path) -> None:
    renderer = make_renderer(tmp_path, {})
    page = make_page(tmp_path, "a.md", "---\ntitle: A\nlayout: nope\n---\n")
    with pytest.raises(SiteError, match=r"template not found: layouts/nope\.html") as info:
        renderer.render(page)
    assert info.value.path == page.source


def test_syntax_error_points_to_the_template_line(tmp_path: Path) -> None:
    renderer = make_renderer(tmp_path, {"layouts/page.html": "ok\n{% if %}\n"})
    page = make_page(tmp_path, "a.md", "---\ntitle: A\n---\n")
    with pytest.raises(SiteError, match="template syntax error") as info:
        renderer.render(page)
    assert info.value.path == tmp_path / "templates" / "layouts" / "page.html"
    assert info.value.line == 2


def test_undefined_variable_points_to_the_template_line(tmp_path: Path) -> None:
    renderer = make_renderer(
        tmp_path,
        {
            "layouts/page.html": '{% include "partials/title.html" %}',
            "partials/title.html": "line one\n{{ page.titel }}\n",
        },
    )
    page = make_page(tmp_path, "a.md", "---\ntitle: A\n---\n")
    with pytest.raises(SiteError, match="titel") as info:
        renderer.render(page)
    assert info.value.path == tmp_path / "templates" / "partials" / "title.html"
    assert info.value.line == 2


def test_missing_templates_dir(tmp_path: Path) -> None:
    with pytest.raises(SiteError, match="templates folder not found"):
        Renderer(tmp_path / "nope", SiteConfig(title="Demo"), {})
