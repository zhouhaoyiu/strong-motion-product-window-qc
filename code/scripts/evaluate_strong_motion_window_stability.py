#!/usr/bin/env python3
"""Evaluate whether candidate strong-motion windows preserve waveform products."""

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
    DEFAULT_KNET_WAVEFORMS,
    highpass_waveform,
    list_hdf5_keys,
    load_instance_waveform,
    load_knet_waveform,
    load_pnw_waveform,
    normalize_waveform_orientation,
    standardize_channels,
)


DEFAULT_FEATURES = "outputs/strong_motion_qc_waveform_features/waveform_features.csv"
GROUP_COLUMNS = ["dataset", "priority_group", "candidate"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default=DEFAULT_FEATURES)
    parser.add_argument("--outdir", default="outputs/strong_motion_qc_window_stability")
    parser.add_argument("--knet-waveforms", default=DEFAULT_KNET_WAVEFORMS)
    parser.add_argument(
        "--knet-highpass-hz",
        type=float,
        default=None,
        help="Optional high-pass corner for K-NET waveforms before product-window evaluation.",
    )
    parser.add_argument("--max-records", type=int, default=None)
    parser.add_argument("--per-group", type=int, default=None, help="Sample up to this many records per dataset/priority group.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--pre-sec", type=float, default=2.0)
    parser.add_argument("--fixed-after-sec", type=float, default=40.0)
    parser.add_argument("--adaptive-post-sec", type=float, default=3.0)
    parser.add_argument("--pga-retention-threshold", type=float, default=0.99)
    parser.add_argument("--energy-retention-threshold", type=float, default=0.95)
    return parser.parse_args()


def vector_signal(waveform: np.ndarray) -> np.ndarray:
    arr = standardize_channels(normalize_waveform_orientation(waveform))
    return np.sqrt(np.sum(np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0) ** 2, axis=0))


def product_metrics(signal: np.ndarray, sampling_rate: float) -> dict[str, float]:
    sig = np.asarray(signal, dtype=np.float64)
    if sig.size == 0:
        return {
            "pga": float("nan"),
            "rms": float("nan"),
            "energy": float("nan"),
            "peak_time_sec": float("nan"),
        }
    sr = float(sampling_rate)
    pga = float(np.max(np.abs(sig)))
    return {
        "pga": pga,
        "rms": float(np.sqrt(np.mean(sig * sig))),
        "energy": float(np.sum(sig * sig) / sr),
        "peak_time_sec": float(int(np.argmax(np.abs(sig))) / sr),
    }


def clamp_window(start_sec: float, end_sec: float, n_samples: int, sampling_rate: float) -> tuple[int, int]:
    sr = float(sampling_rate)
    if not np.isfinite(start_sec) or not np.isfinite(end_sec):
        return 0, 0
    start = int(np.floor(start_sec * sr))
    end = int(np.ceil(end_sec * sr))
    start = int(np.clip(start, 0, n_samples))
    end = int(np.clip(end, 0, n_samples))
    if end < start:
        end = start
    return start, end


def candidate_windows(row: pd.Series, n_samples: int, sampling_rate: float, pre_sec: float, fixed_after_sec: float, adaptive_post_sec: float) -> list[dict[str, float | str]]:
    duration = n_samples / float(sampling_rate)
    candidates: list[dict[str, float | str]] = []
    onset_sources = [
        ("feature_onset_fixed", row.get("feature_onset_sec", np.nan)),
        ("energy_onset_fixed", row.get("feature_energy_onset_sec", np.nan)),
    ]
    if str(row.get("has_catalog_p", "")).lower() in {"true", "1", "yes"}:
        onset_sources.append(("catalog_p_fixed", row.get("catalog_p_sec", np.nan)))
    for name, onset in onset_sources:
        onset = pd.to_numeric(pd.Series([onset]), errors="coerce").iloc[0]
        candidates.append(
            {
                "candidate": name,
                "start_sec": float(onset - pre_sec) if np.isfinite(onset) else float("nan"),
                "end_sec": float(onset + fixed_after_sec) if np.isfinite(onset) else float("nan"),
            }
        )

    onset = pd.to_numeric(pd.Series([row.get("feature_onset_sec", np.nan)]), errors="coerce").iloc[0]
    energy_end = pd.to_numeric(pd.Series([row.get("feature_energy_end_sec", np.nan)]), errors="coerce").iloc[0]
    candidates.append(
        {
            "candidate": "feature_onset_to_energy_end",
            "start_sec": float(onset - pre_sec) if np.isfinite(onset) else float("nan"),
            "end_sec": float(energy_end + adaptive_post_sec) if np.isfinite(energy_end) else float("nan"),
        }
    )
    candidates.append({"candidate": "full_record", "start_sec": 0.0, "end_sec": float(duration)})
    return candidates


