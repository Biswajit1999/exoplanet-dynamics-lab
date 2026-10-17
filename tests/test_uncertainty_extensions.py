import numpy as np
import pytest

from exodynamics.dynamics.uncertainty_extensions import (
    bounded_split_normal_draws,
    kepler_semimajor_uncertainty,
    pair_spacing_uncertainty,
    split_normal_moments,
)


def test_split_symmetric_mean_variance():
    mean,var=split_normal_moments(1.,.2,.2)
    assert np.isclose(mean,1.)
    assert np.isclose(var,.04)


def test_split_asymmetric_moments_match_mc():
    rng=np.random.default_rng(99)
    neg=rng.random(250000) < .2/(.2+.3)
    samples=.1 + np.where(neg,-.2*np.abs(rng.normal(size=len(neg))),
                          .3*np.abs(rng.normal(size=len(neg))))
    mean,var=split_normal_moments(.1,.2,.3)
    assert abs(samples.mean()-mean)<.002
    assert abs(samples.var()-var)<.002


def test_split_zero_uncertainty():
    assert split_normal_moments(.7,0,0)==(.7,0.)


def test_truncated_no_artificial_boundary_atom():
    x=bounded_split_normal_draws(.1,.2,.2,15000,lower=0)
    assert np.all(x>0)
    assert np.all(np.isfinite(x))
    assert np.mean(x)>.1


def test_truncated_reproducible():
    a=bounded_split_normal_draws(.1,.2,.3,2000,lower=0,upper=1,seed=4)
    b=bounded_split_normal_draws(.1,.2,.3,2000,lower=0,upper=1,seed=4)
    np.testing.assert_array_equal(a,b)


def test_bounded_rejects_impossible_constant():
    with pytest.raises(ValueError): bounded_split_normal_draws(-1,0,0,10,lower=0)


def test_kepler_zero_error():
    r=kepler_semimajor_uncertainty(365.256,1.,0,0,trials=1000)
    assert r.delta_sigma_au==0
    assert np.isclose(r.nominal_semimajor_au,r.mc_mean_au,rtol=1e-12)


def test_kepler_analytic_matches_monte_carlo():
    r=kepler_semimajor_uncertainty(365.256,1.,.1,.02,correlation=.3,trials=100000)
    assert abs(r.delta_sigma_au/r.mc_sigma_au-1)<.02
    assert abs(r.mc_mean_au-r.nominal_semimajor_au)<.001


def test_kepler_reject_bad_correlation():
    with pytest.raises(ValueError): kepler_semimajor_uncertainty(365,1,.1,.1,correlation=1.5)


def test_pair_near_3_2_high_probability():
    r=pair_spacing_uncertainty(10,15.02,.02,.03,3,5,.1,.2,1,.01,trials=30000)
    assert r.near_commensurability_probability>.95
    assert r.hill_separation_p05>0
    assert r.period_ratio_p05<r.period_ratio_median<r.period_ratio_p95


def test_pair_far_from_3_2_low_probability():
    r=pair_spacing_uncertainty(10,17.1,.02,.03,3,5,.1,.2,1,.01,trials=10000)
    assert r.near_commensurability_probability==0


def test_pair_reject_swapped_orbits():
    with pytest.raises(ValueError): pair_spacing_uncertainty(15,10,.1,.1,3,5,.1,.2,1,.01)
