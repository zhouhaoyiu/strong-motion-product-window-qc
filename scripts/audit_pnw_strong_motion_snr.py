#!/usr/bin/env python3
"""Stratify the PNW external audit with a result-blind waveform SNR."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.compute_strong_motion_qc_features import load_pnw_waveform, preprocess_acceleration_waveform


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", required=True)
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--selected-windows", required=True)
    parser.add_argument("--window-stability", required=True)
    parser.add_argument("--response-spectrum", required=True)
    parser.add_argument("--safeguarded-windows")
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--highpass-hz", type=float, default=0.1)
    return parser.parse_args()


def vector_rms(waveform: np.ndarray) -> float:
    arr = np.asarray(waveform, dtype=float)
    if arr.ndim == 1:
        arr = arr[None, :]
    if arr.size == 0:
        return float("nan")
    vector_power = np.sum(np.nan_to_num(arr, nan=0.0) ** 2, axis=0)
    return float(np.sqrt(np.mean(vector_power)))


def record_snr(waveform: np.ndarray, sampling_rate: float, p_sec: float, s_sec: float) -> dict[str, float]:
    sr = float(sampling_rate)
    duration = waveform.shape[-1] / sr
    noise_start = max(0.0, p_sec - 22.0)
    noise_end = max(0.0, p_sec - 2.0)
    signal_start = max(0.0, p_sec)
    signal_end = min(duration, max(p_sec + 20.0, s_sec + 20.0))
    if noise_end - noise_start < 5.0 or signal_end - signal_start < 5.0:
        return {"noise_rms": np.nan, "signal_rms": np.nan, "snr_db": np.nan}
    noise = waveform[:, int(noise_start * sr) : int(noise_end * sr)]
    signal = waveform[:, int(signal_start * sr) : int(signal_end * sr)]
    noise_rms = vector_rms(noise)
    signal_rms = vector_rms(signal)
    snr_db = 20.0 * np.log10(signal_rms / noise_rms) if noise_rms > 0 and signal_rms > 0 else np.nan
    return {"noise_rms": noise_rms, "signal_rms": signal_rms, "snr_db": float(snr_db)}


def assign_snr_bin(snr_db: pd.Series) -> pd.Categorical:
    return pd.cut(
        pd.to_numeric(snr_db, errors="coerce"),
        bins=[-np.inf, 3.0, 10.0, np.inf],
        labels=["<3 dB", "3-10 dB", ">=10 dB"],
        right=False,
    )


def to_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin({"true", "1", "yes", "y"})


def summarize(audit: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for snr_bin, group in audit.groupby("snr_bin", observed=True):
        row = {
                "snr_bin": str(snr_bin),
                "records": len(group),
                "median_magnitude": pd.to_numeric(group["magnitude"], errors="coerce").median(),
                "median_snr_db": pd.to_numeric(group["snr_db"], errors="coerce").median(),
                "feature_fixed_unstable_pct": 100.0 * to_bool(group["feature_fixed_unstable"]).mean(),
                "full_record_assignment_pct": 100.0 * to_bool(group["full_record_assignment"]).mean(),
                "median_selected_duration_sec": pd.to_numeric(group["selected_duration_sec"], errors="coerce").median(),
                "selected_3s_psa_failure_pct": 100.0 * to_bool(group["selected_3s_psa_failure"]).mean(),
            }
        if "spectral_stage" in group:
            stage = group["spectral_stage"].astype(str)
            row.update(
                {
                    "spectral_escalation_pct": 100.0 * float(stage.ne("primary").mean()),
                    "spectral_full_record_fallback_pct": 100.0 * float(stage.eq("full_record_fallback").mean()),
                    "median_final_duration_sec": pd.to_numeric(group["final_duration_sec"], errors="coerce").median(),
                }
            )
        rows.append(row)
    return pd.DataFrame(rows)


def build_audit(
    features: pd.DataFrame,
    manifest: pd.DataFrame,
    selected: pd.DataFrame,
    stability: pd.DataFrame,
    response: pd.DataFrame,
    highpass_hz: float,
    safeguarded: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    records = features[features["waveform_qc_status"].eq("ok")].copy()
    timing = manifest[["record_uid", "catalog_p_sec", "catalog_s_sec"]].drop_duplicates("record_uid")
    records = records.drop(columns=["catalog_p_sec"], errors="ignore").merge(timing, on="record_uid", how="left")

    import seisbench.data as sbd

    pnw = sbd.PNWAccelerometers(component_order="ENZ")
    snr_rows = []
    for _, row in records.iterrows():
        waveform, _ = load_pnw_waveform(pnw, row)
        waveform = preprocess_acceleration_waveform(waveform, float(row["sampling_rate_hz"]), highpass_hz)
        metrics = record_snr(
            waveform,
            float(row["sampling_rate_hz"]),
            float(row["catalog_p_sec"]),
            float(row["catalog_s_sec"]),
        )
        snr_rows.append({"record_uid": row["record_uid"], **metrics})
    records = records.merge(pd.DataFrame(snr_rows), on="record_uid", how="left")
    records["snr_bin"] = assign_snr_bin(records["snr_db"])

    selected_main = selected[selected["policy"].eq("shortest_stable_no_catalog")][
        ["record_uid", "selection_status", "window_duration_sec"]
    ].rename(columns={"window_duration_sec": "selected_duration_sec"})
    selected_main["full_record_assignment"] = selected_main["selection_status"].eq("full_record_fallback")
    fixed = stability[stability["candidate"].eq("feature_onset_fixed")][["record_uid", "window_unstable"]].rename(
        columns={"window_unstable": "feature_fixed_unstable"}
    )
    psa = response[
        response["policy"].eq("shortest_stable_no_catalog") & response["period_sec"].eq(3.0)
    ][["record_uid", "spectrum_unstable"]].rename(columns={"spectrum_unstable": "selected_3s_psa_failure"})

    audit = records.merge(selected_main, on="record_uid", how="inner").merge(fixed, on="record_uid", how="inner").merge(psa, on="record_uid", how="inner")
    if safeguarded is not None:
        final = safeguarded[["record_uid", "spectral_stage", "window_duration_sec"]].rename(
            columns={"window_duration_sec": "final_duration_sec"}
        )
        audit = audit.merge(final, on="record_uid", how="inner")
    return audit, summarize(audit)


def write_report(outdir: Path, summary: pd.DataFrame) -> None:
    lines = [
        "# PNWAccelerometers SNR-Stratified Audit",
        "",
        "SNR is computed before product evaluation from a 20 s pre-P noise interval and a P-to-(S+20 s) signal interval after common acceleration preprocessing.",
        "",
        "```csv",
        summary.to_csv(index=False).strip(),
        "```",
        "",
        "The bins use waveform amplitude and catalog timing only. Window-selection and PSA outcomes do not define the strata.",
    ]
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    args = parse_args()
    audit, summary = build_audit(
        pd.read_csv(args.features, low_memory=False),
        pd.read_csv(args.manifest, low_memory=False),
        pd.read_csv(args.selected_windows, low_memory=False),
        pd.read_csv(args.window_stability, low_memory=False),
        pd.read_csv(args.response_spectrum, low_memory=False),
        args.highpass_hz,
        pd.read_csv(args.safeguarded_windows, low_memory=False) if args.safeguarded_windows else None,
    )
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    audit.to_csv(outdir / "pnw_snr_audit.csv", index=False)
    summary.to_csv(outdir / "summary.csv", index=False)
    write_report(outdir, summary)
    print(f"Wrote {outdir.resolve()}")


if __name__ == "__main__":
    main()
