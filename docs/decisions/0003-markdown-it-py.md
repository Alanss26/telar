# ADR 0003: markdown-it-py for Markdown

- **Status:** Accepted
- **Date:** 2026-10-27

## Context

Content is written in Markdown, and authors expect it to behave like GitHub or any other
CommonMark-based tool. We also want room to grow: syntax highlighting, footnotes, maybe
shortcodes.

## Decision

Use **markdown-it-py** with the `commonmark` preset plus the `table` and `strikethrough` rules.
Raw HTML in Markdown is allowed, since the content belongs to the site's author.

## Alternatives considered

- **Python-Markdown:** the oldest option and very popular, but it isn't CommonMark compliant,
  so edge cases render differently from what people expect.
- **mistune:** very fast, but less strict about the spec, and its API has changed a lot between
  major versions.
- **commonmark.py:** deprecated in favour of markdown-it-py.
- **marko:** CommonMark compliant, but a smaller community and fewer extensions.

## Consequences

- Output matches the CommonMark spec, which is what most editors preview.
- The extension ecosystem (`mdit-py-plugins`: footnotes, front matter, containers...) and the
  token/rule architecture leave a clear path for future features.
- Syntax highlighting will plug into its `highlight` option (see the roadmap).
- `MarkdownIt.render()` is typed as returning `Any`, so `markdown.py` annotates it explicitly.
