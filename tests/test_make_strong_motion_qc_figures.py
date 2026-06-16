"""Smoke tests for StrongMotion-QC figure generation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts import make_strong_motion_qc_figures as figures


class MakeStrongMotionQcFiguresTests(unittest.TestCase):
    def test_make_figures_writes_nonempty_pngs_and_manifest(self) -> None:
        import matplotlib

        matplotlib.use("Agg")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            selector = root / "selector.csv"
            impact = root / "impact.csv"
            sensitivity = root / "sensitivity.csv"
            response = root / "response.csv"
            outdir = root / "figures"

            selector_rows = []
            for dataset in ["InstanceGM", "K-NET"]:
                for policy, unstable, duration, fallback in [
                    ("feature_onset_fixed", 80.0 if dataset == "InstanceGM" else 8.0, 42.0, 0.0),
                    ("energy_onset_fixed", 70.0 if dataset == "InstanceGM" else 6.0, 42.0, 0.0),
                    ("catalog_p_fixed", 74.0 if dataset == "InstanceGM" else 8.0, 42.0, 0.0),
                    ("adaptive_energy_end", 1.0, 80.0 if dataset == "InstanceGM" else 27.0, 0.0),
                    ("shortest_stable_no_catalog", 0.0, 83.0 if dataset == "InstanceGM" else 27.0, 1.0),
                ]:
                    selector_rows.append(
                        {
                            "dataset": dataset,
                            "priority_group": "ALL",
                            "policy": policy,
                            "unstable_pct": unstable,
                            "median_window_duration_sec": duration,
                            "p25_window_duration_sec": max(1.0, duration - 5.0),
                            "p75_window_duration_sec": duration + 5.0,
                            "full_record_fallback_pct": fallback,
                        }
                    )
            pd.DataFrame(selector_rows).to_csv(selector, index=False)

            impact_rows = []
            for dataset in ["InstanceGM", "K-NET"]:
                for candidate in ["feature_onset_fixed", "energy_onset_fixed", "catalog_p_fixed"]:
                    impact_rows.append(
                        {
                            "dataset": dataset,
                            "priority_group": "ALL",
                            "baseline_candidate": candidate,
                            "baseline_unstable_pct": 10.0,
                            "baseline_unstable_records": 10,
                            "rescued_records": 10,
                            "median_energy_gain": 0.2,
                            "median_duration_change_sec": 5.0,
                        }
                    )
            pd.DataFrame(impact_rows).to_csv(impact, index=False)

            sens_rows = []
            for dataset in ["InstanceGM", "K-NET"]:
                for energy in [0.90, 0.95, 0.98]:
                    sens_rows.append(
                        {
                            "dataset": dataset,
                            "priority_group": "ALL",
                            "pga_threshold": 0.99,
                            "energy_threshold": energy,
                            "full_record_fallback_pct": 1.0 + 10.0 * (energy - 0.90),
                            "median_window_duration_sec": 50.0 + 100.0 * (energy - 0.90),
                        }
                    )
            pd.DataFrame(sens_rows).to_csv(sensitivity, index=False)

            response_rows = []
            for dataset in ["ALL", "InstanceGM", "K-NET"]:
                for policy in [
                    "feature_onset_fixed",
                    "energy_onset_fixed",
                    "catalog_p_fixed",
                    "shortest_stable_no_catalog",
                ]:
                    for period in [0.2, 1.0, 3.0]:
                        response_rows.append(
                            {
                                "dataset": dataset,
                                "priority_group": "ALL",
                                "policy": policy,
                                "period_sec": period,
                                "spectrum_unstable_pct": 20.0 if policy != "shortest_stable_no_catalog" else 1.0,
                            }
                        )
            pd.DataFrame(response_rows).to_csv(response, index=False)

            generated = figures.make_figures(selector, impact, sensitivity, response, outdir, ["png"])

            self.assertEqual(len(generated), 6)
            for paths in generated.values():
                self.assertEqual(len(paths), 1)
                self.assertTrue(paths[0].exists())
                self.assertGreater(paths[0].stat().st_size, 1000)
            self.assertTrue((outdir / "figure_manifest.csv").exists())
            self.assertTrue((outdir / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
