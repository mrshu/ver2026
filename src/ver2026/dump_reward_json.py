"""Dump VER 2022 -> VER 2026 reward allocation comparison to JSON."""
from __future__ import annotations

import argparse
from pathlib import Path

from .reward import SUBSIDY_2026_XLSX_URL, VER2026_XLSX_URL, write_reward_comparison

DEFAULT_OUT = Path(__file__).resolve().parent.parent.parent / "web" / "reward" / "data.json"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--ver2022",
        default=SUBSIDY_2026_XLSX_URL,
        help="Path or URL to the 2026 subsidy XLSX with sheet T14a-ver2022",
    )
    p.add_argument(
        "--ver2026",
        default=VER2026_XLSX_URL,
        help="Path or URL to the VER 2026 results XLSX",
    )
    p.add_argument("--out", default=str(DEFAULT_OUT), help="Output JSON path")
    args = p.parse_args()

    comparison = write_reward_comparison(args.ver2022, args.ver2026, args.out)
    view_counts = ", ".join(
        f"{name}: {len(view['rows'])}"
        for name, view in comparison["views"].items()
    )
    print(
        f"Wrote reward comparison to {args.out} ({view_counts}); "
        f"pool {comparison['method']['pool_eur']:,.0f} EUR"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
