import math

import numpy as np

from exodynamics.dynamics.diagnostics import (
    angular_momentum_deficit,
    mutual_hill_separation,
    nearest_commensurability,
    orbital_period_days,
    rv_semi_amplitude_ms,
    semimajor_axis_au,
)


def test_earth_kepler_third_law() -> None:
    assert math.isclose(semimajor_axis_au(365.256, 1.0, 1.0), 1.0, rel_tol=5e-4)
    assert math.isclose(orbital_period_days(1.0, 1.0), 365.25, rel_tol=5e-4)


def test_mutual_hill_separation_positive() -> None:
    assert mutual_hill_separation(1.0, 1.5, 1.0, 1.0, 1.0) > 0


def test_commensurability_labels_only_proximity() -> None:
    result = nearest_commensurability(10, 15.01)
    assert result.classification == "near_commensurability"
    assert (result.numerator, result.denominator) == (3, 2)
    assert nearest_commensurability(10, 17.2).classification == "not_near_commensurability"


def test_amd_zero_for_circular_coplanar() -> None:
    assert angular_momentum_deficit(np.ones(2), np.array([1.0, 1.5]), np.zeros(2), np.zeros(2)) == 0


def test_earth_rv_amplitude() -> None:
    assert math.isclose(rv_semi_amplitude_ms(365.256, 1.0, 1.0), 0.089, rel_tol=0.03)
