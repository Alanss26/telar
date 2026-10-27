# Architecture Decision Records

Short notes on the decisions that shaped Telar: what the problem was, what we picked, what we
didn't, and what it costs us. When a decision changes, write a new ADR that supersedes the
old one instead of editing history.

| ADR                                        | Decision                                      |
| ------------------------------------------ | --------------------------------------------- |
| [0001](0001-python-and-tooling.md)         | Python 3.11+, uv, Typer, Pydantic, Ruff, mypy |
| [0002](0002-jinja2-templates.md)           | Jinja2 for templates                          |
| [0003](0003-markdown-it-py.md)             | markdown-it-py for Markdown                   |
| [0004](0004-url-scheme.md)                 | URLs derived from the folder structure        |
| [0005](0005-dev-server.md)                 | Dev server: http.server + SSE + watchfiles    |

Template: Status, Context, Decision, Alternatives considered, Consequences. Keep it under a page.
