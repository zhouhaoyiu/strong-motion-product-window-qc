#!/usr/bin/env python3
"""Validate the revised acceleration-only StrongMotion-QC evidence chain."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


DEFAULTS = {
    "features": "outputs/strong_motion_qc_waveform_features_accel45652_hp0p1/waveform_features.csv",
    "selected_windows": "outputs/strong_motion_qc_product_window_selector_accel44674_hp0p1/selected_windows.csv",
    "response_spectrum": "outputs/strong_motion_qc_response_spectrum_accel44674_hp0p1/response_spectrum_retention.csv",
    "safeguarded_windows": "outputs/strong_motion_qc_spectral_safeguard_accel44674_hp0p1/selected_windows.csv",
    "safeguarded_spectrum": "outputs/strong_motion_qc_spectral_safeguard_accel44674_hp0p1/response_spectrum_retention.csv",
    "pnw_features": "outputs/strong_motion_qc_waveform_features_pnw_accel6107_hp0p1/waveform_features.csv",
    "pnw_selected_windows": "outputs/strong_motion_qc_product_window_selector_pnw_accel6107_hp0p1/selected_windows.csv",
    "pnw_response_spectrum": "outputs/strong_motion_qc_response_spectrum_pnw_accel6107_hp0p1/response_spectrum_retention.csv",
    "pnw_safeguarded_windows": "outputs/strong_motion_qc_spectral_safeguard_pnw_accel6107_hp0p1/selected_windows.csv",
    "pnw_safeguarded_spectrum": "outputs/strong_motion_qc_spectral_safeguard_pnw_accel6107_hp0p1/response_spectrum_retention.csv",
    "filter_005_response": "outputs/strong_motion_qc_response_spectrum_filter_sensitivity_e2e_hp0p05_sample1521/response_spectrum_retention.csv",
    "filter_010_response": "outputs/strong_motion_qc_response_spectrum_filter_sensitivity_e2e_hp0p1_sample1521/response_spectrum_retention.csv",
    "pnw_snr": "outputs/strong_motion_qc_pnw_snr_accel6107_hp0p1/summary.csv",
    "english_draft": "manuscripts/strong_motion_qc_srl/strong_motion_qc_srl_draft.md",
    "chinese_draft": "docs/strong_motion_qc_srl_manuscript_zh.md",
    "chinese_latex": "manuscripts/strong_motion_qc_srl_zh/main.tex",
    "outdir": "outputs/strong_motion_qc_revised_evidence_audit",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    for flag, default in DEFAULTS.items():
        parser.add_argument(f"--{flag.replace('_', '-')}", default=default)
    return parser.parse_args()


def check(rows: list[dict[str, object]], check_id: str, passed: bool, observed: object, expected: object) -> None:
    rows.append(
        {
            "check_id": check_id,
            "status": "PASS" if passed else "FAIL",
            "observed": observed,
            "expected": expected,
        }
    )


def validate_safeguard(
    rows: list[dict[str, object]],
    prefix: str,
    expected_records: int,
    selected: pd.DataFrame,
    spectra: pd.DataFrame,
) -> None:
    record_count = selected["record_uid"].astype(str).nunique()
    check(rows, f"{prefix}_selected_records", record_count == expected_records, record_count, expected_records)
    check(rows, f"{prefix}_selected_unique", not selected["record_uid"].astype(str).duplicated().any(), len(selected), expected_records)
    stages = selected["spectral_stage"].astype(str)
    allowed = {"primary", "arias_escalation", "full_record_fallback"}
    check(rows, f"{prefix}_stage_values", set(stages).issubset(allowed), sorted(set(stages)), sorted(allowed))
    spectrum_grain = spectra[["record_uid", "period_sec"]].copy()
    check(
        rows,
        f"{prefix}_spectrum_grain",
        len(spectrum_grain) == expected_records * 3 and not spectrum_grain.duplicated().any(),
        len(spectrum_grain),
        expected_records * 3,
    )
    periods = set(pd.to_numeric(spectra["period_sec"], errors="coerce").dropna().unique())
    check(rows, f"{prefix}_periods", periods == {0.2, 1.0, 3.0}, sorted(periods), [0.2, 1.0, 3.0])
    retention = pd.to_numeric(spectra["psa_retention"], errors="coerce")
    below = int((retention < 0.95).sum())
    check(rows, f"{prefix}_psa_threshold", below == 0 and retention.notna().all(), below, 0)
    definitions = sorted(set(spectra["psa_retention_definition"].dropna().astype(str)))
    check(
        rows,
        f"{prefix}_psa_definition",
        definitions == ["minimum_component_psa_retention"],
        definitions,
        ["minimum_component_psa_retention"],
    )
    ringdown = sorted(set(pd.to_numeric(spectra["ringdown_cycles"], errors="coerce").dropna()))
    check(rows, f"{prefix}_ringdown_cycles", ringdown == [5.0], ringdown, [5.0])


def run_audit(args: argparse.Namespace) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    features = pd.read_csv(args.features, low_memory=False)
    loaded = features[features["waveform_qc_status"].eq("ok")].copy()
    check(rows, "main_candidate_records", len(features) == 45652, len(features), 45652)
    check(rows, "main_loaded_records", len(loaded) == 44674, len(loaded), 44674)
    check(rows, "main_load_errors", len(features) - len(loaded) == 978, len(features) - len(loaded), 978)
    instance_units = set(loaded.loc[loaded["dataset"].eq("InstanceGM"), "units"].astype(str).str.lower())
    check(rows, "instance_acceleration_units", instance_units.issubset({"mps2", "m/s2", "cm/s2", "gal"}), sorted(instance_units), "acceleration units only")
    preprocessing = sorted(set(loaded["waveform_preprocess"].dropna().astype(str)))
    check(
        rows,
        "main_uniform_preprocessing",
        preprocessing == ["linear_detrend_highpass_0.1hz"],
        preprocessing,
        ["linear_detrend_highpass_0.1hz"],
    )

    selected = pd.read_csv(args.selected_windows, low_memory=False)
    primary = selected[selected["policy"].eq("shortest_stable_no_catalog")]
    check(rows, "main_primary_selector_records", primary["record_uid"].nunique() == len(loaded), primary["record_uid"].nunique(), len(loaded))
    peak_definitions = sorted(set(primary["peak_retention_definition"].dropna().astype(str)))
    check(
        rows,
        "main_peak_definition",
        peak_definitions == ["minimum_component_peak_acceleration_retention"],
        peak_definitions,
        ["minimum_component_peak_acceleration_retention"],
    )
    response = pd.read_csv(args.response_spectrum, low_memory=False)
    expected_response = len(loaded) * 3 * 3
    response_grain = response[["record_uid", "policy", "period_sec"]]
    check(rows, "main_response_grain", len(response) == expected_response and not response_grain.duplicated().any(), len(response), expected_response)
    response_policies = sorted(set(response["policy"].astype(str)))
    expected_policies = ["arias_1_99_padded", "feature_onset_fixed", "shortest_stable_no_catalog"]
    check(rows, "main_response_policies", response_policies == expected_policies, response_policies, expected_policies)

    validate_safeguard(
        rows,
        "main",
        len(loaded),
        pd.read_csv(args.safeguarded_windows, low_memory=False),
        pd.read_csv(args.safeguarded_spectrum, low_memory=False),
    )

    pnw_features = pd.read_csv(args.pnw_features, low_memory=False)
    pnw_loaded = pnw_features[pnw_features["waveform_qc_status"].eq("ok")]
    check(rows, "pnw_loaded_records", len(pnw_loaded) == 6107, len(pnw_loaded), 6107)
    pnw_selected = pd.read_csv(args.pnw_selected_windows, low_memory=False)
    pnw_primary = pnw_selected[pnw_selected["policy"].eq("shortest_stable_no_catalog")]
    check(rows, "pnw_primary_selector_records", pnw_primary["record_uid"].nunique() == 6107, pnw_primary["record_uid"].nunique(), 6107)
    pnw_peak_definitions = sorted(set(pnw_primary["peak_retention_definition"].dropna().astype(str)))
    check(
        rows,
        "pnw_peak_definition",
        pnw_peak_definitions == ["minimum_component_peak_acceleration_retention"],
        pnw_peak_definitions,
        ["minimum_component_peak_acceleration_retention"],
    )
    pnw_response = pd.read_csv(args.pnw_response_spectrum, low_memory=False)
    pnw_response_grain = pnw_response[["record_uid", "policy", "period_sec"]]
    expected_pnw_response = 6107 * 3 * 3
    check(
        rows,
        "pnw_response_grain",
        len(pnw_response) == expected_pnw_response and not pnw_response_grain.duplicated().any(),
        len(pnw_response),
        expected_pnw_response,
    )
    validate_safeguard(
        rows,
        "pnw",
        6107,
        pd.read_csv(args.pnw_safeguarded_windows, low_memory=False),
        pd.read_csv(args.pnw_safeguarded_spectrum, low_memory=False),
    )

    filter_005 = pd.read_csv(args.filter_005_response, low_memory=False)
    filter_010 = pd.read_csv(args.filter_010_response, low_memory=False)
    ids_005 = set(filter_005["record_uid"].astype(str))
    ids_010 = set(filter_010["record_uid"].astype(str))
    check(rows, "filter_sample_identity", ids_005 == ids_010, len(ids_005 & ids_010), len(ids_005 | ids_010))
    grain_005 = set(zip(filter_005["record_uid"].astype(str), filter_005["policy"].astype(str), filter_005["period_sec"]))
    grain_010 = set(zip(filter_010["record_uid"].astype(str), filter_010["policy"].astype(str), filter_010["period_sec"]))
    check(rows, "filter_comparison_grain", grain_005 == grain_010, len(grain_005 & grain_010), len(grain_005 | grain_010))
    filter_ringdown_005 = sorted(set(pd.to_numeric(filter_005["ringdown_cycles"], errors="coerce").dropna()))
    filter_ringdown_010 = sorted(set(pd.to_numeric(filter_010["ringdown_cycles"], errors="coerce").dropna()))
    check(
        rows,
        "filter_ringdown_cycles",
        filter_ringdown_005 == [5.0] and filter_ringdown_010 == [5.0],
        {"0.05 Hz": filter_ringdown_005, "0.10 Hz": filter_ringdown_010},
        {"0.05 Hz": [5.0], "0.10 Hz": [5.0]},
    )

    pnw_snr = pd.read_csv(args.pnw_snr)
    check(rows, "pnw_snr_records", int(pnw_snr["records"].sum()) == 6107, int(pnw_snr["records"].sum()), 6107)
    check(
        rows,
        "pnw_snr_bins",
        pnw_snr["snr_bin"].astype(str).tolist() == ["<3 dB", "3-10 dB", ">=10 dB"],
        pnw_snr["snr_bin"].astype(str).tolist(),
        ["<3 dB", "3-10 dB", ">=10 dB"],
    )
    observed_snr_psa = [round(value, 2) for value in pnw_snr["selected_3s_psa_failure_pct"]]
    observed_snr_fallback = [round(value, 2) for value in pnw_snr["spectral_full_record_fallback_pct"]]
    check(rows, "pnw_snr_primary_psa", observed_snr_psa == [50.81, 63.34, 66.67], observed_snr_psa, [50.81, 63.34, 66.67])
    check(rows, "pnw_snr_final_fallback", observed_snr_fallback == [0.68, 0.76, 38.65], observed_snr_fallback, [0.68, 0.76, 38.65])

    english = Path(args.english_draft).read_text()
    chinese = Path(args.chinese_draft).read_text()
    required_numbers = ["44,674", "37.16%", "60.08%", "19.96%", "34.42%", "48.03%", "17.55%", "22.81%", "21.43%"]
    missing_english = [value for value in required_numbers if value not in english]
    missing_chinese = [value for value in required_numbers if value not in chinese]
    check(rows, "english_key_numbers", not missing_english, missing_english, [])
    check(rows, "chinese_key_numbers", not missing_chinese, missing_chinese, [])
    stale_markers = [
        "53,463",
        "K-NET waveform features were computed after 1 Hz",
        "Only 0.84% of records",
        "10.1785/0120110242",
        "10.1785/0120110090",
    ]
    observed_stale = [marker for marker in stale_markers if marker in english or marker in chinese]
    check(rows, "manuscript_stale_markers", not observed_stale, observed_stale, [])
    corrected_references = ["10.1785/0120110222", "10.1007/s10518-010-9208-4"]
    missing_references = [reference for reference in corrected_references if reference not in english or reference not in chinese]
    check(rows, "corrected_reference_metadata", not missing_references, missing_references, [])
    check(rows, "chinese_no_local_cache_wording", "本地可用子集" not in chinese, "本地可用子集" in chinese, False)
    english_data_resources = english.split("## Data and Resources", 1)[1].split("## Acknowledgments", 1)[0]
    chinese_data_resources = chinese.split("## 数据和资源", 1)[1].split("## 致谢", 1)[0]
    check(rows, "english_ai_disclosure_location", "OpenAI Codex" in english_data_resources, "OpenAI Codex" in english_data_resources, True)
    check(rows, "chinese_ai_disclosure_location", "OpenAI Codex" in chinese_data_resources, "OpenAI Codex" in chinese_data_resources, True)
    chinese_latex = Path(args.chinese_latex).read_text()
    numbered_heading_commands = re.findall(r"\\(?:sub)*section\{", chinese_latex)
    check(rows, "chinese_no_double_section_numbering", not numbered_heading_commands, numbered_heading_commands, [])
    return pd.DataFrame(rows)


def write_report(outdir: Path, checks: pd.DataFrame) -> None:
    passed = int(checks["status"].eq("PASS").sum())
    failed = int(checks["status"].eq("FAIL").sum())
    lines = [
        "# Revised StrongMotion-QC Evidence Audit",
        "",
        f"Result: {passed} PASS, {failed} FAIL.",
        "",
        "```csv",
        checks.to_csv(index=False).strip(),
        "```",
    ]
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    args = parse_args()
    checks = run_audit(args)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    checks.to_csv(outdir / "checks.csv", index=False)
    write_report(outdir, checks)
    print(f"Wrote {outdir.resolve()}")
    if checks["status"].eq("FAIL").any():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
