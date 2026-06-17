#!/usr/bin/env python3
"""Compute label-free waveform QC/onset features for a StrongMotion-QC worklist."""

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
except ImportError:  # pragma: no cover - convenience for minimal envs

    def tqdm(iterable, **kwargs):
        return iterable

from strong_motion_qc.features import compute_strong_motion_features


DEFAULT_WORKLIST = "outputs/strong_motion_qc_worklist/waveform_qc_worklist.csv"
DEFAULT_KNET_WAVEFORMS = "data/knet_accel/waveforms.hdf5"
METADATA_KEEP_COLUMNS = [
    "record_uid",
    "dataset",
    "source_row_index",
    "split",
    "priority_group",
    "magnitude_bin",
    "magnitude",
    "event_id",
    "station_network",
    "station_code",
    "trace_name",
    "waveform_key",
    "component_order",
    "channel_type",
    "units",
    "sampling_rate_hz",
    "n_samples",
    "duration_sec",
    "has_catalog_p",
    "catalog_p_sec",
    "catalog_p_sample",
    "catalog_fields_for_evaluation_only",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worklist", default=DEFAULT_WORKLIST)
    parser.add_argument("--outdir", default="outputs/strong_motion_qc_waveform_features")
    parser.add_argument("--knet-waveforms", default=DEFAULT_KNET_WAVEFORMS)
    parser.add_argument(
        "--knet-highpass-hz",
        type=float,
        default=None,
        help="Optional high-pass corner for K-NET waveforms before feature computation.",
    )
    parser.add_argument("--max-records", type=int, default=None)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--checkpoint-every", type=int, default=500)
    return parser.parse_args()


def normalize_waveform_orientation(waveform: np.ndarray) -> np.ndarray:
    """Return waveform as 1-D or channels x samples."""

    arr = np.asarray(waveform, dtype=np.float64)
    if arr.ndim == 1:
        return arr
    if arr.ndim != 2:
        raise ValueError(f"Expected 1-D or 2-D waveform array, got shape {arr.shape}")
    if arr.shape[0] <= arr.shape[1] and arr.shape[0] <= 6:
        return arr
    if arr.shape[1] <= 6:
        return arr.T
    return arr


def standardize_channels(waveform: np.ndarray, input_channels: int = 3) -> np.ndarray:
    arr = normalize_waveform_orientation(waveform).astype(np.float32, copy=False)
    if arr.ndim == 1:
        arr = arr[None, :]
    if arr.shape[0] > input_channels:
        arr = arr[:input_channels, :]
    if arr.shape[0] < input_channels:
        pad = np.zeros((input_channels - arr.shape[0], arr.shape[1]), dtype=np.float32)
        arr = np.concatenate([arr, pad], axis=0)
    return arr


def list_hdf5_keys(h5file: h5py.File) -> list[str]:
    keys: list[str] = []

    def recurse(obj, prefix: str = "") -> None:
        for key, item in obj.items():
            full_key = f"{prefix}/{key}" if prefix else key
            if isinstance(item, h5py.Group):
                recurse(item, full_key)
            else:
                keys.append(full_key)

    recurse(h5file)
    return keys


def find_waveform_key(row: pd.Series, all_keys: set[str]) -> str | None:
    candidates = [
        str(row.get("trace_name", "")),
        str(row.get("event_name", "")),
    ]
    for value in candidates:
        if not value or value == "nan":
            continue
        direct = value
        data_key = f"data/{value}"
        if direct in all_keys:
            return direct
        if data_key in all_keys:
            return data_key
    return None


def highpass_waveform(waveform: np.ndarray, sampling_rate: float, corner_hz: float | None) -> np.ndarray:
    if corner_hz is None or corner_hz <= 0:
        return waveform
    from scipy.signal import butter, sosfiltfilt

    arr = normalize_waveform_orientation(waveform)
    nyquist = 0.5 * float(sampling_rate)
    if not np.isfinite(nyquist) or nyquist <= 0 or corner_hz >= nyquist:
        raise ValueError(f"Invalid high-pass corner {corner_hz} Hz for sampling rate {sampling_rate} Hz")
    sos = butter(4, corner_hz / nyquist, btype="highpass", output="sos")
    return sosfiltfilt(sos, arr, axis=-1)


def load_instance_waveform(instance_data, row: pd.Series) -> tuple[np.ndarray, str]:
    index = int(row["source_row_index"])
    waveforms = instance_data.get_waveforms([index])[0]
    return normalize_waveform_orientation(waveforms), f"InstanceGM:{index}"


def load_pnw_waveform(pnw_data, row: pd.Series) -> tuple[np.ndarray, str]:
    index = int(row["source_row_index"])
    waveforms = pnw_data.get_waveforms([index])[0]
    return normalize_waveform_orientation(waveforms), f"PNWAccelerometers:{index}"


def load_knet_waveform(h5file: h5py.File, all_keys: set[str], row: pd.Series) -> tuple[np.ndarray, str]:
    key = str(row.get("waveform_key", "") or row.get("trace_name", "") or "")
    normalized = key.lstrip("/")
    candidates = []
    if normalized:
        candidates.extend(
            [
                normalized,
                f"data/{normalized}",
                f"waveforms/{normalized}",
            ]
        )
        if normalized.startswith(("data/", "waveforms/")):
            leaf = normalized.split("/", 1)[1]
            candidates.extend([leaf, f"data/{leaf}", f"waveforms/{leaf}"])
    waveform_key = next((candidate for candidate in candidates if candidate in all_keys), None)
    if waveform_key is None:
        lookup_row = pd.Series(
            {
                "trace_name": row.get("trace_name", ""),
                "event_name": row.get("event_id", ""),
            }
        )
        waveform_key = find_waveform_key(lookup_row, all_keys)
    if waveform_key is None:
        raise KeyError(f"missing K-NET waveform key for {row.get('record_uid', '')}")
    return normalize_waveform_orientation(h5file[waveform_key][:]), waveform_key


def metadata_fields(row: pd.Series) -> dict[str, object]:
    return {col: row[col] if col in row else "" for col in METADATA_KEEP_COLUMNS}


def feature_fields(features: dict[str, object]) -> dict[str, object]:
    return {f"feature_{key}": value for key, value in features.items()}


def compute_row(
    row: pd.Series,
    instance_data=None,
    pnw_data=None,
    knet_h5=None,
    knet_keys: set[str] | None = None,
    knet_highpass_hz: float | None = None,
) -> dict[str, object]:
    result = metadata_fields(row)
    dataset = str(row.get("dataset", ""))
    try:
        sampling_rate = float(row["sampling_rate_hz"])
        if dataset == "InstanceGM":
            waveform, resolved_key = load_instance_waveform(instance_data, row)
        elif dataset == "PNWAccelerometers":
            waveform, resolved_key = load_pnw_waveform(pnw_data, row)
        elif dataset == "K-NET":
            if knet_h5 is None or knet_keys is None:
                raise ValueError("K-NET HDF5 handle is not available")
            waveform, resolved_key = load_knet_waveform(knet_h5, knet_keys, row)
            waveform = highpass_waveform(waveform, sampling_rate=sampling_rate, corner_hz=knet_highpass_hz)
        else:
            raise ValueError(f"Unsupported dataset: {dataset}")

        features = compute_strong_motion_features(waveform, sampling_rate=sampling_rate)
        result.update(
            {
                "waveform_qc_status": "ok",
                "waveform_error": "",
                "resolved_waveform_key": resolved_key,
                "waveform_shape": "x".join(str(v) for v in np.asarray(waveform).shape),
                "waveform_preprocess": f"knet_highpass_{knet_highpass_hz:g}hz" if dataset == "K-NET" and knet_highpass_hz else "",
            }
        )
        result.update(feature_fields(features))
    except Exception as exc:  # keep failed records visible in the output
        result.update(
            {
                "waveform_qc_status": "error",
                "waveform_error": str(exc),
                "resolved_waveform_key": "",
                "waveform_shape": "",
            }
        )
    return result


def progress_path_for(output: Path) -> Path:
    return output.with_name(output.stem + "_progress.csv")


def write_outputs(rows: list[dict[str, object]], output: Path, summary: pd.DataFrame | None = None) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)
    if summary is not None:
        summary.to_csv(output.with_name("summary.csv"), index=False)


