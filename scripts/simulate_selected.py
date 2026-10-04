"""Run the nominal, timestep-convergence, and phase-prior experiments."""

from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
import pandas as pd

from exodynamics.dynamics.diagnostics import semimajor_axis_au
from exodynamics.dynamics.nbody import PlanetInitialCondition, integrate_system

ROOT = Path(__file__).resolve().parents[1]
PHASE_ENSEMBLE_SEED = 20261004
PHASE_ENSEMBLE_SIZE = 32


def load_selected_system() -> tuple[str, float, list[PlanetInitialCondition], float]:
    selection = pd.read_csv(ROOT / "results" / "system_selection.csv")
    chosen = str(selection.iloc[0]["canonical_host"])
    archive = pd.read_csv(ROOT / "data" / "raw" / "ps.csv", low_memory=False)
    group = archive[
        (archive["default_flag"] == 1) & (archive["hostname"] == chosen)
    ].sort_values("pl_orbper")
    star_mass = float(group["st_mass"].dropna().median())
    planets: list[PlanetInitialCondition] = []
    for _, row in group.iterrows():
        mass = float(row["pl_bmasse"])
        axis = (
            float(row["pl_orbsmax"])
            if pd.notna(row["pl_orbsmax"])
            else semimajor_axis_au(float(row["pl_orbper"]), star_mass, mass)
        )
        planets.append(
            PlanetInitialCondition(
                name=str(row["pl_name"]),
                mass_earth=mass,
                semimajor_axis_au=axis,
                eccentricity=float(row["pl_orbeccen"]) if pd.notna(row["pl_orbeccen"]) else 0.0,
                inclination_deg=float(row["pl_orbincl"]) if pd.notna(row["pl_orbincl"]) else 90.0,
            )
        )
    shortest_period_years = float(group["pl_orbper"].min()) / 365.25
    return chosen, star_mass, planets, shortest_period_years


def convergence_experiment(
    star_mass: float, planets: list[PlanetInitialCondition], shortest_period_years: float
) -> pd.DataFrame:
    rows = []
    for steps_per_inner_orbit in (50, 100, 200):
        _, metrics = integrate_system(
            star_mass,
            planets,
            duration_years=10.0,
            samples=700,
            timestep_years=shortest_period_years / steps_per_inner_orbit,
        )
        rows.append({"steps_per_inner_orbit": steps_per_inner_orbit, **asdict(metrics)})
    return pd.DataFrame(rows)


def phase_prior_experiment(
    star_mass: float, planets: list[PlanetInitialCondition], shortest_period_years: float
) -> pd.DataFrame:
    """Sensitivity to unknown mean anomalies; not a posterior distribution."""
    rng = np.random.default_rng(PHASE_ENSEMBLE_SEED)
    rows = []
    initial_e = {planet.name: planet.eccentricity for planet in planets}
    for trial in range(PHASE_ENSEMBLE_SIZE):
        phases = rng.uniform(0.0, 360.0, len(planets))
        trial_planets = [
            replace(planet, mean_anomaly_deg=float(phase))
            for planet, phase in zip(planets, phases, strict=True)
        ]
        trajectory, metrics = integrate_system(
            star_mass,
            trial_planets,
            duration_years=10.0,
            samples=350,
            timestep_years=shortest_period_years / 100,
        )
        max_eccentricity = max(
            max(values["e"]) for values in trajectory["trajectories"].values()
        )
        max_eccentricity_excursion = max(
            max(abs(np.asarray(values["e"]) - initial_e[name]))
            for name, values in trajectory["trajectories"].items()
        )
        rows.append({
            "trial": trial,
            "seed": PHASE_ENSEMBLE_SEED,
            "mean_anomalies_deg": json.dumps(dict(zip(initial_e, phases, strict=True))),
            "max_eccentricity": float(max_eccentricity),
            "max_eccentricity_excursion": float(max_eccentricity_excursion),
            **asdict(metrics),
        })
    return pd.DataFrame(rows)


def main() -> None:
    chosen, star_mass, planets, shortest_period_years = load_selected_system()
    timestep = shortest_period_years / 100
    stability_trajectory, metrics = integrate_system(
        star_mass, planets, duration_years=10.0, samples=700, timestep_years=timestep
    )
    trajectory, _ = integrate_system(
        star_mass,
        planets,
        duration_years=60 / 365.25,
        samples=2400,
        timestep_years=timestep,
    )
    trajectory.update({
        "system": chosen,
        "stellar_mass_solar": star_mass,
        "visualization_interval_days": 60,
        "validation_interval_years": metrics.integration_time_years,
    })
    output_dir = ROOT / "results" / "simulations"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "selected_system.json").write_text(json.dumps(trajectory), encoding="utf-8")
    (output_dir / "stability_trajectory.json").write_text(
        json.dumps(stability_trajectory), encoding="utf-8"
    )

    metrics_row = {"system": chosen, **asdict(metrics)}
    (ROOT / "results" / "simulation_summary.json").write_text(
        json.dumps(metrics_row, indent=2), encoding="utf-8"
    )
    pd.DataFrame([metrics_row]).to_parquet(
        ROOT / "results" / "simulation_summary.parquet", index=False
    )
    pd.DataFrame([{
        **metrics_row,
        "stability_classification": (
            "numerically_conserved_over_simulated_interval"
            if metrics.passed_tolerance
            else "numerical_validation_failed"
        ),
        "scope_note": "10-year nominal trajectory only; no physical long-term stability inference",
    }]).to_parquet(ROOT / "results" / "stability_results.parquet", index=False)

    convergence = convergence_experiment(star_mass, planets, shortest_period_years)
    convergence.to_csv(ROOT / "results" / "timestep_convergence.csv", index=False)
    phase = phase_prior_experiment(star_mass, planets, shortest_period_years)
    phase.to_csv(ROOT / "results" / "phase_prior_sensitivity.csv", index=False)
    sensitivity = {
        "system": chosen,
        "phase_trials": PHASE_ENSEMBLE_SIZE,
        "phase_seed": PHASE_ENSEMBLE_SEED,
        "phase_prior": "independent uniform mean anomaly on [0, 360 degrees); sensitivity experiment, not posterior",
        "all_phase_trials_numerically_conserved": bool(phase["passed_tolerance"].all()),
        "max_phase_trial_energy_drift": float(phase["delta_E_over_E"].max()),
        "max_phase_trial_angular_momentum_drift": float(phase["delta_L_over_L"].max()),
        "max_eccentricity_across_phase_trials": float(phase["max_eccentricity"].max()),
        "max_eccentricity_excursion_across_phase_trials": float(
            phase["max_eccentricity_excursion"].max()
        ),
    }
    (ROOT / "results" / "sensitivity_summary.json").write_text(
        json.dumps(sensitivity, indent=2), encoding="utf-8"
    )

    web = ROOT / "web" / "public" / "data"
    (web / "selected_system.json").write_text(json.dumps(trajectory), encoding="utf-8")
    print(json.dumps({"nominal": metrics_row, "sensitivity": sensitivity}, indent=2))


if __name__ == "__main__":
    main()
