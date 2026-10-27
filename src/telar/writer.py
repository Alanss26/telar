import shutil
from pathlib import Path


def clean_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)


def write_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_static(static_dir: Path, output_dir: Path) -> None:
    if static_dir.is_dir():
        shutil.copytree(static_dir, output_dir, dirs_exist_ok=True)


def list_files(root: Path) -> list[Path]:
    """Every file under root, relative to it."""
    if not root.is_dir():
        return []
    return sorted(path.relative_to(root) for path in root.rglob("*") if path.is_file())
