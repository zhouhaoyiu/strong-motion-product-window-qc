"""Configuration objects for strong-motion automatic processing."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class OnsetConfig:
    """Parameters for label-free effective-motion onset proxies."""

    energy_start_fraction: float = 0.01
    energy_end_fraction: float = 0.95
    noise_window_sec: float = 3.0
    threshold_sigma: float = 6.0
    min_duration_sec: float = 0.1
    min_onset_sec: float = 0.0


@dataclass(frozen=True)
class StrongMotionQCConfig:
    """Heuristic QC settings for strong-motion records."""

    onset: OnsetConfig = field(default_factory=OnsetConfig)
    clip_fraction_threshold: float = 0.002
    zero_fraction_threshold: float = 0.05
    finite_fraction_threshold: float = 1.0
    spike_score_threshold: float = 80.0