def evaluate_window(
    signal: np.ndarray,
    sampling_rate: float,
    start_sec: float,
    end_sec: float,
    pga_retention_threshold: float,
    energy_retention_threshold: float,
) -> dict[str, float | bool | str]:
    full = product_metrics(signal, sampling_rate)
    start, end = clamp_window(start_sec, end_sec, signal.size, sampling_rate)
    window = signal[start:end]
    win = product_metrics(window, sampling_rate)
    peak_sample = int(round(full["peak_time_sec"] * sampling_rate)) if np.isfinite(full["peak_time_sec"]) else -1
    peak_inside = start <= peak_sample < end
    pga_retention = win["pga"] / full["pga"] if full["pga"] and np.isfinite(full["pga"]) else float("nan")
    energy_retention = win["energy"] / full["energy"] if full["energy"] and np.isfinite(full["energy"]) else float("nan")
    pga_fail = np.isfinite(pga_retention) and pga_retention < pga_retention_threshold
    energy_fail = np.isfinite(energy_retention) and energy_retention < energy_retention_threshold
    reasons = []
    if start == end:
        reasons.append("empty_window")
    if not peak_inside:
        reasons.append("peak_outside")
    if pga_fail:
        reasons.append("pga_loss")
    if energy_fail:
        reasons.append("energy_loss")
    return {
        "window_start_sample": int(start),
        "window_end_sample": int(end),
        "window_duration_sec": float((end - start) / float(sampling_rate)),
        "full_pga": full["pga"],
        "window_pga": win["pga"],
        "pga_retention": float(pga_retention),
        "full_energy": full["energy"],
        "window_energy": win["energy"],
        "energy_retention": float(energy_retention),
        "full_rms": full["rms"],
        "window_rms": win["rms"],
        "peak_time_sec": full["peak_time_sec"],
        "peak_inside_window": bool(peak_inside),
        "window_unstable": bool(pga_fail or energy_fail or not peak_inside),
        "failure_reason": ",".join(reasons),
    }


def load_waveforms_for_rows(features: pd.DataFrame, knet_waveforms: Path):
    instance_data = None
    if features["dataset"].eq("InstanceGM").any():
        import seisbench.data as sbd

        instance_data = sbd.InstanceGM()
    pnw_data = None
    if features["dataset"].eq("PNWAccelerometers").any():
        import seisbench.data as sbd

        pnw_data = sbd.PNWAccelerometers()
    h5 = None
    keys = None
    if features["dataset"].eq("K-NET").any():
        h5 = h5py.File(knet_waveforms, "r")
        keys = set(list_hdf5_keys(h5))
    return instance_data, h5, keys, pnw_data


