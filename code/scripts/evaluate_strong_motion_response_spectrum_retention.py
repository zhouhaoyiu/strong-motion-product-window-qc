#!/usr/bin/env python3
"""Audit response-spectrum retention for selected strong-motion windows."""

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

from scripts.compute_strong_motion_qc_features import (  # noqa: E402
    highpass_waveform,
    load_instance_waveform,
    load_knet_waveform,
    normalize_waveform_orientation,
)
from scripts.evaluate_knet_offline import list_hdf5_keys  # noqa: E402
from scripts.train_strong_motion_masked_encoder import DEFAULT_KNET_WAVEFORMS, standardize_channels  # noqa: E402


DEFAULT_FEATURES = "outputs/strong_motion_qc_waveform_features_knet22119_hp1_inst3000/waveform_features.csv"
DEFAULT_SELECTED = "outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/selected_windows.csv"
DEFAULT_OUTDIR = "outputs/strong_motion_qc_response_spectrum_knet22119_hp1_inst3000"
DEFAULT_POLICIES = [
    "feature_onset_fixed",
    "energy_onset_fixed",
    "catalog_p_fixed",
    "adaptive_energy_end",
    "shortest_stable_no_catalog",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default=DEFAULT_FEATURES)
    parser.add_argument("--selected-windows", default=DEFAULT_SELECTED)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    parser.add_argument("--knet-waveforms", default=DEFAULT_KNET_WAVEFORMS)
    parser.add_argument("--knet-highpass-hz", type=float, default=1.0)
    parser.add_argument("--periods", nargs="+", type=float, default=[0.2, 1.0, 3.0])
    parser.add_argument("--damping", type=float, default=0.05)
    parser.add_argument("--retention-threshold", type=float, default=0.95)
    parser.add_argument("--policies", nargs="+", default=DEFAULT_POLICIES)
    parser.add_argument("--max-records", type=int, default=None)
    parser.add_argument("--per-group", type=int, default=None)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def prepare_windows(selected: pd.DataFrame, policies: list[str]) -> pd.DataFrame:
    work = selected[selected["policy"].isin(policies)].copy()
    if "selection_status" in work:
        work = work[~work["selection_status"].eq("missing_candidate")].copy()
    for column in ["window_start_sample", "window_end_sample"]:
        work[column] = pd.to_numeric(work[column], errors="coerce")
    work = work[work["window_start_sample"].notna() & work["window_end_sample"].notna()].copy()
    work["window_start_sample"] = work["window_start_sample"].astype(int)
    work["window_end_sample"] = work["window_end_sample"].astype(int)
    return work


def prepare_record_table(features: pd.DataFrame, selected: pd.DataFrame, max_records: int | None, per_group: int | None, seed: int) -> pd.DataFrame:
    ok = features.copy()
    if "waveform_qc_status" in ok:
        ok = ok[ok["waveform_qc_status"].eq("ok")].copy()
    needed = selected[["record_uid", "dataset", "priority_group"]].drop_duplicates()
    records = ok.merge(needed[["record_uid"]], on="record_uid", how="inner")
    if per_group is not None:
        sampled = []
        for _, group in records.groupby(["dataset", "priority_group"], dropna=False):
            if len(group) > per_group:
                sampled.append(group.sample(n=per_group, random_state=seed))
            else:
                sampled.append(group)
        records = pd.concat(sampled, ignore_index=True) if sampled else records.iloc[0:0].copy()
    elif max_records is not None:
        records = records.head(max_records).copy()
    return records


def load_waveform_handles(records: pd.DataFrame, knet_waveforms: Path):
    instance_data = None
    if records["dataset"].eq("InstanceGM").any():
        import seisbench.data as sbd

        instance_data = sbd.InstanceGM()
    h5 = None
    keys = None
    if records["dataset"].eq("K-NET").any():
        h5 = h5py.File(knet_waveforms, "r")
        keys = set(list_hdf5_keys(h5))
    return instance_data, h5, keys


def load_record_waveform(row: pd.Series, instance_data, h5, keys: set[str] | None, knet_highpass_hz: float | None) -> np.ndarray:
    dataset = str(row["dataset"])
    sampling_rate = float(row["sampling_rate_hz"])
    if dataset == "InstanceGM":
        waveform, _ = load_instance_waveform(instance_data, row)
    elif dataset == "K-NET":
        if h5 is None or keys is None:
            raise ValueError("K-NET HDF5 handle is unavailable")
        waveform, _ = load_knet_waveform(h5, keys, row)
        waveform = highpass_waveform(waveform, sampling_rate=sampling_rate, corner_hz=knet_highpass_hz)
    else:
        raise ValueError(f"unsupported dataset: {dataset}")
    return standardize_channels(normalize_waveform_orientation(waveform))


