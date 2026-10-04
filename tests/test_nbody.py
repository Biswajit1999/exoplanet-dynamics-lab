import pytest

from exodynamics.dynamics.nbody import PlanetInitialCondition, integrate_system


def test_two_body_energy_and_angular_momentum_conservation() -> None:
    trajectory, metrics = integrate_system(
        1.0,
        [PlanetInitialCondition("Earth control", 1.0, 1.0, 0.0167, 0.0)],
        duration_years=5,
        samples=50,
        timestep_years=1 / 100,
        tolerance=1e-8,
    )
    assert metrics.passed_tolerance
    assert metrics.delta_E_over_E < 1e-8
    assert metrics.delta_L_over_L < 1e-12
    assert metrics.delta_E_over_E >= metrics.final_delta_E_over_E
    assert metrics.delta_L_over_L >= metrics.final_delta_L_over_L
    assert len(trajectory["time_years"]) == len(trajectory["requested_time_years"])
    assert metrics.sample_time_max_error_years <= metrics.time_step_years
    assert trajectory["data_kind"] == "simulated"


@pytest.mark.parametrize(
    "planet",
    [
        PlanetInitialCondition("bad mass", 0.0, 1.0),
        PlanetInitialCondition("bad axis", 1.0, 0.0),
        PlanetInitialCondition("bad eccentricity", 1.0, 1.0, 1.0),
        PlanetInitialCondition("bad angle", 1.0, 1.0, mean_anomaly_deg=float("nan")),
    ],
)
def test_invalid_initial_conditions_fail_closed(planet: PlanetInitialCondition) -> None:
    with pytest.raises(ValueError):
        integrate_system(1.0, [planet], duration_years=1.0)


def test_invalid_integration_controls_fail_closed() -> None:
    earth = PlanetInitialCondition("Earth", 1.0, 1.0)
    with pytest.raises(ValueError):
        integrate_system(1.0, [earth], duration_years=0.0)
    with pytest.raises(ValueError):
        integrate_system(1.0, [earth], duration_years=1.0, samples=1)
    with pytest.raises(ValueError):
        integrate_system(1.0, [earth], duration_years=1.0, timestep_years=0.0)

