# VER 2026

A small tool for browsing and sorting the **VER 2026** institutional evaluation
dataset — Slovakia's periodic review of research, development, artistic and
other creative activity at universities and Slovak Academy institutes.

The official results are published at <https://ver.cvtisr.sk/vysledky/>. The
underlying XLSX (`VER2026data`, 270 evaluated institutions, 28 evaluation
fields) is bundled here as `data/VER2026data.xlsx`. This repo gives you:

- A Python package with a clean loader and a sortable dataclass model.
- A command-line tool (`ver2026`) for filtering, sorting, and exporting
  results as JSON.
- A static web viewer (`web/index.html`) that lets you slice, sort, and search
  the full dataset in the browser — no build step, no server, no framework.

## Quick start

```bash
# Install dependencies (uses uv; falls back to pip if uv is unavailable)
uv sync

# Inspect the data
uv run ver2026 summary
uv run ver2026 metrics

# Top 10 institutions in "Informačné a komunikačné vedy" by % of world-class outputs
uv run ver2026 top --area "Informačné a komunikačné vedy" --by vystupy__Svetová

# All VVI (Slovak Academy) institutes, sorted by overall quality (best first)
uv run ver2026 list --type VVI --by celkovy__score --limit 20

# Export filtered+sorted rows as JSON for downstream tooling
uv run ver2026 top --area "Chemické vedy" --by celkovy__score --json --limit 5
```

The same JSON output drives the web viewer:

```bash
# Regenerate web/data.json from the XLSX (the repo already ships a copy)
uv run ver2026-dump

# Serve the web viewer
cd web && python3 -m http.server 8765
# then open http://localhost:8765/
```

## What you can sort and filter by

Every institution row carries four quality profiles, each split into five
levels. The package exposes them as:

| Profile slug           | Slovak label                              | Levels                                                |
|------------------------|-------------------------------------------|-------------------------------------------------------|
| `vystupy`              | Profil kvality výstupov                   | Svetová, Významná medzinárodná, Medzinárodná, ...     |
| `spolocensky_dosah`    | Profil kvality spoločenského dosahu       | Excelentná, Veľmi dobrá, Dobrá, ...                    |
| `tvorive_prostredie`   | Profil kvality tvorivého prostredia       | Excelentná, Veľmi dobrá, Dobrá, ...                    |
| `celkovy`              | Celkový profil kvality                    | Excelentná, Veľmi dobrá, Dobrá, ...                    |

For each profile you can sort by:

- `<slug>__score` — a weighted average 1..5 (1 = best, 5 = worst). `lower is better`.
- `<slug>__top1` — the percentage at the top level (e.g. % of outputs that are
  world-class). `higher is better`.
- `<slug>__top2` — the percentage at the top two levels.
- `<slug>__<LevelName>` — the percentage at one specific level (e.g.
  `vystupy__Svetová` for the % of world-class outputs).

Filters:

- `--area` — exact match on evaluation area (e.g. `"Chemické vedy"`).
- `--group` — exact match on evaluation group (e.g. `"Prírodné vedy"`).
- `--type` — `VVI` (Slovak Academy institute) or `VVŠ` (university / faculty).
- `--min-employees` — minimum head-count.
- `--contains` — case-insensitive substring match against institution name.

## How the data was sourced

I pulled the data straight from the official site. The summary of what I
found on the way:

- The site (<https://ver.cvtisr.sk/vysledky/>) renders the full results table
  for 28 evaluation areas via a WordPress admin-ajax endpoint
  (`POST /wp-admin/admin-ajax.php` with `action=results_prepare_results`,
  `type=evaluation_area`, and a `data[]` list of area IDs). All 28 areas
  together return 270 institution rows.
- The site itself does **not** publish a download. The only machine-readable
  bulk file is the XLSX I copied into `data/VER2026data.xlsx` (it was the
  same file the user already had in `~/Downloads/`).
- The site also publishes one PDF per evaluation area (28 of them) under
  `https://ver.cvtisr.sk/wp-content/uploads/reports/`. Those PDFs are
  qualitative committee reports, not the structured per-institution numbers.
- I did **not** find a separate, more granular open-data mirror of the
  per-institution data on `data.gov.sk` or on the CVTI SR site. The XLSX is
  the most structured form available; the website and the XLSX agree row
  for row.

If a richer source turns up (e.g. an open-data portal release with grant
spend, project IDs, or evaluator comments), the loader in
`src/ver2026/__init__.py` is the only place that would need to change.

## Project layout

```
data/VER2026data.xlsx      # The official dataset, 270 institutions × 28 columns
src/ver2026/
  __init__.py              # Loader, Institution dataclass, filter/sort helpers
  cli.py                   # `ver2026` entry point (summary / list / top / metrics)
  dump_json.py             # `ver2026-dump` entry point, regenerates web/data.json
web/
  index.html               # Static viewer: filter, sort, search the full dataset
  data.json                # The dump consumed by index.html
pyproject.toml             # uv-managed project
```

## Notes on the data

- A handful of rows in the source XLSX have an off-by-one column (one row had
  only 27 of the 28 columns). The loader handles this with `None` and the
  score functions treat missing data as "no signal" (returns the worst score
  of 5.0). I checked — every one of the 270 rows in this snapshot has a
  complete `celkovy` profile.
- Two institution types appear: `VVI` (Slovak Academy institute, 48 rows)
  and `VVŠ` (university / faculty, 222 rows). The viewer shows a coloured
  pill for each.
- Numbers are percentages (0–100) within a profile. The "score" is a simple
  weighted average 1..5 across the five levels; it's intentionally crude so
  you can replace it with whatever you prefer (the dataclass exposes the raw
  five-level vector as `institution.profiles[<slug>]`).
