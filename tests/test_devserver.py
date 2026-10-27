import threading
import time
import urllib.error
import urllib.request
from collections.abc import Iterator
from pathlib import Path

import pytest

from telar.devserver import (
    EVENTS_PATH,
    RELOAD_SCRIPT,
    DevServer,
    ReloadNotifier,
    inject_reload_script,
)
from telar.errors import SiteError


def fetch(url: str) -> tuple[str, str]:
    """Return (headers as text, body) for a GET request."""
    with urllib.request.urlopen(url, timeout=5) as response:
        return str(response.headers), response.read().decode()


@pytest.fixture
def server(site: Path) -> Iterator[DevServer]:
    # Port 0 picks a free port. Polling works the same on every OS, so tests use it.
    server = DevServer(site, port=0, poll=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.stop()
    thread.join(timeout=5)


def test_script_goes_before_closing_body() -> None:
    assert inject_reload_script("<body><p>hi</p></body>") == (
        f"<body><p>hi</p>{RELOAD_SCRIPT}</body>"
    )


def test_script_is_appended_when_there_is_no_body() -> None:
    assert inject_reload_script("<p>hi</p>") == f"<p>hi</p>{RELOAD_SCRIPT}"


def test_notifier_wait_returns_new_version() -> None:
    notifier = ReloadNotifier()
    notifier.notify()
    assert notifier.wait(0, timeout=1) == 1


def test_notifier_wait_times_out() -> None:
    assert ReloadNotifier().wait(0, timeout=0.01) == 0


def test_html_pages_get_the_reload_script(server: DevServer) -> None:
    headers, body = fetch(server.url)
    assert "<strong>Telar</strong>" in body
    assert RELOAD_SCRIPT in body
    assert "Cache-Control: no-store" in headers


def test_folder_without_slash_redirects_to_its_page(server: DevServer) -> None:
    _, body = fetch(server.url + "blog")
    assert "Second" in body


def test_other_files_are_served_untouched(server: DevServer) -> None:
    _, body = fetch(server.url + "css/style.css")
    assert body == "body { margin: 0; }\n"


def test_missing_file_is_404(server: DevServer) -> None:
    with pytest.raises(urllib.error.HTTPError) as info:
        fetch(server.url + "nope/")
    assert info.value.code == 404


def test_rebuild_tells_open_tabs_to_reload(server: DevServer, site: Path) -> None:
    (site / "content" / "index.md").write_text(
        "---\ntitle: Home\n---\nUpdated!\n", encoding="utf-8"
    )
    with urllib.request.urlopen(server.url + EVENTS_PATH[1:], timeout=5) as events:
        server.rebuild()
        assert events.readline() == b"data: reload\n"
    assert "Updated!" in fetch(server.url)[1]


def test_failed_rebuild_keeps_the_last_good_site(
    server: DevServer, site: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (site / "templates" / "layouts" / "page.html").write_text("{{ broken", encoding="utf-8")
    server.rebuild()
    assert server.notifier.version == 0
    assert "error:" in capsys.readouterr().err
    assert "<strong>Telar</strong>" in fetch(server.url)[1]


def test_watcher_rebuilds_when_a_file_is_saved(server: DevServer, site: Path) -> None:
    page = site / "content" / "index.md"
    # The watcher thread needs a moment to start, so keep saving until it notices.
    deadline = time.monotonic() + 15
    while server.notifier.version == 0 and time.monotonic() < deadline:
        page.write_text(f"---\ntitle: Home\n---\nSaved at {time.time()}\n", encoding="utf-8")
        server.notifier.wait(0, timeout=1)
    assert server.notifier.version > 0
    assert "Saved at" in fetch(server.url)[1]


def test_a_rebuild_does_not_trigger_another_one(server: DevServer) -> None:
    # Recreating dist/ changes the mtime of the site folder itself. With polling that used
    # to look like a change, so every build triggered the next one, forever.
    time.sleep(1)  # let the watcher take its first snapshot
    server.rebuild()
    time.sleep(2)
    assert server.notifier.version == 1


def test_busy_port_is_a_site_error(server: DevServer, site: Path) -> None:
    port = server.httpd.server_address[1]
    with pytest.raises(SiteError, match="can't listen"):
        DevServer(site, port=port)
