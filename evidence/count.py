"""Count pain tags in anonymized theme-park reviews (Python stdlib only)."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent / "reviews_anon.csv"

PAIN_TAGS = (
    "xep_hang_chong_gio",
    "di_chuyen_rong",
    "thoi_tiet_mua",
    "chi_phi_ve",
    "tre_nho_chieu_cao_tuoi",
    "lo_show_gio_mo_cua",
)

CORE_HYPOTHESIS_TAGS = {"lo_show_gio_mo_cua", "tre_nho_chieu_cao_tuoi"}
PLANNING_OPS_TAGS = {
    "lo_show_gio_mo_cua",
    "tre_nho_chieu_cao_tuoi",
    "di_chuyen_rong",
    "xep_hang_chong_gio",
}


def fmt(x: int, n: int) -> str:
    """Format count as 'x / N (y%)'."""
    pct = (x / n * 100.0) if n else 0.0
    return f"{x} / {n} ({pct:.1f}%)"


def parse_tags(raw: str) -> list[str]:
    """Parse semicolon-separated pain tags from CSV cell."""
    return [t.strip() for t in raw.split(";") if t.strip()]


def summarize(rows: list[dict[str, str]], label: str) -> None:
    """Print reproducible counts for a subset of rows."""
    n = len(rows)
    tag_counts: Counter[str] = Counter()
    any_pain = 0
    core_hypothesis = 0
    planning_ops = 0

    for row in rows:
        tags = set(parse_tags(row["pain_tags"]))
        for tag in tags:
            tag_counts[tag] += 1
        if tags:
            any_pain += 1
        if tags & CORE_HYPOTHESIS_TAGS:
            core_hypothesis += 1
        if tags & PLANNING_OPS_TAGS:
            planning_ops += 1

    print(f"=== {label} (N = {n}) ===")
    print(f"any_pain (it nhat 1 pain): {fmt(any_pain, n)}")
    print(
        f"core_hours_show_or_kids (lo_show_gio_mo_cua HOAC tre_nho_chieu_cao_tuoi): "
        f"{fmt(core_hypothesis, n)}"
    )
    print(
        f"planning_ops_pain (lo_show/tre_nho/di_chuyen_rong/xep_hang): "
        f"{fmt(planning_ops, n)}"
    )
    for tag in PAIN_TAGS:
        print(f"  {tag}: {fmt(tag_counts[tag], n)}")

    extra_tags = sorted(set(tag_counts) - set(PAIN_TAGS))
    for tag in extra_tags:
        print(f"  [extra] {tag}: {fmt(tag_counts[tag], n)}")
    print()


def main() -> None:
    """Load reviews_anon.csv and print overall, family/kids, and per-place counts."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    with CSV_PATH.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    summarize(rows, "Toan bo tap review da loc (Overall)")

    family_rows = [r for r in rows if r["has_family_kids"].strip().lower() == "true"]
    summarize(family_rows, "Tap nhac toi gia dinh / tre nho (has_family_kids = true)")

    places = sorted({r["place"] for r in rows})
    for place in places:
        place_rows = [r for r in rows if r["place"] == place]
        summarize(place_rows, f"Dia diem: {place}")


if __name__ == "__main__":
    main()
