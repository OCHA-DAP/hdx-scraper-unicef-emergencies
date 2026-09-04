# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fetches UNICEF's per-country Emergency Level (L1/L2/L3) classification from
`open.unicef.org/get-map-humanitarian/{year}` (an internal JSON endpoint behind Cloudflare bot
management, not a documented public API) and updates the
[`unicef-level-of-emergencies`](https://data.humdata.org/dataset/unicef-level-of-emergencies)
dataset on HDX in place, replacing what was previously a manual CSV upload. Single-call API,
one global dataset, no per-country loop, no pagination, no deep history (source only exposes
the current + previous year).

## Commands

Environment setup (Python 3.13, managed with `uv`):

```shell
uv sync
```

Run the pipeline (requires `~/.hdx_configuration.yaml` with an HDX key, and `~/.useragents.yaml`
with a `hdx-scraper-unicef-emergencies` entry — see README.md):

```shell
uv run python -m hdx.scraper.unicef_emergencies
```

Run all tests (with coverage, configured in `pyproject.toml`):

```shell
uv run pytest
```

Lint and format:

```shell
uv run ruff check
uv run ruff format
```

Pre-commit (runs ruff on every commit once installed):

```shell
pre-commit install
pre-commit run --all-files
```

Build:

```shell
uv build
```

Adding a dependency: add it to `project.dependencies` in `pyproject.toml` (or `[dependency-groups]`
for test-only deps), then run `uv lock --upgrade` to refresh `uv.lock` (pre-commit also does this
automatically on commit).

## Architecture

- `pipeline.py` — `Pipeline` class: `get_latest_year()` reads the source's year-index endpoint
  and picks the max; `get_emergency_levels(year)` fetches that year's data and derives the
  display-level (`emergency=="Others"` + `hacFlag==1` → "Level 1"; `"Level 2"`/`"Level 3"` pass
  through directly); `generate_dataset()` builds the `Dataset`, adds country locations, and
  writes the single CSV resource.
- `__main__.py` — standard `facade()` orchestration entrypoint; wires up `Retrieve`/`Download`
  and calls `Pipeline.generate_dataset()`.
- `config/project_configuration.yaml` — source URLs, dataset name/title, HXL tags.
- `config/hdx_dataset_static.yaml` — dataset identity fields (org, maintainer, license, etc.).

## Code Style

- Formatted with `ruff` via pre-commit hooks. After changing any Python code, run:

```bash
pre-commit run --all-files
```

- Python ≥ 3.13

## Collaboration Style

- Be objective, not agreeable. Act as a partner, not a sycophant. Push back when you disagree, flag
  tradeoffs honestly, and don't sugarcoat problems.
- Keep explanations brief and to the point.
- Don't rely on recalled knowledge for facts that could be stale (API behaviour, library versions,
  external systems). Search or read the actual source first. If you lack verified information, say
  so rather than speculate.

## Scope of Changes

When fixing a bug or addressing PR feedback, change only what is necessary to resolve the specific
issue. Do not refactor surrounding code, rename variables, adjust formatting, or make improvements
in the same commit unless they are directly required by the fix. Unrelated changes obscure the
intent of the fix and complicate review and blame.

## Decision Records

Non-trivial design decisions are recorded in `docs/decisions/` (see `docs/decisions/README.md`) —
the distilled decision, not the full planning narrative, belongs here.
