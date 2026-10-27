from pathlib import Path

from telar.writer import clean_dir, copy_static, list_files, write_file


def test_clean_dir_removes_old_files(tmp_path: Path) -> None:
    out = tmp_path / "dist"
    write_file(out / "old" / "index.html", "old")
    clean_dir(out)
    assert out.is_dir()
    assert list_files(out) == []


def test_write_file_creates_parent_folders(tmp_path: Path) -> None:
    write_file(tmp_path / "a" / "b" / "index.html", "<p>hi</p>")
    assert (tmp_path / "a" / "b" / "index.html").read_text(encoding="utf-8") == "<p>hi</p>"


def test_copy_static_keeps_the_tree(tmp_path: Path) -> None:
    write_file(tmp_path / "static" / "css" / "style.css", "body {}")
    write_file(tmp_path / "static" / "robots.txt", "")
    copy_static(tmp_path / "static", tmp_path / "dist")
    assert list_files(tmp_path / "dist") == [Path("css/style.css"), Path("robots.txt")]


def test_copy_static_without_static_folder(tmp_path: Path) -> None:
    copy_static(tmp_path / "static", tmp_path / "dist")
    assert not (tmp_path / "dist").exists()
