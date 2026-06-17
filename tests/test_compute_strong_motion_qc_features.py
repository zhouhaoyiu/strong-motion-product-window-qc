"""Tests for waveform-level StrongMotion-QC feature computation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

from scripts import compute_strong_motion_qc_features as qc_features


def base_row(dataset: str, uid: str) -> pd.Series:
    return pd.Series(
        {
            "record_uid": uid,
            "dataset": dataset,
            "source_row_index": 0,
            "split": "train",
            "priority_group": "m3_to_m4_small_event",
            "magnitude_bin": "3-4",
            "magnitude": 3.5,
            "event_id": "event-1",
            "station_network": "AA",
            "station_code": "STA",
            "trace_name": "TRACE1",
            "waveform_key": "TRACE1",
            "component_order": "ZNE",
            "channel_type": "HN",
            "units": "mps2",
            "sampling_rate_hz": 100.0,
            "n_samples": 1000,
            "duration_sec": 10.0,
            "has_catalog_p": True,
            "catalog_p_sec": 3.0,
            "catalog_p_sample": 300,
            "catalog_fields_for_evaluation_only": "catalog_p_sec,catalog_s_sec,catalog_p_sample,catalog_s_sample",
        }
    )


class FakeInstanceData:
    def get_waveforms(self, indexes):
        waveform = np.zeros((3, 1000), dtype=np.float32)
        waveform[:, 300:500] = 2.0
        return [waveform]


class FakePNWData:
    def get_waveforms(self, indexes):
        waveform = np.zeros((3, 1000), dtype=np.float32)
        waveform[:, 300:500] = 1.0
        return [waveform]


class ComputeStrongMotionQCFeaturesTests(unittest.TestCase):
    def test_compute_row_loads_instance_waveform(self) -> None:
        result = qc_features.compute_row(base_row("InstanceGM", "InstanceGM:0"), instance_data=FakeInstanceData())

        self.assertEqual(result["waveform_qc_status"], "ok")
        self.assertEqual(result["resolved_waveform_key"], "InstanceGM:0")
        self.assertIn("feature_onset_sec", result)
        self.assertGreaterEqual(result["feature_qc_issue_count"], 0)

    def test_compute_row_loads_pnw_waveform(self) -> None:
        result = qc_features.compute_row(
            base_row("PNWAccelerometers", "PNWAccelerometers:0"),
            pnw_data=FakePNWData(),
        )

        self.assertEqual(result["waveform_qc_status"], "ok")
        self.assertEqual(result["resolved_waveform_key"], "PNWAccelerometers:0")
        self.assertIn("feature_onset_sec", result)

    def test_compute_row_loads_knet_hdf5_waveform(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            h5_path = Path(tmp) / "waveforms.hdf5"
            with h5py.File(h5_path, "w") as h5:
                data = np.zeros((1000, 3), dtype=np.float32)
                data[300:500, :] = 1.5
                h5.create_dataset("data/TRACE1", data=data)
            with h5py.File(h5_path, "r") as h5:
                keys = set(qc_features.list_hdf5_keys(h5))
                result = qc_features.compute_row(base_row("K-NET", "K-NET:0"), knet_h5=h5, knet_keys=keys)

        self.assertEqual(result["waveform_qc_status"], "ok")
        self.assertEqual(result["resolved_waveform_key"], "data/TRACE1")
        self.assertEqual(result["waveform_shape"], "3x1000")
        self.assertIn("feature_energy_onset_sec", result)

    def test_compute_row_loads_waveforms_prefixed_knet_hdf5_waveform(self) -> None:
        row = base_row("K-NET", "K-NET:0")
        row["waveform_key"] = "/waveforms/TRACE1"
        with tempfile.TemporaryDirectory() as tmp:
            h5_path = Path(tmp) / "waveforms.hdf5"
            with h5py.File(h5_path, "w") as h5:
                data = np.zeros((3, 1000), dtype=np.float32)
                data[:, 300:500] = 1.5
                h5.create_dataset("waveforms/TRACE1", data=data)
            with h5py.File(h5_path, "r") as h5:
                keys = set(qc_features.list_hdf5_keys(h5))
                result = qc_features.compute_row(row, knet_h5=h5, knet_keys=keys)

        self.assertEqual(result["waveform_qc_status"], "ok")
        self.assertEqual(result["resolved_waveform_key"], "waveforms/TRACE1")
        self.assertEqual(result["waveform_shape"], "3x1000")

    def test_compute_row_can_highpass_knet_waveform(self) -> None:
        row = base_row("K-NET", "K-NET:0")
        with tempfile.TemporaryDirectory() as tmp:
            h5_path = Path(tmp) / "waveforms.hdf5"
            with h5py.File(h5_path, "w") as h5:
                t = np.arange(1000, dtype=np.float32) / 100.0
                data = np.vstack([10.0 + np.sin(2 * np.pi * 5.0 * t)] * 3).astype(np.float32)
                h5.create_dataset("waveforms/TRACE1", data=data)
            row["waveform_key"] = "waveforms/TRACE1"
            with h5py.File(h5_path, "r") as h5:
                keys = set(qc_features.list_hdf5_keys(h5))
                result = qc_features.compute_row(
                    row,
                    knet_h5=h5,
                    knet_keys=keys,
                    knet_highpass_hz=1.0,
                )

        self.assertEqual(result["waveform_qc_status"], "ok")
        self.assertEqual(result["waveform_preprocess"], "knet_highpass_1hz")
        self.assertIn("feature_energy_onset_sec", result)

    def test_compute_row_keeps_errors_visible(self) -> None:
        result = qc_features.compute_row(base_row("Unknown", "bad:0"))

        self.assertEqual(result["waveform_qc_status"], "error")
        self.assertIn("Unsupported dataset", result["waveform_error"])

    def test_summarize_handles_all_error_rows(self) -> None:
        df = pd.DataFrame(
            [
                {
                    "dataset": "K-NET",
                    "priority_group": "m4plus_strong_motion",
                    "waveform_qc_status": "error",
                }
            ]
        )
        summary = qc_features.summarize(df)

        self.assertEqual(int(summary.loc[0, "loaded_records"]), 0)
        self.assertEqual(int(summary.loc[0, "qc_issue_records"]), 0)


if __name__ == "__main__":
    unittest.main()
