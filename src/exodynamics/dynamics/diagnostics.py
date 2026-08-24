"""Unit-explicit analytical dynamics diagnostics."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

G_SI = 6.67430e-11
AU_M = 149_597_870_700.0
DAY_S = 86_400.0
M_SUN_KG = 1.98847e30
M_EARTH_KG = 5.9722e24


def semimajor_axis_au(period_days: float, stellar_mass_solar: float, planet_mass_earth: float = 0.0) -> float:
    period_s = period_days * DAY_S
    total_mass = stellar_mass_solar * M_SUN_KG + planet_mass_earth * M_EARTH_KG
    return (G_SI * total_mass * period_s**2 / (4 * math.pi**2)) ** (1 / 3) / AU_M


def orbital_period_days(semimajor_axis_au_value: float, stellar_mass_solar: float) -> float:
    a_m = semimajor_axis_au_value * AU_M
    return 2 * math.pi * math.sqrt(a_m**3 / (G_SI * stellar_mass_solar * M_SUN_KG)) / DAY_S


def mutual_hill_radius_au(a_inner: float, a_outer: float, m_inner_earth: float, m_outer_earth: float, stellar_mass_solar: float) -> float:
    mass_ratio = (m_inner_earth + m_outer_earth) * M_EARTH_KG / (3 * stellar_mass_solar * M_SUN_KG)
    return ((a_inner + a_outer) / 2) * mass_ratio ** (1 / 3)


def mutual_hill_separation(a_inner: float, a_outer: float, m_inner_earth: float, m_outer_earth: float, stellar_mass_solar: float) -> float:
    return (a_outer - a_inner) / mutual_hill_radius_au(a_inner, a_outer, m_inner_earth, m_outer_earth, stellar_mass_solar)


def angular_momentum_deficit(mass: np.ndarray, semimajor_axis: np.ndarray, eccentricity: np.ndarray, inclination_rad: np.ndarray) -> float:
    circular = mass * np.sqrt(semimajor_axis)
    return float(np.sum(circular * (1 - np.sqrt(1 - eccentricity**2) * np.cos(inclination_rad))))


@dataclass(frozen=True)
class Commensurability:
    numerator: int
    denominator: int
    observed_ratio: float
    fractional_offset: float
    classification: str


def nearest_commensurability(period_inner: float, period_outer: float, tolerance: float = 0.02) -> Commensurability:
    ratio = period_outer / period_inner
    candidates = [(2, 1), (3, 2), (4, 3), (5, 4), (5, 3), (3, 1)]
    p, q = min(candidates, key=lambda item: abs(ratio - item[0] / item[1]) / (item[0] / item[1]))
    offset = (ratio - p / q) / (p / q)
    label = "near_commensurability" if abs(offset) <= tolerance else "not_near_commensurability"
    return Commensurability(p, q, ratio, offset, label)


def rv_semi_amplitude_ms(period_days: float, planet_mass_earth: float, stellar_mass_solar: float, eccentricity: float = 0.0, inclination_deg: float = 90.0) -> float:
    period_s = period_days * DAY_S
    mp = planet_mass_earth * M_EARTH_KG
    ms = stellar_mass_solar * M_SUN_KG
    return (2 * math.pi * G_SI / period_s) ** (1 / 3) * mp * math.sin(math.radians(inclination_deg)) / ((ms + mp) ** (2 / 3) * math.sqrt(1 - eccentricity**2))

