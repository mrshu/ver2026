"""Dump the full VER 2026 dataset to JSON for the static viewer."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import PROFILE_GROUPS, load

DEFAULT_DATA = Path(__file__).resolve().parent.parent.parent / "data" / "VER2026data.xlsx"
DEFAULT_OUT = Path(__file__).resolve().parent.parent.parent / "web" / "data.json"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--data", default=str(DEFAULT_DATA))
    p.add_argument("--out", default=str(DEFAULT_OUT))
    args = p.parse_args()

    rows = load(args.data)

    profile_meta = {
        slug: {"label": label, "levels": levels}
        for slug, (label, _, levels) in PROFILE_GROUPS.items()
    }

    eval_areas = sorted({r.eval_area for r in rows})
    eval_groups = sorted({r.eval_group for r in rows})
    inst_types = sorted({r.inst_type for r in rows})

    out = {
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
    print(f"Wrote {len(rows)} institutions to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
