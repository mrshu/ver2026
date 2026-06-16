"""CLI for browsing and sorting the VER 2026 institution evaluations.

Examples:

    # Top 10 institutions in "Informačné a komunikačné vedy" by % of world-class outputs.
    uv run ver2026 top --area "Informačné a komunikačné vedy" --by vystupy__Svetová

    # All VVI institutes, sorted by overall quality score.
    uv run ver2026 list --type VVI --by celkovy__score

    # All institutions, no filter, sorted by % of social impact rated "Excellent".
    uv run ver2026 list --by spolocensky_dosah__Excelentná
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import PROFILE_GROUPS, filter_rows, load, sort_rows

DEFAULT_DATA = Path(__file__).resolve().parent.parent.parent / "data" / "VER2026data.xlsx"


def _fmt_pct(v):
    return f"{v:5.1f}%" if v is not None else "  -  "


def _fmt_int(v):
    return f"{v:>4}" if v is not None else "  - "


def render_table(rows, *, columns=None) -> str:
    """Pretty-print a slice of institutions as a fixed-width table."""
    if columns is None:
        columns = [
            ("area",        "Oblasť",        lambda r: r.eval_area),
            ("institution", "Inštitúcia",    lambda r: r.institution),
            ("level",       "Úroveň",        lambda r: r.inst_level),
            ("type",        "Typ",           lambda r: r.inst_type),
            ("emp",         "Zam",           lambda r: _fmt_int(r.employees)),
            ("v1",          "VýSvet%",       lambda r: _fmt_pct(r.top_pct("vystupy"))),
            ("v2",          "VTop2%",        lambda r: _fmt_pct(r.top_two_pct("vystupy"))),
            ("c1",          "CExcel%",       lambda r: _fmt_pct(r.top_pct("celkovy"))),
            ("c2",          "CTop2%",        lambda r: _fmt_pct(r.top_two_pct("celkovy"))),
            ("cs",          "CScore",        lambda r: f"{r.score('celkovy'):.2f}"),
        ]
    header = "  ".join(h for _, h, _ in columns)
    lines = [header, "-" * len(header)]
    for r in rows:
        cells = [str(fn(r)) for _, _, fn in columns]
        lines.append("  ".join(cells))
    return "\n".join(lines)


def cmd_top(args) -> int:
    data = load(args.data)
    rows = filter_rows(
        data,
        eval_area=args.area,
        eval_group=args.group,
        inst_type=args.type,
        min_employees=args.min_employees,
        institution_contains=args.contains,
    )
    rows = sort_rows(rows, by=args.by, descending=not args.ascending)
    rows = rows[: args.limit]
    if args.json:
        print(json.dumps([r.as_dict() for r in rows], ensure_ascii=False, indent=2))
    else:
        print(render_table(rows))
    return 0


def cmd_list(args) -> int:
    data = load(args.data)
    rows = filter_rows(
        data,
        eval_area=args.area,
        eval_group=args.group,
        inst_type=args.type,
        min_employees=args.min_employees,
        institution_contains=args.contains,
    )
    rows = sort_rows(rows, by=args.by, descending=not args.ascending)
    if args.json:
        print(json.dumps([r.as_dict() for r in rows], ensure_ascii=False, indent=2))
    else:
        print(render_table(rows[: args.limit]))
    return 0


def cmd_summary(args) -> int:
    data = load(args.data)
    areas = sorted({r.eval_area for r in data})
    types = sorted({r.inst_type for r in data})
    groups = sorted({r.eval_group for r in data})
    print(f"Total institutions: {len(data)}")
    print(f"Evaluation areas:   {len(areas)}")
    for a in areas:
        print(f"  - {a}")
    print()
    print(f"Institution types:  {', '.join(types)}")
    print(f"Evaluation groups:  {', '.join(groups)}")
    return 0


def cmd_metrics(args) -> int:
    print("Available sort/filter keys (use with --by):")
    for slug, (label, _, levels) in PROFILE_GROUPS.items():
        print(f"  {label}:")
        print(f"    {slug}__score  (weighted score 1..5, lower = better)")
        print(f"    {slug}__top1   (% at level 1)")
        print(f"    {slug}__top2   (% at levels 1+2)")
        for lvl in levels:
            print(f"    {slug}__{lvl}   (% at level '{lvl}')")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default=str(DEFAULT_DATA), help="Path to VER2026data.xlsx")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--area", help="Filter by evaluation area (exact match)")
    common.add_argument("--group", help="Filter by evaluation group (e.g. 'Prírodné vedy')")
    common.add_argument("--type", choices=["VVI", "VVŠ"], help="Filter by institution type")
    common.add_argument("--min-employees", type=int, help="Minimum number of employees")
    common.add_argument("--contains", help="Substring match against institution name")
    common.add_argument("--by", default="vystupy__Svetová", help="Sort key (run `metrics` to list)")
    common.add_argument("--ascending", action="store_true", help="Sort ascending (default: descending)")
    common.add_argument("--json", action="store_true", help="Emit JSON instead of a table")
    common.add_argument("--limit", type=int, default=20, help="Number of rows to show")

    for name, fn in [("top", cmd_top), ("list", cmd_list)]:
        sp = sub.add_parser(name, parents=[common], help=fn.__doc__)
        sp.set_defaults(func=fn)

    sp = sub.add_parser("summary", help="Print counts and unique values")
    sp.set_defaults(func=cmd_summary)

    sp = sub.add_parser("metrics", help="List all available sort/filter keys")
    sp.set_defaults(func=cmd_metrics)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
