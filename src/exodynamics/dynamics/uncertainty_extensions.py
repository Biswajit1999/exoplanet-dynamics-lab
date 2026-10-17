"""Reproducible distribution and two-planet uncertainty diagnostics.

Pure numerical methods, no archive access. Synthetic examples are not orbital
solutions and proximity to commensurability is not resonance confirmation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from exodynamics.dynamics.diagnostics import (
    AU_M,
    DAY_S,
    G_SI,
    M_EARTH_KG,
    M_SUN_KG,
)


def split_normal_moments(value: float, error_minus: float, error_plus: float) -> tuple[float, float]:
    """Exact mean and variance of the repository's two-piece half-normal sampler.

    Probability of the negative half is sigma_minus/(sigma_minus+sigma_plus).
    This is NOT the same as a Gaussian with unequal upper/lower error bars.
    No truncation or clipping is included in these moments.
    """
    if not all(np.isfinite([value, error_minus, error_plus])) or min(error_minus, error_plus) < 0:
        raise ValueError('finite value and nonnegative finite uncertainties required')
    total = error_minus + error_plus
    if total == 0:
        return float(value), 0.
    shift = np.sqrt(2 / np.pi) * (error_plus - error_minus)
    raw2 = (error_minus**3 + error_plus**3) / total
    return float(value + shift), float(max(0., raw2 - shift**2))


def bounded_split_normal_draws(
    value: float, error_minus: float, error_plus: float, size: int,
    *, lower: float = 0., upper: float = np.inf, seed: int = 20261017,
    max_attempt_factor: int = 1000,
) -> np.ndarray:
    """Reject out-of-range draws rather than clipping them to physical bounds.

    Rejection samples the correctly *truncated* two-piece distribution; unlike
    np.clip it does not introduce an artificial point mass at either bound.
    Raises when acceptance is too small instead of silently returning biased data.
    """
    if (size < 1 or max_attempt_factor < 1 or not all(np.isfinite([value,error_minus,error_plus,lower]))
            or not (np.isfinite(upper) or np.isposinf(upper)) or lower > upper
            or error_minus < 0 or error_plus < 0):
        raise ValueError('invalid bounded split-normal configuration')
    if lower == upper:
        if error_minus == error_plus == 0 and value == lower:
            return np.full(size, value)
        raise ValueError('zero-width interval has zero acceptance for continuous draws')
    if error_minus == error_plus == 0:
        if not lower <= value <= upper:
            raise ValueError('deterministic value outside bounds')
        return np.full(size, value)
    rng = np.random.default_rng(seed)
    accepted = []
    remaining = size
    attempted = 0
    total = error_minus + error_plus
    while remaining:
        batch = min(max(2 * remaining, 100), size * max_attempt_factor - attempted)
        if batch <= 0:
            raise ValueError('acceptance too small for requested bounds')
        negative = rng.random(batch) < error_minus / total
        noise = np.abs(rng.normal(size=batch))
        draws = value + np.where(negative, -error_minus * noise, error_plus * noise)
        keep = draws[(draws >= lower) & (draws <= upper)][:remaining]
        accepted.append(keep)
        remaining -= len(keep)
        attempted += batch
    return np.concatenate(accepted)


@dataclass(frozen=True)
class KeplerUncertainty:
    nominal_semimajor_au: float
    delta_sigma_au: float
    mc_mean_au: float
    mc_sigma_au: float
    mc_p05_au: float
    mc_p95_au: float
    n_draws: int


def kepler_semimajor_uncertainty(
    period_days: float, stellar_mass_solar: float,
    sigma_period_days: float, sigma_stellar_mass_solar: float,
    *, correlation: float = 0., trials: int = 40_000,
    seed: int = 20261017,
) -> KeplerUncertainty:
    """Delta method versus correlated Monte Carlo for Kepler's third law.

    a=[G*M*(P*86400)^2/(4*pi^2)]^(1/3)/AU.
    Var(a)/a^2 = (2*sP/(3P))^2 + (sM/(3M))^2
                 + 4*rho*sP*sM/(9*P*M).
    Planet mass neglected in this first-order diagnostic.
    """
    v=(period_days, stellar_mass_solar, sigma_period_days, sigma_stellar_mass_solar, correlation)
    if (not all(np.isfinite(v)) or period_days <= 0 or stellar_mass_solar <= 0
            or sigma_period_days < 0 or sigma_stellar_mass_solar < 0
            or abs(correlation) > 1 or trials < 100):
        raise ValueError('invalid Kepler uncertainty inputs')
    a = ((G_SI * stellar_mass_solar * M_SUN_KG * (period_days * DAY_S)**2)
         / (4*np.pi**2))**(1/3)/AU_M
    cov = correlation * sigma_period_days * sigma_stellar_mass_solar
    relvar = (4/9)*(sigma_period_days/period_days)**2 + (1/9)*(sigma_stellar_mass_solar/stellar_mass_solar)**2 + (4/9)*cov/(period_days*stellar_mass_solar)
    if relvar < -1e-12:
        raise ValueError('negative covariance-propagated variance')
    covmat=np.array([[sigma_period_days**2,cov],[cov,sigma_stellar_mass_solar**2]])
    rng=np.random.default_rng(seed)
    samples=rng.multivariate_normal([period_days,stellar_mass_solar],covmat,trials,check_valid='raise')
    if np.any(samples <= 0):
        raise ValueError('Gaussian uncertainty generated nonphysical period or stellar mass; use bounded prior')
    axes=((G_SI * samples[:,1] * M_SUN_KG * (samples[:,0]*DAY_S)**2)/(4*np.pi**2))**(1/3)/AU_M
    return KeplerUncertainty(float(a),float(a*np.sqrt(max(relvar,0))),float(axes.mean()),
                             float(axes.std(ddof=1)),float(np.quantile(axes,.05)),
                             float(np.quantile(axes,.95)),trials)


@dataclass(frozen=True)
class PairUncertainty:
    period_ratio_median: float
    period_ratio_p05: float
    period_ratio_p95: float
    hill_separation_median: float
    hill_separation_p05: float
    hill_separation_p95: float
    near_commensurability_probability: float
    commensurability_numerator: int
    commensurability_denominator: int
    trials: int


def pair_spacing_uncertainty(
    inner_period_days: float, outer_period_days: float,
    sigma_inner_period_days: float, sigma_outer_period_days: float,
    inner_mass_earth: float, outer_mass_earth: float,
    sigma_inner_mass_earth: float, sigma_outer_mass_earth: float,
    stellar_mass_solar: float, sigma_stellar_mass_solar: float,
    *, resonance: tuple[int, int] = (3, 2), tolerance: float = .02,
    trials: int = 30_000, seed: int = 20261017,
) -> PairUncertainty:
    """Propagate independent parameter errors into period ratio and Hill spacing.

    No dynamical integration, correlated posterior, mutual inclination or
    resonance-angle libration is modeled; proximity is NOT resonance trapping.
    """
    means=np.array([inner_period_days,outer_period_days,inner_mass_earth,
                    outer_mass_earth,stellar_mass_solar],dtype=float)
    errors=np.array([sigma_inner_period_days,sigma_outer_period_days,
                     sigma_inner_mass_earth,sigma_outer_mass_earth,
                     sigma_stellar_mass_solar],dtype=float)
    p,q=resonance
    if (not np.all(np.isfinite(means)) or not np.all(np.isfinite(errors))
            or np.any(means <= 0) or np.any(errors < 0) or inner_period_days >= outer_period_days
            or p <= q or q <= 0 or not 0 < tolerance < 1 or trials < 100):
        raise ValueError('invalid two-planet uncertainty inputs')
    rng=np.random.default_rng(seed)
    draws=rng.normal(means,errors,(trials,5))
    if np.any(draws <= 0) or np.any(draws[:,1] <= draws[:,0]):
        raise ValueError('uncertainty produces nonphysical or swapped orbits; use constrained posterior')
    inner_p,outer_p,m1,m2,ms=draws.T
    a1=(G_SI*ms*M_SUN_KG*(inner_p*DAY_S)**2/(4*np.pi**2))**(1/3)/AU_M
    a2=(G_SI*ms*M_SUN_KG*(outer_p*DAY_S)**2/(4*np.pi**2))**(1/3)/AU_M
    hill=(a2-a1)/(.5*(a1+a2)*((m1+m2)*M_EARTH_KG/(3*ms*M_SUN_KG))**(1/3))
    ratios=outer_p/inner_p
    target=p/q
    near=np.mean(np.abs(ratios/target-1) <= tolerance)
    return PairUncertainty(float(np.median(ratios)),float(np.quantile(ratios,.05)),
                           float(np.quantile(ratios,.95)),float(np.median(hill)),
                           float(np.quantile(hill,.05)),float(np.quantile(hill,.95)),
                           float(near),int(p),int(q),trials)


def example_summary() -> dict[str, object]:
    """Synthetic, deliberately non-identifying two-planet illustration."""
    mean,var=split_normal_moments(.1,.2,.3)
    clipped=np.maximum(np.random.default_rng(17).normal(.1,.2,10000),0)
    truncated=bounded_split_normal_draws(.1,.2,.2,10000,lower=0,seed=17)
    return {'split_normal':{'analytic_mean':mean,'analytic_variance':var,
                            'clipped_boundary_fraction':float(np.mean(clipped==0)),
                            'truncated_boundary_fraction':float(np.mean(truncated==0))},
            'kepler':asdict(kepler_semimajor_uncertainty(365.256,1.,.1,.02,correlation=.2)),
            'pair':asdict(pair_spacing_uncertainty(10.,15.02,.04,.06,3.,5.,.3,.5,1.,.02))}