def evaluate_record(
    row: pd.Series,
    waveform: np.ndarray,
    pre_sec: float,
    fixed_after_sec: float,
    adaptive_post_sec: float,
    pga_retention_threshold: float,
    energy_retention_threshold: float,
) -> list[dict[str, object]]:
    sr = float(row["sampling_rate_hz"])
    signal = vector_signal(waveform)
    rows = []
    for candidate in candidate_windows(row, signal.size, sr, pre_sec, fixed_after_sec, adaptive_post_sec):
        metrics = evaluate_window(
            signal,
            sr,
            float(candidate["start_sec"]),
            float(candidate["end_sec"]),
            pga_retention_threshold=pga_retention_threshold,
            energy_retention_threshold=energy_retention_threshold,
        )
        out = {
            "record_uid": row.get("record_uid", ""),
            "dataset": row.get("dataset", ""),
            "priority_group": row.get("priority_group", ""),
            "split": row.get("split", ""),
            "magnitude": row.get("magnitude", np.nan),
            "candidate": candidate["candidate"],
            "candidate_start_sec": candidate["start_sec"],
            "candidate_end_sec": candidate["end_sec"],
            "feature_onset_sec": row.get("feature_onset_sec", np.nan),
            "feature_energy_onset_sec": row.get("feature_energy_onset_sec", np.nan),
            "feature_energy_end_sec": row.get("feature_energy_end_sec", np.nan),
            "catalog_p_sec": row.get("catalog_p_sec", np.nan),
            "feature_spike_score": row.get("feature_spike_score", np.nan),
            "feature_significant_duration_sec": row.get("feature_significant_duration_sec", np.nan),
        }
        out.update(metrics)
        rows.append(out)
    return rows


def summarize(results: pd.DataFrame) -> pd.DataFrame:
    if results.empty:
        return pd.DataFrame()
    rows = []
    for keys, group in results.groupby(GROUP_COLUMNS, dropna=False):
        rows.append(summary_row(keys, group))
    rows.append(summary_row(("ALL", "ALL", "ALL"), results))
    return pd.DataFrame(rows)


