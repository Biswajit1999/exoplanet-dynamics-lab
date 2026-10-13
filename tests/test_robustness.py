"""Numerical invariants and injection/recovery tests for screening diagnostics."""
import math

import numpy as np
import pytest

from exodynamics.dynamics.robustness import (
    first_order_resonance_screen,
    hill_spacing_ensemble,
    weighted_rv_scan,
)


def test_exact_three_to_two_is_infinite_superperiod() -> None:
    result = first_order_resonance_screen(10.0, 15.0, 3)
    assert result.fractional_offset == pytest.approx(0)
    assert math.isinf(result.superperiod_days)


def test_resonance_beat_formula_and_period_scaling() -> None:
    a = first_order_resonance_screen(10, 15.3, 3)
    b = first_order_resonance_screen(20, 30.6, 3)
    assert a.superperiod_days == pytest.approx(1 / abs(3 / 15.3 - 2 / 10))
    assert b.superperiod_days == pytest.approx(2 * a.superperiod_days)
    assert b.fractional_offset == pytest.approx(a.fractional_offset)


@pytest.mark.parametrize(
    "inner,outer,j",
    [(10, 9, 3), (0, 10, 2), (10, 15, 1), (10, 15, 2.5), (10, math.nan, 2)],
)
def test_invalid_resonance_inputs(inner: float, outer: float, j: int) -> None:
    with pytest.raises(ValueError):
        first_order_resonance_screen(inner, outer, j)


def test_hill_draws_reproducible_and_ordered() -> None:
    kwargs = dict(periods_days=(10, 20), planet_masses_earth=(3, 5), stellar_mass_solar=1.0,
                  period_sigmas_days=(0.1, 0.2), mass_sigmas_earth=(0.3, 0.5), draws=1024)
    a = hill_spacing_ensemble(**kwargs)
    b = hill_spacing_ensemble(**kwargs)
    assert a == b
    assert a.p05_spacing <= a.median_spacing <= a.p95_spacing
    assert 0 <= a.fraction_above_analytic_threshold <= 1
    assert a.valid_draws + a.discarded_order_crossings == 1024


def test_hill_spacing_decreases_for_heavier_planets() -> None:
    light = hill_spacing_ensemble((10, 14), (1, 1), 1, draws=128)
    heavy = hill_spacing_ensemble((10, 14), (20, 20), 1, draws=128)
    assert light.median_spacing > heavy.median_spacing
    assert light.p05_spacing == pytest.approx(light.p95_spacing)


def test_hill_uncertainty_can_cross_orbital_order() -> None:
    result = hill_spacing_ensemble((10, 10.2), (3, 4), 1, period_sigmas_days=(1, 1), draws=2048)
    assert result.discarded_order_crossings > 0


def test_hill_rejects_nonpositive_uncertainty() -> None:
    with pytest.raises(ValueError):
        hill_spacing_ensemble((10, 20), (1, 2), 1, mass_sigmas_earth=(-1, 0))


def _rv_example() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(13)
    times = np.sort(rng.uniform(0, 210, 140))
    labels = np.where(np.arange(times.size) % 2, "HARPS", "HIRES")
    offsets = np.where(labels == "HARPS", 7.0, -4.0)
    errors = rng.uniform(0.7, 1.2, times.size)
    signal = 3.4 * np.cos(2 * np.pi * times / 17.0 + 0.3)
    rv = offsets + signal + rng.normal(0, errors)
    return times, rv, errors, labels, np.linspace(14, 20, 121)


def test_rv_recovers_injected_period_with_two_offsets() -> None:
    t, rv, err, instruments, periods = _rv_example()
    scan = weighted_rv_scan(t, rv, err, instruments, periods)
    assert abs(scan.best_period_days - 17) < 0.2
    assert scan.best_semi_amplitude_ms == pytest.approx(3.4, abs=0.4)
    assert np.nanmax(scan.improvement_fraction) > 0.7
    assert np.all((scan.spectral_window >= 0) & (scan.spectral_window <= 1 + 1e-12))


def test_rv_scan_invariant_to_instrument_zero_points_and_time_origin() -> None:
    t, rv, err, instruments, periods = _rv_example()
    a = weighted_rv_scan(t, rv, err, instruments, periods)
    extra = np.where(instruments == "HARPS", 250.0, -123.0)
    b = weighted_rv_scan(t + 2_450_000.0, rv + extra, err, instruments, periods)
    np.testing.assert_allclose(a.improvement_fraction, b.improvement_fraction, atol=1e-8)
    np.testing.assert_allclose(a.spectral_window, b.spectral_window, atol=1e-8)


def test_rv_scan_rejects_nonpositive_errors() -> None:
    t, rv, err, instruments, periods = _rv_example()
    err[0] = 0
    with pytest.raises(ValueError):
        weighted_rv_scan(t, rv, err, instruments, periods)
