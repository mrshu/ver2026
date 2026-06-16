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

For the main website table and the summary analysis, the most useful version is
`celkovy__top2_per_100_emp`: overall top-two quality profile percentage points
per 100 employees.

## Interpretation

Higher values mean a smaller evaluated unit achieved a higher share of
excellent or very good overall profile. That can be useful for spotting compact
teams that perform well, but it has two important limitations:

- It is sensitive to very small headcounts, so the homepage summary uses a
  minimum of 10 employees.
- It does not measure money. If budget or grant-spend data becomes available,
  this metric should be replaced or complemented by a real cost-normalized
  measure.

## Reproducing the ranking

The website computes the top table from `web/data.json`, limited to the three
FMFI-related areas:

- Matematické vedy
- Fyzikálne vedy
- Informačné a komunikačné vedy

The same idea can be reproduced from the CLI:

```bash
uv run ver2026 list \
  --area "Informačné a komunikačné vedy" \
  --min-employees 10 \
  --by celkovy__top2_per_100_emp \
  --limit 10
```

For all areas, omit `--area`. For a stricter comparison, raise
`--min-employees`.

## Current readout for FMFI-related areas

Using a minimum of 10 employees, the proxy gives this interpretation:

- In **Matematické vedy**, FMFI UK is 2nd of 5 sizeable evaluated units by
  headcount efficiency. It has the strongest absolute overall profile in the
  area, but UPJŠ Košice gets more profile percentage points per employee
  because it is much smaller.
- In **Fyzikálne vedy**, FMFI UK is 1st by absolute overall profile but 6th of
  6 sizeable evaluated units by the per-head proxy. This is the clearest case
  where scale changes the story: FMFI has 109 employees in this area.
- In **Informačné a komunikačné vedy**, FMFI UK is 4th by absolute overall
  profile and 8th of 13 sizeable evaluated units by the per-head proxy. Compact
  institutions such as UCM Trnava and UPJŠ Košice rank higher on this proxy.

Top entries by `celkovy__top2_per_100_emp`:

| Oblasť | # | Inštitúcia | Zam. | Celkový 1+2 | Efektivita / 100 zam. |
|--------|---|------------|------|-------------|------------------------|
| Matematické vedy | 1 | Univerzita Pavla Jozefa Šafárika v Košiciach | 21 | 33.6 % | 160.0 |
| Matematické vedy | 2 | Univerzita Komenského v Bratislave / FMFI | 53 | 75.7 % | 142.9 |
| Matematické vedy | 3 | Matematický ústav SAV, v. v. i. | 27 | 36.5 % | 135.0 |
| Fyzikálne vedy | 1 | Univerzita Pavla Jozefa Šafárika v Košiciach | 42 | 51.3 % | 122.3 |
| Fyzikálne vedy | 2 | Slovenská technická univerzita v Bratislave | 42 | 48.5 % | 115.6 |
| Fyzikálne vedy | 3 | Astronomický ústav SAV, v. v. i. | 26 | 27.1 % | 104.2 |
| Informačné a komunikačné vedy | 1 | Univerzita sv. Cyrila a Metoda v Trnave | 11 | 66.4 % | 603.6 |
| Informačné a komunikačné vedy | 2 | Univerzita Pavla Jozefa Šafárika v Košiciach | 16 | 47.7 % | 298.1 |
| Informačné a komunikačné vedy | 3 | Univerzita Mateja Bela v Banskej Bystrici | 10 | 28.1 % | 280.5 |

The ICT numbers show why the metric should be read as a prompt for further
inspection rather than a final ranking. An 11-person evaluated unit with a good
profile will naturally score very high per employee.
