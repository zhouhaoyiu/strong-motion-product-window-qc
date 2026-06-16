"""Tests for selector threshold-sensitivity evaluation."""

from __future__ import annotations

import unittest

import pandas as pd

from scripts import evaluate_strong_motion_selector_sensitivity as sensitivity


def row(record_uid: str, candidate: str, energy: float, duration: float, peak: bool = True) -> dict[str, object]:
    return {
        "record_uid": record_uid,
        "dataset": "K-NET",
        "priority_group": "m4",
        "candidate": candidate,
        "pga_retention": 1.0,
        "energy_retention": energy,
        "peak_inside_window": peak,
        "window_duration_sec": duration,
    }


class SelectorSensitivityTests(unittest.TestCase):
    def test_choose_record_falls_back_when_threshold_is_strict(self) -> None:
        stability = pd.DataFrame(
            [
                row("a", "feature_onset_fixed", 0.94, 42.0),
                row("a", "energy_onset_fixed", 0.93, 42.0),
                row("a", "feature_onset_to_energy_end", 0.95, 50.0),
                row("a", "full_record", 1.0, 120.0),
            ]
        )
        work = sensitivity.prepare(stability)

        chosen = sensitivity.choose_record(work, pga_threshold=0.99, energy_threshold=0.98)

        self.assertEqual(chosen["candidate"], "full_record")
        self.assertEqual(chosen["selection_status"], "full_record_fallback")

    def test_summary_reports_fallback_rate(self) -> None:
        stability = pd.DataFrame(
            [
                row("a", "feature_onset_fixed", 0.99, 20.0),
                row("a", "energy_onset_fixed", 0.99, 30.0),
                row("a", "feature_onset_to_energy_end", 0.99, 40.0),
                row("a", "full_record", 1.0, 120.0),
                row("b", "feature_onset_fixed", 0.90, 20.0),
                row("b", "energy_onset_fixed", 0.90, 30.0),
                row("b", "feature_onset_to_energy_end", 0.90, 40.0),
                row("b", "full_record", 1.0, 120.0),
            ]
        )

        _, summary = sensitivity.evaluate_sensitivity(stability, [0.99], [0.95])
        group = summary[
            summary["dataset"].eq("K-NET")
            & summary["priority_group"].eq("m4")
            & summary["pga_threshold"].eq(0.99)
            & summary["energy_threshold"].eq(0.95)
        ].iloc[0]

        self.assertEqual(int(group["records"]), 2)
        self.assertEqual(int(group["full_record_fallback_records"]), 1)
        self.assertAlmostEqual(float(group["full_record_fallback_pct"]), 50.0)


if __name__ == "__main__":
    unittest.main()
