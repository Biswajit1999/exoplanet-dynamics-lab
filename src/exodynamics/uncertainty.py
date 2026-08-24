"""Reproducible sampling of symmetric and asymmetric published uncertainties."""

from __future__ import annotations

import numpy as np


def split_normal_draws(value: float, error_minus: float, error_plus: float, size: int, seed: int = 42, lower: float | None = None, upper: float | None = None) -> np.ndarray:
    if error_minus < 0 or error_plus < 0:
        raise ValueError("uncertainty magnitudes must be non-negative")
    rng = np.random.default_rng(seed)
    side = rng.random(size) < error_minus / max(error_minus + error_plus, np.finfo(float).eps)
    draws = value + np.where(side, -np.abs(rng.normal(0, error_minus, size)), np.abs(rng.normal(0, error_plus, size)))
    if lower is not None:
        draws = np.maximum(draws, lower)
    if upper is not None:
        draws = np.minimum(draws, upper)
    return draws

