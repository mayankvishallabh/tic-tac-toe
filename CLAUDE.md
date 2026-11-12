# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project state

This is a freshly scaffolded `uv` project (`uv init --package`). The only code is a placeholder `main()` in `src/tic_tac_toe/__init__.py`; there are no tests yet and the README is empty. Game logic has not been written.

## Tooling

- Python **3.14** (pinned in `.python-version`, `requires-python = ">=3.14"`), managed with **uv**; build backend is `uv_build`.
- No runtime dependencies. Dev group: `pytest`, `ruff`.
- Use `uv` for everything — do not use `pip` directly. Add deps with `uv add <pkg>` (or `uv add --dev <pkg>`), which updates `pyproject.toml` and `uv.lock`.

## Commands

```bash
uv sync                          # create .venv and install project + dev deps
uv run tic-tac-toe               # run the CLI entry point (tic_tac_toe:main)
uv run pytest                    # run all tests
uv run pytest tests/test_x.py::test_name   # run a single test
uv run ruff check .              # lint
uv run ruff check --fix .        # lint with autofix
uv run ruff format .             # format
```

## Layout

- `src/` layout: the package is `src/tic_tac_toe/`. The console script `tic-tac-toe` maps to `tic_tac_toe:main`, so `main` must stay importable from the package root (`__init__.py`) or the `[project.scripts]` entry must be updated.
- Tests do not exist yet; put them in a top-level `tests/` directory so `uv run pytest` discovers them.


# Tic-Tac-Toe — instructions for Claude

## About me
- I'm learning professional Python development. I've done small hobby projects in R and Python.
- Before a big change, explain your plan in plain English.
- The first time you use a concept I may not know (type hints, dataclasses, enums, pytest fixtures,
  minimax...), explain it in 2–3 sentences.

## Commenting style (important)
- Comment heavily. I want to be able to read any file top to bottom and understand it.
- Every file starts with a docstring: what the file is for and how it fits into the project.
- Every function and class has a Google-style docstring: what it does, Args, Returns, Raises,
  and a short example where helpful.
- Inside functions, put a comment above each logical step explaining WHY, not just what.
- Prefer clear, explicit code over clever one-liners.

## Project structure
- Source code: src/tic_tac_toe/. Tests: tests/ (one test file per module).
- board.py, game.py and players.py must never call print() or input().
  All terminal input/output lives in cli.py.

## Commands
- Python 3.14, managed by uv. Never use pip. Add packages with `uv add <pkg>`
  (development tools: `uv add --dev <pkg>`).
- Run the game: `uv run tic-tac-toe`
- Run tests: `uv run pytest`
- Lint and format: `uv run ruff check --fix .` then `uv run ruff format .`

## How to work
- Work in small steps. After each change, run the tests and ruff, and fix anything they report.
- Write or update tests for every new behaviour.
- Use type hints on every function signature.
- Never commit, push or create branches unless I ask.
- Commit messages: imperative subject under 50 characters ("Add win detection"), then a blank line and a short body explaining why.