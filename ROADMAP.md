# Roadmap

What comes after v0.1, roughly in the order it should happen. Each item says what it is, how hard
it looks, and which modules it would touch (see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)).

Difficulty is a rough guess: **low** (an evening), **medium** (a weekend), **high** (needs a
design discussion first, probably an ADR).

## Priority 1: next up

Small changes that fix real problems for people publishing a site today.

### Subpath support (`base_path`)

Templates and Markdown links are root-relative (`/blog/`, `/css/style.css`). That works on a
custom domain or on `username.github.io`, but breaks on a GitHub Pages **project** site, which is
served from a subpath: `https://username.github.io/telar/`. There, `/css/style.css` points to
`username.github.io/css/style.css` and the site loads without styles.

Add a `base_path` option (e.g. `base_path = "/telar"`) and a `url` template filter that prefixes
it: `{{ "/css/style.css" | url }}` → `/telar/css/style.css`. Root-relative links written by hand
in Markdown need the same prefix, which a small markdown-it rule can add. The dev server should
serve the site under the same prefix so local links behave like production.

An alternative is to take the path from `base_url` (`https://username.github.io/telar` →
`/telar`), which avoids a new option but mixes two concerns in one field.

- **Difficulty:** medium.
- **Touches:** `config.py` (new field), `render.py` (filter), `markdown.py` (link rule),
  `devserver.py` (serve under the prefix), the starter templates, tests, and the URL scheme ADR.

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

### Slugify file names in URLs

Right now file and folder names go into the URL as they are: `content/blog/Mi Primer Post.md`
becomes `/blog/Mi Primer Post/`. Turn them into slugs instead: lowercase, accents stripped
(`á → a`, `ñ → n`), spaces and punctuation replaced by `-` → `/blog/mi-primer-post/`.

- **Difficulty:** low. `unicodedata.normalize("NFKD", ...)` handles accents without new
  dependencies. An optional `slug:` front matter field could override the generated one.
- **Touches:** `content.py` (`route_for`), its tests and the routes ADR.
- **Watch out:** it changes existing URLs, so already published links would break. Ship it with
  a note in the changelog, or behind a `site.toml` option at first.

### Syntax highlighting

Code blocks come out as plain `<pre><code class="language-python">`. Highlight them at build
time with Pygments through markdown-it-py's `highlight` option, so no JavaScript is needed in
the browser. Ship a light/dark stylesheet in the starter site.

- **Difficulty:** low.
- **Touches:** `markdown.py`, `pyproject.toml` (Pygments, which needs a line in the
  dependency list explaining why), the starter CSS, and the Markdown ADR.

### Sitemap and RSS

Generate `sitemap.xml` with every page, and an RSS/Atom feed per collection (`/blog/feed.xml`).
Both need absolute URLs, so they only make sense when `base_url` is set, and the build should
say so instead of writing broken files.

- **Difficulty:** low–medium. The XML is simple; the details are dates (RSS wants a full
  datetime, we only keep a date) and escaping.
- **Touches:** a new `feeds.py`, `build.py` (write the extra files), `config.py` (feed options),
  the starter `base.html` (`<link rel="alternate">`).

## Priority 2: soon

Features most sites end up wanting once they grow past a handful of pages.

### Pagination

Split long listings into pages: `/blog/`, `/blog/page/2/`, ... A `paginate: 10` front matter
field on `_index.md` turns it on, and templates get a `paginator` with the current page's items
and links to the previous and next pages.

- **Difficulty:** medium. Today one content file produces exactly one output file; pagination
  breaks that assumption.
- **Touches:** `collections.py` (slicing), `build.py` (one listing → several outputs),
  `render.py` (extra context), `content.py` (routes for `page/N/`).

### Search index

Write a `search.json` with title, URL, summary and plain text of every page, plus a small,
dependency-free script in the starter site that searches it in the browser.

- **Difficulty:** low for the index, medium for a search UI that feels good.
- **Touches:** a new `search.py`, `build.py`, the starter templates and static files.

### Shortcodes / components

Let Markdown call template snippets, e.g. `{{< youtube id="..." >}}` rendered with a Jinja
macro from `templates/shortcodes/`. The hard parts are the syntax, escaping, and keeping error
messages pointing at the right line of the Markdown file.

- **Difficulty:** medium–high. Needs an ADR.
- **Touches:** `markdown.py` (a markdown-it plugin), `render.py` (expose macros),
  `content.py` (error locations).

### Image optimization

Resize images and convert them to modern formats (WebP/AVIF), and offer a template helper that
outputs `srcset`. It's slow, so it really wants a cache (see incremental builds).

- **Difficulty:** medium–high. Adds Pillow as a dependency.
- **Touches:** a new `images.py`, `writer.py` (static pipeline), `render.py` (template helper).

## Priority 3: later

Big features that change the shape of the code. They should wait until the internals above
have settled.

### Internationalization (i18n)

Several languages in one site: `languages` in `site.toml`, content in `content/en/`,
`content/es/` (or `post.es.md`), language-prefixed URLs, per-language collections, and a way to
translate template strings.

- **Difficulty:** high.
- **Touches:** `config.py`, `content.py`, `collections.py`, `render.py`, `build.py`, starter
  site.

### Incremental builds and caching

Rebuild only what changed. That means tracking which templates and partials each page used,
and hashing inputs to skip work. Builds are fast for small sites today, so this only pays off
for big sites or for image processing.

- **Difficulty:** high. Cache invalidation bugs are easy to write and hard to see.
- **Touches:** `build.py`, `render.py` (record template dependencies), `devserver.py` (pass the
  changed files to the build), a new `cache.py`.

### Installable themes

A theme is a folder or Python package with `templates/` and `static/`. Set `theme = "name"` in
`site.toml`, and the site's own files override the theme's (a Jinja `ChoiceLoader` with the
site first, then the theme).

- **Difficulty:** medium–high, mostly in deciding how themes are distributed and versioned.
- **Touches:** `config.py`, `render.py` (loader), `build.py` and `writer.py` (merge static
  files), `scaffold.py`.

### Plugin system

Hooks at fixed points of the build (after loading content, before rendering, after writing),
discovered through Python entry points. Several items above could then live outside the core.
It commits us to a public API, so it comes last.

- **Difficulty:** high. Needs an ADR about which hooks exist and what they're allowed to change.
- **Touches:** `build.py` (call the hooks), a new `plugins.py`, and the public shape of
  `Page`, `SiteConfig` and `BuildResult`.

## Known limitations

### `telar dev` doesn't follow changes to `output_dir`

The dev server reads `output_dir` once, at startup. If you change it in `site.toml` while
the server is running, rebuilds go to the new folder but the server keeps serving the old one.
Restart `telar dev` after changing it.

- **Possible fix:** after each rebuild, compare `BuildResult.output_dir` with the folder being
  served and point the request handler to the new one.
- **Touches:** `devserver.py`.

### Only the site folder is watched

`telar dev` watches the folder that contains `site.toml`. If `content_dir`, `templates_dir` or
`static_dir` point outside of it, changes there won't trigger a rebuild.

- **Possible fix:** watch each configured folder instead of the site root.
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
