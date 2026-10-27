# Telar

A small static site generator: Markdown in, HTML out.

Telar takes a folder of Markdown files with YAML front matter, runs them through Jinja2
templates, and writes a plain HTML site you can publish anywhere. It's deliberately small:
the whole thing is about 700 lines of typed Python, split into small modules you can read in an
afternoon.

- `telar init` creates a working starter site.
- `telar build` writes the site to `dist/`.
- `telar dev` serves it locally and reloads the browser when you save.
- URLs come from the folder structure, and drafts are left out of the build.
- Layouts and partials are Jinja2 templates.
- Each top-level content folder becomes a collection (like a blog), sorted by date.
- Errors point to the file and line that caused them.

No telemetry, no accounts, no network access: it only reads and writes files on your disk.

## Installation

Telar needs Python 3.11 or newer. It isn't on PyPI yet, so install it from a clone:

```sh
git clone <repo-url> telar
cd telar
uv tool install .      # or: pipx install .
```

Either way you get a `telar` command on your `PATH`. Check it with `telar --version`.

## Quickstart

```sh
telar init my-site
cd my-site
telar dev
```

Open <http://127.0.0.1:8000>, edit `content/index.md`, save, and the page reloads by itself.
When you're happy with it:

```sh
telar build
```

Then upload the `dist/` folder to any static host.

## Commands

| Command                  | What it does                                                   |
| ------------------------ | -------------------------------------------------------------- |
| `telar init <dir>`       | Create a starter site in a new or empty folder.                |
| `telar build [dir]`      | Build the site in `dir` (default: current folder).             |
| `telar dev [dir]`        | Build, serve at `http://127.0.0.1:8000` and rebuild on save.   |

Useful options:

- `telar build --out <dir>` writes somewhere other than `output_dir`.
- `telar dev --port 3000` (or `-p 3000`) and `--host 0.0.0.0` change where the dev server
  listens.
- `telar dev --poll` checks for changes by polling. Use it when saves aren't picked up, for
  example on network drives, in Docker volumes, or with a WSL repo under `/mnt/c` that you edit
  from Windows.

## Site structure

```text
my-site/
├── site.toml               # site configuration
├── content/                # Markdown pages
│   ├── index.md            # → /
│   ├── about.md            # → /about/
│   └── blog/
│       ├── _index.md       # → /blog/            (lists the "blog" collection)
│       └── hello-world.md  # → /blog/hello-world/
├── templates/
│   ├── layouts/            # one template per layout: page.html, list.html, ...
│   └── partials/           # pieces included from layouts
├── static/                 # copied to the output as is
└── dist/                   # build output (don't edit, it's wiped on every build)
```

### Content

Every page starts with front matter:

```markdown
---
title: Hello, world      # required
date: 2026-10-20         # optional, used to sort collections
draft: true              # optional, drafts aren't built
tags: [intro, news]      # optional
layout: post             # optional, uses templates/layouts/post.html
summary: Anything else   # extra fields end up in page.extra
---

The body is **CommonMark**, plus tables and ~~strikethrough~~.
```

**URLs** come from the path inside `content/`:

| File                    | URL                  | Output file                  |
| ----------------------- | -------------------- | ---------------------------- |
| `index.md`              | `/`                  | `index.html`                 |
| `about.md`              | `/about/`            | `about/index.html`           |
| `blog/hello-world.md`   | `/blog/hello-world/` | `blog/hello-world/index.html`|
| `blog/_index.md`        | `/blog/`             | `blog/index.html`            |

Files and folders whose name starts with `.` are ignored. If two files end up with the same URL,
the build stops and tells you which ones.

**Collections:** every page inside a top-level folder (`content/blog/...`) belongs to that
folder's collection, sorted newest first, with undated pages last. A `_index.md` in the
folder is the collection's listing page: it isn't part of the collection and uses the `list`
layout by default.

### Templates

A page is rendered with `templates/layouts/<layout>.html`. The default layout is `page`, or
`list` for `_index.md` files. Use Jinja2 as usual: `{% extends %}`, `{% block %}` and
`{% include "partials/header.html" %}`.

Every template gets three variables:

| Variable      | What's in it                                                                  |
| ------------- | ----------------------------------------------------------------------------- |
| `page`        | `title`, `date`, `draft`, `tags`, `layout`, `url`, `content` (HTML), `extra`, `collection`, `is_listing` |
| `site`        | Everything from `site.toml`: `title`, `description`, `base_url`, `params`... |
| `collections` | `{"blog": [page, page, ...], ...}`, newest first                              |

`page.content` is already HTML, so `{{ page.content }}` is enough (no `| safe`). Everything
else is escaped.

Undefined variables are errors, so a typo like `{{ page.titel }}` stops the build instead of
rendering nothing. For optional values use `page.extra.get("summary")` or
`{% if page.date %}`.

## Configuration

`site.toml` lives at the root of the site. Only `title` is required:

```toml
title = "My Site"
description = "What this site is about."
author = "Your Name"
language = "en"
base_url = "https://example.com"

[params]
github = "https://github.com/you"
```

| Key             | Default       | Notes                                                       |
| --------------- | ------------- | ----------------------------------------------------------- |
| `title`         | (required)    |                                                             |
| `description`   | `""`          |                                                             |
| `author`        | `""`          |                                                             |
| `language`      | `"en"`        | Handy for `<html lang="...">`.                              |
| `base_url`      | `""`          | Full URL of the published site, without trailing slash.   |
| `content_dir`   | `"content"`   | Paths are relative to the folder that has `site.toml`.     |
| `templates_dir` | `"templates"` |                                                             |
| `static_dir`    | `"static"`    |                                                             |
| `output_dir`    | `"dist"`      | Wiped on every build, so it can't overlap the other folders. |
| `[params]`      | `{}`          | Anything you want, available as `site.params` in templates. |

Unknown keys are rejected so that typos don't go unnoticed:

```text
error: /home/you/my-site/site.toml: invalid config:
  - titel: Extra inputs are not permitted
```

## Development

You need [uv](https://docs.astral.sh/uv/). Then:

```sh
make install     # install dependencies and the pre-commit hooks
make check       # lint + typecheck + tests, the same as CI
```

| Make target      | Without make                                       |
| ---------------- | -------------------------------------------------- |
| `make test`      | `uv run pytest`                                    |
| `make lint`      | `uv run ruff check . && uv run ruff format --check .` |
| `make format`    | `uv run ruff format . && uv run ruff check --fix .`   |
| `make typecheck` | `uv run mypy`                                      |
| `make example`   | Regenerate `examples/basic` from the starter site. |

More about how it works and why:

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): how a build works, step by step.
- [docs/decisions/](docs/decisions/): the decisions behind the design (ADRs).
- [ROADMAP.md](ROADMAP.md): what's planned next.
- [CONTRIBUTING.md](CONTRIBUTING.md): how to contribute.

## License

[MIT](LICENSE) © Alan Joseph Salazar Segura
