"""REBOUND integration with conservation diagnostics and explicit assumptions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Any

import numpy as np

EARTH_MASS_IN_SOLAR = 3.0034896e-6


@dataclass(frozen=True)
class PlanetInitialCondition:
    name: str
    mass_earth: float
    semimajor_axis_au: float
    eccentricity: float = 0.0
    inclination_deg: float = 90.0
    omega_deg: float = 0.0
    ascending_node_deg: float = 0.0
    mean_anomaly_deg: float = 0.0


@dataclass(frozen=True)
class SimulationMetrics:
    delta_E_over_E: float
    delta_L_over_L: float
    integration_time_years: float
    time_step_years: float
    integrator: str
    number_of_steps: int
    wall_time_seconds: float
    passed_tolerance: bool


def build_simulation(stellar_mass_solar: float, planets: list[PlanetInitialCondition], integrator: str = "whfast", timestep_years: float | None = None) -> Any:
    try:
        import rebound
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install the 'dynamics' extra to run N-body integrations") from exc
    simulation = rebound.Simulation()
    simulation.units = ("yr", "AU", "Msun")
    simulation.integrator = integrator
    simulation.add(m=stellar_mass_solar, hash="star")
    for planet in planets:
        simulation.add(
            m=planet.mass_earth * EARTH_MASS_IN_SOLAR,
            a=planet.semimajor_axis_au,
            e=planet.eccentricity,
            inc=np.radians(planet.inclination_deg),
            omega=np.radians(planet.omega_deg),
            Omega=np.radians(planet.ascending_node_deg),
            M=np.radians(planet.mean_anomaly_deg),
            hash=planet.name,
        )
    simulation.move_to_com()
    if integrator.lower() == "whfast":
        simulation.dt = timestep_years if timestep_years is not None else 0.001
    return simulation


def integrate_system(stellar_mass_solar: float, planets: list[PlanetInitialCondition], duration_years: float, samples: int = 500, integrator: str = "whfast", timestep_years: float | None = None, tolerance: float = 1e-7) -> tuple[dict[str, object], SimulationMetrics]:
    simulation = build_simulation(stellar_mass_solar, planets, integrator, timestep_years)
    initial_energy = simulation.energy()
    initial_l_vector = simulation.angular_momentum()
    initial_angular_momentum = float(np.sqrt(initial_l_vector.x**2 + initial_l_vector.y**2 + initial_l_vector.z**2))
    times = np.linspace(0, duration_years, samples)
    trajectories = {planet.name: {key: [] for key in ("x", "y", "z", "a", "e", "inc")} for planet in planets}
    started = perf_counter()
    for time in times:
        simulation.integrate(float(time), exact_finish_time=0)
        for index, planet in enumerate(planets, start=1):
            particle = simulation.particles[index]
            orbit = particle.orbit(primary=simulation.particles[0])
            target = trajectories[planet.name]
            target["x"].append(particle.x)
            target["y"].append(particle.y)
            target["z"].append(particle.z)
            target["a"].append(orbit.a)
            target["e"].append(orbit.e)
            target["inc"].append(orbit.inc)
    wall = perf_counter() - started
    final_energy = simulation.energy()
    final_l_vector = simulation.angular_momentum()
    final_angular_momentum = float(np.sqrt(final_l_vector.x**2 + final_l_vector.y**2 + final_l_vector.z**2))
    delta_e = abs((final_energy - initial_energy) / initial_energy)
    delta_l = abs((final_angular_momentum - initial_angular_momentum) / initial_angular_momentum)
    metrics = SimulationMetrics(
        delta_E_over_E=delta_e,
        delta_L_over_L=delta_l,
        integration_time_years=duration_years,
        time_step_years=float(simulation.dt),
        integrator=integrator,
        number_of_steps=int(duration_years / simulation.dt),
        wall_time_seconds=wall,
        passed_tolerance=delta_e < tolerance and delta_l < tolerance,
    )
    output: dict[str, object] = {
        "time_years": times.tolist(),
        "trajectories": trajectories,
        "initial_conditions": [asdict(planet) for planet in planets],
        "data_kind": "simulated",
        "assumptions": [
            "Published/default archive masses, semi-major axes and eccentricities where present.",
            "Longitude of ascending node and mean anomaly set to project-prior zero when unconstrained.",
            "Planet rendering is a model trajectory, not direct imaging.",
        ],
    }
    return output, metrics


def calculate_megno(stellar_mass_solar: float, planets: list[PlanetInitialCondition], duration_years: float, timestep_years: float) -> float:
    simulation = build_simulation(stellar_mass_solar, planets, "whfast", timestep_years)
    simulation.init_megno(seed=42)
    simulation.integrate(duration_years)
    return float(simulation.megno())
