"""Radial-velocity forward model with explicit instrument offsets."""

from __future__ import annotations

import numpy as np


def circular_multi_planet_rv(time_days: np.ndarray, periods_days: np.ndarray, amplitudes_ms: np.ndarray, phases_rad: np.ndarray, offset_ms: float = 0.0) -> np.ndarray:
    time = np.asarray(time_days, dtype=float)
    model = np.full_like(time, float(offset_ms))
    for period, amplitude, phase in zip(periods_days, amplitudes_ms, phases_rad, strict=True):
        model += amplitude * np.cos(2 * np.pi * time / period + phase)
    return model


def apply_instrument_offsets(model_ms: np.ndarray, instruments: np.ndarray, offsets_ms: dict[str, float]) -> np.ndarray:
    result = np.asarray(model_ms, dtype=float).copy()
    names = np.asarray(instruments).astype(str)
    for instrument, offset in offsets_ms.items():
        result[names == instrument] += offset
    return result

