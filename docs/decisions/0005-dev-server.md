# ADR 0005: Dev server with http.server, Server-Sent Events and watchfiles

- **Status:** Accepted
- **Date:** 2026-10-27

## Context

`telar dev` should serve the site, rebuild when a file is saved, and reload the open browser
tabs. It's only for local use, so it doesn't need to be fast or hardened, but it does need to
be simple, work on Linux, macOS and WSL, and add as few dependencies as possible.

## Decision

- **Serving:** `ThreadingHTTPServer` and `SimpleHTTPRequestHandler` from the standard library,
  serving the output folder.
- **Reloading:** a Server-Sent Events endpoint (`/__telar/reload`). The server injects a
  one-line script into each HTML page as it serves it:
  `new EventSource("/__telar/reload").onmessage = () => location.reload();`
- **Watching:** `watchfiles` watches the site folder and calls `build()` after each batch of
  changes. `--poll` forces polling for filesystems where native events don't arrive (WSL
  repos under `/mnt/c` edited from Windows, network drives, Docker volumes).
- A full rebuild on every change. A failed rebuild prints the error and keeps serving the
  last good build.

## Alternatives considered

- **WebSockets:** two-way communication we don't need, and it would add a dependency
  (`websockets`) or a lot of hand-written protocol code. SSE is plain HTTP and browsers
  reconnect automatically.
- **The `livereload` package:** does all of this, but brings its own server and dependencies,
  and hides how it works.
- **An ASGI stack (Starlette + Uvicorn):** robust, but heavy for serving static files locally.
- **Polling from the browser** (`fetch` every second): no server support needed, but it's
  wasteful and reloads late.
- **Injecting the script at build time:** simpler handler, but `dist/` would end up with dev
  code in it, risking a published site that tries to connect to a dev server.

## Consequences

- The only new dependency is watchfiles, which is fast and works on every OS.
- `http.server` isn't meant for production, and we only use it locally (it binds to
  `127.0.0.1` by default).
- Full rebuilds are fine for small sites; incremental builds are on the roadmap.
- While `dist/` is being rewritten there's a short window where a request can 404. Building
  into a temp folder and swapping it in is on the roadmap.
- With polling, folders show up as "modified" whenever something inside them changes,
  including the site folder when `dist/` is recreated. The watcher ignores folder events
  so that a build can't trigger the next one.
