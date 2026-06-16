"""Tests for the VER 2026 loader and sort/filter helpers."""
from __future__ import annotations

from pathlib import Path

import pytest

from ver2026 import filter_rows, load, sort_rows
from ver2026.cli import main
from ver2026.official_web import parse_results_html

DATA = Path(__file__).resolve().parent.parent / "data" / "VER2026data.xlsx"


@pytest.fixture(scope="module")
def data():
    return load(DATA)


def test_load_returns_all_270_institutions(data):
    assert len(data) == 270


def test_profiles_are_populated(data):
    # Every row should have 4 profiles × 5 levels each.
    for r in data:
        assert set(r.profiles.keys()) == {"vystupy", "spolocensky_dosah", "tvorive_prostredie", "celkovy"}
        for slug, levels in r.profiles.items():
            assert len(levels) == 5, f"{r.institution} {slug} has {len(levels)} levels"
            assert all(0 <= (p or 0) <= 100 for p in levels)


def test_score_lower_is_better(data):
    # The institution with the highest % world-class outputs should have the
    # lowest (best) vystupy score among rows where any outputs are scored.
    scored = sorted(data, key=lambda r: r.score("vystupy"))
    best = scored[0]
    worst = scored[-1]
    assert best.score("vystupy") <= worst.score("vystupy")


def test_filter_by_area(data):
    chem = filter_rows(data, eval_area="Chemické vedy")
    assert all(r.eval_area == "Chemické vedy" for r in chem)
    assert len(chem) > 0


def test_filter_by_type_vvi(data):
    vvi = filter_rows(data, inst_type="VVI")
    assert all(r.inst_type == "VVI" for r in vvi)
    assert len(vvi) == 48


def test_filter_by_contains(data):
    sav = filter_rows(data, institution_contains="akadémie vied")
    assert all("akadémie vied" in r.institution.lower() for r in sav)
    assert len(sav) > 0


def test_sort_by_overall_score_ascending(data):
    rows = sort_rows(data, by="celkovy__score", descending=False)
    # First rows should have the lowest (best) scores.
    assert rows[0].score("celkovy") <= rows[-1].score("celkovy")


def test_top1_sums_correctly(data):
    # For the vystupy profile, top1 + top2 = sum of first two levels.
    r = data[0]
    assert r.top_pct("vystupy") == r.profiles["vystupy"][0]
    assert r.top_two_pct("vystupy") == r.profiles["vystupy"][0] + r.profiles["vystupy"][1]


def test_top_two_per_100_employees(data):
    row = next(r for r in data if r.employees)
    assert row.top_two_per_100_employees("celkovy") == pytest.approx(
        row.top_two_pct("celkovy") * 100 / row.employees
    )
    assert row.as_dict()["celkovy__top2_per_100_emp"] == pytest.approx(
        row.top_two_per_100_employees("celkovy")
    )


def test_money_normalized_metrics_can_be_computed(data):
    row = next(r for r in data if r.employees)
    row.financing_eur = 2_000_000
    assert row.financing_per_employee() == pytest.approx(2_000_000 / row.employees)
    assert row.top_two_per_million_eur("celkovy") == pytest.approx(
        row.top_two_pct("celkovy") / 2
    )
    as_dict = row.as_dict()
    assert as_dict["financing_eur"] == 2_000_000
    assert as_dict["celkovy__top2_per_million_eur"] == pytest.approx(
        row.top_two_per_million_eur("celkovy")
    )


def test_parse_official_results_html_extracts_financing_and_links():
    html = """
    <table><tbody>
      <tr class="print-info">
        <td><b>Univerzita Komenského v Bratislave</b>
        <b>(Fakulta matematiky, fyziky a informatiky)</b><br>
        Počet zamestnancov: 53 • Financovanie: 10 373 579€
        • Oblasť hodnotenia: Matematické vedy</td>
      </tr>
      <tr>
        <td><a href="https://ver.cvtisr.sk/vysledky/zobrazit-ziadost/?id=7560&show=final-outputs-list">Výstupy</a></td>
        <td><a href="https://ver.cvtisr.sk/vysledky/zobrazit-ziadost/?id=7560&show=creative-environment">Tvorivé prostredie</a></td>
      </tr>
    </tbody></table>
    """
    rows = parse_results_html(html)
    assert len(rows) == 1
    row = rows[0]
    assert row.eval_area == "Matematické vedy"
    assert row.institution == "Univerzita Komenského v Bratislave"
    assert row.inst_level == "Fakulta matematiky, fyziky a informatiky"
    assert row.employees == 53
    assert row.financing_eur == 10_373_579
    assert row.official_application_id == "7560"
    assert "Výstupy" in row.official_links


def test_sort_by_top_two_per_100_employees(data):
    rows = [r for r in data if r.employees]
    ranked = sort_rows(rows, by="celkovy__top2_per_100_emp", descending=True)
    assert ranked[0].top_two_per_100_employees("celkovy") >= ranked[-1].top_two_per_100_employees(
        "celkovy"
    )


def test_efficiency_cli_outputs_reproducible_table(capsys):
    rc = main(["efficiency", "--limit", "3"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "CTop2/100zam" in out
    assert "Ústav orientalistiky Slovenskej akadémie vied" in out


def test_money_cli_outputs_financing_table(capsys):
    rc = main(["money", "--limit", "2"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "CTop2/1M€" in out
    assert "Financovanie" in out


def test_fmfi_summary_values_match_reference_table(data):
    """Guard the FMFI UK three-area summary shown by the static viewer."""
    expected = {
        "Matematické vedy": (53, 68.0, 87.5, 100.0, 75.7, 1, 8),
        "Fyzikálne vedy": (109, 68.0, 33.3, 75.0, 63.9, 1, 6),
        "Informačné a komunikačné vedy": (45, 52.0, 100.0, 100.0, 66.4, 4, 15),
    }

    for area, values in expected.items():
        area_rows = [r for r in data if r.eval_area == area]
        fmfi = next(
            r for r in area_rows
            if r.institution == "Univerzita Komenského v Bratislave"
            and "Fakulta matematiky, fyziky a informatiky" in r.inst_level
        )
        ranked = sorted(area_rows, key=lambda r: r.score("celkovy"))
        actual = (
            fmfi.employees,
            round(fmfi.top_two_pct("vystupy"), 1),
            round(fmfi.top_two_pct("spolocensky_dosah"), 1),
            round(fmfi.top_two_pct("tvorive_prostredie"), 1),
            round(fmfi.top_two_pct("celkovy"), 1),
            ranked.index(fmfi) + 1,
            len(area_rows),
        )

        assert actual == values
