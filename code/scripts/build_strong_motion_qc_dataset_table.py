#!/usr/bin/env python3
"""Build compact dataset-description tables for the StrongMotion-QC SRL route."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_FEATURES = "outputs/strong_motion_qc_waveform_features/waveform_features.csv"
DEFAULT_OUTDIR = "outputs/strong_motion_qc_dataset_table"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default=DEFAULT_FEATURES)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    return parser.parse_args()


def to_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin(["true", "1", "yes", "y"])


def summarize_dataset(features: pd.DataFrame) -> pd.DataFrame:
    rows = []
    work = features.copy()
    for column in ["sampling_rate_hz", "duration_sec", "magnitude"]:
        if column in work:
            work[column] = pd.to_numeric(work[column], errors="coerce")
    if "has_catalog_p" in work:
        work["has_catalog_p_bool"] = to_bool(work["has_catalog_p"])
    else:
        work["has_catalog_p_bool"] = False
    if "waveform_qc_status" in work:
        work["waveform_loaded_bool"] = work["waveform_qc_status"].astype(str).eq("ok")
    else:
        work["waveform_loaded_bool"] = True
    for dataset, group in work.groupby("dataset", dropna=False):
        rows.append(
            {
                "dataset": dataset,
                "records": int(len(group)),
                "events": int(group["event_id"].nunique()) if "event_id" in group else 0,
                "stations": int(group["station_code"].nunique()) if "station_code" in group else 0,
                "loaded_records": int(group["waveform_loaded_bool"].sum()),
                "catalog_p_records": int(group["has_catalog_p_bool"].sum()),
                "median_sampling_rate_hz": float(group["sampling_rate_hz"].median()),
                "median_duration_sec": float(group["duration_sec"].median()),
                "p05_duration_sec": float(group["duration_sec"].quantile(0.05)),
                "p95_duration_sec": float(group["duration_sec"].quantile(0.95)),
                "median_magnitude": float(group["magnitude"].median()) if "magnitude" in group else float("nan"),
                "min_magnitude": float(group["magnitude"].min()) if "magnitude" in group else float("nan"),
                "max_magnitude": float(group["magnitude"].max()) if "magnitude" in group else float("nan"),
            }
        )
    return pd.DataFrame(rows)


def summarize_strata(features: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, group in features.groupby(["dataset", "priority_group"], dropna=False):
        rows.append(
            {
                "dataset": keys[0],
                "priority_group": keys[1],
                "records": int(len(group)),
                "median_duration_sec": float(pd.to_numeric(group["duration_sec"], errors="coerce").median()),
                "median_magnitude": float(pd.to_numeric(group["magnitude"], errors="coerce").median())
                if "magnitude" in group
                else float("nan"),
            }
        )
    return pd.DataFrame(rows).sort_values(["dataset", "priority_group"])


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


def write_report(outdir: Path, dataset_summary: pd.DataFrame, strata_summary: pd.DataFrame) -> None:
    lines = [
        "# StrongMotion-QC Dataset Table",
        "",
        "Compact dataset description for the SRL manuscript route.",
        "",
        "## Dataset Summary",
        "",
        markdown_table(dataset_summary),
        "",
        "## Priority Strata",
        "",
        markdown_table(strata_summary),
        "",
        "## Interpretation Boundary",
        "",
        "These counts describe the waveform-feature audit set. They are not the full underlying InstanceGM or K-NET archive sizes.",
    ]
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def run_dataset_table(features: pd.DataFrame, outdir: Path) -> dict[str, Path]:
    dataset_summary = summarize_dataset(features)
    strata_summary = summarize_strata(features)
    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "dataset_summary": outdir / "dataset_summary.csv",
        "strata_summary": outdir / "priority_strata_summary.csv",
        "report": outdir / "README.md",
    }
    dataset_summary.to_csv(outputs["dataset_summary"], index=False)
    strata_summary.to_csv(outputs["strata_summary"], index=False)
    write_report(outdir, dataset_summary, strata_summary)
    return outputs


def main() -> None:
    args = parse_args()
    features = pd.read_csv(args.features, low_memory=False)
    outputs = run_dataset_table(features, Path(args.outdir))
    for path in outputs.values():
        print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
