from pathlib import Path

from telar.errors import SiteError


def test_message_only() -> None:
    assert str(SiteError("boom")) == "boom"


def test_with_path() -> None:
    assert str(SiteError("boom", Path("a.md"))) == "a.md: boom"


def test_with_path_and_line() -> None:
    assert str(SiteError("boom", Path("a.md"), 3)) == "a.md:3: boom"
