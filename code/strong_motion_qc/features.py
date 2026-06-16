"""Strong-motion record features for onset/QC model development."""

from __future__ import annotations

import numpy as np

from .config import StrongMotionQCConfig
from .onset import effective_motion_onset


def vector_amplitude(waveform: np.ndarray) -> np.ndarray:
    """Return absolute amplitude for 1-D input or vector amplitude for 3-C input."""

    arr = np.asarray(waveform, dtype=np.float64)
    if arr.ndim == 1:
        return np.abs(arr)
    if arr.ndim == 2:
        return np.sqrt(np.sum(arr * arr, axis=0))
    raise ValueError("waveform must be 1-D or channels x samples")


def _mad_scale(values: np.ndarray) -> float:
    finite = values[np.isfinite(values)]
    if finite.size == 0:
        return float("nan")
    median = float(np.median(finite))
    mad = float(np.median(np.abs(finite - median)))
    return 1.4826 * mad


def _clip_fraction(values: np.ndarray) -> float:
    finite = np.abs(values[np.isfinite(values)])
    if finite.size == 0:
        return float("nan")
    max_abs = float(np.max(finite))
    if max_abs <= 0:
        return 0.0
    return float(np.mean(finite >= 0.999 * max_abs))


def compute_strong_motion_features(
    waveform: np.ndarray,
    sampling_rate: float,
    config: StrongMotionQCConfig | None = None,
) -> dict[str, float | bool]:
    """Compute label-free onset and QC features for a strong-motion record."""

    cfg = config or StrongMotionQCConfig()
    arr = np.asarray(waveform, dtype=np.float64)
    amp = vector_amplitude(arr)
    finite_mask = np.isfinite(arr)
    finite_fraction = float(finite_mask.mean()) if arr.size else 0.0
    cleaned = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    clean_amp = vector_amplitude(cleaned)
    onset = effective_motion_onset(cleaned, sampling_rate, cfg.onset)
    scale = _mad_scale(clean_amp)
    max_abs = float(np.max(clean_amp)) if clean_amp.size else float("nan")
    rms = float(np.sqrt(np.mean(clean_amp * clean_amp))) if clean_amp.size else float("nan")
    spike_score = max_abs / scale if np.isfinite(scale) and scale > 0 else float("nan")
    clip_fraction = _clip_fraction(amp)
    zero_fraction = float(np.mean(clean_amp == 0.0)) if clean_amp.size else float("nan")
    flags = {
        "flag_nonfinite": finite_fraction < cfg.finite_fraction_threshold,
        "flag_zero_heavy": zero_fraction > cfg.zero_fraction_threshold,
        "flag_clipped": clip_fraction > cfg.clip_fraction_threshold,
        "flag_spiky": np.isfinite(spike_score) and spike_score > cfg.spike_score_threshold,
    }
    return {
        "n_samples": int(clean_amp.size),
        "sampling_rate_hz": float(sampling_rate),
        "duration_sec": float(clean_amp.size / float(sampling_rate)),
        "finite_fraction": finite_fraction,
        "zero_fraction": zero_fraction,
        "max_abs": max_abs,
        "rms": rms,
        "mad_scale": scale,
        "spike_score": float(spike_score),
        "clip_fraction": clip_fraction,
        **onset,
        **flags,
        "qc_issue_count": int(sum(bool(v) for v in flags.values())),
    }
