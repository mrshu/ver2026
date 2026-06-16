"""Fetch and parse structured fields from the official VER results website."""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

from bs4 import BeautifulSoup

AJAX_URL = "https://ver.cvtisr.sk/wp-admin/admin-ajax.php"
RESULTS_URL = "https://ver.cvtisr.sk/vysledky/"
MINISTRY_XLSX_URL = "https://www.minedu.sk/data/att/b00/36762.f7eba0.xlsx"


@dataclass(frozen=True)
class OfficialResult:
    """One row parsed from the public interactive VER results table."""

    eval_area: str
    institution: str
    inst_level: str
    employees: int | None
    financing_eur: int | None
    financing_display: str | None
    official_application_id: str | None
    official_links: dict[str, str]

    @property
    def key(self) -> tuple[str, str, str, int | None]:
        return (
            normalize_key(self.eval_area),
            normalize_key(self.institution),
            normalize_key(self.inst_level),
            self.employees,
        )

    def as_dict(self) -> dict:
        return asdict(self)


def normalize_key(value: str | None) -> str:
    """Normalize official/XLSX labels for matching rows across sources."""
    value = (value or "").replace("\xa0", " ")
    value = re.sub(r"\s+", " ", value).strip().casefold()
    value = re.sub(r"^za súčasť inštitúcie\s*-\s*", "", value)
    return value


def official_key(row) -> tuple[str, str, str, int | None]:
    """Build a comparable key for an XLSX-loaded Institution."""
    return (
        normalize_key(row.eval_area),
        normalize_key(row.institution),
        normalize_key(row.inst_level),
        row.employees,
    )


def _post(action: str, **fields: str | list[str]) -> str:
    data: list[tuple[str, str]] = [("action", action), ("lang", "sk")]
    for key, value in fields.items():
        if isinstance(value, list):
            data.extend((key, str(item)) for item in value)
        else:
            data.append((key, str(value)))

    body = urllib.parse.urlencode(data).encode("utf-8")
    request = urllib.request.Request(
        AJAX_URL,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "ver2026-data-loader/0.1",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def fetch_evaluation_area_ids() -> dict[str, str]:
    """Return mapping of official area label -> public AJAX area ID."""
    html = _post("results_get_evaluation_areas")
    soup = BeautifulSoup(html, "html.parser")
    out: dict[str, str] = {}
    for item in soup.select("input[data-id]"):
        data_id = item.get("data-id")
        label = ""
        if item.get("id"):
            label_el = soup.find("label", attrs={"for": item.get("id")})
            label = label_el.get_text(" ", strip=True) if label_el else ""
        if data_id and label:
            out[label] = data_id
    return out


def _parse_int(value: str | None) -> int | None:
    if not value:
        return None
    digits = re.sub(r"\D+", "", value)
    return int(digits) if digits else None


def _strip_wrapping_parens(value: str) -> str:
    value = value.strip()
    if value.startswith("(") and value.endswith(")"):
        return value[1:-1].strip()
    return value


def _extract_application_id(url: str | None) -> str | None:
    if not url:
        return None
    parsed = urllib.parse.urlparse(url)
    return urllib.parse.parse_qs(parsed.query).get("id", [None])[0]


def parse_results_html(html: str) -> list[OfficialResult]:
    """Parse official result rows from one `results_prepare_results` response."""
    soup = BeautifulSoup(html, "html.parser")
    rows: list[OfficialResult] = []
    for info in soup.select("tr.print-info"):
        detail_row = info.find_next_sibling("tr")
        if detail_row is None:
            continue

        bolds = [b.get_text(" ", strip=True) for b in info.select("b")]
        if not bolds:
            continue
        institution = bolds[0]
        inst_level = _strip_wrapping_parens(bolds[1]) if len(bolds) > 1 else ""

        text = info.get_text(" ", strip=True)
        employees_match = re.search(r"Počet zamestnancov:\s*([0-9 ]+)", text)
        financing_match = re.search(r"Financovanie:\s*([0-9 ]+€)", text)
        area_match = re.search(r"Oblasť hodnotenia:\s*(.+)$", text)

        links: dict[str, str] = {}
        app_id = None
        for link in detail_row.select('a[href*="zobrazit-ziadost"]'):
            label = link.get_text(" ", strip=True)
            href = link.get("href")
            if label and href:
                links[label] = href
                app_id = app_id or _extract_application_id(href)

        rows.append(
            OfficialResult(
                eval_area=area_match.group(1).strip() if area_match else "",
                institution=institution,
                inst_level=inst_level,
                employees=_parse_int(employees_match.group(1) if employees_match else None),
                financing_eur=_parse_int(financing_match.group(1) if financing_match else None),
                financing_display=financing_match.group(1).strip() if financing_match else None,
                official_application_id=app_id,
                official_links=links,
            )
        )
    return rows


def fetch_official_results() -> list[OfficialResult]:
    """Fetch all public official result rows from the interactive VER site."""
    rows: list[OfficialResult] = []
    for area_label, area_id in fetch_evaluation_area_ids().items():
        html = _post(
            "results_prepare_results",
            type="evaluation_area",
            **{"data[]": [area_id]},
        )
        parsed = parse_results_html(html)
        if not parsed:
            raise RuntimeError(f"No official result rows parsed for {area_label!r}")
        rows.extend(parsed)
    return rows


def write_cache(path: str | Path, rows: list[OfficialResult]) -> None:
    Path(path).write_text(
        json.dumps([row.as_dict() for row in rows], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def read_cache(path: str | Path) -> list[OfficialResult]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return [OfficialResult(**item) for item in raw]


def load_or_fetch(path: str | Path, *, refresh: bool = False) -> list[OfficialResult]:
    path = Path(path)
    if path.exists() and not refresh:
        return read_cache(path)
    rows = fetch_official_results()
    write_cache(path, rows)
    return rows