def summary_row(keys, group: pd.DataFrame) -> dict[str, object]:
    unstable = group["window_unstable"].astype(bool)
    return {
        "dataset": keys[0],
        "priority_group": keys[1],
        "candidate": keys[2],
        "records": int(len(group)),
        "unstable_records": int(unstable.sum()),
        "unstable_pct": 100.0 * float(unstable.mean()) if len(group) else 0.0,
        "median_pga_retention": float(pd.to_numeric(group["pga_retention"], errors="coerce").median()),
        "p05_pga_retention": float(pd.to_numeric(group["pga_retention"], errors="coerce").quantile(0.05)),
        "median_energy_retention": float(pd.to_numeric(group["energy_retention"], errors="coerce").median()),
        "p05_energy_retention": float(pd.to_numeric(group["energy_retention"], errors="coerce").quantile(0.05)),
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


def write_report(outdir: Path, summary: pd.DataFrame, results: pd.DataFrame) -> None:
    display = summary.sort_values(["dataset", "priority_group", "candidate"]).copy()
    unstable = results[results["window_unstable"].astype(bool)].copy()
    lines = [
        "# StrongMotion-QC Window Stability",
        "",
        "This audit evaluates whether candidate windows preserve full-record waveform products.",
        "",
        "The endpoints are product stability metrics: PGA retention, relative energy retention, and whether the full-record peak falls inside the candidate window. They are closer to engineering processing needs than spike-threshold classification.",
        "",
        "Catalog P windows are included only as an evaluation comparator when catalog P is present.",
        "",
        "## Summary",
        "",
        markdown_table(display),
        "",
        "## Outputs",
        "",
        "- `window_stability.csv`: per-record candidate-window product retention.",
        "- `summary.csv`: grouped instability and retention metrics.",
        "",
        "## Interpretation",
        "",
        "A failed window indicates a product-level issue, not a manual QC label. The next model objective should predict or reduce these failures directly.",
    ]
    if len(unstable):
        top = (
            unstable.groupby(["candidate", "failure_reason"], dropna=False)
            .size()
            .reset_index(name="records")
            .sort_values("records", ascending=False)
            .head(12)
        )
        lines.extend(["", "## Common Failure Reasons", "", markdown_table(top)])
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def run_window_stability(
    features: pd.DataFrame,
    outdir: Path,
    knet_waveforms: Path = Path(DEFAULT_KNET_WAVEFORMS),
    knet_highpass_hz: float | None = None,
    max_records: int | None = None,
    per_group: int | None = None,
    seed: int = 42,
    pre_sec: float = 2.0,
    fixed_after_sec: float = 40.0,
    adaptive_post_sec: float = 3.0,
    pga_retention_threshold: float = 0.99,
    energy_retention_threshold: float = 0.95,
) -> dict[str, Path]:
    work = features.copy()
    if "waveform_qc_status" in work:
        work = work[work["waveform_qc_status"].eq("ok")].copy()
    if per_group is not None:
        sampled = []
        for _, group in work.groupby(["dataset", "priority_group"], dropna=False):
            if len(group) > per_group:
                sampled.append(group.sample(n=per_group, random_state=seed))
            else:
                sampled.append(group)
        work = pd.concat(sampled, ignore_index=True) if sampled else work.iloc[0:0].copy()
    elif max_records is not None:
        work = work.head(max_records).copy()
    rows = []
    instance_data, h5, keys, pnw_data = load_waveforms_for_rows(work, knet_waveforms)
    try:
        for _, row in tqdm(work.iterrows(), total=len(work), desc="Evaluate windows"):
            try:
                if row["dataset"] == "InstanceGM":
                    waveform, _ = load_instance_waveform(instance_data, row)
                elif row["dataset"] == "PNWAccelerometers":
                    waveform, _ = load_pnw_waveform(pnw_data, row)
                elif row["dataset"] == "K-NET":
                    if h5 is None or keys is None:
                        raise ValueError("K-NET HDF5 handle is unavailable")
                    waveform, _ = load_knet_waveform(h5, keys, row)
                    waveform = highpass_waveform(
                        waveform,
                        sampling_rate=float(row["sampling_rate_hz"]),
                        corner_hz=knet_highpass_hz,
                    )
                else:
                    raise ValueError(f"unsupported dataset: {row['dataset']}")
                rows.extend(
                    evaluate_record(
                        row,
                        waveform,
                        pre_sec=pre_sec,
                        fixed_after_sec=fixed_after_sec,
                        adaptive_post_sec=adaptive_post_sec,
                        pga_retention_threshold=pga_retention_threshold,
                        energy_retention_threshold=energy_retention_threshold,
                    )
                )
            except Exception as exc:
                rows.append(
                    {
                        "record_uid": row.get("record_uid", ""),
                        "dataset": row.get("dataset", ""),
                        "priority_group": row.get("priority_group", ""),
                        "candidate": "load_error",
                        "window_unstable": True,
                        "failure_reason": f"load_error:{exc}",
                    }
                )
    finally:
        if h5 is not None:
            h5.close()

    results = pd.DataFrame(rows)
    summary = summarize(results[results["candidate"].ne("load_error")].copy())
    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "results": outdir / "window_stability.csv",
        "summary": outdir / "summary.csv",
        "report": outdir / "README.md",
    }
    results.to_csv(outputs["results"], index=False)
    summary.to_csv(outputs["summary"], index=False)
    write_report(outdir, summary, results)
    return outputs


def main() -> None:
    args = parse_args()
    features = pd.read_csv(args.features, low_memory=False)
    outputs = run_window_stability(
        features=features,
        outdir=Path(args.outdir),
        knet_waveforms=Path(args.knet_waveforms),
        knet_highpass_hz=args.knet_highpass_hz,
        max_records=args.max_records,
        per_group=args.per_group,
        seed=args.seed,
        pre_sec=args.pre_sec,
        fixed_after_sec=args.fixed_after_sec,
        adaptive_post_sec=args.adaptive_post_sec,
        pga_retention_threshold=args.pga_retention_threshold,
        energy_retention_threshold=args.energy_retention_threshold,
    )
    for path in outputs.values():
        print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
