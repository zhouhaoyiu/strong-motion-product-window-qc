#!/usr/bin/env python3
"""Evaluate sensitivity of product-stable selector to retention thresholds."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_STABILITY = "outputs/strong_motion_qc_window_stability_full/window_stability.csv"
DEFAULT_OUTDIR = "outputs/strong_motion_qc_selector_sensitivity"
NO_CATALOG_CANDIDATES = ["feature_onset_fixed", "energy_onset_fixed", "feature_onset_to_energy_end"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window-stability", default=DEFAULT_STABILITY)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    parser.add_argument("--pga-thresholds", default="0.99,0.995")
    parser.add_argument("--energy-thresholds", default="0.90,0.95,0.98")
    return parser.parse_args()


def parse_thresholds(text: str) -> list[float]:
    values = [float(item.strip()) for item in text.split(",") if item.strip()]
    if not values:
        raise ValueError("at least one threshold is required")
    return values


def to_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin(["true", "1", "yes", "y"])


def prepare(stability: pd.DataFrame) -> pd.DataFrame:
    required = {
        "record_uid",
        "dataset",
        "priority_group",
        "candidate",
        "pga_retention",
        "energy_retention",
        "peak_inside_window",
        "window_duration_sec",
    }
    missing = required - set(stability.columns)
    if missing:
        raise ValueError(f"window stability table missing columns: {sorted(missing)}")
    work = stability[stability["candidate"].ne("load_error")].copy()
    work["pga_retention"] = pd.to_numeric(work["pga_retention"], errors="coerce")
    work["energy_retention"] = pd.to_numeric(work["energy_retention"], errors="coerce")
    work["window_duration_sec"] = pd.to_numeric(work["window_duration_sec"], errors="coerce")
    work["peak_inside_bool"] = to_bool(work["peak_inside_window"])
    return work


def stable_mask(group: pd.DataFrame, pga_threshold: float, energy_threshold: float) -> pd.Series:
    return (
        group["peak_inside_bool"]
        & group["pga_retention"].ge(pga_threshold)
        & group["energy_retention"].ge(energy_threshold)
    )


def choose_record(group: pd.DataFrame, pga_threshold: float, energy_threshold: float) -> pd.Series:
    candidates = group[group["candidate"].isin(NO_CATALOG_CANDIDATES)].copy()
    candidates = candidates[stable_mask(candidates, pga_threshold, energy_threshold)].copy()
    if not candidates.empty:
        return candidates.sort_values(["window_duration_sec", "candidate"], kind="mergesort").iloc[0]
    full = group[group["candidate"].eq("full_record")]
    if full.empty:
        return group.iloc[0]
    row = full.iloc[0].copy()
    row["selection_status"] = "full_record_fallback"
    return row


def selected_for_threshold(stability: pd.DataFrame, pga_threshold: float, energy_threshold: float) -> pd.DataFrame:
    rows = []
    for _, group in stability.groupby("record_uid", sort=False):
        chosen = choose_record(group, pga_threshold, energy_threshold).to_dict()
        if "selection_status" not in chosen or pd.isna(chosen.get("selection_status")):
            chosen["selection_status"] = "stable_candidate"
        chosen["pga_threshold"] = pga_threshold
        chosen["energy_threshold"] = energy_threshold
        chosen["selected_candidate"] = chosen.get("candidate", "")
        chosen["selected_stable"] = (
            bool(chosen.get("peak_inside_bool", False))
            and float(chosen.get("pga_retention", np.nan)) >= pga_threshold
            and float(chosen.get("energy_retention", np.nan)) >= energy_threshold
        )
        rows.append(chosen)
    return pd.DataFrame(rows)


def evaluate_sensitivity(stability: pd.DataFrame, pga_thresholds: list[float], energy_thresholds: list[float]) -> tuple[pd.DataFrame, pd.DataFrame]:
    work = prepare(stability)
    selected_frames = []
    for pga_threshold in pga_thresholds:
        for energy_threshold in energy_thresholds:
            selected_frames.append(selected_for_threshold(work, pga_threshold, energy_threshold))
    selected = pd.concat(selected_frames, ignore_index=True) if selected_frames else pd.DataFrame()
    summary = summarize(selected)
    return selected, summary


def summarize(selected: pd.DataFrame) -> pd.DataFrame:
    rows = []
    group_cols = ["dataset", "priority_group", "pga_threshold", "energy_threshold"]
    for keys, group in selected.groupby(group_cols, dropna=False):
        rows.append(summary_row(keys[0], keys[1], keys[2], keys[3], group))
    for keys, group in selected.groupby(["dataset", "pga_threshold", "energy_threshold"], dropna=False):
        rows.append(summary_row(keys[0], "ALL", keys[1], keys[2], group))
    for keys, group in selected.groupby(["pga_threshold", "energy_threshold"], dropna=False):
        rows.append(summary_row("ALL", "ALL", keys[0], keys[1], group))
    return pd.DataFrame(rows)


def summary_row(dataset: str, priority_group: str, pga_threshold: float, energy_threshold: float, group: pd.DataFrame) -> dict[str, object]:
    full_fallback = group["selection_status"].astype(str).eq("full_record_fallback")
    selected_stable = to_bool(group["selected_stable"])
    duration = pd.to_numeric(group["window_duration_sec"], errors="coerce")
    return {
        "dataset": dataset,
        "priority_group": priority_group,
        "pga_threshold": float(pga_threshold),
        "energy_threshold": float(energy_threshold),
        "records": int(len(group)),
        "selected_stable_pct": 100.0 * float(selected_stable.mean()) if len(group) else 0.0,
        "full_record_fallback_records": int(full_fallback.sum()),
        "full_record_fallback_pct": 100.0 * float(full_fallback.mean()) if len(group) else 0.0,
        "median_window_duration_sec": float(duration.median()),
        "p75_window_duration_sec": float(duration.quantile(0.75)),
        "p95_window_duration_sec": float(duration.quantile(0.95)),
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


def write_report(outdir: Path, summary: pd.DataFrame) -> None:
    display = summary[summary["priority_group"].eq("ALL")].sort_values(
        ["dataset", "pga_threshold", "energy_threshold"]
    )
    lines = [
        "# StrongMotion-QC Selector Sensitivity",
        "",
        "This report recomputes shortest-stable no-catalog selection under alternative PGA and energy-retention thresholds.",
        "",
        "## Dataset-Level Summary",
        "",
        markdown_table(display),
        "",
        "## Interpretation Boundary",
        "",
        "The selected windows are stable by the tested product-retention criteria because the selector falls back to the full record when no non-full candidate passes. The sensitivity result should be interpreted through fallback rate and selected duration, not through stable percentage alone.",
    ]
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def run_sensitivity(
    stability: pd.DataFrame,
    outdir: Path,
    pga_thresholds: list[float],
    energy_thresholds: list[float],
) -> dict[str, Path]:
    selected, summary = evaluate_sensitivity(stability, pga_thresholds, energy_thresholds)
    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "selected_windows": outdir / "selected_windows_by_threshold.csv",
        "summary": outdir / "sensitivity_summary.csv",
        "report": outdir / "README.md",
    }
    selected.to_csv(outputs["selected_windows"], index=False)
    summary.to_csv(outputs["summary"], index=False)
    write_report(outdir, summary)
    return outputs


def main() -> None:
    args = parse_args()
    stability = pd.read_csv(args.window_stability, low_memory=False)
    outputs = run_sensitivity(
        stability,
        Path(args.outdir),
        pga_thresholds=parse_thresholds(args.pga_thresholds),
        energy_thresholds=parse_thresholds(args.energy_thresholds),
    )
    for path in outputs.values():
        print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