def discrete_oscillator_coefficients(period: float, damping: float, sampling_rate: float) -> tuple[np.ndarray, np.ndarray, float]:
    from scipy.signal import cont2discrete

    if period <= 0:
        raise ValueError(f"period must be positive, got {period}")
    omega = 2.0 * np.pi / float(period)
    numerator = np.array([-1.0], dtype=float)
    denominator = np.array([1.0, 2.0 * damping * omega, omega * omega], dtype=float)
    b, a, _ = cont2discrete((numerator, denominator), 1.0 / float(sampling_rate), method="bilinear")
    return np.ravel(b), np.ravel(a), omega


def pseudo_spectral_acceleration(component: np.ndarray, period: float, damping: float, sampling_rate: float) -> float:
    from scipy.signal import lfilter

    x = np.asarray(component, dtype=np.float64)
    if x.size == 0:
        return float("nan")
    b, a, omega = discrete_oscillator_coefficients(period, damping, sampling_rate)
    displacement = lfilter(b, a, np.nan_to_num(x, nan=0.0, posinf=0.0, neginf=0.0))
    return float((omega * omega) * np.max(np.abs(displacement)))


def max_component_psa(waveform: np.ndarray, period: float, damping: float, sampling_rate: float) -> float:
    arr = standardize_channels(normalize_waveform_orientation(waveform))
    values = [pseudo_spectral_acceleration(arr[channel], period, damping, sampling_rate) for channel in range(arr.shape[0])]
    finite = [value for value in values if np.isfinite(value)]
    return float(max(finite)) if finite else float("nan")


def record_spectrum_rows(
    row: pd.Series,
    waveform: np.ndarray,
    windows: pd.DataFrame,
    periods: list[float],
    damping: float,
    retention_threshold: float,
) -> list[dict[str, object]]:
    sampling_rate = float(row["sampling_rate_hz"])
    n_samples = int(waveform.shape[-1])
    full_by_period = {
        period: max_component_psa(waveform, period=period, damping=damping, sampling_rate=sampling_rate)
        for period in periods
    }
    cache: dict[tuple[int, int, float], float] = {}
    rows: list[dict[str, object]] = []
    for _, window_row in windows.iterrows():
        start = int(np.clip(int(window_row["window_start_sample"]), 0, n_samples))
        end = int(np.clip(int(window_row["window_end_sample"]), 0, n_samples))
        if end < start:
            end = start
        segment = waveform[:, start:end]
        for period in periods:
            key = (start, end, float(period))
            if key not in cache:
                cache[key] = max_component_psa(segment, period=period, damping=damping, sampling_rate=sampling_rate)
            full_psa = full_by_period[period]
            window_psa = cache[key]
            retention = window_psa / full_psa if np.isfinite(full_psa) and full_psa > 0 else float("nan")
            rows.append(
                {
                    "record_uid": row["record_uid"],
                    "dataset": row["dataset"],
                    "priority_group": row.get("priority_group", ""),
                    "split": row.get("split", ""),
                    "magnitude": row.get("magnitude", np.nan),
                    "policy": window_row["policy"],
                    "selected_candidate": window_row.get("selected_candidate", ""),
                    "selection_status": window_row.get("selection_status", ""),
                    "window_start_sample": start,
                    "window_end_sample": end,
                    "window_duration_sec": float((end - start) / sampling_rate),
                    "period_sec": float(period),
                    "damping": float(damping),
                    "full_psa": full_psa,
                    "window_psa": window_psa,
                    "psa_retention": float(retention),
                    "spectrum_unstable": bool(np.isfinite(retention) and retention < retention_threshold),
                    "retention_threshold": float(retention_threshold),
                }
            )
    return rows


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return pd.DataFrame()
    rows = []
    group_cols = ["dataset", "priority_group", "policy", "period_sec"]
    for keys, group in results.groupby(group_cols, dropna=False):
        rows.append(summary_row(keys, group))
    for keys, group in results.groupby(["dataset", "policy", "period_sec"], dropna=False):
        rows.append(summary_row((keys[0], "ALL", keys[1], keys[2]), group))
    for keys, group in results.groupby(["policy", "period_sec"], dropna=False):
        rows.append(summary_row(("ALL", "ALL", keys[0], keys[1]), group))
    return pd.DataFrame(rows)


