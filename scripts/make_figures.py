"""Generate publication-style population figures from acquired archive rows."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
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

    convergence = pd.read_csv(ROOT / "results" / "timestep_convergence.csv")
    phase = pd.read_csv(ROOT / "results" / "phase_prior_sensitivity.csv")
    trajectory = json.loads(
        (ROOT / "results" / "simulations" / "stability_trajectory.json").read_text(
            encoding="utf-8"
        )
    )
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.2))
    times = np.asarray(trajectory["time_years"])
    energy_drift = np.maximum(np.asarray(trajectory["relative_energy_drift"]), 1e-18)
    axes[0].plot(times, energy_drift, color="#256b8f", linewidth=1)
    axes[0].set_yscale("log")
    axes[0].set(
        xlabel="Actual integrator time [yr]",
        ylabel="|ΔE/E₀|",
        title="Nominal sampled conservation",
    )

    axes[1].plot(
        convergence["steps_per_inner_orbit"],
        convergence["delta_E_over_E"],
        "o-",
        color="#a16207",
    )
    axes[1].set_xscale("log", base=2)
    axes[1].set_yscale("log")
    axes[1].set_xticks(
        convergence["steps_per_inner_orbit"],
        [str(value) for value in convergence["steps_per_inner_orbit"]],
    )
    axes[1].set(
        xlabel="Steps per inner orbit",
        ylabel="Maximum sampled |ΔE/E₀|",
        title="WHFast timestep convergence",
    )

    axes[2].hist(
        phase["max_eccentricity_excursion"], bins=10, color="#4f8198", edgecolor="white"
    )
    axes[2].axvline(
        phase["max_eccentricity_excursion"].max(),
        color="#a16207",
        linestyle="--",
        linewidth=1,
    )
    axes[2].set(
        xlabel="Maximum |e(t) − e(0)|",
        ylabel="Phase-prior trials",
        title="32 unknown-phase sensitivity runs",
    )
    fig.suptitle(
        "K2-138 numerical validation and phase-prior sensitivity (10-year conditional model)",
        x=0.05,
        ha="left",
        fontweight="bold",
    )
    fig.tight_layout()
    fig.savefig(out / "dynamical_validation.png", dpi=200)
    plt.close(fig)

    public_figures = ROOT / "web" / "public" / "figures"
    public_figures.mkdir(parents=True, exist_ok=True)
    shutil.copy2(out / "dynamical_validation.png", public_figures / "dynamical_validation.png")
    shutil.copy2(
        ROOT / "results" / "sensitivity_summary.json",
        ROOT / "web" / "public" / "data" / "sensitivity_summary.json",
    )
    for name in ("timestep_convergence.csv", "phase_prior_sensitivity.csv"):
        shutil.copy2(ROOT / "results" / name, ROOT / "web" / "public" / "data" / name)

    summary = json.loads((ROOT / "results" / "archive_summary.json").read_text(encoding="utf-8"))
    (out / "figure_manifest.json").write_text(json.dumps({"source_summary": summary, "figures": ["multiplicity.png", "period_ratios.png", "radius_period.png", "dynamical_validation.png"]}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()

