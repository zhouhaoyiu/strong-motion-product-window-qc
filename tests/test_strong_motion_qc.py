"""Tests for strong-motion onset and QC helpers."""

from __future__ import annotations

import unittest

import numpy as np

from strong_motion_qc import (
    OnsetConfig,
    compute_strong_motion_features,
    effective_motion_onset,
    energy_fraction_time,
    vector_amplitude,
)


class StrongMotionQCTests(unittest.TestCase):
    def test_energy_fraction_time_tracks_delayed_motion(self) -> None:
        waveform = np.zeros(1000, dtype=np.float64)
        waveform[400:600] = 2.0

        onset = energy_fraction_time(waveform, sampling_rate=100.0, fraction=0.01)

        self.assertAlmostEqual(onset, 4.01, places=2)

    def test_effective_motion_onset_combines_energy_and_threshold(self) -> None:
        waveform = np.zeros(1000, dtype=np.float64)
        waveform[:300] = 0.01
        waveform[500:700] = 1.0
        cfg = OnsetConfig(noise_window_sec=2.0, threshold_sigma=5.0, min_duration_sec=0.05)

        result = effective_motion_onset(waveform, sampling_rate=100.0, config=cfg)

        self.assertGreaterEqual(result["onset_sec"], 4.9)
        self.assertLessEqual(result["onset_sec"], 5.1)
        self.assertGreater(result["significant_duration_sec"], 1.0)

    def test_vector_amplitude_handles_three_components(self) -> None:
        waveform = np.array([[3.0, 0.0], [4.0, 0.0], [0.0, 12.0]])

        amp = vector_amplitude(waveform)

        np.testing.assert_allclose(amp, np.array([5.0, 12.0]))

    def test_qc_features_flag_nonfinite_and_clipping(self) -> None:
        waveform = np.zeros(1000, dtype=np.float64)
        waveform[200:500] = 1.0
        waveform[10] = np.nan
        waveform[700:710] = 20.0

        features = compute_strong_motion_features(waveform, sampling_rate=100.0)

        self.assertEqual(features["n_samples"], 1000)
        self.assertTrue(features["flag_nonfinite"])
        self.assertTrue(features["flag_clipped"])
        self.assertGreaterEqual(features["qc_issue_count"], 1)


if __name__ == "__main__":
    unittest.main()
