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

### Build into a temporary folder and swap it in

Today a build renders everything in memory, then wipes `dist/` and writes the files one by one.
While that happens (well under a second) `dist/` is half empty, so the dev server can answer a
request with a 404. Write the new build into a sibling temp folder (`dist.tmp-xxxx`) and swap it
in with renames: `dist` → `dist.old`, `dist.tmp-xxxx` → `dist`, then delete `dist.old`.

- **Difficulty:** low–medium. The renames are quick, but there's still a tiny gap between
  them. Windows also refuses to rename folders that have open files, so a fallback or a retry
  is needed there.
- **Touches:** `build.py` and `writer.py`. The dev server keeps serving the same path, so it
  doesn't change.

## Known limitations

### `telar dev` doesn't follow changes to `output_dir`

The dev server reads `output_dir` once, at startup. If you change it in `site.toml` while
the server is running, rebuilds go to the new folder but the server keeps serving the old one.
Restart `telar dev` after changing it.

- **Possible fix:** after each rebuild, compare `BuildResult.output_dir` with the folder being
  served and point the request handler to the new one.
- **Touches:** `devserver.py`.

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