def summarize(features: pd.DataFrame) -> pd.DataFrame:
    if features.empty:
        return pd.DataFrame()
    rows = []
    for (dataset, priority), group in features.groupby(["dataset", "priority_group"], dropna=False):
        ok = group["waveform_qc_status"] == "ok"
        rows.append(summary_row(dataset, priority, group))
    rows.append(summary_row("ALL", "ALL", features))
    return pd.DataFrame(rows)


def summary_row(dataset: str, priority: str, group: pd.DataFrame) -> dict[str, object]:
    ok = group["waveform_qc_status"] == "ok"
    return {
        "dataset": dataset,
        "priority_group": priority,
        "records": len(group),
        "loaded_records": int(ok.sum()),
        "load_success_pct": 100.0 * float(ok.mean()) if len(group) else 0.0,
        "median_onset_sec": median_ok(group, ok, "feature_onset_sec"),
        "median_significant_duration_sec": median_ok(group, ok, "feature_significant_duration_sec"),
        "median_spike_score": median_ok(group, ok, "feature_spike_score"),
        "qc_issue_records": count_positive_ok(group, ok, "feature_qc_issue_count"),
    }


def median_ok(group: pd.DataFrame, ok: pd.Series, column: str) -> float:
    if not ok.any() or column not in group:
        return float("nan")
    return float(pd.to_numeric(group.loc[ok, column], errors="coerce").median())


