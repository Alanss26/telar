import datetime
from pathlib import Path

import pytest

from telar.content import load_pages, route_for
from telar.errors import SiteError


def write(root: Path, relative: str, text: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


@pytest.mark.parametrize(
    ("relative", "url", "output"),
    [
        ("index.md", "/", "index.html"),
        ("about.md", "/about/", "about/index.html"),
        ("blog/hola.md", "/blog/hola/", "blog/hola/index.html"),
        ("blog/_index.md", "/blog/", "blog/index.html"),
        ("docs/guide/setup.md", "/docs/guide/setup/", "docs/guide/setup/index.html"),
    ],
)
def test_route_for(relative: str, url: str, output: str) -> None:
    assert route_for(Path(relative)) == (url, Path(output))


def test_reads_front_matter_and_body(tmp_path: Path) -> None:
    write(
        tmp_path,
        "blog/hola.md",
        "---\ntitle: Hola\ndate: 2024-05-01\ntags: [intro]\nsummary: First post\n---\n# Hi\n",
    )
    [page] = load_pages(tmp_path)
    assert page.title == "Hola"
    assert page.date == datetime.date(2024, 5, 1)
    assert page.tags == ["intro"]
    assert page.extra == {"summary": "First post"}
    assert page.collection == "blog"
    assert not page.is_listing
    assert page.body.strip() == "# Hi"


def test_root_page_has_no_collection(tmp_path: Path) -> None:
    write(tmp_path, "about.md", "---\ntitle: About\n---\n")
    [page] = load_pages(tmp_path)
    assert page.collection is None


def test_listing_page_is_flagged(tmp_path: Path) -> None:
    write(tmp_path, "blog/_index.md", "---\ntitle: Blog\n---\n")
    [page] = load_pages(tmp_path)
    assert page.is_listing
    assert page.url == "/blog/"


def test_datetime_is_reduced_to_date(tmp_path: Path) -> None:
    write(tmp_path, "a.md", "---\ntitle: A\ndate: 2024-05-01 10:30:00\n---\n")
    [page] = load_pages(tmp_path)
    assert page.date == datetime.date(2024, 5, 1)


def test_drafts_are_skipped(tmp_path: Path) -> None:
    write(tmp_path, "a.md", "---\ntitle: A\n---\n")
    write(tmp_path, "b.md", "---\ntitle: B\ndraft: true\n---\n")
    assert [page.title for page in load_pages(tmp_path)] == ["A"]


def test_hidden_and_non_markdown_files_are_ignored(tmp_path: Path) -> None:
    write(tmp_path, "a.md", "---\ntitle: A\n---\n")
    write(tmp_path, ".trash/old.md", "---\ntitle: Old\n---\n")
    write(tmp_path, "notes.txt", "not content")
    assert [page.title for page in load_pages(tmp_path)] == ["A"]


def test_invalid_yaml_points_to_the_line(tmp_path: Path) -> None:
    path = write(tmp_path, "bad.md", "---\ntitle: Ok\ndate: a: b\n---\n")
    with pytest.raises(SiteError, match="invalid front matter") as info:
        load_pages(tmp_path)
    assert info.value.path == path
    assert info.value.line == 3


def test_invalid_field_points_to_the_line(tmp_path: Path) -> None:
    write(tmp_path, "bad.md", "---\ntitle: Ok\ndraft: maybe\n---\n")
    with pytest.raises(SiteError, match="draft") as info:
        load_pages(tmp_path)
    assert info.value.line == 3


def test_missing_title(tmp_path: Path) -> None:
    write(tmp_path, "bad.md", "# no front matter\n")
    with pytest.raises(SiteError, match="title: Field required"):
        load_pages(tmp_path)


def test_duplicate_urls_are_rejected(tmp_path: Path) -> None:
    write(tmp_path, "blog/hola.md", "---\ntitle: A\n---\n")
    write(tmp_path, "blog/hola/index.md", "---\ntitle: B\n---\n")
    with pytest.raises(SiteError, match="/blog/hola/ is already used"):
        load_pages(tmp_path)


def test_missing_content_dir(tmp_path: Path) -> None:
    with pytest.raises(SiteError, match="content folder not found"):
        load_pages(tmp_path / "nope")
