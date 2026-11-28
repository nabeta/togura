# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Togura (「極めてシンプルな機関リポジトリ」) is a Python CLI built with [Typer](https://typer.tiangolo.com/). It manages repository records as YAML files (JPCOAR 2.0 metadata) and generates a static site, JPCOAR/JaLC XML, RO-Crate and ResourceSync output from them. Source lives under `src/togura/` (src layout). Code comments and user-facing messages are in Japanese.

## Setup

```bash
uv sync
```

The project uses `uv` (`uv.lock`, `.python-version`). There is no `dev` extra; `ruff` is not a project dependency, so run it with `uvx`.

## Commands

| Task | Command |
|------|---------|
| Run CLI | `uv run togura` |
| Run tests | `uv run pytest` |
| Run single test | `uv run pytest tests/test_migrate.py::test_whole_document_matches_sample` |
| Lint | `uvx ruff check .` |
| Format | `uvx ruff format .` |

`src/togura/migrate.py` has a few pre-existing `ruff check` warnings (import order, PIE804, SIM102); don't treat them as regressions.

## Architecture

- `src/togura/cli.py` — CLI entry point (`togura = "togura.cli:app"`) and the implementation of its commands: `init`, `setup`, `generate`, `migrate`, `check-expired-embargo`, `validate`, and the `work-file` sub-app.
- `src/togura/migrate.py` — harvests JPCOAR XML over OAI-PMH (`oaipmh_scythe.Scythe`) and writes one `jpcoar20.yaml` per record. Inverse of `jpcoar.py`.
- `src/togura/jpcoar.py` — converts `jpcoar20.yaml` to JPCOAR 2.0 XML.
- `src/togura/jalc.py`, `ro_crate.py`, `resourcesync.py`, `html.py` — other output formats; `templates/` holds the HTML templates.
- `src/togura/schema/jpcoar.yaml` / `jpcoar.json` — JSON Schema for `jpcoar20.yaml`. Keep the two files in sync.
- `src/togura/samples/<NN_name>/jpcoar20.yaml` — sample records copied into new projects by `togura init`, and used as fixtures by several tests.

## YAML key conventions

The YAML keys must agree across `schema/jpcoar.json`, `jpcoar.py` (reader) and `migrate.py` (writer). When they disagree, `jpcoar.py` and the schema are the reference. Examples: `jpcoar_publisher[].publication_place`, `conference[].conference_date.start_day` (integers), `conference[].conference_country.conference_country`, `holding_agent.holding_agent_name_identifier.identifier`, `dataset_series` (boolean), name identifiers use the `nameIdentifierURI` as `identifier` when present.

## Tests

- `tests/test_migrate.py` — round-trip test: each `tests/samples/<NN_name>.xml` (JPCOAR 2.0 sample XML) is fed through `migrate.migrate()` with `Scythe` mocked, and the output must equal `src/togura/samples/<NN_name>/jpcoar20.yaml`. Cases are discovered automatically from XML files that have a matching sample directory.
- Treat the XML files in `tests/samples/` as the source of truth: if migration output and a sample YAML disagree, fix `migrate.py` or the sample YAML, never the XML.
- `tests/test_jpcoar.py`, `test_jalc.py`, `test_html*.py` read the sample YAMLs too, so editing a sample can surface bugs in other converters.
