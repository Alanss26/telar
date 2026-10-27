.PHONY: install test lint format typecheck check example

install:
	uv sync
	uv run pre-commit install

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .
	uv run ruff check --fix .

typecheck:
	uv run mypy

check: lint typecheck test

# examples/basic is a copy of the starter site; run this after changing src/telar/starter/.
example:
	rm -rf examples/basic
	uv run telar init examples/basic
