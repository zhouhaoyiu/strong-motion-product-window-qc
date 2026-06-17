"""Tests for response-spectrum retention auditing."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from scripts import evaluate_strong_motion_response_spectrum_retention as spectrum


class ResponseSpectrumRetentionTests(unittest.TestCase):
    def test_pseudo_spectral_acceleration_prefers_matching_period(self) -> None:
        sampling_rate = 100.0
        time = np.arange(0, 20, 1 / sampling_rate)
        signal = np.sin(2 * np.pi * time / 1.0)

        psa_1s = spectrum.pseudo_spectral_acceleration(signal, period=1.0, damping=0.05, sampling_rate=sampling_rate)
        psa_02s = spectrum.pseudo_spectral_acceleration(signal, period=0.2, damping=0.05, sampling_rate=sampling_rate)

        self.assertGreater(psa_1s, psa_02s)

    def test_prepare_windows_skips_missing_candidates(self) -> None:
        selected = pd.DataFrame(
            {
                "record_uid": ["a", "a"],
                "policy": ["catalog_p_fixed", "feature_onset_fixed"],
                "selection_status": ["missing_candidate", "direct_candidate"],
                "window_start_sample": [np.nan, 10],
                "window_end_sample": [np.nan, 50],
            }
        )

        out = spectrum.prepare_windows(selected, ["catalog_p_fixed", "feature_onset_fixed"])

        self.assertEqual(len(out), 1)
        self.assertEqual(out.iloc[0]["policy"], "feature_onset_fixed")
        self.assertEqual(int(out.iloc[0]["window_start_sample"]), 10)

    def test_run_response_spectrum_retention_writes_outputs_with_mocked_loader(self) -> None:
        features = pd.DataFrame(
            {
                "record_uid": ["r1"],
                "dataset": ["InstanceGM"],
                "priority_group": ["m4plus_strong_motion"],
                "split": ["dev"],
                "magnitude": [5.0],
                "sampling_rate_hz": [50.0],
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
                "window_end_sample": [100, 500],
                "window_duration_sec": [2.0, 10.0],
            }
        )
        time = np.arange(500) / 50.0
        waveform = np.vstack(
            [
                np.sin(2 * np.pi * time / 1.0),
                np.zeros_like(time),
                np.zeros_like(time),
            ]
        )

        original_handles = spectrum.load_waveform_handles
        original_loader = spectrum.load_record_waveform
        try:
            spectrum.load_waveform_handles = lambda _records, _knet_waveforms: (object(), None, None, None)
            spectrum.load_record_waveform = lambda _row, _instance_data, _h5, _keys, _hp, pnw_data=None: waveform
            with tempfile.TemporaryDirectory() as tmp:
                outputs = spectrum.run_response_spectrum_retention(
                    features=features,
                    selected_windows=selected,
                    outdir=Path(tmp),
                    periods=[1.0],
                    policies=["feature_onset_fixed", "shortest_stable_no_catalog"],
                )
                self.assertTrue(outputs["results"].exists())
                self.assertTrue(outputs["summary"].exists())
                self.assertTrue(outputs["report"].exists())
                results = pd.read_csv(outputs["results"])
                self.assertIn("psa_retention", results.columns)
                full = results[results["policy"].eq("shortest_stable_no_catalog")].iloc[0]
                self.assertAlmostEqual(float(full["psa_retention"]), 1.0, places=6)
        finally:
            spectrum.load_waveform_handles = original_handles
            spectrum.load_record_waveform = original_loader


if __name__ == "__main__":
    unittest.main()
