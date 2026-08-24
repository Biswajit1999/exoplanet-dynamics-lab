"""Refresh the README statistics block from generated results."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    summary = json.loads((ROOT / "results" / "archive_summary.json").read_text(encoding="utf-8"))
    rows = [
        ("Genuine source rows surveyed", "archive_rows_surveyed"),
        ("Confirmed planets", "confirmed_planets"),
        ("Host systems", "host_systems"),
        ("Multi-planet systems", "multi_planet_systems"),
        ("High-multiplicity systems (≥6)", "high_multiplicity_systems"),
        ("Tier A systems", "tier_a_systems"),
        ("Tier B systems", "tier_b_systems"),
        ("Near-commensurate adjacent pairs", "near_commensurate_pairs"),
    ]
    table = "<!-- BEGIN GENERATED STATS -->\n| Quantity | Generated value |\n|---|---:|\n"
    table += "\n".join(f"| {label} | **{int(summary[key]):,}** |" for label, key in rows)
    table += "\n<!-- END GENERATED STATS -->"
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    updated = re.sub(r"<!-- BEGIN GENERATED STATS -->.*?<!-- END GENERATED STATS -->", table, text, flags=re.DOTALL)
    readme.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    main()
