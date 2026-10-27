from pathlib import Path

import pytest

from telar.config import load_config
from telar.errors import SiteError


def write_config(site_dir: Path, text: str) -> Path:
    (site_dir / "site.toml").write_text(text, encoding="utf-8")
    return site_dir


def test_defaults(tmp_path: Path) -> None:
    config = load_config(write_config(tmp_path, 'title = "Demo"\n'))
    assert config.title == "Demo"
    assert config.content_dir == Path("content")
    assert config.output_dir == Path("dist")
    assert config.base_url == ""
    assert config.params == {}


def test_base_url_trailing_slash_is_removed(tmp_path: Path) -> None:
    write_config(tmp_path, 'title = "Demo"\nbase_url = "https://example.com/"\n')
    assert load_config(tmp_path).base_url == "https://example.com"


def test_params_are_free_form(tmp_path: Path) -> None:
    write_config(tmp_path, 'title = "Demo"\n[params]\ntwitter = "@demo"\nyear = 2026\n')
    assert load_config(tmp_path).params == {"twitter": "@demo", "year": 2026}


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(SiteError, match=r"site\.toml: not found"):
        load_config(tmp_path)


def test_invalid_toml_mentions_the_line(tmp_path: Path) -> None:
    write_config(tmp_path, 'title = "Demo"\noops\n')
    with pytest.raises(SiteError, match="line 2"):
        load_config(tmp_path)


def test_missing_title(tmp_path: Path) -> None:
    write_config(tmp_path, 'description = "no title here"\n')
    with pytest.raises(SiteError, match="title: Field required"):
        load_config(tmp_path)


def test_unknown_key_is_rejected(tmp_path: Path) -> None:
    write_config(tmp_path, 'title = "Demo"\ntitel = "typo"\n')
    with pytest.raises(SiteError, match="titel: Extra inputs are not permitted"):
        load_config(tmp_path)
