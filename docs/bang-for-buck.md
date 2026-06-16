# Bang-for-buck analysis

The VER 2026 XLSX does not include budgets, grant income, operating cost, or
salary cost. The only resource-like denominator in the dataset is `Počet
zamestnancov`, so this analysis uses a headcount-efficiency proxy rather than
financial ROI.

## Metric

For each profile, the generated JSON includes:

```text
<profile>__top2_per_100_emp = <profile>__top2 * 100 / employees
```

For the website and CLI leaderboard, the default metric is
`celkovy__top2_per_100_emp`: overall top-two quality profile percentage points
per 100 employees.

## Interpretation

Higher values mean a smaller evaluated unit achieved a higher share of
excellent or very good overall profile. This is useful for spotting compact
teams that perform well, but it has two important limitations:

- It is sensitive to very small headcounts, so the default leaderboard uses a
  minimum of 10 employees.
- It does not measure money. If budget or grant-spend data becomes available,
  this metric should be replaced or complemented by a real cost-normalized
  measure.

## Reproducing the ranking

The homepage leaderboard is reproducible from the CLI:

```bash
uv run ver2026 efficiency
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
