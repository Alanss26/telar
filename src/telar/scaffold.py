import shutil
from pathlib import Path

from telar.errors import SiteError
from telar.writer import list_files

# Shipped inside the package so `telar init` works from any install (uv tool, pipx...).
STARTER_DIR = Path(__file__).parent / "starter"


def create_site(target: Path) -> list[Path]:
    """Copy the starter site into target and return the files created.

    target may be missing or empty. Anything else is refused so we never overwrite files.
    """
    if target.exists():
        if not target.is_dir():
            raise SiteError("already exists and is not a folder", target)
        if any(target.iterdir()):
            raise SiteError("folder is not empty; pick a new or empty one", target)

    shutil.copytree(STARTER_DIR, target, dirs_exist_ok=True)
    return list_files(target)
