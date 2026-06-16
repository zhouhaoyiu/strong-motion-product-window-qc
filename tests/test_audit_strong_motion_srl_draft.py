"""Tests for the StrongMotion-QC SRL draft audit."""

from __future__ import annotations

import unittest

import pandas as pd

from scripts import audit_strong_motion_srl_draft as audit


def dataset_summary() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "dataset": "InstanceGM",
                "records": 2,
                "events": 1,
                "stations": 1,
                "median_duration_sec": 120.0,
            },
            {
                "dataset": "K-NET",
                "records": 1,
                "events": 1,
                "stations": 1,
                "median_duration_sec": 119.0,
            },
        ]
    )


def selector_summary() -> pd.DataFrame:
    rows = []
    for dataset in ["InstanceGM", "K-NET"]:
        for priority_group in ["ALL", "m3_to_m4_small_event"]:
            for policy in [
                "feature_onset_fixed",
                "energy_onset_fixed",
                "catalog_p_fixed",
                "adaptive_energy_end",
                "shortest_stable_no_catalog",
            ]:
                rows.append(
                    {
                        "dataset": dataset,
                        "priority_group": priority_group,
                        "policy": policy,
                        "unstable_pct": 10.0,
                        "median_window_duration_sec": 42.0,
                        "full_record_fallback_pct": 1.0,
                        "full_record_fallback_records": 1,
                    }
                )
    rows.append(
        {
            "dataset": "ALL",
            "priority_group": "ALL",
            "policy": "shortest_stable_no_catalog",
            "unstable_pct": 0.0,
            "median_window_duration_sec": 42.0,
            "full_record_fallback_pct": 1.0,
            "full_record_fallback_records": 1,
        }
    )
    return pd.DataFrame(rows)


def selector_usage() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "dataset": dataset,
                "policy": "shortest_stable_no_catalog",
                "selected_candidate": candidate,
                "pct": 50.0,
            }
            for dataset in ["InstanceGM", "K-NET"]
            for candidate in ["feature_onset_to_energy_end", "energy_onset_fixed"]
        ]
    )


def product_impact() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "dataset": dataset,
                "priority_group": "ALL",
                "baseline_candidate": baseline,
                "rescued_records": 1,
                "median_energy_gain": 0.123,
                "median_duration_change_sec": -2.0,
            }
            for dataset in ["InstanceGM", "K-NET"]
            for baseline in ["feature_onset_fixed", "energy_onset_fixed"]
        ]
    )


def sensitivity_summary() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "dataset": dataset,
                "priority_group": "ALL",
                "pga_threshold": 0.99,
                "energy_threshold": energy,
                "full_record_fallback_pct": 1.0 if energy == 0.95 else 20.0,
            }
            for dataset in ["ALL", "InstanceGM", "K-NET"]
            for energy in [0.95, 0.98]
        ]
    )


def key_metrics() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "dataset": dataset,
                "method": method,
                "unstable_pct": 25.0,
            }
            for dataset in ["InstanceGM", "K-NET"]
            for method in ["local4096_model", "fullrecord_model"]
        ]
    )


def response_spectrum_summary() -> pd.DataFrame:
    rows = []
    for dataset in ["ALL", "InstanceGM", "K-NET"]:
        for policy in ["feature_onset_fixed", "shortest_stable_no_catalog"]:
            for period in [0.2, 1.0, 3.0]:
                rows.append(
                    {
                        "dataset": dataset,
                        "priority_group": "ALL",
                        "policy": policy,
                        "period_sec": period,
                        "spectrum_unstable_records": 1,
                        "spectrum_unstable_pct": 1.0,
                    }
                )
    return pd.DataFrame(rows)


class StrongMotionSrlDraftAuditTests(unittest.TestCase):
    def test_pattern_audit_flags_defensive_and_scope_phrases(self) -> None:
        text = "This is not a picker but a product selector. However, it is not real-time."

        pattern_audit = pd.concat(
            [
                audit.build_pattern_audit(text, audit.STYLE_PATTERNS, "style"),
                audit.build_pattern_audit(text, audit.SCOPE_PATTERNS, "scope"),
            ],
            ignore_index=True,
        )

        failed = pattern_audit[~pattern_audit["passed"]]
        self.assertIn("not-x-but-y", set(failed["pattern"]))
        self.assertIn("real-time claim", set(failed["pattern"]))

    def test_number_audit_reports_missing_and_found_strings(self) -> None:
        text = "3 records 2 records 1 records 120.00 s 119.00 s 1.00%"

        number_audit = audit.build_number_audit(
            text,
            dataset_summary(),
            selector_summary(),
            selector_usage(),
            product_impact(),
            sensitivity_summary(),
            response_spectrum_summary(),
        )

        self.assertTrue(number_audit[number_audit["metric_id"].eq("all_records")]["found"].iloc[0])
        self.assertTrue(number_audit[number_audit["metric_id"].eq("InstanceGM_median_duration")]["found"].iloc[0])
        self.assertFalse(number_audit[number_audit["metric_id"].eq("InstanceGM_feature_energy_gain")]["found"].iloc[0])

    def test_display_audit_requires_each_figure_and_table(self) -> None:
        text = " ".join([f"Figure {idx}" for idx in range(1, 7)] + [f"Table {idx}" for idx in range(1, 4)])

        display = audit.build_display_audit(text)

        self.assertTrue(display["passed"].all())
        self.assertEqual(len(display), 9)


if __name__ == "__main__":
    unittest.main()
