from telar.content import Page


def group_collections(pages: list[Page]) -> dict[str, list[Page]]:
    """Group pages by their top-level folder, newest first.

    Root pages and listing pages (_index.md) don't belong to any collection.
    """
    groups: dict[str, list[Page]] = {}
    for page in pages:
        if page.collection is None or page.is_listing:
            continue
        groups.setdefault(page.collection, []).append(page)

    for items in groups.values():
        items.sort(key=_newest_first)
    return groups


def _newest_first(page: Page) -> tuple[bool, int, str]:
    # Undated pages go last; ties are broken by title so the order is stable.
    ordinal = page.date.toordinal() if page.date else 0
    return (page.date is None, -ordinal, page.title)
