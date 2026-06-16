#!/usr/bin/env python3
"""Build a stratified waveform-QC worklist from the full StrongMotion-QC manifest."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_MANIFEST = "outputs/strong_motion_qc_full_manifest/strong_motion_qc_full_manifest.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--outdir", default="outputs/strong_motion_qc_worklist")
    parser.add_argument("--per-stratum", type=int, default=300)
    parser.add_argument(
        "--include-all-dataset",
        action="append",
        default=[],
        help="Dataset name to include without per-stratum sampling. Can be supplied multiple times.",
    )
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def assign_priority(manifest: pd.DataFrame) -> pd.Series:
    magnitude = pd.to_numeric(manifest["magnitude"], errors="coerce")
    return pd.Series(
        np.select(
            [
                manifest["m4plus_eval_candidate"].astype(bool),
                manifest["m3_to_m4_eval_candidate"].astype(bool),
                magnitude < 3.0,
            ],
            [
                "m4plus_strong_motion",
                "m3_to_m4_small_event",
                "low_magnitude_background",
            ],
            default="other",
        ),
        index=manifest.index,
    )


def build_worklist(
    manifest: pd.DataFrame,
    per_stratum: int = 300,
    seed: int = 42,
    include_all_datasets: list[str] | None = None,
) -> pd.DataFrame:
    pool = manifest[manifest["metadata_waveform_candidate"].astype(bool)].copy()
    if pool.empty:
        raise ValueError("No metadata waveform candidates found")
    pool["priority_group"] = assign_priority(pool)
    strata = ["dataset", "split", "magnitude_bin"]
    include_all = set(include_all_datasets or [])
    sampled_parts = []
    for _, group in pool.groupby(strata, dropna=False):
        if str(group["dataset"].iloc[0]) in include_all:
            sampled_parts.append(group)
        else:
            sampled_parts.append(group.sample(n=min(per_stratum, len(group)), random_state=seed))
    sampled = pd.concat(sampled_parts, ignore_index=True)
    keep = [
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
        "waveform_access",
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
    return sampled[keep].sort_values(["dataset", "split", "magnitude_bin", "record_uid"]).reset_index(drop=True)


def summarize(worklist: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    priority_summary = (
        worklist.groupby(["dataset", "priority_group"], dropna=False)
        .size()
        .reset_index(name="records")
        .sort_values(["dataset", "priority_group"])
    )
    stratum_summary = (
        worklist.groupby(["dataset", "split", "magnitude_bin"], dropna=False)
        .size()
        .reset_index(name="records")
        .sort_values(["dataset", "split", "magnitude_bin"])
    )
    return priority_summary, stratum_summary


def write_report(outdir: Path, worklist: pd.DataFrame, priority_summary: pd.DataFrame) -> None:
    lines = [
        "# StrongMotion-QC Waveform Worklist",
        "",
        "This is a stratified waveform-loading worklist drawn from the all-magnitude metadata manifest. It is meant for the first waveform-QC and representation-learning pass.",
        "",
        "The worklist includes low-magnitude background records, M3-M4 small-event records, and M4+ strong-motion records. Catalog P fields remain evaluation-only columns.",
        "",
        "## Counts",
        "",
        f"- Worklist records: {len(worklist)}",
        f"- Datasets: {', '.join(sorted(worklist['dataset'].unique()))}",
        "",
        "## Priority Summary",
        "",
        markdown_table(priority_summary),
        "",
        "## Next Step",
        "",
        "Load waveform records from this worklist, compute label-free onset/QC features, then train the first compact self-supervised encoder on records that pass waveform QC.",
    ]
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def markdown_table(df: pd.DataFrame) -> str:
    columns = list(df.columns)
    rows = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in df.iterrows():
        rows.append("| " + " | ".join(str(row[col]) for col in columns) + " |")
    return "\n".join(rows)


def build_from_manifest(
    manifest_path: Path,
    outdir: Path,
    per_stratum: int = 300,
    seed: int = 42,
    include_all_datasets: list[str] | None = None,
) -> dict[str, Path]:
    manifest = pd.read_csv(manifest_path, low_memory=False)
    worklist = build_worklist(
        manifest,
        per_stratum=per_stratum,
        seed=seed,
        include_all_datasets=include_all_datasets,
    )
    priority_summary, stratum_summary = summarize(worklist)
    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "worklist": outdir / "waveform_qc_worklist.csv",
        "priority_summary": outdir / "priority_summary.csv",
        "stratum_summary": outdir / "stratum_summary.csv",
        "report": outdir / "README.md",
    }
    worklist.to_csv(outputs["worklist"], index=False)
    priority_summary.to_csv(outputs["priority_summary"], index=False)
    stratum_summary.to_csv(outputs["stratum_summary"], index=False)
    write_report(outdir, worklist, priority_summary)
    return outputs


def main() -> None:
    args = parse_args()
    outputs = build_from_manifest(
        manifest_path=Path(args.manifest),
        outdir=Path(args.outdir),
        per_stratum=args.per_stratum,
        seed=args.seed,
        include_all_datasets=args.include_all_dataset,
    )
    for path in outputs.values():
        print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
