from pathlib import Path

from pydantic import ValidationError


class SiteError(Exception):
    """A problem the user can fix: bad config, content or templates, a busy port..."""

    def __init__(self, message: str, path: Path | None = None, line: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.path = path
        self.line = line

    def __str__(self) -> str:
        if self.path is None:
            return self.message
        location = f"{self.path}:{self.line}" if self.line else str(self.path)
        return f"{location}: {self.message}"


def describe_validation_error(heading: str, exc: ValidationError) -> str:
    lines = [heading]
    for error in exc.errors():
        field = ".".join(str(part) for part in error["loc"])
        lines.append(f"  - {field}: {error['msg']}")
    return "\n".join(lines)
