# VER 2026

A small tool for browsing and sorting the **VER 2026** institutional evaluation
dataset — Slovakia's periodic review of research, development, artistic and
other creative activity at universities and Slovak Academy institutes.

The official results are published at <https://ver.cvtisr.sk/vysledky/>. The
Ministry XLSX is published at
<https://www.minedu.sk/data/att/b00/36762.f7eba0.xlsx> and bundled here as
`data/VER2026data.xlsx`. This repo gives you:

- A Python package with a clean loader and a sortable dataclass model.
- A command-line tool (`ver2026`) for filtering, sorting, and exporting
  results as JSON.
- A static web viewer (`web/index.html`) that lets you slice, sort, and search
  the full dataset in the browser — no build step, no server, no framework.
- A static Slovak-language dashboard with pre-built analysis links and
  URL-reproducible filters for sharing specific comparisons.
- A separate static VER 2022 → VER 2026 reward-allocation simulator using the
  T14a method: quality profile weights, employee counts, and area cost
  coefficients.

Live viewer: <https://mrshu.github.io/ver2026/>
Reward simulator: <https://mrshu.github.io/ver2026/reward/>

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

# Size-normalized proxy: overall top-two profile per 100 employees
uv run ver2026 efficiency --min-employees 10 --limit 20

# Money-normalized proxy: overall top-two profile per EUR 1M of funding
uv run ver2026 money --min-employees 10 --limit 20

# Export filtered+sorted rows as JSON for downstream tooling
uv run ver2026 top --area "Chemické vedy" --by celkovy__score --json --limit 5
```

The same JSON output drives the web viewer:

```bash
# Regenerate web/data.json from the XLSX (the repo already ships a copy)
uv run ver2026-dump

# Regenerate the separate VER 2022 → VER 2026 reward simulator data
# Defaults read the official XLSX URLs below; pass --ver2022/--ver2026 for local copies.
uv run ver2026-reward-dump

# Serve the web viewer
cd web && python3 -m http.server 8765
# then open http://localhost:8765/
```

The reward simulator is based on these official sources:

- VER 2026 profiles XLSX:
  <https://www.minedu.sk/data/att/b00/36762.f7eba0.xlsx>
- 2026 public-university subsidy allocation XLSX, sheet `T14a-ver2022`:
  <https://www.minedu.sk/data/att/7c5/35059.48a629.xlsx>
- VER 2022 methodology note:
  <https://www.minedu.sk/metodicke-usmernenie-k-pouzitiu-vysledkov-periodickeho-hodnotenia-ver-2022-pre-ucely-posudenia-kvality-urovne-tvorivej-cinnosti-pri-standardoch-pre-studijny-program/>

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
- `<slug>__top2_per_100_emp` — top-two percentage points per 100 employees.
  This is a headcount-efficiency proxy, not a financial ROI metric.
- `<slug>__top2_per_million_eur` — top-two percentage points per EUR 1M of
  official 2020-2024 financing. This is a derived analysis column, not an
  official VER metric.
- `<slug>__<LevelName>` — the percentage at one specific level (e.g.
  `vystupy__Svetová` for the % of world-class outputs).

The official interactive results also expose:

- `financing_eur` — "Financovanie" from the official website. The VER
  explanation defines it as the total volume of research funding in 2020-2024.
- `financing_per_employee_eur` — `financing_eur / employees`.

The separate reward simulator at `web/reward/` exposes:

- VVŠ-level, evaluation-area-level, and evaluation-group-level views.
- A row-level "Žiadosti / súčasti" view keyed by university, evaluation area,
  and component/faculty/department label, so specific source rows such as a
  faculty or department can be searched directly.
- A fixed T14a 2026 pool redistributed by VER 2026 celkový profil quality
  weights `(8, 5, 3, 1, 0)`, employees, and the T14a area cost coefficient.
- Area and group views aggregate the published application rows from each
  source as separate evaluated rows, then conserve the same fixed T14a pool
  inside that view.
- Row-level entries that cannot be matched between VER 2022 and VER 2026 are
  kept and marked as old-only or new-only rather than silently merged.

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
  together return 270 institution rows, including "Financovanie" values and
  public detail links.
- The Ministry XLSX is published at
  <https://www.minedu.sk/data/att/b00/36762.f7eba0.xlsx>. It contains the
  profile percentages, employee counts, and institution metadata, but not the
  financing column.
- The site also publishes one PDF per evaluation area (28 of them) under
  `https://ver.cvtisr.sk/wp-content/uploads/reports/`. Those PDFs are
  qualitative committee reports, not the structured per-institution numbers.
- I did **not** find a separate, more granular open-data mirror of the
  per-institution data on `data.gov.sk` or on the CVTI SR site. The XLSX is
  the most structured form available; the website and the XLSX agree row
  for row.

The generated static JSON merges both sources. The XLSX remains authoritative
for quality profiles; the official interactive site is authoritative for
financing and detail links.

## Project layout

```
data/VER2026data.xlsx      # The official dataset, 270 institutions × 28 columns
data/VER2026official.json  # Scraped official web rows with financing/detail links
docs/bang-for-buck.md      # Size-normalized analysis notes
docs/fmfi-summary.md       # How the FMFI UK reference rows are reproduced
src/ver2026/
  __init__.py              # Loader, Institution dataclass, filter/sort helpers
  cli.py                   # `ver2026` entry point (summary / list / top / metrics)
  dump_json.py             # `ver2026-dump` entry point, regenerates web/data.json
  dump_reward_json.py      # `ver2026-reward-dump`, derives web/reward/data.json
  official_web.py          # Scraper/parser for public VER website fields
  reward.py                # VER 2022 → VER 2026 reward-allocation methodology
web/
  index.html               # Static viewer: filter, sort, search the full dataset
  data.json                # The dump consumed by index.html
  reward/index.html        # Separate T14a reward simulator
  reward/data.json         # The dump consumed by reward/index.html
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
- Numbers are percentages (0–100) within a profile. The "score" is a weighted
  average across the five levels: `(1*p1 + 2*p2 + 3*p3 + 4*p4 + 5*p5) / 100`.
  It uses all five buckets, so two rows with the same 1+2 percentage can have
  different scores.
- `Financovanie` is scraped from the public interactive results and matched
  back to all 270 XLSX rows. It is official funding data for 2020-2024, but
  the money-normalized ratios in this repo are exploratory analysis, not
  official VER methodology.
