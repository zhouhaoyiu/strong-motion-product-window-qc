"""Tests for StrongMotion-QC window-stability evaluation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from scripts import evaluate_strong_motion_window_stability as stability


class EvaluateStrongMotionWindowStabilityTests(unittest.TestCase):
    def test_evaluate_window_flags_peak_outside_and_product_loss(self) -> None:
        signal = np.zeros(100, dtype=float)
        signal[80] = 10.0
        signal[10:20] = 1.0

        out = stability.evaluate_window(
            signal,
            sampling_rate=10.0,
            start_sec=0.0,
            end_sec=3.0,
            pga_retention_threshold=0.99,
            energy_retention_threshold=0.95,
        )

        self.assertTrue(out["window_unstable"])
        self.assertFalse(out["peak_inside_window"])
        self.assertIn("peak_outside", out["failure_reason"])
        self.assertLess(out["pga_retention"], 0.99)

    def test_candidate_windows_include_catalog_only_when_available(self) -> None:
        row = pd.Series(
            {
                "feature_onset_sec": 5.0,
                "feature_energy_onset_sec": 6.0,
                "feature_energy_end_sec": 20.0,
                "has_catalog_p": True,
                "catalog_p_sec": 4.0,
            }
        )

        candidates = stability.candidate_windows(
            row,
            n_samples=1000,
            sampling_rate=10.0,
            pre_sec=2.0,
            fixed_after_sec=40.0,
            adaptive_post_sec=3.0,
        )

        names = {item["candidate"] for item in candidates}
        self.assertIn("catalog_p_fixed", names)
        self.assertIn("feature_onset_to_energy_end", names)
        adaptive = next(item for item in candidates if item["candidate"] == "feature_onset_to_energy_end")
        self.assertAlmostEqual(float(adaptive["start_sec"]), 3.0)
        self.assertAlmostEqual(float(adaptive["end_sec"]), 23.0)

    def test_run_window_stability_writes_outputs_with_mocked_loader(self) -> None:
        features = pd.DataFrame(
            {
                "record_uid": ["r1"],
                "dataset": ["InstanceGM"],
                "priority_group": ["m4"],
                "split": ["dev"],
                "magnitude": [5.0],
                "sampling_rate_hz": [10.0],
                "waveform_qc_status": ["ok"],
                "feature_onset_sec": [2.0],
                "feature_energy_onset_sec": [2.0],
                "feature_energy_end_sec": [8.0],
                "catalog_p_sec": [2.0],
                "has_catalog_p": [True],
                "feature_spike_score": [1.0],
                "feature_significant_duration_sec": [6.0],
            }
        )
        waveform = np.zeros((3, 100), dtype=float)
        waveform[:, 30] = 2.0

        original_load = stability.load_instance_waveform
        original_open = stability.load_waveforms_for_rows
        try:
            stability.load_waveforms_for_rows = lambda _features, _knet_waveforms: (object(), None, None, None)
            stability.load_instance_waveform = lambda _instance_data, _row: (waveform, "mock")
            with tempfile.TemporaryDirectory() as tmp:
                outputs = stability.run_window_stability(
                    features=features,
                    outdir=Path(tmp),
                    max_records=None,
                    per_group=None,
                )
                self.assertTrue(outputs["results"].exists())
                self.assertTrue(outputs["summary"].exists())
                self.assertTrue(outputs["report"].exists())
                results = pd.read_csv(outputs["results"])
                self.assertIn("pga_retention", results.columns)
        finally:
            stability.load_instance_waveform = original_load
            stability.load_waveforms_for_rows = original_open


if __name__ == "__main__":
    unittest.main()
