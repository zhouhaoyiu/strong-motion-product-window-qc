"""Tests for the StrongMotion-QC SRL readiness report."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts import build_strong_motion_srl_readiness_report as report


class StrongMotionSrlReadinessReportTests(unittest.TestCase):
    def test_compute_score_counts_warn_half_weight(self) -> None:
        checks = pd.DataFrame(
            [
                {"status": "PASS", "readiness_weight": 10},
                {"status": "WARN", "readiness_weight": 5},
                {"status": "FAIL", "readiness_weight": 20},
            ]
        )

        self.assertEqual(report.compute_score(checks), 12)

    def test_figure_status_checks_png_and_pdf_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "fig1.png").write_text("png")
            (root / "fig1.pdf").write_text("pdf")
            manifest = root / "manifest.csv"
            pd.DataFrame(
                [
                    {
                        "figure_id": "Fig. 1",
                        "png": str(root / "fig1.png"),
                        "pdf": str(root / "fig1.pdf"),
                    }
                ]
            ).to_csv(manifest, index=False)

            status = report.figure_status(manifest)

        self.assertTrue(status["all_present"])
        self.assertEqual(status["figure_files_present"], 2)

    def test_acceptance_band_is_conservative(self) -> None:
        self.assertIn("82", report.acceptance_band(95))
        self.assertIn("70%", report.acceptance_band(80))
        self.assertIn("blocking", report.acceptance_band(50))

    def test_pgv_and_record_audit_status_helpers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pgv = root / "pgv.csv"
            pd.DataFrame(
                [
                    {
                        "dataset": "ALL",
                        "priority_group": "ALL",
                        "policy": "feature_onset_fixed",
                        "records": 10,
                        "pgv_unstable_pct": 20.0,
                    },
                    {
                        "dataset": "ALL",
                        "priority_group": "ALL",
                        "policy": "shortest_stable_no_catalog",
                        "records": 10,
                        "pgv_unstable_pct": 1.0,
                    },
                ]
            ).to_csv(pgv, index=False)
            audit_dir = root / "record_audit"
            audit_dir.mkdir()
            pd.DataFrame([{"case_id": "case_01"}]).to_csv(audit_dir / "cases.csv", index=False)
            pd.DataFrame([{"case_id": "case_01", "path": "figures/case_01.png"}]).to_csv(
                audit_dir / "plot_manifest.csv", index=False
            )
            (audit_dir / "README.md").write_text("# Record audit\n")

            pgv_status = report.pgv_status(pgv)
            audit_status = report.record_audit_status(audit_dir)

        self.assertEqual(pgv_status["records"], 10)
        self.assertEqual(pgv_status["selected_failure_pct"], 1.0)
        self.assertTrue(audit_status["exists"])
        self.assertEqual(audit_status["cases"], 1)
        self.assertEqual(audit_status["load_errors"], 0)


if __name__ == "__main__":
    unittest.main()
