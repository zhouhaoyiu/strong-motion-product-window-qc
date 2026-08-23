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
            candidates = ["feature_onset_fixed_20s", "feature_onset_fixed", "feature_onset_fixed_60s", "feature_onset_fixed_90s"]
            main_stability = pd.DataFrame(
                [
                    {"dataset": dataset, "candidate": candidate, "records": 100, "unstable_records": 80 - 15 * idx}
                    for dataset in ["InstanceGM", "K-NET"]
                    for idx, candidate in enumerate(candidates)
                ]
            )
            pnw_stability = pd.DataFrame(
                [{"dataset": "PNWAccelerometers", "candidate": candidate, "records": 100, "unstable_records": 90 - 5 * idx} for idx, candidate in enumerate(candidates)]
            )
            safeguard = pd.DataFrame(
                [
                    {
                        "dataset": dataset,
                        "priority_group": "ALL",
                        "primary_pct": 80.0,
                        "arias_escalation_pct": 12.0,
                        "full_record_fallback_pct": 8.0,
                        "median_window_duration_sec": 50.0,
                        "p75_window_duration_sec": 80.0,
                    }
                    for dataset in ["InstanceGM", "K-NET"]
                ]
            )
            pnw_safeguard = pd.DataFrame(
                [{"dataset": "PNWAccelerometers", "priority_group": "ALL", "primary_pct": 60.0, "arias_escalation_pct": 28.0, "full_record_fallback_pct": 12.0, "median_window_duration_sec": 145.0, "p75_window_duration_sec": 150.0}]
            )
            response_rows = []
            final_rows = []
            for dataset in ["ALL", "InstanceGM", "K-NET"]:
                for policy, failure in [("feature_onset_fixed", 35.0), ("shortest_stable_no_catalog", 18.0)]:
                    for period in [0.2, 1.0, 3.0]:
                        response_rows.append({"dataset": dataset, "priority_group": "ALL", "policy": policy, "period_sec": period, "spectrum_unstable_pct": failure * period / 3.0})
                for period in [0.2, 1.0, 3.0]:
                    final_rows.append({"dataset": dataset, "priority_group": "ALL", "policy": "product_spectral_safeguard", "period_sec": period, "spectrum_unstable_pct": 0.0})
            filter_response = pd.DataFrame(
                [{"dataset": dataset, "priority_group": "ALL", "policy": "shortest_stable_no_catalog", "period_sec": 3.0, "spectrum_unstable_pct": 25.0} for dataset in ["InstanceGM", "K-NET"]]
            )
            filter_safeguard = pd.DataFrame(
                [{"dataset": dataset, "priority_group": "ALL", "full_record_fallback_pct": 12.0} for dataset in ["InstanceGM", "K-NET"]]
            )
            pnw_snr = pd.DataFrame(
                {
                    "snr_bin": ["<3 dB", "3-10 dB", ">=10 dB"],
                    "records": [100, 200, 300],
                    "feature_fixed_unstable_pct": [99.0, 95.0, 70.0],
                    "selected_3s_psa_failure_pct": [15.0, 25.0, 45.0],
                    "spectral_full_record_fallback_pct": [1.0, 2.0, 20.0],
                }
            )

            paths = {}
            for name, frame in {
                "main_stability": main_stability,
                "pnw_stability": pnw_stability,
                "safeguard": safeguard,
                "pnw_safeguard": pnw_safeguard,
                "response": pd.DataFrame(response_rows),
                "final": pd.DataFrame(final_rows),
                "filter_response_005": filter_response,
                "filter_response_010": filter_response,
                "filter_safeguard_005": filter_safeguard,
                "filter_safeguard_010": filter_safeguard,
                "pnw_snr": pnw_snr,
            }.items():
                paths[name] = root / f"{name}.csv"
                frame.to_csv(paths[name], index=False)

            outdir = root / "figures"
            generated = figures.make_figures(
                paths["main_stability"],
                paths["pnw_stability"],
                paths["safeguard"],
                paths["pnw_safeguard"],
                paths["response"],
                paths["final"],
                paths["filter_response_005"],
                paths["filter_response_010"],
                paths["filter_safeguard_005"],
                paths["filter_safeguard_010"],
                paths["pnw_snr"],
                outdir,
                ["png"],
            )

            self.assertEqual(len(generated), 6)
            for outputs in generated.values():
                self.assertEqual(len(outputs), 1)
                self.assertGreater(outputs[0].stat().st_size, 1000)
            self.assertTrue((outdir / "figure_manifest.csv").exists())


if __name__ == "__main__":
    unittest.main()
