# Roadmap

What comes after v0.1. The full, prioritized list of features lands with the v0.1 docs.

## Features

### Slugify file names in URLs

Right now file and folder names go into the URL as they are: `content/blog/Mi Primer Post.md`
becomes `/blog/Mi Primer Post/`. Turn them into slugs instead: lowercase, accents stripped
(`á → a`, `ñ → n`), spaces and punctuation replaced by `-` → `/blog/mi-primer-post/`.

- **Difficulty:** low. `unicodedata.normalize("NFKD", ...)` handles accents without new
  dependencies. An optional `slug:` front matter field could override the generated one.
- **Touches:** `content.py` (`route_for`), its tests and the routes ADR.
- **Watch out:** it changes existing URLs, so already published links would break. Ship it with
  a note in the changelog, or behind a `site.toml` option at first.

## Pending chores

### Move the working copy into the WSL filesystem

The repo currently lives on the Windows drive (`/mnt/c/...`) and is used from WSL2. Move it to
`~/telar` inside WSL.

- **Why:** files under `/mnt/c` are slow to read from Linux, uv can't hardlink from its cache
  (hence `UV_LINK_MODE=copy`), and edits made from Windows don't trigger inotify, so `telar dev`
  needs `--poll` to notice them.
- **Difficulty:** low. Clone or move the repo, then run `make install` again.
- **Touches:** no code. After the move, `UV_LINK_MODE=copy` can go from `~/.bashrc`. `--poll` stays,
  since it's still useful on network drives and Docker volumes.
