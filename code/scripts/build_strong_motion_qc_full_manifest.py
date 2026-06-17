#!/usr/bin/env python3
"""Build a metadata-only all-magnitude manifest for StrongMotion-QC."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


DEFAULT_KNET_METADATA = Path("data/knet_accel/metadata.csv")
MAGNITUDE_BINS = [-np.inf, 3.0, 4.0, 4.5, 5.0, 5.5, 6.0, np.inf]
MAGNITUDE_LABELS = ["<3", "3-4", "4-4.5", "4.5-5", "5-5.5", "5.5-6", ">=6"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", default="outputs/strong_motion_qc_full_manifest")
    parser.add_argument("--knet-metadata", default=str(DEFAULT_KNET_METADATA))
    parser.add_argument("--min-duration-sec", type=float, default=20.0)
    parser.add_argument("--skip-instance", action="store_true")
    parser.add_argument("--skip-knet", action="store_true")
    parser.add_argument("--include-pnw", action="store_true")
    return parser.parse_args()


def to_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def first_existing(df: pd.DataFrame, columns: Iterable[str], default: object = "") -> pd.Series:
    for col in columns:
        if col in df.columns:
            return df[col]
    return pd.Series([default] * len(df), index=df.index)


def numeric_first(df: pd.DataFrame, columns: Iterable[str]) -> pd.Series:
    return to_numeric(first_existing(df, columns, np.nan))


def strip_hdf5_prefix(series: pd.Series) -> pd.Series:
    return series.astype(str).str.replace(r"^/", "", regex=True)


def npts_from_trace_name(series: pd.Series) -> pd.Series:
    return to_numeric(series.astype(str).str.extract(r":(\d+)$", expand=False))


def valid_catalog_sample(sample: pd.Series, sampling_rate: pd.Series, n_samples: pd.Series) -> pd.Series:
    return sample.notna() & sampling_rate.notna() & n_samples.notna() & (sampling_rate > 0) & (sample >= 0) & (sample < n_samples)


def duration_from_metadata(n_samples: pd.Series, sampling_rate: pd.Series) -> pd.Series:
    return (n_samples / sampling_rate).where((sampling_rate > 0) & n_samples.notna())


def add_pool_columns(manifest: pd.DataFrame, min_duration_sec: float) -> pd.DataFrame:
    manifest = manifest.copy()
    manifest["magnitude_bin"] = pd.cut(
        manifest["magnitude"],
        bins=MAGNITUDE_BINS,
        labels=MAGNITUDE_LABELS,
        right=False,
    ).astype(str)
    manifest.loc[manifest["magnitude"].isna(), "magnitude_bin"] = "unknown"
    manifest["metadata_waveform_candidate"] = (
        manifest["sampling_rate_hz"].notna()
        & manifest["n_samples"].notna()
        & (manifest["sampling_rate_hz"] > 0)
        & (manifest["duration_sec"] >= min_duration_sec)
    )
    manifest["catalog_p_eval_candidate"] = manifest["metadata_waveform_candidate"] & manifest["has_catalog_p"]
    manifest["catalog_s_eval_candidate"] = manifest["metadata_waveform_candidate"] & manifest["has_catalog_s"]
    manifest["m4plus_eval_candidate"] = manifest["catalog_p_eval_candidate"] & (manifest["magnitude"] >= 4.0)
    manifest["m3_to_m4_eval_candidate"] = (
        manifest["catalog_p_eval_candidate"] & (manifest["magnitude"] >= 3.0) & (manifest["magnitude"] < 4.0)
    )
    manifest["self_supervised_pool_stage"] = np.where(
        manifest["metadata_waveform_candidate"],
        "metadata_candidate_pending_waveform_qc",
        "metadata_reject",
    )
    manifest["waveform_qc_status"] = "pending_waveform_qc"
    manifest["catalog_fields_for_evaluation_only"] = "catalog_p_sec,catalog_s_sec,catalog_p_sample,catalog_s_sample"
    return manifest


def normalize_instance_metadata(metadata: pd.DataFrame, min_duration_sec: float = 20.0) -> pd.DataFrame:
    md = metadata.copy()
    source_index = pd.Series(md.index, index=md.index)
    sampling_rate = numeric_first(md, ["trace_sampling_rate_hz"])
    n_samples = numeric_first(md, ["trace_npts"])
    duration = duration_from_metadata(n_samples, sampling_rate)
    p_sample = numeric_first(md, ["trace_P_arrival_sample", "trace_p_arrival_sample"])
    s_sample = numeric_first(md, ["trace_S_arrival_sample", "trace_s_arrival_sample"])
    has_p = valid_catalog_sample(p_sample, sampling_rate, n_samples)
    has_s = valid_catalog_sample(s_sample, sampling_rate, n_samples)
    event_id = first_existing(md, ["source_id"], "")
    station_code = first_existing(md, ["station_code"], "")

    manifest = pd.DataFrame(
        {
            "record_uid": [f"InstanceGM:{idx}" for idx in source_index.astype(str)],
            "dataset": "InstanceGM",
            "source_row_index": source_index,
            "source_manifest": "SeisBench InstanceGM metadata",
            "waveform_access": "seisbench.data.InstanceGM",
            "event_id": event_id,
            "station_network": first_existing(md, ["station_network_code"], ""),
            "station_code": station_code,
            "trace_name": "",
            "waveform_key": "",
            "split": first_existing(md, ["split"], ""),
            "component_order": first_existing(md, ["trace_component_order"], ""),
            "channel_type": first_existing(md, ["station_channels"], ""),
            "units": first_existing(md, ["trace_deconvolved_units"], ""),
            "magnitude": numeric_first(md, ["source_magnitude"]),
            "depth_km": numeric_first(md, ["source_depth_km"]),
            "distance_km": numeric_first(md, ["path_ep_distance_km", "path_hyp_distance_km"]),
            "sampling_rate_hz": sampling_rate,
            "n_samples": n_samples,
            "duration_sec": duration,
            "has_catalog_p": has_p,
            "has_catalog_s": has_s,
            "catalog_p_sample": p_sample,
            "catalog_s_sample": s_sample,
            "catalog_p_sec": (p_sample / sampling_rate).where(has_p),
            "catalog_s_sec": (s_sample / sampling_rate).where(has_s),
        }
    )
    return add_pool_columns(manifest, min_duration_sec=min_duration_sec)


def normalize_knet_metadata(
    metadata: pd.DataFrame,
    min_duration_sec: float = 20.0,
    source_manifest: str = str(DEFAULT_KNET_METADATA),
) -> pd.DataFrame:
    md = metadata.copy()
    source_index = pd.Series(md.index, index=md.index)
    sampling_rate = numeric_first(md, ["trace_sampling_rate_hz", "sampling_rate_hz"])
    n_samples = numeric_first(md, ["trace_npts", "n_samples"])
    duration = duration_from_metadata(n_samples, sampling_rate)
    p_sample = numeric_first(md, ["trace_p_arrival_sample", "trace_P_arrival_sample", "p_pick_sample"])
    s_sample = numeric_first(md, ["trace_s_arrival_sample", "trace_S_arrival_sample", "s_pick_sample"])
    has_p = valid_catalog_sample(p_sample, sampling_rate, n_samples)
    has_s = valid_catalog_sample(s_sample, sampling_rate, n_samples)
    trace_name = first_existing(md, ["trace_name", "record_id"], "")
    waveform_key = first_existing(md, ["hdf5_key", "trace_name", "record_id"], "")
    waveform_key = strip_hdf5_prefix(waveform_key)

    manifest = pd.DataFrame(
        {
            "record_uid": [f"K-NET:{idx}" for idx in source_index.astype(str)],
            "dataset": "K-NET",
            "source_row_index": source_index,
            "source_manifest": source_manifest,
            "waveform_access": "converted HDF5 metadata",
            "event_id": first_existing(md, ["event_name", "event_id"], ""),
            "station_network": "",
            "station_code": first_existing(md, ["station_code"], ""),
            "trace_name": trace_name,
            "waveform_key": waveform_key,
            "split": first_existing(md, ["split"], ""),
            "component_order": first_existing(md, ["trace_channel", "component_order"], ""),
            "channel_type": first_existing(md, ["trace_channel", "component_order"], ""),
            "units": first_existing(md, ["preprocess_method"], ""),
            "magnitude": numeric_first(md, ["source_magnitude", "magnitude"]),
            "depth_km": numeric_first(md, ["source_depth_km"]),
            "distance_km": numeric_first(md, ["source_distance_km"]),
            "sampling_rate_hz": sampling_rate,
            "n_samples": n_samples,
            "duration_sec": duration,
            "has_catalog_p": has_p,
            "has_catalog_s": has_s,
            "catalog_p_sample": p_sample,
            "catalog_s_sample": s_sample,
            "catalog_p_sec": (p_sample / sampling_rate).where(has_p),
            "catalog_s_sec": (s_sample / sampling_rate).where(has_s),
        }
    )
    return add_pool_columns(manifest, min_duration_sec=min_duration_sec)


def normalize_pnw_metadata(metadata: pd.DataFrame, min_duration_sec: float = 20.0) -> pd.DataFrame:
    md = metadata.copy()
    source_index = pd.Series(md.index, index=md.index)
    sampling_rate = numeric_first(md, ["trace_sampling_rate_hz"])
    n_samples = numeric_first(md, ["trace_npts"])
    if n_samples.isna().all():
        n_samples = npts_from_trace_name(first_existing(md, ["trace_name"], ""))
    duration = duration_from_metadata(n_samples, sampling_rate)
    p_sample = numeric_first(md, ["trace_P_arrival_sample", "trace_p_arrival_sample"])
    s_sample = numeric_first(md, ["trace_S_arrival_sample", "trace_s_arrival_sample"])
    has_p = valid_catalog_sample(p_sample, sampling_rate, n_samples)
    has_s = valid_catalog_sample(s_sample, sampling_rate, n_samples)

    manifest = pd.DataFrame(
        {
            "record_uid": [f"PNWAccelerometers:{idx}" for idx in source_index.astype(str)],
            "dataset": "PNWAccelerometers",
            "source_row_index": source_index,
            "source_manifest": "SeisBench PNWAccelerometers metadata",
            "waveform_access": "seisbench.data.PNWAccelerometers",
            "event_id": first_existing(md, ["event_id"], ""),
            "station_network": first_existing(md, ["station_network_code"], ""),
            "station_code": first_existing(md, ["station_code"], ""),
            "trace_name": first_existing(md, ["trace_name"], ""),
            "waveform_key": first_existing(md, ["trace_name"], ""),
            "split": first_existing(md, ["split"], ""),
            "component_order": first_existing(md, ["trace_component_order"], ""),
            "channel_type": first_existing(md, ["station_channel_code"], ""),
            "units": "accelerometer",
            "magnitude": numeric_first(md, ["preferred_source_magnitude", "source_local_magnitude", "source_duration_magnitude"]),
            "depth_km": numeric_first(md, ["source_depth_km"]),
            "distance_km": numeric_first(md, ["path_ep_distance_km", "source_distance_km"]),
            "sampling_rate_hz": sampling_rate,
            "n_samples": n_samples,
            "duration_sec": duration,
            "has_catalog_p": has_p,
            "has_catalog_s": has_s,
            "catalog_p_sample": p_sample,
            "catalog_s_sample": s_sample,
            "catalog_p_sec": (p_sample / sampling_rate).where(has_p),
            "catalog_s_sec": (s_sample / sampling_rate).where(has_s),
        }
    )
    return add_pool_columns(manifest, min_duration_sec=min_duration_sec)


def dataset_summary(manifest: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for dataset, group in manifest.groupby("dataset", dropna=False):
        rows.append(summary_row(dataset, group))
    rows.append(summary_row("ALL", manifest))
    return pd.DataFrame(rows)


def summary_row(dataset: str, group: pd.DataFrame) -> dict[str, object]:
    return {
        "dataset": dataset,
        "records": len(group),
        "metadata_waveform_candidates": int(group["metadata_waveform_candidate"].sum()),
        "catalog_p_eval_candidates": int(group["catalog_p_eval_candidate"].sum()),
        "catalog_s_eval_candidates": int(group["catalog_s_eval_candidate"].sum()),
        "m3_to_m4_eval_candidates": int(group["m3_to_m4_eval_candidate"].sum()),
        "m4plus_eval_candidates": int(group["m4plus_eval_candidate"].sum()),
        "median_magnitude": float(group["magnitude"].median()),
        "median_duration_sec": float(group["duration_sec"].median()),
    }


def magnitude_summary(manifest: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (dataset, magnitude_bin), group in manifest.groupby(["dataset", "magnitude_bin"], dropna=False):
        rows.append(
            {
                "dataset": dataset,
                "magnitude_bin": magnitude_bin,
                "records": len(group),
                "metadata_waveform_candidates": int(group["metadata_waveform_candidate"].sum()),
                "catalog_p_eval_candidates": int(group["catalog_p_eval_candidate"].sum()),
            }
        )
    return pd.DataFrame(rows).sort_values(["dataset", "magnitude_bin"])


def split_summary(manifest: pd.DataFrame) -> pd.DataFrame:
    counts = manifest.groupby(["dataset", "split"], dropna=False).size().reset_index(name="records")
    return counts.sort_values(["dataset", "split"])


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


def write_report(outdir: Path, manifest: pd.DataFrame, summary: pd.DataFrame, mag_summary: pd.DataFrame) -> None:
    lines = [
        "# StrongMotion-QC Full Metadata Manifest",
        "",
        "This manifest is the all-magnitude entry point for the new StrongMotion-QC project. It does not apply the old M>=4 experiment cutoff.",
        "",
        "Waveform QC is still pending. The manifest separates metadata-level waveform candidates, catalog-P evaluation candidates, M3-M4 evaluation candidates, and M4+ strong-motion evaluation candidates.",
        "",
        "Catalog P/S fields are retained for filtering and evaluation only. They are not self-supervised training targets.",
        "",
        "## Dataset Summary",
        "",
        markdown_table(summary),
        "",
        "## Magnitude Summary",
        "",
        markdown_table(mag_summary),
        "",
        "## Outputs",
        "",
        "- `strong_motion_qc_full_manifest.csv`: all-magnitude metadata manifest.",
        "- `dataset_summary.csv`: dataset-level funnel counts.",
        "- `magnitude_summary.csv`: magnitude-bin funnel counts.",
        "- `split_summary.csv`: split counts by dataset.",
        "",
        "## Interpretation",
        "",
        "Use `metadata_waveform_candidate == True` as the first broad waveform-loading pool. Use `catalog_p_eval_candidate == True` only for validation and benchmarking. Use `m4plus_eval_candidate == True` as a strong-motion test stratum, not as the full project denominator.",
    ]
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def build_from_frames(
    instance_metadata: pd.DataFrame | None,
    knet_metadata: pd.DataFrame | None,
    outdir: Path,
    min_duration_sec: float = 20.0,
    knet_source_manifest: str = str(DEFAULT_KNET_METADATA),
    pnw_metadata: pd.DataFrame | None = None,
) -> dict[str, Path]:
    frames = []
    if instance_metadata is not None:
        frames.append(normalize_instance_metadata(instance_metadata, min_duration_sec=min_duration_sec))
    if knet_metadata is not None:
        frames.append(
            normalize_knet_metadata(
                knet_metadata,
                min_duration_sec=min_duration_sec,
                source_manifest=knet_source_manifest,
            )
        )
    if pnw_metadata is not None:
        frames.append(normalize_pnw_metadata(pnw_metadata, min_duration_sec=min_duration_sec))
    if not frames:
        raise ValueError("At least one metadata frame is required")

    manifest = pd.concat(frames, ignore_index=True)
    summary = dataset_summary(manifest)
    mag_summary = magnitude_summary(manifest)
    splits = split_summary(manifest)

    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "manifest": outdir / "strong_motion_qc_full_manifest.csv",
        "summary": outdir / "dataset_summary.csv",
        "magnitude_summary": outdir / "magnitude_summary.csv",
        "split_summary": outdir / "split_summary.csv",
        "report": outdir / "README.md",
    }
    manifest.to_csv(outputs["manifest"], index=False)
    summary.to_csv(outputs["summary"], index=False)
    mag_summary.to_csv(outputs["magnitude_summary"], index=False)
    splits.to_csv(outputs["split_summary"], index=False)
    write_report(outdir, manifest, summary, mag_summary)
    return outputs


def load_instance_metadata() -> pd.DataFrame:
    import seisbench.data as sbd

    data = sbd.InstanceGM()
    return data.metadata


def load_pnw_metadata() -> pd.DataFrame:
    import seisbench.data as sbd

    data = sbd.PNWAccelerometers()
    return data.metadata


def main() -> None:
    args = parse_args()
    instance_metadata = None if args.skip_instance else load_instance_metadata()
    knet_metadata = None if args.skip_knet else pd.read_csv(args.knet_metadata)
    pnw_metadata = load_pnw_metadata() if args.include_pnw else None
    outputs = build_from_frames(
        instance_metadata=instance_metadata,
        knet_metadata=knet_metadata,
        outdir=Path(args.outdir),
        min_duration_sec=args.min_duration_sec,
        knet_source_manifest=args.knet_metadata,
        pnw_metadata=pnw_metadata,
    )
    for path in outputs.values():
        print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
