# ADR 0004: URLs derived from the folder structure

- **Status:** Accepted
- **Date:** 2026-10-27

## Context

Every page needs a URL and an output file. The rule has to be predictable at a glance, work on
any static host without server configuration, and give a natural way to define collections
and their listing pages.

## Decision

The path inside `content/` is the URL. Every page becomes a folder with an `index.html`
("pretty URLs"):

| File                  | URL                  | Output file                   |
| --------------------- | -------------------- | ----------------------------- |
| `about.md`            | `/about/`            | `about/index.html`            |
| `blog/hello-world.md` | `/blog/hello-world/` | `blog/hello-world/index.html` |
| `index.md`            | `/`                  | `index.html`                  |
| `blog/_index.md`      | `/blog/`             | `blog/index.html`             |

- `index.md` and `_index.md` take their folder's URL. `_index.md` additionally marks the
  folder's **listing page**, which uses the `list` layout and isn't part of the collection.
- A page's **collection** is its top-level folder (`blog/2026/post.md` belongs to `blog`).
- Two files that produce the same URL (`blog/a.md` and `blog/a/index.md`) stop the build.
- File names are used as they are (no slugs yet), and templates use root-relative links.

## Alternatives considered

- **`.html` files** (`/blog/hello-world.html`): simpler, but URLs show the file extension,
  and dropping it later breaks links.
- **A `permalink` field on every page:** maximum flexibility, but every page needs it and the
  folder structure stops telling you anything.
- **Date-based URLs** (`/2026/10/hello-world/`): ties URLs to dates, which then can't be
  corrected without breaking links.

## Consequences

- Works on any static host: GitHub Pages, Netlify, S3, a plain nginx. No rewrite rules needed.
- Renaming or moving a file changes its URL. That's the price of "the path is the URL".
- Names with spaces, accents or capitals end up in the URL as they are. Slugs are on the
  roadmap.
- Root-relative links break when the site is served from a subpath, such as a GitHub Pages
  project site. A `base_path` option is on the roadmap.