def count_positive_ok(group: pd.DataFrame, ok: pd.Series, column: str) -> int:
    if not ok.any() or column not in group:
        return 0
    return int((pd.to_numeric(group.loc[ok, column], errors="coerce") > 0).sum())


def markdown_table(df: pd.DataFrame) -> str:
    columns = list(df.columns)
    rows = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in df.iterrows():
        values = []
        for col in columns:
            value = row[col]
            if isinstance(value, float):
                values.append(f"{value:.2f}")
            else:
                values.append(str(value))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def write_report(outdir: Path, features: pd.DataFrame, summary: pd.DataFrame) -> None:
    lines = [
        "# StrongMotion-QC Waveform Features",
        "",
        "This table contains label-free onset and QC features computed from the stratified waveform worklist.",
        "",
        "Catalog P fields remain evaluation-only columns. The feature columns are derived from waveform samples and do not use catalog P/S as training targets.",
        "",
        "## Summary",
        "",
        markdown_table(summary),
        "",
        "## Outputs",
        "",
        "- `waveform_features.csv`: per-record waveform features and load status.",
        "- `summary.csv`: grouped feature/load summary.",
        "",
        "## Next Step",
        "",
        "Use loaded records with acceptable waveform-QC flags to build the first self-supervised training shard, then evaluate onset behavior by dataset, magnitude group, and split.",
    ]
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def compute_features(
    worklist: pd.DataFrame,
    output: Path,
    knet_waveforms: Path = Path(DEFAULT_KNET_WAVEFORMS),
    knet_highpass_hz: float | None = None,
    max_records: int | None = None,
    resume: bool = False,
    checkpoint_every: int = 500,
) -> dict[str, Path]:
    if max_records is not None:
        worklist = worklist.head(max_records).copy()
    outdir = output.parent
    progress_path = progress_path_for(output)
    rows: list[dict[str, object]] = []
    done: set[str] = set()
    if resume and progress_path.exists():
        previous = pd.read_csv(progress_path, low_memory=False)
        rows = previous.to_dict("records")
        done = set(previous["record_uid"].astype(str))

    pending = worklist[~worklist["record_uid"].astype(str).isin(done)].copy()
    instance_data = None
    if (pending["dataset"] == "InstanceGM").any():
        import seisbench.data as sbd

        instance_data = sbd.InstanceGM()
    pnw_data = None
    if (pending["dataset"] == "PNWAccelerometers").any():
        import seisbench.data as sbd

        pnw_data = sbd.PNWAccelerometers()

    h5 = None
    knet_keys = None
    try:
        if (pending["dataset"] == "K-NET").any():
            h5 = h5py.File(knet_waveforms, "r")
            knet_keys = set(list_hdf5_keys(h5))
        for _, row in tqdm(pending.iterrows(), total=len(pending), desc="Waveform QC"):
            rows.append(
                compute_row(
                    row,
                    instance_data=instance_data,
                    pnw_data=pnw_data,
                    knet_h5=h5,
                    knet_keys=knet_keys,
                    knet_highpass_hz=knet_highpass_hz,
                )
            )
            if checkpoint_every > 0 and len(rows) % checkpoint_every == 0:
                write_outputs(rows, progress_path)
    finally:
        if h5 is not None:
            h5.close()

    features = pd.DataFrame(rows)
    summary = summarize(features)
    output.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output, index=False)
    features.to_csv(progress_path, index=False)
    summary.to_csv(outdir / "summary.csv", index=False)
    write_report(outdir, features, summary)
    return {
        "features": output,
        "summary": outdir / "summary.csv",
        "report": outdir / "README.md",
        "progress": progress_path,
    }


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    worklist = pd.read_csv(args.worklist, low_memory=False)
    outputs = compute_features(
        worklist=worklist,
        output=outdir / "waveform_features.csv",
        knet_waveforms=Path(args.knet_waveforms),
        knet_highpass_hz=args.knet_highpass_hz,
        max_records=args.max_records,
        resume=args.resume,
        checkpoint_every=args.checkpoint_every,
    )
    for path in outputs.values():
        print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
