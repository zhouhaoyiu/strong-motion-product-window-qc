"""Label-free effective-motion onset proxies for strong-motion records."""

from __future__ import annotations

import numpy as np

from .config import OnsetConfig


def _as_1d_signal(values: np.ndarray) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    if arr.ndim == 1:
        return arr
    if arr.ndim == 2:
        return np.sqrt(np.sum(arr * arr, axis=0))
    raise ValueError("waveform must be 1-D or channels x samples")


def _validate_sampling_rate(sampling_rate: float) -> float:
    sr = float(sampling_rate)
    if not np.isfinite(sr) or sr <= 0:
        raise ValueError("sampling_rate must be a positive finite value")
    return sr


def arias_curve(waveform: np.ndarray, sampling_rate: float) -> np.ndarray:
    """Return a normalized cumulative squared-amplitude curve.

    This is an Arias-style relative energy curve. It intentionally does not
    assume physical acceleration units, so it can be used for K-NET, InstanceGM,
    and intermediate normalized arrays.
    """

    sr = _validate_sampling_rate(sampling_rate)
    signal = np.nan_to_num(_as_1d_signal(waveform), nan=0.0, posinf=0.0, neginf=0.0)
    if signal.size == 0:
        return np.array([], dtype=np.float64)
    energy = np.cumsum(signal * signal) / sr
    total = float(energy[-1])
    if total <= 0 or not np.isfinite(total):
        return np.zeros_like(energy)
    return energy / total


def energy_fraction_time(
    waveform: np.ndarray,
    sampling_rate: float,
    fraction: float,
) -> float:
    """Return the first time where cumulative relative energy reaches fraction."""

    sr = _validate_sampling_rate(sampling_rate)
    if not 0 <= fraction <= 1:
        raise ValueError("fraction must be in [0, 1]")
    curve = arias_curve(waveform, sr)
    if curve.size == 0 or float(curve[-1]) <= 0:
        return float("nan")
    idx = int(np.searchsorted(curve, fraction, side="left"))
    idx = min(idx, curve.size - 1)
    return idx / sr


def _noise_threshold_onset(
    signal: np.ndarray,
    sampling_rate: float,
    config: OnsetConfig,
) -> float:
    sr = _validate_sampling_rate(sampling_rate)
    if signal.size == 0:
        return float("nan")
    start_idx = max(0, int(config.min_onset_sec * sr))
    noise_n = max(1, int(config.noise_window_sec * sr))
    noise = signal[: min(noise_n, signal.size)]
    median = float(np.median(noise))
    mad = float(np.median(np.abs(noise - median)))
    scale = 1.4826 * mad
    if not np.isfinite(scale) or scale <= 0:
        scale = float(np.std(noise))
    if not np.isfinite(scale) or scale <= 0:
        return float("nan")
    threshold = median + config.threshold_sigma * scale
    flags = np.abs(signal) >= abs(threshold)
    min_samples = max(1, int(config.min_duration_sec * sr))
    run = 0
    for idx in range(start_idx, signal.size):
        run = run + 1 if flags[idx] else 0
        if run >= min_samples:
            return (idx - min_samples + 1) / sr
    return float("nan")


def effective_motion_onset(
    waveform: np.ndarray,
    sampling_rate: float,
    config: OnsetConfig | None = None,
) -> dict[str, float]:
    """Estimate effective-motion onset and significant duration without labels."""

    cfg = config or OnsetConfig()
    sr = _validate_sampling_rate(sampling_rate)
    signal = np.nan_to_num(_as_1d_signal(waveform), nan=0.0, posinf=0.0, neginf=0.0)
    t_start = energy_fraction_time(signal, sr, cfg.energy_start_fraction)
    t_end = energy_fraction_time(signal, sr, cfg.energy_end_fraction)
    threshold_onset = _noise_threshold_onset(signal, sr, cfg)
    candidates = [v for v in [t_start, threshold_onset] if np.isfinite(v)]
    onset = min(candidates) if candidates else float("nan")
    duration = t_end - t_start if np.isfinite(t_start) and np.isfinite(t_end) else float("nan")
    return {
        "onset_sec": float(onset),
        "energy_onset_sec": float(t_start),
        "threshold_onset_sec": float(threshold_onset),
        "energy_end_sec": float(t_end),
        "significant_duration_sec": float(duration),
    }
