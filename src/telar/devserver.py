"""Local dev server: serves the output folder and reloads the browser after each rebuild.

The browser side is a one-line EventSource (Server-Sent Events) injected into every HTML page.
"""

import sys
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from watchfiles import Change, DefaultFilter, watch

from telar.build import build
from telar.errors import SiteError

EVENTS_PATH = "/__telar/reload"
RELOAD_SCRIPT = (
    f'<script>new EventSource("{EVENTS_PATH}").onmessage = () => location.reload();</script>'
)
KEEPALIVE_SECONDS = 15


def inject_reload_script(html: str) -> str:
    index = html.lower().rfind("</body>")
    if index == -1:
        return html + RELOAD_SCRIPT
    return html[:index] + RELOAD_SCRIPT + html[index:]


class ReloadNotifier:
    """Lets the watcher thread wake up every open browser tab."""

    def __init__(self) -> None:
        self.version = 0
        self.closed = False
        self._condition = threading.Condition()

    def notify(self) -> None:
        with self._condition:
            self.version += 1
            self._condition.notify_all()

    def close(self) -> None:
        with self._condition:
            self.closed = True
            self._condition.notify_all()

    def wait(self, seen: int, timeout: float) -> int:
        """Block until the version moves past `seen`, the notifier closes, or time runs out."""
        with self._condition:
            self._condition.wait_for(lambda: self.version != seen or self.closed, timeout)
            return self.version


class DevRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, notifier: ReloadNotifier, **kwargs: Any) -> None:
        # Must be set before super().__init__, which handles the request right away.
        self.notifier = notifier
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        if self.path == EVENTS_PATH:
            self._stream_events()
            return

        html_file = self._html_file()
        if html_file is None:
            super().do_GET()
            return

        body = inject_reload_script(html_file.read_text(encoding="utf-8")).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self) -> None:
        # A stylesheet cached from before the rebuild is confusing, so never cache.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
        # One line per request is too noisy here. Errors still show up via log_error.
        pass

    def _html_file(self) -> Path | None:
        path = Path(self.translate_path(self.path))
        # "/blog" without the slash is left to the parent class, which redirects to "/blog/".
        if path.is_dir() and urlsplit(self.path).path.endswith("/"):
            path = path / "index.html"
        if path.suffix == ".html" and path.is_file():
            return path
        return None

    def _stream_events(self) -> None:
        seen = self.notifier.version
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        try:
            while not self.notifier.closed:
                version = self.notifier.wait(seen, KEEPALIVE_SECONDS)
                if version != seen:
                    seen = version
                    self.wfile.write(b"data: reload\n\n")
                else:
                    # An SSE comment. Writing something now and then is how we notice closed tabs.
                    self.wfile.write(b": ping\n\n")
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass


class DevServer:
    """Builds the site, serves it, and rebuilds it whenever a source file changes."""

    def __init__(
        self,
        site_dir: Path,
        host: str = "127.0.0.1",
        port: int = 8000,
        *,
        poll: bool = False,
    ) -> None:
        self.site_dir = site_dir.resolve()
        self.poll = poll
        self.output_dir = build(self.site_dir).output_dir
        self.notifier = ReloadNotifier()
        self._stop = threading.Event()

        handler = partial(DevRequestHandler, notifier=self.notifier, directory=str(self.output_dir))
        try:
            self.httpd = ThreadingHTTPServer((host, port), handler)
        except OSError as exc:
            raise SiteError(f"can't listen on {host}:{port} ({exc.strerror})") from exc
        # Open event streams must not keep the process alive after Ctrl+C.
        self.httpd.daemon_threads = True

    @property
    def url(self) -> str:
        host, port = self.httpd.server_address[:2]
        return f"http://{host!s}:{port}/"

    def serve_forever(self) -> None:
        watcher = threading.Thread(target=self._watch, daemon=True)
        watcher.start()
        try:
            self.httpd.serve_forever()
        finally:
            self._stop.set()
            self.notifier.close()
            self.httpd.server_close()

    def stop(self) -> None:
        """Make serve_forever() return. Call it from another thread."""
        self.httpd.shutdown()

    def rebuild(self) -> None:
        started = time.perf_counter()
        try:
            result = build(self.site_dir)
        except SiteError as exc:
            # Keep serving the last good build; the next save will try again.
            print(f"error: {exc}", file=sys.stderr, flush=True)
            return
        elapsed = time.perf_counter() - started
        print(f"Rebuilt {result.page_count} pages in {elapsed:.2f}s", flush=True)
        self.notifier.notify()

    def _watch(self) -> None:
        default_filter = DefaultFilter()

        def should_watch(change: Change, path: str) -> bool:
            changed = Path(path)
            # The output changes on every build; watching it would rebuild forever.
            if changed.is_relative_to(self.output_dir):
                return False
            # Same trap, sneakier: recreating dist/ bumps the site folder's mtime, which
            # polling reports as a change. Changed files are reported on their own anyway.
            if changed.is_dir():
                return False
            return default_filter(change, path)

        changes = watch(
            self.site_dir,
            watch_filter=should_watch,
            # None lets watchfiles pick (it also honours WATCHFILES_FORCE_POLLING).
            force_polling=self.poll or None,
            stop_event=self._stop,
        )
        for _ in changes:
            self.rebuild()
