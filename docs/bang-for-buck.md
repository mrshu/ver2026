# Veľkostne a finančne normalizovaná analýza

The Ministry XLSX does not include budgets or funding, but the official
interactive VER results expose `Financovanie` for every evaluated row. The
static dataset therefore merges two official sources:

- Ministry XLSX: profile percentages, employee counts, institution metadata.
- VER interactive results: `Financovanie` and public detail links.

The VER explanation defines `Financovanie` as total research funding for
2020-2024 from state subsidy, competitive grants/EU sources, and other sources.

## Metric

For each profile, the generated JSON includes:

```text
<profile>__top2_per_100_emp = <profile>__top2 * 100 / employees
```

For money-normalized comparisons, it also includes:

```text
<profile>__top2_per_million_eur = <profile>__top2 * 1_000_000 / financing_eur
financing_per_employee_eur = financing_eur / employees
```

For the website and CLI leaderboard, the default metric is
`celkovy__top2_per_100_emp`: overall top-two quality profile percentage points
per 100 employees.

The money view defaults to `celkovy__top2_per_million_eur`: overall top-two
quality profile percentage points per EUR 1M of official 2020-2024 funding.

## Interpretation

Higher values mean a smaller evaluated unit achieved a higher share of
excellent or very good overall profile. This is useful for spotting compact
workplaces that perform well, but it has two important limitations:

- It is sensitive to very small headcounts, so the default leaderboard uses a
  minimum of 10 employees.
- `Financovanie` is funding, not full institutional cost. It should not be
  interpreted as complete operating expenditure, payroll cost, or ROI.
- Money-normalized metrics can over-reward small or low-funded units. Use them
  as prompts for closer comparison inside an evaluation area, not as a final
  ranking of institutional value.

## Reproducing the ranking

The size-normalized analysis is available as a pre-built website link:

```text
http://localhost:8766/?sort=celkovy__top2_per_100_emp&dir=desc&min_emp=10
```

The money-normalized analysis is available as:

```text
http://localhost:8766/?sort=celkovy__top2_per_million_eur&dir=desc&min_emp=10
```

The same ranking is reproducible from the CLI:

```bash
uv run ver2026 efficiency
```

Money-normalized ranking:

```bash
uv run ver2026 money
```

That command is equivalent to:

```bash
uv run ver2026 efficiency \
  --min-employees 10 \
  --by celkovy__top2_per_100_emp \
  --limit 20
```

Useful variants:

```bash
# One evaluation area only
uv run ver2026 efficiency --area "Informačné a komunikačné vedy"

# Stricter minimum size
uv run ver2026 efficiency --min-employees 25

# Machine-readable output for notebooks or spreadsheets
uv run ver2026 efficiency --json --limit 270
```

The web viewer also stores filters in the URL. The supported query parameters
are:

- `q` - text search across institution name, institutional level, and area
- `area` - exact evaluation area
- `group` - exact evaluation group
- `type` - `VVŠ` or `VVI`
- `min_emp` - minimum employee count
- `sort` - any generated metric key, for example `celkovy__top2_per_100_emp`
- `dir` - `asc` or `desc`

Example:

```text
http://localhost:8766/?q=Fakulta%20matematiky%2C%20fyziky%20a%20informatiky&sort=eval_area
```

That URL recreates a specific filtered table without changing the default page
focus.

## Current dataset-wide readout

Using the default minimum of 10 employees, the top entries by
`celkovy__top2_per_100_emp` are:

| # | Oblasť | Inštitúcia | Zam. | Celkový 1+2 | Efektivita / 100 zam. |
|---|--------|------------|------|-------------|------------------------|
| 1 | Historické vedy | Ústav orientalistiky SAV, v. v. i. | 10 | 92.8 % | 928.0 |
| 2 | Politické vedy | Univerzita Komenského v Bratislave / Fakulta sociálnych a ekonomických vied | 10 | 76.0 % | 760.0 |
| 3 | Historické vedy | Univerzita Pavla Jozefa Šafárika v Košiciach / Filozofická fakulta | 12 | 85.6 % | 713.3 |
| 4 | Filológia | Katolícka univerzita v Ružomberku / Filozofická fakulta | 11 | 78.2 % | 710.9 |
| 5 | Historické vedy | Centrum spoločenských a psychologických vied SAV, v. v. i. | 12 | 78.2 % | 651.7 |
| 6 | Historické vedy | Univerzita Mateja Bela v Banskej Bystrici / Filozofická fakulta | 11 | 68.6 % | 623.6 |
| 7 | Psychológia | Univerzita Komenského v Bratislave / Fakulta sociálnych a ekonomických vied | 10 | 61.6 % | 616.0 |
| 8 | Historické vedy | Trnavská univerzita v Trnave / Filozofická fakulta | 12 | 73.6 % | 613.3 |
| 9 | Politické vedy | Univerzita Komenského v Bratislave / Filozofická fakulta | 10 | 61.2 % | 612.0 |
| 10 | Filológia | Prešovská univerzita v Prešove / Centrum jazykov a kultúr národnostných menšín | 10 | 60.8 % | 608.0 |

This readout shows the main behavior of the proxy: it strongly rewards compact
evaluated units. For broader institutional comparisons, rerun the same command
with a larger `--min-employees` threshold.
