import datetime
from pathlib import Path

from telar.collections import group_collections
from telar.content import Page


def make_page(
    title: str,
    collection: str | None,
    date: datetime.date | None = None,
    *,
    is_listing: bool = False,
) -> Page:
    return Page(
        source=Path(f"{title}.md"),
        url=f"/{title}/",
        output_path=Path(title, "index.html"),
        title=title,
        date=date,
        draft=False,
        tags=[],
        layout=None,
        extra={},
        body="",
        collection=collection,
        is_listing=is_listing,
    )


def test_groups_by_folder_and_skips_root_and_listing_pages() -> None:
    pages = [
        make_page("about", None),
        make_page("blog", "blog", is_listing=True),
        make_page("post", "blog"),
        make_page("project", "work"),
    ]
    groups = group_collections(pages)
    assert {name: [p.title for p in items] for name, items in groups.items()} == {
        "blog": ["post"],
        "work": ["project"],
    }


def test_listing_page_creates_an_empty_collection() -> None:
    assert group_collections([make_page("news", "news", is_listing=True)]) == {"news": []}


def test_sorts_newest_first_with_undated_last() -> None:
    pages = [
        make_page("old", "blog", datetime.date(2023, 1, 1)),
        make_page("undated", "blog"),
        make_page("new", "blog", datetime.date(2024, 1, 1)),
        make_page("also-new", "blog", datetime.date(2024, 1, 1)),
    ]
    titles = [page.title for page in group_collections(pages)["blog"]]
    assert titles == ["also-new", "new", "old", "undated"]