def summary_row(keys, group: pd.DataFrame) -> dict[str, object]:
    retention = pd.to_numeric(group["psa_retention"], errors="coerce")
    unstable = group["spectrum_unstable"].astype(bool)
    return {
        "dataset": keys[0],
        "priority_group": keys[1],
        "policy": keys[2],
        "period_sec": float(keys[3]),
        "records": int(len(group)),
        "spectrum_unstable_records": int(unstable.sum()),
        "spectrum_unstable_pct": 100.0 * float(unstable.mean()) if len(group) else 0.0,
        "median_psa_retention": float(retention.median()),
        "p05_psa_retention": float(retention.quantile(0.05)),
        "p01_psa_retention": float(retention.quantile(0.01)),
        "median_window_duration_sec": float(pd.to_numeric(group["window_duration_sec"], errors="coerce").median()),
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


def write_report(outdir: Path, summary: pd.DataFrame, periods: list[float], policies: list[str]) -> None:
    focus = summary[
        summary["priority_group"].eq("ALL")
        & summary["dataset"].isin(["InstanceGM", "K-NET", "ALL"])
        & summary["policy"].isin(policies)
    ].copy()
    lines = [
        "# StrongMotion-QC Response-Spectrum Retention",
        "",
        "This audit compares 5%-damped pseudo-spectral acceleration computed inside selected processing windows with the same product computed on the full record.",
        "",
        f"Periods: {', '.join(f'{period:g} s' for period in periods)}.",
        "",
        "The result is a relative retention audit. It strengthens the product-window claim because response spectra are closer to strong-motion engineering products than PGA and waveform energy alone.",
        "",
        "## Summary",
        "",
        markdown_table(focus),
        "",
        "## Outputs",
        "",
        "- `response_spectrum_retention.csv`: per-record, per-policy, per-period response-spectrum retention.",
        "- `summary.csv`: grouped spectrum-retention summary.",
        "",
        "## Boundary",
        "",
        "The current calculation reports relative pseudo-spectral acceleration retention. It does not establish absolute site-specific design spectra.",
    ]
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def run_response_spectrum_retention(
    features: pd.DataFrame,
    selected_windows: pd.DataFrame,
    outdir: Path,
    knet_waveforms: Path = Path(DEFAULT_KNET_WAVEFORMS),
    knet_highpass_hz: float | None = 1.0,
    periods: list[float] | None = None,
    damping: float = 0.05,
    retention_threshold: float = 0.95,
    policies: list[str] | None = None,
    max_records: int | None = None,
    per_group: int | None = None,
    seed: int = 42,
) -> dict[str, Path]:
    period_values = periods or [0.2, 1.0, 3.0]
    policy_values = policies or DEFAULT_POLICIES
    windows = prepare_windows(selected_windows, policy_values)
    records = prepare_record_table(features, windows, max_records=max_records, per_group=per_group, seed=seed)
    windows = windows[windows["record_uid"].astype(str).isin(records["record_uid"].astype(str))].copy()
    windows_by_record = {record_uid: group for record_uid, group in windows.groupby("record_uid", sort=False)}

    rows: list[dict[str, object]] = []
    load_errors: list[dict[str, object]] = []
    instance_data, h5, keys = load_waveform_handles(records, knet_waveforms)
    try:
        for _, row in tqdm(records.iterrows(), total=len(records), desc="Response spectra"):
            record_uid = str(row["record_uid"])
            record_windows = windows_by_record.get(record_uid)
            if record_windows is None or record_windows.empty:
                continue
            try:
                waveform = load_record_waveform(row, instance_data, h5, keys, knet_highpass_hz)
                rows.extend(
                    record_spectrum_rows(
                        row,
                        waveform,
                        record_windows,
                        periods=period_values,
                        damping=damping,
                        retention_threshold=retention_threshold,
                    )
                )
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
        "results": outdir / "response_spectrum_retention.csv",
        "summary": outdir / "summary.csv",
        "report": outdir / "README.md",
    }
    results.to_csv(outputs["results"], index=False)
    summary.to_csv(outputs["summary"], index=False)
    write_report(outdir, summary, period_values, policy_values)
    if load_errors:
        error_path = outdir / "load_errors.csv"
        pd.DataFrame(load_errors).to_csv(error_path, index=False)
        outputs["load_errors"] = error_path
    return outputs


def main() -> None:
    args = parse_args()
    features = pd.read_csv(args.features, low_memory=False)
    selected = pd.read_csv(args.selected_windows, low_memory=False)
    outputs = run_response_spectrum_retention(
        features=features,
        selected_windows=selected,
        outdir=Path(args.outdir),
        knet_waveforms=Path(args.knet_waveforms),
        knet_highpass_hz=args.knet_highpass_hz,
        periods=args.periods,
        damping=args.damping,
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
