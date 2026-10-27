# Contributing to Telar

Thanks for wanting to help! Telar is a small personal project, so the bar is simple: changes
should keep the code easy to read and the scope tight.

## Before you start

- **Check the [roadmap](ROADMAP.md).** If what you want isn't there, or it's in Priority 3,
  open an issue first so we can agree on the approach before you write code.
- **Big decisions get an ADR.** If your change picks a new dependency, changes the URL scheme,
  or adds a public API, add a short record to [docs/decisions/](docs/decisions/) (copy an
  existing one).

## Setup

You need [uv](https://docs.astral.sh/uv/) and git.

```sh
git clone https://github.com/Alanss26/telar.git
cd telar
make install    # uv sync + pre-commit install
make check      # everything CI runs: lint, format check, mypy, tests
```

No `make`? Run the commands from the [README](README.md#development) directly.

To try your changes on a real site:

```sh
uv run telar dev examples/basic
```

## Code style

- **Readable over clever.** Someone new should be able to follow every line. Prefer a plain loop
  over a dense one-liner.
- **Type hints everywhere.** mypy runs in strict mode.
- **Comments explain why, not what.** If the code needs a comment to say what it does, try
  making the code clearer first.
- **Errors the user can fix are `SiteError`s**, with a file and line when possible. Don't let a
  raw exception reach the user for something like a typo in their front matter.
- Ruff handles formatting and import order; pre-commit runs it on every commit.
- Code, comments, commits and docs are in English.

## Tests

- Every module has its own `tests/test_<module>.py`. Add tests next to the code you change.
- Use `tmp_path` and write tiny sites; the `site` fixture in `tests/conftest.py` gives you a
  complete one.
- `tests/test_integration.py` builds `examples/basic` end to end.
- Changed the starter site in `src/telar/starter/`? Run `make example` to regenerate
  `examples/basic`, or `test_scaffold.py` will fail.
- For bug fixes, write the failing test first.

## Commits and pull requests

Use [Conventional Commits](https://www.conventionalcommits.org/):

```text
feat: add sitemap.xml generation
fix: keep the line number for YAML errors in nested keys
docs: explain collections in the README
test: cover duplicate URLs across folders
refactor: split route_for out of content.py
chore: bump ruff
```

Before opening a PR:

- [ ] `make check` passes.
- [ ] New behaviour has tests.
- [ ] README, ARCHITECTURE or an ADR are updated if the change affects them.
- [ ] No new runtime dependency without a reason in the PR (and probably an ADR).

## Working from WSL

If the repo lives on the Windows drive (`/mnt/c/...`):

- Add `export UV_LINK_MODE=copy` to your `~/.bashrc`. uv can't hardlink across filesystems and
  would warn on every sync.
- Use `telar dev --poll`. Edits made from Windows don't reach Linux's file watcher otherwise.

Keeping the repo inside the WSL filesystem (`~/telar`) avoids both.

## License

By contributing you agree that your contributions are licensed under the [MIT License](LICENSE).
