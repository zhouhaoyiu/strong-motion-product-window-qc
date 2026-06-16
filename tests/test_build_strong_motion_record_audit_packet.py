"""Tests for StrongMotion-QC record-level audit packet generation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from scripts import build_strong_motion_record_audit_packet as audit


def selected_row(
    record_uid: str,
    dataset: str,
    policy: str,
    *,
    priority_group: str = "m4plus_strong_motion",
    magnitude: float = 5.0,
    selected_candidate: str = "",
    selection_status: str = "stable_candidate",
    duration: float = 42.0,
    unstable: bool = False,
    failure_reason: str = "",
    pga_retention: float = 1.0,
    energy_retention: float = 1.0,
    peak_inside: bool = True,
    peak_time: float = 20.0,
    start_sample: int = 0,
    end_sample: int = 420,
) -> dict[str, object]:
    return {
        "record_uid": record_uid,
        "dataset": dataset,
        "priority_group": priority_group,
        "split": "dev",
        "magnitude": magnitude,
        "policy": policy,
        "selected_candidate": selected_candidate or policy,
        "selection_status": selection_status,
        "window_duration_sec": duration,
        "window_unstable_bool": unstable,
        "failure_reason": failure_reason,
        "pga_retention": pga_retention,
        "energy_retention": energy_retention,
        "peak_inside_window": peak_inside,
        "peak_time_sec": peak_time,
        "candidate_start_sec": start_sample / 10.0,
        "candidate_end_sec": end_sample / 10.0,
        "window_start_sample": start_sample,
        "window_end_sample": end_sample,
    }


def selected_fixture() -> pd.DataFrame:
    rows = []
    rows.extend(
        [
            selected_row(
                "ig1",
                "InstanceGM",
                "feature_onset_fixed",
                priority_group="low_magnitude_background",
                magnitude=2.1,
                unstable=True,
                failure_reason="peak_outside,pga_loss,energy_loss",
                pga_retention=0.1,
                energy_retention=0.05,
                peak_inside=False,
                peak_time=80.0,
                start_sample=0,
                end_sample=420,
            ),
            selected_row("ig1", "InstanceGM", "energy_onset_fixed", priority_group="low_magnitude_background", magnitude=2.1),
            selected_row(
                "ig1",
                "InstanceGM",
                "shortest_stable_no_catalog",
                priority_group="low_magnitude_background",
                magnitude=2.1,
                selected_candidate="energy_onset_fixed",
                duration=42.0,
                pga_retention=1.0,
                energy_retention=0.99,
                peak_time=80.0,
                start_sample=500,
                end_sample=920,
            ),
        ]
    )
    rows.extend(
        [
            selected_row(
                "kn1",
                "K-NET",
                "feature_onset_fixed",
                magnitude=7.0,
                unstable=True,
                failure_reason="peak_outside,pga_loss,energy_loss",
                pga_retention=0.3,
                energy_retention=0.2,
                peak_inside=False,
                peak_time=60.0,
            ),
            selected_row("kn1", "K-NET", "energy_onset_fixed", magnitude=7.0),
            selected_row(
                "kn1",
                "K-NET",
                "shortest_stable_no_catalog",
                magnitude=7.0,
                selected_candidate="feature_onset_to_energy_end",
                duration=70.0,
                pga_retention=1.0,
                energy_retention=0.98,
                peak_time=60.0,
                start_sample=0,
                end_sample=700,
            ),
        ]
    )
    rows.extend(
        [
            selected_row("kn2", "K-NET", "feature_onset_fixed", priority_group="m3_to_m4_small_event", magnitude=3.5),
            selected_row("kn2", "K-NET", "energy_onset_fixed", priority_group="m3_to_m4_small_event", magnitude=3.5),
            selected_row(
                "kn2",
                "K-NET",
                "shortest_stable_no_catalog",
                priority_group="m3_to_m4_small_event",
                magnitude=3.5,
                selected_candidate="feature_onset_to_energy_end",
                duration=8.0,
                pga_retention=1.0,
                energy_retention=0.99,
                peak_time=5.0,
                start_sample=0,
                end_sample=80,
            ),
        ]
    )
    rows.extend(
        [
            selected_row("fb1", "K-NET", "feature_onset_fixed", priority_group="m3_to_m4_small_event", magnitude=3.6),
            selected_row("fb1", "K-NET", "energy_onset_fixed", priority_group="m3_to_m4_small_event", magnitude=3.6),
            selected_row(
                "fb1",
                "K-NET",
                "shortest_stable_no_catalog",
                priority_group="m3_to_m4_small_event",
                magnitude=3.6,
                selected_candidate="full_record",
                selection_status="full_record_fallback",
                duration=120.0,
                pga_retention=1.0,
                energy_retention=1.0,
                peak_time=40.0,
                start_sample=0,
                end_sample=1200,
            ),
        ]
    )
    return pd.DataFrame(rows)


class StrongMotionRecordAuditPacketTests(unittest.TestCase):
    def test_select_representative_cases_covers_expected_categories(self) -> None:
        cases = audit.select_representative_cases(selected_fixture(), cases_per_category=1)
        categories = set(cases["case_category"])

        self.assertIn("instance_fixed_failure_rescued", categories)
        self.assertIn("knet_fixed_failure_rescued", categories)
        self.assertIn("knet_compact_stable_window", categories)
        self.assertIn("full_record_fallback_boundary", categories)

    def test_build_packet_writes_case_tables_and_plots_with_mocked_loader(self) -> None:
        selected = selected_fixture()
        features = pd.DataFrame(
            {
                "record_uid": ["ig1", "kn1", "kn2", "fb1"],
                "dataset": ["InstanceGM", "K-NET", "K-NET", "K-NET"],
                "priority_group": ["low_magnitude_background", "m4plus_strong_motion", "m3_to_m4_small_event", "m3_to_m4_small_event"],
                "sampling_rate_hz": [10.0, 10.0, 10.0, 10.0],
                "units": ["mps2", "mps2", "mps2", "mps2"],
                "waveform_qc_status": ["ok", "ok", "ok", "ok"],
            }
        )
        waveform = np.zeros((3, 1200), dtype=float)
        waveform[0, 800] = 1.0

        original_handles = audit.load_waveform_handles
        original_loader = audit.load_record_waveform
        try:
            audit.load_waveform_handles = lambda _records, _knet_waveforms: (object(), None, None)
            audit.load_record_waveform = lambda _row, _instance_data, _h5, _keys, _hp: waveform
            with tempfile.TemporaryDirectory() as tmp:
                outputs = audit.build_record_audit_packet(
                    features=features,
                    selected_windows=selected,
                    outdir=Path(tmp),
                    cases_per_category=1,
                    formats=["png"],
                )
                cases = pd.read_csv(outputs["cases"])
                manifest = pd.read_csv(outputs["plot_manifest"])
                self.assertTrue(outputs["report"].exists())
                self.assertEqual(int(outputs["load_error_count"]), 0)
                self.assertGreaterEqual(len(cases), 4)
                self.assertEqual(len(manifest), int(outputs["plot_count"]))
                self.assertTrue((Path(tmp) / manifest.iloc[0]["path"]).exists())
        finally:
            audit.load_waveform_handles = original_handles
            audit.load_record_waveform = original_loader


if __name__ == "__main__":
    unittest.main()
