"""Builds examples/basic end to end, the way a user would."""

from pathlib import Path

import pytest

from telar.build import build
from telar.writer import list_files

EXAMPLE_DIR = Path(__file__).parent.parent / "examples" / "basic"


@pytest.fixture(scope="module")
def output(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return build(EXAMPLE_DIR, tmp_path_factory.mktemp("out")).output_dir


def read(output: Path, relative: str) -> str:
    return (output / relative).read_text(encoding="utf-8")


def test_all_pages_and_assets_are_written(output: Path) -> None:
    assert list_files(output) == [
        Path("about/index.html"),
        Path("blog/hello-world/index.html"),
        Path("blog/index.html"),
        Path("blog/writing-posts/index.html"),
        Path("css/style.css"),
        Path("index.html"),
    ]


def test_drafts_are_not_published(output: Path) -> None:
    assert not (output / "blog" / "draft-idea").exists()
    assert "half-baked" not in read(output, "blog/index.html")


def test_home_page(output: Path) -> None:
    home = read(output, "index.html")
    assert "<title>My Telar Site</title>" in home
    assert "<h1>Hi there!</h1>" in home
    assert '<link rel="stylesheet" href="/css/style.css">' in home
    # Latest posts, newest first.
    assert home.index("Writing posts") < home.index("Hello, world")


def test_blog_listing(output: Path) -> None:
    listing = read(output, "blog/index.html")
    assert '<a href="/blog/writing-posts/">Writing posts</a>' in listing
    assert '<time datetime="2026-10-25">Oct 25, 2026</time>' in listing
    assert "The first post on this site." in listing


def test_post_page(output: Path) -> None:
    post = read(output, "blog/writing-posts/index.html")
    assert "<title>Writing posts · My Telar Site</title>" in post
    assert "<table>" in post
    assert "<s>strikethrough</s>" in post
    assert '<span class="tag">#guide</span>' in post


def test_plain_page(output: Path) -> None:
    about = read(output, "about/index.html")
    assert "<h1>About</h1>" in about
    assert 'class="meta"' not in about
