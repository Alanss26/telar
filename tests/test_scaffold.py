import filecmp
from pathlib import Path

import pytest

from telar.build import build
from telar.errors import SiteError
from telar.scaffold import STARTER_DIR, create_site
from telar.writer import list_files

EXAMPLE_DIR = Path(__file__).parent.parent / "examples" / "basic"


def test_creates_the_starter_site(tmp_path: Path) -> None:
    files = create_site(tmp_path / "blog")
    assert files == list_files(STARTER_DIR)
    assert (tmp_path / "blog" / "site.toml").is_file()


def test_new_site_builds(tmp_path: Path) -> None:
    create_site(tmp_path / "blog")
    assert build(tmp_path / "blog").page_count > 0


def test_empty_folder_is_fine(tmp_path: Path) -> None:
    create_site(tmp_path)
    assert (tmp_path / "site.toml").is_file()


def test_non_empty_folder_is_refused(tmp_path: Path) -> None:
    (tmp_path / "notes.txt").write_text("mine", encoding="utf-8")
    with pytest.raises(SiteError, match="not empty"):
        create_site(tmp_path)
    assert list_files(tmp_path) == [Path("notes.txt")]


def test_file_is_refused(tmp_path: Path) -> None:
    target = tmp_path / "site"
    target.write_text("", encoding="utf-8")
    with pytest.raises(SiteError, match="not a folder"):
        create_site(target)


def test_example_matches_the_starter_site() -> None:
    # examples/basic is generated with `make example`; this catches forgetting to rerun it.
    example_files = [f for f in list_files(EXAMPLE_DIR) if f.parts[0] != "dist"]
    assert example_files == list_files(STARTER_DIR)
    _, mismatch, errors = filecmp.cmpfiles(
        STARTER_DIR, EXAMPLE_DIR, [str(f) for f in example_files], shallow=False
    )
    assert mismatch == []
    assert errors == []
