"""Simulate the highest-ranked archive-selected system with measured mass coverage."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from exodynamics.dynamics.diagnostics import semimajor_axis_au
from exodynamics.dynamics.nbody import PlanetInitialCondition, integrate_system

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    selection = pd.read_csv(ROOT / "results" / "system_selection.csv")
    chosen = str(selection.iloc[0]["canonical_host"])
    planets_frame = pd.read_csv(ROOT / "data" / "raw" / "ps.csv", low_memory=False)
    group = planets_frame[(planets_frame["default_flag"] == 1) & (planets_frame["hostname"] == chosen)].sort_values("pl_orbper")
    star_mass = float(group["st_mass"].dropna().median())
    planets: list[PlanetInitialCondition] = []
    for _, row in group.iterrows():
        mass = float(row["pl_bmasse"])
        a = float(row["pl_orbsmax"]) if pd.notna(row["pl_orbsmax"]) else semimajor_axis_au(float(row["pl_orbper"]), star_mass, mass)
        planets.append(
            PlanetInitialCondition(
                name=str(row["pl_name"]), mass_earth=mass, semimajor_axis_au=a,
                eccentricity=float(row["pl_orbeccen"]) if pd.notna(row["pl_orbeccen"]) else 0.0,
                inclination_deg=float(row["pl_orbincl"]) if pd.notna(row["pl_orbincl"]) else 90.0,
            )
        )
    shortest_period_years = float(group["pl_orbper"].min()) / 365.25
    trajectory, metrics = integrate_system(star_mass, planets, duration_years=10.0, samples=700, timestep_years=shortest_period_years / 100)
    trajectory["system"] = chosen
    trajectory["stellar_mass_solar"] = star_mass
    output_dir = ROOT / "results" / "simulations"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "selected_system.json").write_text(json.dumps(trajectory), encoding="utf-8")
    metrics_row = {"system": chosen, **asdict(metrics)}
    (ROOT / "results" / "simulation_summary.json").write_text(json.dumps(metrics_row, indent=2), encoding="utf-8")
    pd.DataFrame([metrics_row]).to_parquet(ROOT / "results" / "simulation_summary.parquet", index=False)
    pd.DataFrame([{**metrics_row, "stability_classification": "stable_over_simulated_interval" if metrics.passed_tolerance else "numerical_validation_failed", "scope_note": "10-year numerical interval only; no gigayear inference"}]).to_parquet(ROOT / "results" / "stability_results.parquet", index=False)
    web = ROOT / "web" / "public" / "data"
    (web / "selected_system.json").write_text(json.dumps(trajectory), encoding="utf-8")
    print(json.dumps(metrics_row, indent=2))


if __name__ == "__main__":
    main()
