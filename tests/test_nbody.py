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
    assert trajectory["data_kind"] == "simulated"

