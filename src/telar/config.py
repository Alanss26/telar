import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from telar.errors import SiteError, describe_validation_error

CONFIG_FILE = "site.toml"


class SiteConfig(BaseModel):
    # Unknown keys are almost always typos, so we reject them.
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str = ""
    author: str = ""
    language: str = "en"
    base_url: str = ""
    content_dir: Path = Path("content")
    templates_dir: Path = Path("templates")
    static_dir: Path = Path("static")
    output_dir: Path = Path("dist")
    params: dict[str, Any] = Field(default_factory=dict)

    @field_validator("base_url")
    @classmethod
    def _strip_trailing_slash(cls, value: str) -> str:
        # Links are built as base_url + page.url, and page.url already starts with "/".
        return value.rstrip("/")


def load_config(site_dir: Path) -> SiteConfig:
    path = site_dir / CONFIG_FILE
    if not path.is_file():
        raise SiteError("not found. Is this a Telar site? Try `telar init`.", path)

    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise SiteError(f"invalid TOML: {exc}", path) from exc

    try:
        return SiteConfig.model_validate(data)
    except ValidationError as exc:
        raise SiteError(describe_validation_error("invalid config:", exc), path) from exc
