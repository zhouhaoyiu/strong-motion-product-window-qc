"""Tests for strong-motion product-impact summaries."""

from __future__ import annotations

import unittest

import pandas as pd

from scripts import analyze_strong_motion_window_product_impact as impact


class StrongMotionWindowProductImpactTests(unittest.TestCase):
    def test_compare_baseline_to_selector_counts_rescued_records(self) -> None:
        stability = pd.DataFrame(
            [
                {
                    "record_uid": "a",
                    "dataset": "K-NET",
                    "priority_group": "m4",
                    "candidate": "energy_onset_fixed",
                    "window_unstable": True,
                    "failure_reason": "energy_loss",
                    "energy_retention": 0.5,
                    "pga_retention": 1.0,
                    "window_duration_sec": 42.0,
                },
                {
                    "record_uid": "b",
                    "dataset": "K-NET",
                    "priority_group": "m4",
                    "candidate": "energy_onset_fixed",
                    "window_unstable": False,
                    "failure_reason": "",
                    "energy_retention": 0.98,
                    "pga_retention": 1.0,
                    "window_duration_sec": 42.0,
                },
            ]
        )
        selected = pd.DataFrame(
            [
                {
                    "record_uid": "a",
                    "dataset": "K-NET",
                    "priority_group": "m4",
                    "policy": "shortest_stable_no_catalog",
                    "selected_candidate": "feature_onset_to_energy_end",
                    "selection_status": "stable_candidate",
                    "window_unstable": False,
                    "energy_retention": 0.97,
                    "pga_retention": 1.0,
                    "window_duration_sec": 50.0,
                },
                {
                    "record_uid": "b",
                    "dataset": "K-NET",
                    "priority_group": "m4",
                    "policy": "shortest_stable_no_catalog",
                    "selected_candidate": "energy_onset_fixed",
                    "selection_status": "stable_candidate",
                    "window_unstable": False,
                    "energy_retention": 0.98,
                    "pga_retention": 1.0,
                    "window_duration_sec": 42.0,
                },
            ]
        )

        out = impact.compare_baseline_to_selector(stability, selected, policy="shortest_stable_no_catalog")
        row = out[
            out["dataset"].eq("K-NET")
            & out["priority_group"].eq("m4")
            & out["baseline_candidate"].eq("energy_onset_fixed")
        ].iloc[0]

        self.assertEqual(int(row["records"]), 2)
        self.assertEqual(int(row["baseline_unstable_records"]), 1)
        self.assertEqual(int(row["rescued_records"]), 1)
        self.assertEqual(int(row["baseline_energy_loss_records"]), 1)
        self.assertAlmostEqual(float(row["median_energy_gain"]), 0.235)


if __name__ == "__main__":
    unittest.main()
