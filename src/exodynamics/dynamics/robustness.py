"""Independent dynamical screening and instrument-aware RV diagnostics.

These diagnostics are not dynamical integrations, resonance detections, or
claims of planet detections. They deliberately expose their assumptions.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from exodynamics.dynamics.diagnostics import (
    AU_M,
    DAY_S,
    G_SI,
    M_EARTH_KG,
    M_SUN_KG,
)


@dataclass(frozen=True)
class ResonanceScreen:
    j: int
    fractional_offset: float
    superperiod_days: float


def first_order_resonance_screen(
    period_inner_days: float, period_outer_days: float, j: int
) -> ResonanceScreen:
    """Screen proximity to j:(j-1), without asserting resonant libration.

    The superperiod is the beat period of the two orbital frequencies.
    Exactly commensurate periods return math.inf. TTV amplitudes and
    resonant angles require additional physics not captured here.
    """
    if isinstance(j, bool) or not isinstance(j, int) or j < 2:
        raise ValueError("j must be an integer >= 2")
    periods = np.asarray([period_inner_days, period_outer_days], dtype=float)
    if not np.all(np.isfinite(periods)) or np.any(periods <= 0) or periods[1] <= periods[0]:
        raise ValueError("periods must be finite, positive and ordered inner < outer")
    offset = (periods[1] / periods[0]) * (j - 1) / j - 1
    frequency_difference = j / periods[1] - (j - 1) / periods[0]
    scale = (j - 1) / periods[0]
    beat = math.inf if abs(frequency_difference) <= 1e-13 * scale else 1 / abs(frequency_difference)
    return ResonanceScreen(j=j, fractional_offset=float(offset), superperiod_days=float(beat))


@dataclass(frozen=True)
class HillEnsemble:
    median_spacing: float
    p05_spacing: float
    p95_spacing: float
    fraction_above_analytic_threshold: float
    valid_draws: int
    discarded_order_crossings: int
    seed: int


def _positive_draws(rng: np.random.Generator, mean: float, sigma: float, size: int) -> np.ndarray:
    """Moment-matched lognormal positive prior; sigma is absolute, not fractional."""
    if not math.isfinite(mean) or mean <= 0 or not math.isfinite(sigma) or sigma < 0:
        raise ValueError("positive finite mean and nonnegative finite sigma required")
    if sigma == 0:
        return np.full(size, mean)
    log_variance = math.log1p((sigma / mean) ** 2)
    return rng.lognormal(math.log(mean) - 0.5 * log_variance, math.sqrt(log_variance), size)


def hill_spacing_ensemble(
    periods_days: tuple[float, float],
    planet_masses_earth: tuple[float, float],
    stellar_mass_solar: float,
    *,
    period_sigmas_days: tuple[float, float] = (0.0, 0.0),
    mass_sigmas_earth: tuple[float, float] = (0.0, 0.0),
    stellar_mass_sigma_solar: float = 0.0,
    draws: int = 4096,
    seed: int = 42,
) -> HillEnsemble:
    """Monte Carlo mutual-Hill spacing with positive lognormal input priors.

    The 2*sqrt(3) threshold is an approximate sufficient two-planet criterion
    for nearly circular, coplanar, low-mass systems, not a generic long-term
    stability guarantee. Input priors are independent by assumption.
    """
    if not isinstance(draws, int) or draws < 32:
        raise ValueError("draws must be an integer >= 32")
    if len(periods_days) != 2 or len(planet_masses_earth) != 2:
        raise ValueError("exactly two periods and two planet masses required")
    if periods_days[1] <= periods_days[0]:
        raise ValueError("outer nominal period must exceed inner nominal period")
    rng = np.random.default_rng(seed)
    pi, po = (
        _positive_draws(rng, float(v), float(s), draws)
        for v, s in zip(periods_days, period_sigmas_days, strict=True)
    )
    mi, mo = (
        _positive_draws(rng, float(v), float(s), draws)
        for v, s in zip(planet_masses_earth, mass_sigmas_earth, strict=True)
    )
    star = _positive_draws(rng, stellar_mass_solar, stellar_mass_sigma_solar, draws)
    valid = po > pi
    n_valid = int(np.count_nonzero(valid))
    if n_valid < 32:
        raise ValueError("fewer than 32 ordered-period draws remain")
    pi, po, mi, mo, star = (x[valid] for x in (pi, po, mi, mo, star))
    ai = (
        G_SI * (star * M_SUN_KG + mi * M_EARTH_KG) * (pi * DAY_S) ** 2 / (4 * np.pi**2)
    ) ** (1 / 3) / AU_M
    ao = (
        G_SI * (star * M_SUN_KG + mo * M_EARTH_KG) * (po * DAY_S) ** 2 / (4 * np.pi**2)
    ) ** (1 / 3) / AU_M
    hill = 0.5 * (ai + ao) * ((mi + mo) * M_EARTH_KG / (3 * star * M_SUN_KG)) ** (1 / 3)
    separation = (ao - ai) / hill
    if not np.all(np.isfinite(separation)):
        raise ArithmeticError("non-finite Hill separation")
    q05, median, q95 = np.quantile(separation, [0.05, 0.5, 0.95])
    return HillEnsemble(
        median_spacing=float(median), p05_spacing=float(q05), p95_spacing=float(q95),
        fraction_above_analytic_threshold=float(np.mean(separation > 2 * np.sqrt(3))),
        valid_draws=n_valid, discarded_order_crossings=draws - n_valid, seed=seed,
    )


@dataclass(frozen=True)
class RVScan:
    periods_days: np.ndarray
    improvement_fraction: np.ndarray
    spectral_window: np.ndarray
    best_period_days: float
    best_semi_amplitude_ms: float
    chi2_null: float
    chi2_best: float


def weighted_rv_scan(
    times_days: np.ndarray,
    velocities_ms: np.ndarray,
    errors_ms: np.ndarray,
    instruments: np.ndarray,
    periods_days: np.ndarray,
) -> RVScan:
    """Weighted circular-signal scan with independent instrument zero points.

    Compare an instrument-offset-only null with offset + sine + cosine fits.
    The returned improvement is descriptive and NOT a false-alarm probability;
    correlated stellar activity and the look-elsewhere effect are not modelled.
    The spectral window is a cadence-only alias diagnostic.
    """
    t, y, e = (np.asarray(x, dtype=float) for x in (times_days, velocities_ms, errors_ms))
    labels = np.asarray(instruments).astype(str)
    periods = np.asarray(periods_days, dtype=float)
    if t.ndim != 1 or any(x.shape != t.shape for x in (y, e, labels)):
        raise ValueError("times, velocities, errors and instruments must be equal 1-D arrays")
    if (
        periods.ndim != 1 or periods.size == 0 or np.any(~np.isfinite(periods))
        or np.any(periods <= 0)
    ):
        raise ValueError("trial periods must be positive finite 1-D values")
    if (
        np.any(~np.isfinite(t)) or np.any(~np.isfinite(y))
        or np.any(~np.isfinite(e)) or np.any(e <= 0)
    ):
        raise ValueError("data must be finite and measurement errors positive")
    if t.size < 6 or np.unique(t).size < 4:
        raise ValueError("insufficient distinct epochs")
    _, group = np.unique(labels, return_inverse=True)
    n_group = int(group.max()) + 1
    if t.size < n_group + 3:
        raise ValueError("insufficient degrees of freedom for offsets and sinusoid")
    t = t - t.min()
    null = np.eye(n_group, dtype=float)[group]
    w = 1.0 / e
    null_w = null * w[:, None]
    if np.linalg.matrix_rank(null_w) != n_group:
        raise ValueError("rank-deficient instrument design")
    beta0 = np.linalg.lstsq(null_w, y * w, rcond=None)[0]
    chi2_null = float(np.sum(((y - null @ beta0) * w) ** 2))
    if chi2_null <= np.finfo(float).eps:
        raise ValueError("zero null residual: a period scan is not identifiable")
    improvement = np.empty(periods.size)
    window = np.empty(periods.size)
    amplitudes = np.empty(periods.size)
    chi2_values = np.empty(periods.size)
    for k, period in enumerate(periods):
        angle = (2 * np.pi / period) * t
        design = np.column_stack((null, np.cos(angle), np.sin(angle)))
        design_w = design * w[:, None]
        if np.linalg.matrix_rank(design_w) != n_group + 2:
            improvement[k] = np.nan
            amplitudes[k] = np.nan
            chi2_values[k] = np.nan
        else:
            beta = np.linalg.lstsq(design_w, y * w, rcond=None)[0]
            chi2 = float(np.sum(((y - design @ beta) * w) ** 2))
            chi2_values[k] = chi2
            improvement[k] = float(np.clip(1 - chi2 / chi2_null, 0, 1))
            amplitudes[k] = float(np.hypot(beta[-2], beta[-1]))
        window[k] = float(abs(np.mean(np.exp(1j * angle))) ** 2)
    if np.all(np.isnan(improvement)):
        raise ValueError("all trial periods are rank-deficient")
    best = int(np.nanargmax(improvement))
    return RVScan(
        periods_days=periods.copy(), improvement_fraction=improvement,
        spectral_window=window, best_period_days=float(periods[best]),
        best_semi_amplitude_ms=float(amplitudes[best]), chi2_null=chi2_null,
        chi2_best=float(chi2_values[best]),
    )
