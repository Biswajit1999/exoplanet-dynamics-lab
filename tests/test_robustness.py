"""Analytical and synthetic recovery checks for dynamical screening."""
import math
import numpy as np
import pytest
from exodynamics.dynamics.robustness import (
    first_order_resonance_screen, hill_spacing_ensemble, weighted_rv_scan,
)

def test_resonance_exact_and_nearby() -> None:
    assert math.isinf(first_order_resonance_screen(10, 15, 3).superperiod_days)
    near = first_order_resonance_screen(10, 15.3, 3)
    assert near.superperiod_days == pytest.approx(1 / abs(3 / 15.3 - 2 / 10))

def test_hill_reproducibility_and_mass_sensitivity() -> None:
    a = hill_spacing_ensemble((10, 14), (1, 1), 1, draws=128)
    b = hill_spacing_ensemble((10, 14), (1, 1), 1, draws=128)
    c = hill_spacing_ensemble((10, 14), (20, 20), 1, draws=128)
    assert a == b
    assert a.median_spacing > c.median_spacing

def test_rv_two_instrument_injection() -> None:
    rng = np.random.default_rng(13)
    t = np.sort(rng.uniform(0, 210, 140))
    names = np.where(np.arange(t.size) % 2, "A", "B")
    e = rng.uniform(0.7, 1.2, t.size)
    rv = np.where(names == "A", 7.0, -4.0)
    rv = rv + 3.4 * np.cos(2 * np.pi * t / 17 + 0.3) + rng.normal(0, e)
    scan = weighted_rv_scan(t, rv, e, names, np.linspace(14, 20, 121))
    assert abs(scan.best_period_days - 17) < 0.2
    assert scan.best_semi_amplitude_ms == pytest.approx(3.4, abs=0.4)
