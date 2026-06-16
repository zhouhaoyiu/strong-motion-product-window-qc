#!/usr/bin/env python3
"""Audit relative PGV retention for selected strong-motion windows."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import h5py
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from tqdm import tqdm
except ImportError:  # pragma: no cover

    def tqdm(iterable, **kwargs):
        return iterable

from scripts.evaluate_strong_motion_response_spectrum_retention import (  # noqa: E402
    DEFAULT_FEATURES,
    DEFAULT_KNET_WAVEFORMS,
    DEFAULT_POLICIES,
    DEFAULT_SELECTED,
    load_record_waveform,
    load_waveform_handles,
    prepare_record_table,
    prepare_windows,
)
from scripts.compute_strong_motion_qc_features import standardize_channels  # noqa: E402
from strong_motion_qc.features import vector_amplitude  # noqa: E402


DEFAULT_OUTDIR = "outputs/strong_motion_qc_pgv_retention_knet22119_hp1_inst3000"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default=DEFAULT_FEATURES)
    parser.add_argument("--selected-windows", default=DEFAULT_SELECTED)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    parser.add_argument("--knet-waveforms", default=DEFAULT_KNET_WAVEFORMS)
    parser.add_argument("--knet-highpass-hz", type=float, default=1.0)
    parser.add_argument("--retention-threshold", type=float, default=0.95)
    parser.add_argument("--policies", nargs="+", default=DEFAULT_POLICIES)
    parser.add_argument("--max-records", type=int, default=None)
    parser.add_argument("--per-group", type=int, default=None)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def normalize_unit(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip().lower().replace(" ", "")


def cumulative_trapezoid(values: np.ndarray, dt: float) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    if arr.shape[-1] == 0:
        return arr.copy()
    out = np.zeros_like(arr, dtype=np.float64)
    if arr.shape[-1] > 1:
        out[..., 1:] = np.cumsum(0.5 * (arr[..., 1:] + arr[..., :-1]) * float(dt), axis=-1)
    return out


def acceleration_to_velocity_proxy(acceleration: np.ndarray, sampling_rate: float) -> np.ndarray:
    """Return a baseline-corrected velocity proxy from acceleration."""

    from scipy.signal import detrend

    arr = standardize_channels(acceleration)
    cleaned = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    demeaned = detrend(cleaned, axis=-1, type="constant")
    velocity = cumulative_trapezoid(demeaned, dt=1.0 / float(sampling_rate))
    return detrend(velocity, axis=-1, type="linear")


def velocity_proxy(row: pd.Series, waveform: np.ndarray) -> tuple[np.ndarray, str]:
    """Convert a loaded waveform to a velocity-like series for relative PGV."""

    arr = standardize_channels(waveform)
    unit = normalize_unit(row.get("units", ""))
    dataset = str(row.get("dataset", ""))
    sampling_rate = float(row["sampling_rate_hz"])
    if unit in {"mps", "m/s", "meter/second", "meters/second"}:
        return np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0), "direct_velocity"
    if unit in {"mps2", "m/s2", "meter/second2", "meters/second2"}:
        return acceleration_to_velocity_proxy(arr, sampling_rate), "integrated_acceleration"
    if dataset == "K-NET":
        return acceleration_to_velocity_proxy(arr, sampling_rate), "integrated_knet_acceleration"
    return np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0), "unknown_units_direct"


def peak_vector_velocity(velocity: np.ndarray) -> float:
    arr = standardize_channels(velocity)
    if arr.size == 0 or arr.shape[-1] == 0:
        return float("nan")
    return float(np.nanmax(vector_amplitude(arr)))


def record_pgv_rows(
    row: pd.Series,
    waveform: np.ndarray,
    windows: pd.DataFrame,
    retention_threshold: float,
) -> list[dict[str, object]]:
    sampling_rate = float(row["sampling_rate_hz"])
    n_samples = int(waveform.shape[-1])
    velocity, velocity_source = velocity_proxy(row, waveform)
    full_pgv = peak_vector_velocity(velocity)
    rows: list[dict[str, object]] = []
    cache: dict[tuple[int, int], float] = {}
    for _, window_row in windows.iterrows():
        start = int(np.clip(int(window_row["window_start_sample"]), 0, n_samples))
        end = int(np.clip(int(window_row["window_end_sample"]), 0, n_samples))
        if end < start:
            end = start
        key = (start, end)
        if key not in cache:
            cache[key] = peak_vector_velocity(velocity[:, start:end])
        window_pgv = cache[key]
        retention = window_pgv / full_pgv if np.isfinite(full_pgv) and full_pgv > 0 else float("nan")
        rows.append(
            {
                "record_uid": row["record_uid"],
                "dataset": row["dataset"],
                "priority_group": row.get("priority_group", ""),
                "split": row.get("split", ""),
                "magnitude": row.get("magnitude", np.nan),
                "units": row.get("units", ""),
                "velocity_source": velocity_source,
                "policy": window_row["policy"],
                "selected_candidate": window_row.get("selected_candidate", ""),
                "selection_status": window_row.get("selection_status", ""),
                "window_start_sample": start,
                "window_end_sample": end,
                "window_duration_sec": float((end - start) / sampling_rate),
                "full_pgv_proxy": full_pgv,
                "window_pgv_proxy": window_pgv,
                "pgv_retention": float(retention),
                "pgv_unstable": bool(np.isfinite(retention) and retention < retention_threshold),
                "retention_threshold": float(retention_threshold),
            }
        )
    return rows


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return pd.DataFrame()
    rows = []
    for keys, group in results.groupby(["dataset", "priority_group", "policy"], dropna=False):
        rows.append(summary_row(keys, group))
    for keys, group in results.groupby(["dataset", "policy"], dropna=False):
        rows.append(summary_row((keys[0], "ALL", keys[1]), group))
    for policy, group in results.groupby("policy", dropna=False):
        rows.append(summary_row(("ALL", "ALL", policy), group))
    return pd.DataFrame(rows)


def summary_row(keys, group: pd.DataFrame) -> dict[str, object]:
    retention = pd.to_numeric(group["pgv_retention"], errors="coerce")
    unstable = group["pgv_unstable"].astype(bool)
    source_counts = group["velocity_source"].astype(str).value_counts().to_dict()
    return {
        "dataset": keys[0],
        "priority_group": keys[1],
        "policy": keys[2],
        "records": int(len(group)),
        "pgv_unstable_records": int(unstable.sum()),
        "pgv_unstable_pct": 100.0 * float(unstable.mean()) if len(group) else 0.0,
        "median_pgv_retention": float(retention.median()),
        "p05_pgv_retention": float(retention.quantile(0.05)),
        "p01_pgv_retention": float(retention.quantile(0.01)),
        "median_window_duration_sec": float(pd.to_numeric(group["window_duration_sec"], errors="coerce").median()),
        "direct_velocity_records": int(source_counts.get("direct_velocity", 0)),
        "integrated_acceleration_records": int(source_counts.get("integrated_acceleration", 0)),
        "integrated_knet_acceleration_records": int(source_counts.get("integrated_knet_acceleration", 0)),
        "unknown_units_direct_records": int(source_counts.get("unknown_units_direct", 0)),
    }


def markdown_table(df: pd.DataFrame) -> str:
    columns = list(df.columns)
    rows = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in df.iterrows():
        values = []
        for col in columns:
            value = row[col]
            if isinstance(value, float):
                values.append("" if pd.isna(value) else f"{value:.3f}")
            else:
                values.append(str(value))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def write_report(outdir: Path, summary: pd.DataFrame, policies: list[str]) -> None:
    focus = summary[
        summary["priority_group"].eq("ALL")
        & summary["dataset"].isin(["InstanceGM", "K-NET", "ALL"])
        & summary["policy"].isin(policies)
    ].copy()
    lines = [
        "# StrongMotion-QC Relative PGV Retention",
        "",
        "This diagnostic compares a peak-vector-velocity proxy inside each processing window with the same proxy computed on the full record.",
        "",
        "## Summary",
        "",
        markdown_table(focus),
        "",
        "## Outputs",
        "",
        "- `pgv_retention.csv`: per-record, per-policy relative PGV-retention proxy.",
        "- `summary.csv`: grouped PGV-retention summary.",
        "",
        "## Boundary",
        "",
        "This is a relative retention audit, not an absolute PGV product release. Records already in velocity units use the waveform directly. Acceleration records use demeaned acceleration, trapezoidal integration, and linear velocity detrending before the retention ratio is computed. The ratio is useful for checking whether a window contains the full-record peak velocity proxy; final manuscript use should keep this unit-processing boundary visible.",
    ]
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def run_pgv_retention(
    features: pd.DataFrame,
    selected_windows: pd.DataFrame,
    outdir: Path,
    knet_waveforms: Path = Path(DEFAULT_KNET_WAVEFORMS),
    knet_highpass_hz: float | None = 1.0,
    retention_threshold: float = 0.95,
    policies: list[str] | None = None,
    max_records: int | None = None,
    per_group: int | None = None,
    seed: int = 42,
) -> dict[str, Path]:
    policy_values = policies or DEFAULT_POLICIES
    windows = prepare_windows(selected_windows, policy_values)
    records = prepare_record_table(features, windows, max_records=max_records, per_group=per_group, seed=seed)
    windows = windows[windows["record_uid"].astype(str).isin(records["record_uid"].astype(str))].copy()
    windows_by_record = {record_uid: group for record_uid, group in windows.groupby("record_uid", sort=False)}

    rows: list[dict[str, object]] = []
    load_errors: list[dict[str, object]] = []
    instance_data, h5, keys = load_waveform_handles(records, knet_waveforms)
    try:
        for _, row in tqdm(records.iterrows(), total=len(records), desc="PGV retention"):
            record_uid = str(row["record_uid"])
            record_windows = windows_by_record.get(record_uid)
            if record_windows is None or record_windows.empty:
                continue
            try:
                waveform = load_record_waveform(row, instance_data, h5, keys, knet_highpass_hz)
                rows.extend(record_pgv_rows(row, waveform, record_windows, retention_threshold=retention_threshold))
            except Exception as exc:
                load_errors.append(
                    {
                        "record_uid": record_uid,
                        "dataset": row.get("dataset", ""),
                        "priority_group": row.get("priority_group", ""),
                        "error": str(exc),
                    }
                )
    finally:
        if h5 is not None:
            h5.close()

    results = pd.DataFrame(rows)
    summary = summarize(results)
    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "results": outdir / "pgv_retention.csv",
        "summary": outdir / "summary.csv",
        "report": outdir / "README.md",
    }
    results.to_csv(outputs["results"], index=False)
    summary.to_csv(outputs["summary"], index=False)
    write_report(outdir, summary, policy_values)
    if load_errors:
        error_path = outdir / "load_errors.csv"
        pd.DataFrame(load_errors).to_csv(error_path, index=False)
        outputs["load_errors"] = error_path
    return outputs


def main() -> None:
    args = parse_args()
    features = pd.read_csv(args.features, low_memory=False)
    selected = pd.read_csv(args.selected_windows, low_memory=False)
    outputs = run_pgv_retention(
        features=features,
        selected_windows=selected,
        outdir=Path(args.outdir),
        knet_waveforms=Path(args.knet_waveforms),
        knet_highpass_hz=args.knet_highpass_hz,
        retention_threshold=args.retention_threshold,
        policies=args.policies,
        max_records=args.max_records,
        per_group=args.per_group,
        seed=args.seed,
    )
    for path in outputs.values():
        print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
