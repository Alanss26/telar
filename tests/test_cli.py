from pathlib import Path

from typer.testing import CliRunner

from telar import __version__
from telar.cli import app

runner = CliRunner()


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_build_command(site: Path) -> None:
    result = runner.invoke(app, ["build", str(site)])
    assert result.exit_code == 0
    assert "Built 4 pages" in result.output
    assert (site / "dist" / "index.html").is_file()


def test_build_command_reports_site_errors(tmp_path: Path) -> None:
    result = runner.invoke(app, ["build", str(tmp_path)])
    assert result.exit_code == 1
    assert "error:" in result.output
    assert "site.toml: not found" in result.output


def test_dev_command_fails_fast_when_the_first_build_fails(tmp_path: Path) -> None:
    result = runner.invoke(app, ["dev", str(tmp_path)])
    assert result.exit_code == 1
    assert "site.toml: not found" in result.output


def test_dev_command_has_a_poll_flag() -> None:
    result = runner.invoke(app, ["dev", "--help"])
    assert "--poll" in result.output
