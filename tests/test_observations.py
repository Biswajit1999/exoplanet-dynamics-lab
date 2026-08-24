import numpy as np
import pytest

from exodynamics.observations.rv import apply_instrument_offsets, circular_multi_planet_rv
from exodynamics.observations.transit import normalize_flux, observed_minus_calculated, transit_probability


def test_flux_normalization() -> None:
    normalized = normalize_flux(np.array([0.99, 1.0, 1.01]))
    assert np.nanmedian(normalized) == pytest.approx(1.0)


def test_ttv_observed_minus_calculated() -> None:
    numbers, residuals = observed_minus_calculated(np.array([1.0, 3.01, 4.99]), 1.0, 2.0)
    np.testing.assert_array_equal(numbers, [0, 1, 2])
    np.testing.assert_allclose(residuals, [0, 0.01, -0.01])


def test_transit_probability_bounded() -> None:
    assert 0 < transit_probability(1, 1) < 1


def test_rv_model_and_offsets() -> None:
    t = np.array([0.0, 0.5])
    model = circular_multi_planet_rv(t, np.array([1.0]), np.array([2.0]), np.array([0.0]))
    shifted = apply_instrument_offsets(model, np.array(["A", "B"]), {"A": 10, "B": -3})
    np.testing.assert_allclose(shifted, [12, -5])

