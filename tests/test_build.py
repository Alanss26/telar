from pathlib import Path

import pytest

from telar.build import build
from telar.errors import SiteError
from telar.writer import list_files


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_build_writes_pages_and_static_files(site: Path) -> None:
    result = build(site)
    assert result.output_dir == site / "dist"
    assert result.page_count == 4
    assert list_files(result.output_dir) == [
        Path("blog/first/index.html"),
        Path("blog/index.html"),
        Path("blog/second/index.html"),
        Path("css/style.css"),
        Path("index.html"),
    ]


def test_pages_are_rendered_with_their_layout(site: Path) -> None:
    out = build(site).output_dir
    home = read(out / "index.html")
    assert "<title>Home | Test Site</title>" in home
    assert "<nav>" in home
    assert "<strong>Telar</strong>" in home


def test_listing_shows_posts_newest_first(site: Path) -> None:
    listing = read(build(site).output_dir / "blog" / "index.html")
    assert listing.index("Second") < listing.index("First")
    assert "Secret" not in listing


def test_output_dir_can_be_overridden(site: Path, tmp_path: Path) -> None:
    result = build(site, tmp_path / "public")
    assert result.output_dir == tmp_path / "public"
    assert (tmp_path / "public" / "index.html").is_file()


def test_old_output_is_removed(site: Path) -> None:
    stale = site / "dist" / "stale.html"
    stale.parent.mkdir()
    stale.write_text("old", encoding="utf-8")
    build(site)
    assert not stale.exists()


def test_failed_build_leaves_old_output_alone(site: Path) -> None:
    build(site)
    (site / "templates" / "layouts" / "page.html").write_text("{{ broken", encoding="utf-8")
    with pytest.raises(SiteError):
        build(site)
    assert (site / "dist" / "index.html").is_file()


@pytest.mark.parametrize("output_dir", [".", "..", "content", "static/out"])
def test_output_dir_cannot_overlap_the_sources(site: Path, output_dir: str) -> None:
    with pytest.raises(SiteError, match="output_dir"):
        build(site, site / output_dir)
    assert (site / "content" / "index.md").is_file()


def test_static_file_cannot_shadow_a_page(site: Path) -> None:
    (site / "static" / "index.html").write_text("<p>static</p>", encoding="utf-8")
    with pytest.raises(SiteError, match="same output path"):
        build(site)
