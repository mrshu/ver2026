"""Dump the full VER 2026 dataset to JSON for the static viewer."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import PROFILE_GROUPS, load
from .official_web import (
    MINISTRY_XLSX_URL,
    RESULTS_URL,
    load_or_fetch,
    official_key,
)

DEFAULT_DATA = Path(__file__).resolve().parent.parent.parent / "data" / "VER2026data.xlsx"
DEFAULT_OFFICIAL = Path(__file__).resolve().parent.parent.parent / "data" / "VER2026official.json"
DEFAULT_OUT = Path(__file__).resolve().parent.parent.parent / "web" / "data.json"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--data", default=str(DEFAULT_DATA))
    p.add_argument("--official-results", default=str(DEFAULT_OFFICIAL))
    p.add_argument(
        "--refresh-official",
        action="store_true",
        help="Fetch financing/detail data from the official interactive VER website.",
    )
    p.add_argument("--out", default=str(DEFAULT_OUT))
    args = p.parse_args()

    rows = load(args.data)
    official_rows = load_or_fetch(args.official_results, refresh=args.refresh_official)
    official_by_key = {row.key: row for row in official_rows}
    matched = 0
    for row in rows:
        official = official_by_key.get(official_key(row))
        if not official:
            continue
        row.financing_eur = official.financing_eur
        row.financing_display = official.financing_display
        row.official_application_id = official.official_application_id
        row.official_links = official.official_links
        matched += 1

    profile_meta = {
        slug: {"label": label, "levels": levels}
        for slug, (label, _, levels) in PROFILE_GROUPS.items()
    }

    eval_areas = sorted({r.eval_area for r in rows})
    eval_groups = sorted({r.eval_group for r in rows})
    inst_types = sorted({r.inst_type for r in rows})

    out = {
        "sources": {
            "official_results": RESULTS_URL,
            "official_xlsx": MINISTRY_XLSX_URL,
            "local_xlsx": "data/VER2026data.xlsx",
            "official_web_cache": str(Path(args.official_results)),
        },
        "merge_stats": {
            "xlsx_rows": len(rows),
            "official_rows": len(official_rows),
            "matched_rows": matched,
            "unmatched_xlsx_rows": len(rows) - matched,
        },
        "profile_meta": profile_meta,
        "eval_areas": eval_areas,
        "eval_groups": eval_groups,
        "inst_types": inst_types,
        "institutions": [r.as_dict() for r in rows],
    }
    Path(args.out).write_text(
        json.dumps(out, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(
        f"Wrote {len(rows)} institutions to {args.out}; "
        f"merged official financing for {matched}/{len(rows)} rows"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
