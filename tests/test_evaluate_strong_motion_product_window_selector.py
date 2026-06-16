"""Tests for product-stable strong-motion window selector policies."""

from __future__ import annotations

import unittest

import pandas as pd

from scripts import evaluate_strong_motion_product_window_selector as selector


def row(record_uid: str, candidate: str, unstable: bool, duration: float, energy: float = 0.98) -> dict[str, object]:
    return {
        "record_uid": record_uid,
        "dataset": "K-NET",
        "priority_group": "m4_plus_strong_motion",
        "split": "dev",
        "candidate": candidate,
        "window_unstable": unstable,
        "window_duration_sec": duration,
        "energy_retention": energy,
        "pga_retention": 1.0,
    }


class ProductWindowSelectorTests(unittest.TestCase):
    def test_fixed_policy_selects_requested_candidate(self) -> None:
        stability = pd.DataFrame(
            [
                row("a", "feature_onset_fixed", False, 42.0),
                row("a", "energy_onset_fixed", False, 40.0),
                row("a", "feature_onset_to_energy_end", False, 30.0),
                row("a", "full_record", False, 120.0),
            ]
        )

        selected = selector.evaluate_policies(stability, policies=["energy_onset_fixed"])

        self.assertEqual(selected.loc[0, "selected_candidate"], "energy_onset_fixed")
        self.assertEqual(float(selected.loc[0, "window_duration_sec"]), 40.0)

    def test_shortest_stable_policy_chooses_shorter_passing_candidate(self) -> None:
        stability = pd.DataFrame(
            [
                row("a", "feature_onset_fixed", True, 42.0, energy=0.5),
                row("a", "energy_onset_fixed", False, 42.0),
                row("a", "catalog_p_fixed", False, 35.0),
                row("a", "feature_onset_to_energy_end", False, 25.0),
                row("a", "full_record", False, 120.0),
            ]
        )

        selected = selector.evaluate_policies(stability, policies=["shortest_stable_all"])

        self.assertEqual(selected.loc[0, "selected_candidate"], "feature_onset_to_energy_end")
        self.assertEqual(selected.loc[0, "selection_status"], "stable_candidate")
        self.assertEqual(float(selected.loc[0, "window_duration_sec"]), 25.0)

    def test_shortest_stable_policy_falls_back_to_full_record(self) -> None:
        stability = pd.DataFrame(
            [
                row("a", "feature_onset_fixed", True, 42.0, energy=0.5),
                row("a", "energy_onset_fixed", True, 42.0, energy=0.5),
                row("a", "feature_onset_to_energy_end", True, 90.0, energy=0.5),
                row("a", "full_record", False, 120.0),
            ]
        )

        selected = selector.evaluate_policies(stability, policies=["shortest_stable_no_catalog"])

        self.assertEqual(selected.loc[0, "selected_candidate"], "full_record")
        self.assertEqual(selected.loc[0, "selection_status"], "full_record_fallback")
        self.assertFalse(bool(selected.loc[0, "window_unstable"]))

    def test_summary_reports_instability_and_fallback(self) -> None:
        selected = pd.DataFrame(
            [
                {
                    "dataset": "K-NET",
                    "priority_group": "m4_plus_strong_motion",
                    "policy": "shortest_stable_all",
                    "selection_status": "stable_candidate",
                    "window_unstable": False,
                    "window_duration_sec": 20.0,
                    "energy_retention": 0.97,
                    "pga_retention": 1.0,
                },
                {
                    "dataset": "K-NET",
                    "priority_group": "m4_plus_strong_motion",
                    "policy": "shortest_stable_all",
                    "selection_status": "full_record_fallback",
                    "window_unstable": False,
                    "window_duration_sec": 120.0,
                    "energy_retention": 1.0,
                    "pga_retention": 1.0,
                },
            ]
        )

        summary = selector.summarize(selected)
        group = summary[
            summary["dataset"].eq("K-NET")
            & summary["priority_group"].eq("m4_plus_strong_motion")
            & summary["policy"].eq("shortest_stable_all")
        ].iloc[0]

        self.assertEqual(int(group["records"]), 2)
        self.assertEqual(float(group["unstable_pct"]), 0.0)
        self.assertEqual(int(group["full_record_fallback_records"]), 1)


if __name__ == "__main__":
    unittest.main()
