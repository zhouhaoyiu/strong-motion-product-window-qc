"""Tests for relative PGV retention auditing."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from scripts import evaluate_strong_motion_pgv_retention as pgv


class PgvRetentionTests(unittest.TestCase):
    def test_direct_velocity_proxy_keeps_velocity_waveform(self) -> None:
        row = pd.Series({"units": "mps", "dataset": "InstanceGM", "sampling_rate_hz": 10.0})
        waveform = np.ones((3, 20), dtype=float)

        velocity, source = pgv.velocity_proxy(row, waveform)

        self.assertEqual(source, "direct_velocity")
        self.assertAlmostEqual(float(velocity.max()), 1.0)

    def test_acceleration_proxy_integrates_to_velocity(self) -> None:
        row = pd.Series({"units": "mps2", "dataset": "InstanceGM", "sampling_rate_hz": 10.0})
        waveform = np.zeros((3, 100), dtype=float)
        waveform[0, 20:40] = 1.0

        velocity, source = pgv.velocity_proxy(row, waveform)

        self.assertEqual(source, "integrated_acceleration")
        self.assertEqual(velocity.shape, waveform.shape)
        self.assertGreater(pgv.peak_vector_velocity(velocity), 0.0)

    def test_run_pgv_retention_writes_outputs_with_mocked_loader(self) -> None:
        features = pd.DataFrame(
            {
                "record_uid": ["r1"],
                "dataset": ["InstanceGM"],
                "priority_group": ["m4plus_strong_motion"],
                "split": ["dev"],
                "magnitude": [5.0],
                "sampling_rate_hz": [20.0],
                "units": ["mps"],
                "waveform_qc_status": ["ok"],
            }
        )
        selected = pd.DataFrame(
            {
                "record_uid": ["r1", "r1"],
                "dataset": ["InstanceGM", "InstanceGM"],
                "priority_group": ["m4plus_strong_motion", "m4plus_strong_motion"],
                "policy": ["feature_onset_fixed", "shortest_stable_no_catalog"],
                "selected_candidate": ["feature_onset_fixed", "full_record"],
                "selection_status": ["direct_candidate", "full_record_fallback"],
                "window_start_sample": [0, 0],
                "window_end_sample": [50, 200],
            }
        )
        waveform = np.zeros((3, 200), dtype=float)
        waveform[0, 150] = 10.0

        original_handles = pgv.load_waveform_handles
        original_loader = pgv.load_record_waveform
        try:
            pgv.load_waveform_handles = lambda _records, _knet_waveforms: (object(), None, None)
            pgv.load_record_waveform = lambda _row, _instance_data, _h5, _keys, _hp: waveform
            with tempfile.TemporaryDirectory() as tmp:
                outputs = pgv.run_pgv_retention(
                    features=features,
                    selected_windows=selected,
                    outdir=Path(tmp),
                    policies=["feature_onset_fixed", "shortest_stable_no_catalog"],
                )
                results = pd.read_csv(outputs["results"])
                full = results[results["policy"].eq("shortest_stable_no_catalog")].iloc[0]
                fixed = results[results["policy"].eq("feature_onset_fixed")].iloc[0]
                self.assertTrue(outputs["summary"].exists())
                self.assertTrue(outputs["report"].exists())

        finally:
            pgv.load_waveform_handles = original_handles
            pgv.load_record_waveform = original_loader

        self.assertAlmostEqual(float(full["pgv_retention"]), 1.0, places=6)
        self.assertEqual(float(fixed["pgv_retention"]), 0.0)
        self.assertTrue(bool(fixed["pgv_unstable"]))


if __name__ == "__main__":
    unittest.main()
