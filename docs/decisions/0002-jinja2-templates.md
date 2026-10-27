# ADR 0002: Jinja2 for templates

- **Status:** Accepted
- **Date:** 2026-10-27

## Context

Sites need layouts that share a base, reusable partials, loops over collections, and safe
escaping of user data. Template errors must point to the file and line.

## Decision

Use **Jinja2** with:

- A `FileSystemLoader` on `templates/`. Layouts live in `templates/layouts/<name>.html` and
  partials in `templates/partials/`. Both are conventions, not special cases in the code.
- **Autoescaping** for HTML. The page body is passed as `Markup`, so `{{ page.content }}`
  works without `| safe` while titles and other fields are still escaped.
- **`StrictUndefined`**: a typo like `{{ page.titel }}` is an error, not an empty string.
- Three variables in every template: `page`, `site` and `collections`.

## Alternatives considered

- **Mako:** fast and powerful, but allows arbitrary Python in templates and is less familiar.
- **Django templates:** familiar to many, but needs Django's settings machinery.
- **python-liquid:** would feel like home to Jekyll users, but it's a smaller ecosystem and
  less known among Python developers.
- **`string.Template` or f-strings:** no inheritance, no loops, no escaping.

## Consequences

- Jinja2 is the de facto standard in Python (Flask, Ansible, MkDocs...), so most people already
  know the syntax.
- `StrictUndefined` makes optional values a bit more verbose (`page.extra.get("summary")`,
  `{% if page.date %}`), in exchange for catching typos.
- Jinja rewrites tracebacks to point at template lines, which is what lets us report
  `template.html:12` for runtime errors.
- Themes can later be added with a `ChoiceLoader` (site templates first, then the theme's).
