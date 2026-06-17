"""Tests for the all-magnitude StrongMotion-QC metadata manifest."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts import build_strong_motion_qc_full_manifest as builder


class BuildStrongMotionQCFullManifestTests(unittest.TestCase):
    def test_full_manifest_keeps_sub_m4_records(self) -> None:
        instance = pd.DataFrame(
            [
                {
                    "source_id": "ev2",
                    "station_network_code": "AA",
                    "station_code": "S1",
                    "station_channels": "HN",
                    "source_magnitude": 2.8,
                    "source_depth_km": 8.0,
                    "path_ep_distance_km": 40.0,
                    "trace_sampling_rate_hz": 100.0,
                    "trace_npts": 12000,
                    "trace_P_arrival_sample": 2000,
                    "trace_S_arrival_sample": 4000,
                    "trace_deconvolved_units": "mps2",
                    "trace_component_order": "ZNE",
                    "split": "train",
                },
                {
                    "source_id": "ev4",
                    "station_network_code": "AA",
                    "station_code": "S2",
                    "station_channels": "HN",
                    "source_magnitude": 4.3,
                    "source_depth_km": 8.0,
                    "path_ep_distance_km": 50.0,
                    "trace_sampling_rate_hz": 100.0,
                    "trace_npts": 12000,
                    "trace_P_arrival_sample": 2100,
                    "trace_S_arrival_sample": 4300,
                    "trace_deconvolved_units": "mps2",
                    "trace_component_order": "ZNE",
                    "split": "test",
                },
            ]
        )
        knet = pd.DataFrame(
            [
                {
                    "trace_name": "K1",
                    "event_name": "ke3",
                    "station_code": "KST",
                    "split": "train",
                    "source_magnitude": 3.5,
                    "source_depth_km": 12.0,
                    "source_distance_km": 60.0,
                    "trace_sampling_rate_hz": 100.0,
                    "trace_npts": 11900,
                    "trace_p_arrival_sample": 500,
                    "trace_s_arrival_sample": 1200,
                    "trace_channel": "ZNE",
                    "preprocess_method": "raw-accel",
                }
            ]
        )

        with tempfile.TemporaryDirectory() as tmp:
            outputs = builder.build_from_frames(instance, knet, Path(tmp))
            manifest = pd.read_csv(outputs["manifest"])
            summary = pd.read_csv(outputs["summary"])

        self.assertEqual(len(manifest), 3)
        self.assertEqual(int((manifest["magnitude"] < 4.0).sum()), 2)
        self.assertEqual(int(manifest["m4plus_eval_candidate"].sum()), 1)
        self.assertEqual(int(manifest["metadata_waveform_candidate"].sum()), 3)
        self.assertIn("ALL", set(summary["dataset"]))

    def test_invalid_catalog_p_is_not_eval_candidate(self) -> None:
        instance = pd.DataFrame(
            [
                {
                    "source_id": "badp",
                    "station_network_code": "AA",
                    "station_code": "S1",
                    "station_channels": "HN",
                    "source_magnitude": 5.0,
                    "source_depth_km": 8.0,
                    "path_ep_distance_km": 40.0,
                    "trace_sampling_rate_hz": 100.0,
                    "trace_npts": 12000,
                    "trace_P_arrival_sample": 13000,
                    "trace_S_arrival_sample": 4000,
                    "trace_deconvolved_units": "mps2",
                    "trace_component_order": "ZNE",
                    "split": "train",
                }
            ]
        )

        manifest = builder.normalize_instance_metadata(instance)
        row = manifest.iloc[0]

        self.assertTrue(row["metadata_waveform_candidate"])
        self.assertFalse(row["has_catalog_p"])
        self.assertFalse(row["catalog_p_eval_candidate"])
        self.assertFalse(row["m4plus_eval_candidate"])

    def test_normalizes_full_knet_converted_manifest_schema(self) -> None:
        knet = pd.DataFrame(
            [
                {
                    "record_id": "MIE0010204112316",
                    "event_id": "0204112316",
                    "station_code": "MIE001",
                    "hdf5_key": "/waveforms/MIE0010204112316",
                    "component_order": "ZNE",
                    "n_samples": 11900,
                    "split": "val",
                    "p_pick_sample": 502,
                    "s_pick_sample": 1313,
                    "magnitude": 4.2,
                    "source_depth_km": 40.0,
                    "source_distance_km": 62.765,
                    "sampling_rate_hz": 100.0,
                }
            ]
        )

        manifest = builder.normalize_knet_metadata(knet, source_manifest="knet_full_manifest.csv")
        row = manifest.iloc[0]

        self.assertEqual(row["trace_name"], "MIE0010204112316")
        self.assertEqual(row["waveform_key"], "waveforms/MIE0010204112316")
        self.assertEqual(row["component_order"], "ZNE")
        self.assertAlmostEqual(float(row["catalog_p_sec"]), 5.02)
        self.assertTrue(row["m4plus_eval_candidate"])

    def test_normalizes_pnw_accelerometer_metadata(self) -> None:
        pnw = pd.DataFrame(
            [
                {
                    "event_id": "uw1",
                    "station_network_code": "UW",
                    "station_code": "STA",
                    "station_channel_code": "EN",
                    "trace_name": "bucket1$1,:3,:15001",
                    "trace_sampling_rate_hz": 100.0,
                    "trace_P_arrival_sample": 5000,
                    "trace_S_arrival_sample": 5600,
                    "preferred_source_magnitude": 3.2,
                    "source_depth_km": 12.0,
                    "trace_component_order": "ENZ",
                }
            ]
        )

        manifest = builder.normalize_pnw_metadata(pnw)
        row = manifest.iloc[0]

        self.assertEqual(row["dataset"], "PNWAccelerometers")
        self.assertEqual(int(row["n_samples"]), 15001)
        self.assertAlmostEqual(float(row["duration_sec"]), 150.01)
        self.assertTrue(row["m3_to_m4_eval_candidate"])


if __name__ == "__main__":
    unittest.main()
