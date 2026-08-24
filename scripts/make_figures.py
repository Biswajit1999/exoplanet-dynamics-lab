"""Generate publication-style population figures from acquired archive rows."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def style() -> None:
    plt.rcParams.update({"figure.dpi": 160, "axes.grid": True, "grid.alpha": 0.18, "font.size": 10})


def main() -> None:
    style()
    out = ROOT / "results" / "figures"
    out.mkdir(parents=True, exist_ok=True)
    systems = pd.read_parquet(ROOT / "results" / "system_completeness.parquet")
    ps = pd.read_csv(ROOT / "data" / "raw" / "ps.csv", low_memory=False)
    planets = ps[ps["default_flag"] == 1]
    resonance = pd.read_parquet(ROOT / "results" / "resonance_results.parquet")

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    counts = systems["n_planets"].value_counts().sort_index()
    ax.bar(counts.index, counts.values, color="#256b8f")
    ax.set(xlabel="Confirmed planets per host", ylabel="Host systems", title="Observed catalogue multiplicity")
    ax.text(0.99, 0.97, "Source: NASA Exoplanet Archive ps", transform=ax.transAxes, ha="right", va="top", fontsize=8)
    fig.tight_layout(); fig.savefig(out / "multiplicity.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    ratios = resonance["period_ratio"].clip(upper=4)
    ax.hist(ratios, bins=70, color="#4f8198")
    for ratio, label in [(1.25, "5:4"), (4/3, "4:3"), (1.5, "3:2"), (2, "2:1"), (3, "3:1")]:
        ax.axvline(ratio, color="#a16207", alpha=.6, linewidth=.8); ax.text(ratio, ax.get_ylim()[1]*.94, label, rotation=90, va="top", fontsize=7)
    ax.set(xlabel="Adjacent period ratio (outer / inner)", ylabel="Adjacent pairs", title="Period-ratio architecture (ratios ≤ 4)")
    fig.tight_layout(); fig.savefig(out / "period_ratios.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    sample = planets.dropna(subset=["pl_orbper", "pl_rade"])
    ax.scatter(sample["pl_orbper"], sample["pl_rade"], s=8, alpha=.38, color="#256b8f")
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set(xlabel="Orbital period [days]", ylabel="Planet radius [Earth radii]", title="Confirmed-planet radius–period plane")
    fig.tight_layout(); fig.savefig(out / "radius_period.png"); plt.close(fig)

    summary = json.loads((ROOT / "results" / "archive_summary.json").read_text(encoding="utf-8"))
    (out / "figure_manifest.json").write_text(json.dumps({"source_summary": summary, "figures": ["multiplicity.png", "period_ratios.png", "radius_period.png"]}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

