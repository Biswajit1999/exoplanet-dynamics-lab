"""Transit ephemeris and robust light-curve utilities."""

from __future__ import annotations

import numpy as np


def normalize_flux(flux: np.ndarray) -> np.ndarray:
    values = np.asarray(flux, dtype=float)
    median = np.nanmedian(values)
    if not np.isfinite(median) or median == 0:
        raise ValueError("finite non-zero median required")
    return values / median


def linear_ephemeris(epoch: float, period: float, epochs: np.ndarray) -> np.ndarray:
    return epoch + period * np.asarray(epochs, dtype=float)


def observed_minus_calculated(observed_times: np.ndarray, epoch: float, period: float) -> tuple[np.ndarray, np.ndarray]:
    observed = np.asarray(observed_times, dtype=float)
    transit_numbers = np.rint((observed - epoch) / period).astype(int)
    return transit_numbers, observed - linear_ephemeris(epoch, period, transit_numbers)


def transit_probability(stellar_radius_solar: float, semimajor_axis_au: float, planet_radius_earth: float = 0.0) -> float:
    solar_radius_au = 0.00465047
    earth_radius_au = 4.26352e-5
    return min(1.0, (stellar_radius_solar * solar_radius_au + planet_radius_earth * earth_radius_au) / semimajor_axis_au)

