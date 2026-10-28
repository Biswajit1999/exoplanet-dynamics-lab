import numpy as np
import pytest

from exodynamics.dynamics.robustness import (
    HILL_THRESHOLD,
    circular_angle_diagnostics,
    first_order_resonant_angles,
    fit_linear_ephemeris,
    hill_logmass_sensitivity,
    hill_spacing_from_periods,
    synthetic_ephemeris_sensitivity,
    synthetic_resonance_sampling,
)


def test_first_order_resonant_angle_invariant_under_common_rotation():
    n = 100
    lam_i = np.linspace(0, 20, n)
    lam_o = 2 / 3 * lam_i + 0.2
    varpi_i = np.full(n, 0.1)
    varpi_o = np.full(n, -0.1)
    a, b = first_order_resonant_angles(lam_i, lam_o, varpi_i, varpi_o)
    shifted = first_order_resonant_angles(lam_i + 0.7, lam_o + 0.7, varpi_i + 0.7, varpi_o + 0.7)
    np.testing.assert_allclose(a, shifted[0], atol=1e-14)
    np.testing.assert_allclose(b, shifted[1], atol=1e-14)
    assert circular_angle_diagnostics(a)["resultant_length"] > 0.999


def test_circulation_and_libration_differ_in_circular_statistics():
    r = synthetic_resonance_sampling()
    assert r["libration_like"]["resultant_length"] > 0.9
    assert r["circulation_like"]["resultant_length"] < 0.02
    assert r["circulation_like"]["unwrapped_span_rad"] > 20


def test_invalid_angles_rejected():
    with pytest.raises(ValueError):
        first_order_resonant_angles(np.ones(4), np.ones(4), np.ones(4), np.ones(4), j=1)
    with pytest.raises(ValueError):
        circular_angle_diagnostics(np.array([0, np.nan, 1, 2]))


def test_hill_spacing_mass_scaling_and_threshold():
    a = hill_spacing_from_periods(10, 15, 5, 5, 1)
    b = hill_spacing_from_periods(10, 15, 40, 40, 1)
    assert a / b == pytest.approx(2.0, rel=1e-12)
    assert a > HILL_THRESHOLD


def test_hill_zero_uncertainty_is_deterministic():
    r = hill_logmass_sensitivity(log_mass_sigma=0, log_stellar_sigma=0, draws=300)
    assert r["q16"] == pytest.approx(r["nominal_spacing"])
    assert r["q84"] == pytest.approx(r["nominal_spacing"])


def test_hill_positive_mass_correlation_increases_interval_width():
    a = hill_logmass_sensitivity(mass_correlation=-0.8, draws=15000)
    b = hill_logmass_sensitivity(mass_correlation=0.8, draws=15000)
    assert b["q84"] - b["q16"] > a["q84"] - a["q16"]


def test_invalid_hill_input_rejected():
    with pytest.raises(ValueError):
        hill_spacing_from_periods(10, 8, 1, 1, 1)
    with pytest.raises(ValueError):
        hill_logmass_sensitivity(mass_correlation=1.01)


def test_gls_ephemeris_exact_recovery():
    epochs = np.arange(12, dtype=float)
    times = 2450000.0 + 4.7 * epochs
    cov = np.eye(12) * 1e-6
    fit = fit_linear_ephemeris(epochs, times, cov)
    assert fit.period_days == pytest.approx(4.7, abs=1e-10)
    assert fit.epoch_zero_days == pytest.approx(2450000.0, abs=1e-8)
    assert fit.chi_square < 1e-10


def test_correlated_timing_errors_increase_period_uncertainty():
    r = synthetic_ephemeris_sensitivity()
    assert r["correlated_period_sigma_days"] > r["independent_period_sigma_days"]
    assert r["max_leave_one_out_period_shift_days"] > 0


def test_invalid_covariance_rejected():
    e = np.arange(6, dtype=float)
    t = 10 + 2 * e
    with pytest.raises(ValueError):
        fit_linear_ephemeris(e, t, np.ones((6, 6)))
    with pytest.raises(ValueError):
        fit_linear_ephemeris(e[::-1], t[::-1], np.eye(6))
