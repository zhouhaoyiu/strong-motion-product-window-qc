"""Tests for product-production routing case generation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts import build_strong_motion_product_production_case as production_case


class ProductProductionCaseTests(unittest.TestCase):
    def test_build_case_routes_full_record_before_psa_review(self) -> None:
        selected = pd.DataFrame(
            {
                "record_uid": ["a", "b", "c"],
                "dataset": ["D", "D", "D"],
                "policy": ["shortest_stable_no_catalog"] * 3,
                "selection_status": ["stable_candidate", "full_record_fallback", "stable_candidate"],
                "window_duration_sec": [10.0, 100.0, 20.0],
            }
        )
        response = pd.DataFrame(
            {
                "record_uid": ["a", "b", "c"],
                "policy": ["shortest_stable_no_catalog"] * 3,
                "period_sec": [3.0, 3.0, 3.0],
                "psa_retention": [1.0, 0.4, 0.8],
                "spectrum_unstable": [False, True, True],
            }
        )

        case, summary = production_case.build_case(selected, response, "shortest_stable_no_catalog", 3.0)
        routes = dict(zip(case["record_uid"], case["production_route"]))

        self.assertEqual(routes["a"], "stable_window_accept")
        self.assertEqual(routes["b"], "full_record_required")
        self.assertEqual(routes["c"], "long_period_psa_review")
        self.assertEqual(int(summary[summary["production_route"].eq("ALL")]["records"].iloc[0]), 3)

    def test_build_product_production_case_writes_files(self) -> None:
        selected = pd.DataFrame(
            {
                "record_uid": ["a"],
                "dataset": ["D"],
                "policy": ["shortest_stable_no_catalog"],
                "selection_status": ["stable_candidate"],
                "window_duration_sec": [10.0],
            }
        )
        response = pd.DataFrame(
            {
                "record_uid": ["a"],
                "policy": ["shortest_stable_no_catalog"],
                "period_sec": [3.0],
                "psa_retention": [1.0],
                "spectrum_unstable": [False],
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            selected_path = Path(tmp) / "selected.csv"
            response_path = Path(tmp) / "response.csv"
            selected.to_csv(selected_path, index=False)
            response.to_csv(response_path, index=False)
            outputs = production_case.build_product_production_case(
                [str(selected_path)],
                [str(response_path)],
                Path(tmp) / "out",
            )

            self.assertTrue(outputs["routes"].exists())
            self.assertTrue(outputs["summary"].exists())
            self.assertTrue(outputs["review_queue"].exists())
            self.assertTrue(outputs["report"].exists())


if __name__ == "__main__":
    unittest.main()
