"""Tests for StrongMotion-QC dataset table generation."""

from __future__ import annotations

import unittest

import pandas as pd

from scripts import build_strong_motion_qc_dataset_table as table


class StrongMotionQcDatasetTableTests(unittest.TestCase):
    def test_summarize_dataset_counts_records_events_and_catalog_p(self) -> None:
        features = pd.DataFrame(
            {
                "dataset": ["K-NET", "K-NET", "InstanceGM"],
                "event_id": ["e1", "e1", "e2"],
                "station_code": ["s1", "s2", "s3"],
                "waveform_qc_status": ["ok", "error", "ok"],
                "has_catalog_p": [True, False, "True"],
                "sampling_rate_hz": [100.0, 100.0, 100.0],
                "duration_sec": [119.0, 119.0, 120.0],
                "magnitude": [4.0, 4.2, 3.5],
                "priority_group": ["m4", "m4", "m3"],
            }
        )

        summary = table.summarize_dataset(features)
        knet = summary[summary["dataset"].eq("K-NET")].iloc[0]

        self.assertEqual(int(knet["records"]), 2)
        self.assertEqual(int(knet["events"]), 1)
        self.assertEqual(int(knet["stations"]), 2)
        self.assertEqual(int(knet["loaded_records"]), 1)
        self.assertEqual(int(knet["catalog_p_records"]), 1)

    def test_summarize_strata_groups_by_dataset_and_priority(self) -> None:
        features = pd.DataFrame(
            {
                "dataset": ["K-NET", "K-NET", "K-NET"],
                "priority_group": ["a", "a", "b"],
                "duration_sec": [10.0, 20.0, 30.0],
                "magnitude": [3.0, 4.0, 5.0],
            }
        )

        strata = table.summarize_strata(features)
        group_a = strata[strata["priority_group"].eq("a")].iloc[0]

        self.assertEqual(int(group_a["records"]), 2)
        self.assertAlmostEqual(float(group_a["median_duration_sec"]), 15.0)


if __name__ == "__main__":
    unittest.main()
