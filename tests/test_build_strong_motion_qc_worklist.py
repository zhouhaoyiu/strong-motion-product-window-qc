"""Tests for StrongMotion-QC stratified waveform worklists."""

from __future__ import annotations

import unittest

import pandas as pd

from scripts import build_strong_motion_qc_worklist as builder


def make_row(uid: str, dataset: str, magnitude: float, magnitude_bin: str, split: str) -> dict[str, object]:
    return {
        "record_uid": uid,
        "dataset": dataset,
        "source_row_index": uid.split(":")[-1],
        "split": split,
        "magnitude_bin": magnitude_bin,
        "magnitude": magnitude,
        "event_id": f"event-{uid}",
        "station_network": "AA",
        "station_code": "STA",
        "trace_name": uid,
        "waveform_key": uid,
        "waveform_access": "test",
        "component_order": "ZNE",
        "channel_type": "HN",
        "units": "mps2",
        "sampling_rate_hz": 100.0,
        "n_samples": 12000,
        "duration_sec": 120.0,
        "has_catalog_p": True,
        "catalog_p_sec": 12.0,
        "catalog_p_sample": 1200,
        "catalog_fields_for_evaluation_only": "catalog_p_sec,catalog_s_sec,catalog_p_sample,catalog_s_sample",
        "metadata_waveform_candidate": True,
        "m4plus_eval_candidate": magnitude >= 4.0,
        "m3_to_m4_eval_candidate": 3.0 <= magnitude < 4.0,
    }


class BuildStrongMotionQCWorklistTests(unittest.TestCase):
    def test_worklist_keeps_all_priority_groups(self) -> None:
        manifest = pd.DataFrame(
            [
                make_row("InstanceGM:0", "InstanceGM", 2.4, "<3", "train"),
                make_row("InstanceGM:1", "InstanceGM", 3.4, "3-4", "train"),
                make_row("InstanceGM:2", "InstanceGM", 4.4, "4-4.5", "train"),
                make_row("K-NET:0", "K-NET", 3.5, "3-4", "test"),
                make_row("K-NET:1", "K-NET", 4.8, "4.5-5", "test"),
            ]
        )

        worklist = builder.build_worklist(manifest, per_stratum=2, seed=7)

        self.assertEqual(len(worklist), 5)
        self.assertIn("low_magnitude_background", set(worklist["priority_group"]))
        self.assertIn("m3_to_m4_small_event", set(worklist["priority_group"]))
        self.assertIn("m4plus_strong_motion", set(worklist["priority_group"]))

    def test_worklist_can_include_all_records_for_named_dataset(self) -> None:
        manifest = pd.DataFrame(
            [
                make_row(f"InstanceGM:{idx}", "InstanceGM", 4.4, "4-4.5", "train")
                for idx in range(4)
            ]
            + [
                make_row(f"K-NET:{idx}", "K-NET", 4.4, "4-4.5", "train")
                for idx in range(4)
            ]
        )

        worklist = builder.build_worklist(
            manifest,
            per_stratum=2,
            seed=7,
            include_all_datasets=["K-NET"],
        )

        self.assertEqual(int(worklist["dataset"].eq("InstanceGM").sum()), 2)
        self.assertEqual(int(worklist["dataset"].eq("K-NET").sum()), 4)


if __name__ == "__main__":
    unittest.main()
