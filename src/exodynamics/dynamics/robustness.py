"""Synthetic resonance, Hill-spacing and transit-ephemeris robustness checks.

These diagnostics are not dynamical stability proofs or observed exoplanet TTVs.
Time units are days, planet masses Earth masses, stellar masses solar masses.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

EARTH_PER_SOLAR_MASS = 5.9722e24 / 1.98847e30
HILL_THRESHOLD = 2 * np.sqrt(3)


def _angles(*values: np.ndarray) -> list[np.ndarray]:
    arrays = [np.asarray(x, dtype=float) for x in values]
    if not arrays or arrays[0].ndim != 1 or arrays[0].size < 4:
        raise ValueError("at least four time samples are required")
    if any(a.shape != arrays[0].shape or not np.all(np.isfinite(a)) for a in arrays):
        raise ValueError("all angle series must be finite and same length")
    return arrays


def first_order_resonant_angles(lambda_inner_rad: np.ndarray, lambda_outer_rad: np.ndarray,
                                varpi_inner_rad: np.ndarray, varpi_outer_rad: np.ndarray,
                                j: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """Angles j*lambda_outer-(j-1)*lambda_inner-varpi_i/o for j:(j-1)."""
    if isinstance(j, bool) or not isinstance(j, (int, np.integer)) or j < 2:
        raise ValueError("j must be an integer >=2")
    inner, outer, varpi_i, varpi_o = _angles(
        lambda_inner_rad, lambda_outer_rad, varpi_inner_rad, varpi_outer_rad)
    common = j * outer - (j - 1) * inner
    return np.angle(np.exp(1j * (common - varpi_i))), np.angle(np.exp(1j * (common - varpi_o)))


def circular_angle_diagnostics(angle_rad: np.ndarray) -> dict[str, float]:
    """Concentration and sampled unwrapped span; not a resonance classifier.

    Rapid circulating angles can alias into apparent libration if cadence is
    insufficient. A large concentration alone is not evidence of resonance.
    """
    a = _angles(angle_rad)[0]
    phasor = np.mean(np.exp(1j * a))
    return {"mean_angle_rad": float(np.angle(phasor)),
            "resultant_length": float(abs(phasor)),
            "unwrapped_span_rad": float(np.ptp(np.unwrap(a))),
            "samples": int(a.size)}


def hill_spacing_from_periods(period_inner_days: float, period_outer_days: float,
                              mass_inner_earth: np.ndarray, mass_outer_earth: np.ndarray,
                              stellar_mass_solar: np.ndarray) -> np.ndarray:
    """Circular-coplanar two-planet mutual Hill spacing, Keplerian massless a.

    This uses a_out/a_in=(P_out/P_in)^(2/3); no absolute a is needed.
    The 2*sqrt(3) threshold is a sufficient idealized two-planet criterion,
    NOT a guarantee for eccentric, inclined or multi-planet configurations.
    """
    masses = [np.asarray(v, dtype=float) for v in (mass_inner_earth, mass_outer_earth, stellar_mass_solar)]
    if not (np.isfinite(period_inner_days) and np.isfinite(period_outer_days)
            and 0 < period_inner_days < period_outer_days):
        raise ValueError("periods must be positive and ordered")
    if any(np.any(~np.isfinite(m)) or np.any(m <= 0) for m in masses):
        raise ValueError("masses must be finite and positive")
    m1, m2, ms = np.broadcast_arrays(*masses)
    ratio = (period_outer_days / period_inner_days) ** (2 / 3)
    return (2 * (ratio - 1) / (ratio + 1)
            * (3 * ms / ((m1 + m2) * EARTH_PER_SOLAR_MASS)) ** (1 / 3))


def hill_logmass_sensitivity(*, period_inner_days: float = 10.0,
                             period_outer_days: float = 15.0,
                             mass_inner_earth: float = 5.0,
                             mass_outer_earth: float = 5.0,
                             stellar_mass_solar: float = 1.0,
                             log_mass_sigma: float = 0.2,
                             log_stellar_sigma: float = 0.05,
                             mass_correlation: float = 0.0,
                             draws: int = 20_000, seed: int = 20261028) -> dict[str, float]:
    """Lognormal assumed-prior sensitivity, with correlated planet masses."""
    if draws < 2 or not np.isfinite(mass_correlation) or abs(mass_correlation) > 1:
        raise ValueError("invalid sample count or correlation")
    if not np.isfinite(log_mass_sigma) or not np.isfinite(log_stellar_sigma) or min(log_mass_sigma, log_stellar_sigma) < 0:
        raise ValueError("log-mass sigmas must be non-negative")
    nominal = float(hill_spacing_from_periods(period_inner_days, period_outer_days,
                                              mass_inner_earth, mass_outer_earth, stellar_mass_solar))
    rng = np.random.default_rng(seed)
    z1 = rng.standard_normal(draws)
    z2 = mass_correlation * z1 + np.sqrt(max(0.0, 1 - mass_correlation**2)) * rng.standard_normal(draws)
    m1 = mass_inner_earth * np.exp(log_mass_sigma * z1)
    m2 = mass_outer_earth * np.exp(log_mass_sigma * z2)
    ms = stellar_mass_solar * np.exp(log_stellar_sigma * rng.standard_normal(draws))
    delta = hill_spacing_from_periods(period_inner_days, period_outer_days, m1, m2, ms)
    q16, q50, q84 = np.quantile(delta, [0.16, 0.5, 0.84])
    return {"draws": draws, "mass_correlation": mass_correlation,
            "nominal_spacing": nominal, "q16": float(q16), "median": float(q50),
            "q84": float(q84), "fraction_below_idealized_threshold": float(np.mean(delta < HILL_THRESHOLD))}


@dataclass(frozen=True)
class EphemerisFit:
    epoch_zero_days: float
    period_days: float
    epoch_zero_sigma_days: float
    period_sigma_days: float
    chi_square: float
    dof: int
    residual_days: np.ndarray


def _ephemeris_fit(epochs: np.ndarray, times: np.ndarray, covariance: np.ndarray,
                   quadratic: bool = False) -> tuple[np.ndarray, np.ndarray, float, np.ndarray]:
    e = np.asarray(epochs, dtype=float)
    t = np.asarray(times, dtype=float)
    cov = np.asarray(covariance, dtype=float)
    k = 3 if quadratic else 2
    if e.ndim != 1 or e.size <= k or t.shape != e.shape or cov.shape != (e.size, e.size):
        raise ValueError("incompatible epochs, times or covariance shape")
    if not (np.all(np.isfinite(e)) and np.all(np.isfinite(t)) and np.all(np.isfinite(cov))):
        raise ValueError("inputs must be finite")
    if np.any(np.diff(e) <= 0):
        raise ValueError("epochs must be strictly increasing")
    if not np.allclose(cov, cov.T, rtol=1e-10, atol=1e-15):
        raise ValueError("timing covariance must be symmetric")
    try:
        cholesky = np.linalg.cholesky(cov)
    except np.linalg.LinAlgError as exc:
        raise ValueError("timing covariance must be positive definite") from exc
    x = e - np.mean(e)
    design = np.column_stack((np.ones_like(x), x, 0.5 * x*x)) if quadratic else np.column_stack((np.ones_like(x), x))
    whitened = np.linalg.solve(cholesky, design)
    data = np.linalg.solve(cholesky, t)
    if np.linalg.matrix_rank(whitened) < k:
        raise ValueError("ephemeris design is rank deficient")
    beta = np.linalg.lstsq(whitened, data, rcond=None)[0]
    parameter_cov = np.linalg.inv(whitened.T @ whitened)
    residual = t - design @ beta
    chi2 = float(np.sum(np.linalg.solve(cholesky, residual)**2))
    if not quadratic:
        intercept = beta[0] - beta[1] * np.mean(e)
        transform = np.array([[1, -np.mean(e)], [0, 1]])
        parameter_cov = transform @ parameter_cov @ transform.T
        beta = np.array([intercept, beta[1]])
    return beta, parameter_cov, chi2, residual


def fit_linear_ephemeris(epochs: np.ndarray, times_days: np.ndarray,
                         covariance_days2: np.ndarray) -> EphemerisFit:
    """GLS ephemeris t=t0+P*epoch with full known timing covariance."""
    beta, cov, chi2, residual = _ephemeris_fit(epochs, times_days, covariance_days2)
    return EphemerisFit(float(beta[0]), float(beta[1]), float(np.sqrt(cov[0, 0])),
                        float(np.sqrt(cov[1, 1])), chi2, len(epochs) - 2, residual)


def synthetic_ephemeris_sensitivity(*, seed: int = 20261028) -> dict[str, object]:
    """Correlated timing errors, TTV-like sine, LOO influence and curvature check."""
    rng = np.random.default_rng(seed)
    epochs = np.arange(45, dtype=float)
    t0, period = 2457000.0, 5.0
    sigma_days, rho = 0.0007, 0.65
    cov = sigma_days**2 * rho ** abs(epochs[:, None] - epochs[None, :])
    injected_ttv = 0.0015 * np.sin(2 * np.pi * epochs / 18.0)
    times = t0 + period * epochs + injected_ttv + np.linalg.cholesky(cov) @ rng.standard_normal(len(epochs))
    correlated = fit_linear_ephemeris(epochs, times, cov)
    independent = fit_linear_ephemeris(epochs, times, np.diag(np.diag(cov)))
    leave_one_out = []
    for index in range(len(epochs)):
        keep = np.arange(len(epochs)) != index
        trial = fit_linear_ephemeris(epochs[keep], times[keep], cov[np.ix_(keep, keep)])
        leave_one_out.append(trial.period_days - correlated.period_days)
    _, _, chi2_quadratic, _ = _ephemeris_fit(epochs, times, cov, quadratic=True)
    return {
        "kind": "seeded synthetic correlated timing plus sinusoidal residuals",
        "n_transits": len(epochs), "injected_period_days": period,
        "injected_ttv_amplitude_days": 0.0015, "assumed_rho": rho,
        "correlated_period_days": correlated.period_days,
        "correlated_period_sigma_days": correlated.period_sigma_days,
        "independent_period_sigma_days": independent.period_sigma_days,
        "linear_chi2": correlated.chi_square,
        "quadratic_delta_chi2": correlated.chi_square - chi2_quadratic,
        "max_leave_one_out_period_shift_days": float(np.max(np.abs(leave_one_out))),
    }


def synthetic_resonance_sampling() -> dict[str, object]:
    """Compare sampled circulating and librating angles; not a dynamical proof."""
    time = np.linspace(0, 20, 401)
    librating = 0.35 * np.sin(2 * np.pi * time / 5)
    circulating = 2 * np.pi * time / 5
    return {"kind": "synthetic angle time series",
            "libration_like": circular_angle_diagnostics(librating),
            "circulation_like": circular_angle_diagnostics(circulating)}
