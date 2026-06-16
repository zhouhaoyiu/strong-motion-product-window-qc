#!/usr/bin/env python3
"""Quantify product impact recovered by product-stable window selection."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_STABILITY = "outputs/strong_motion_qc_window_stability_full/window_stability.csv"
DEFAULT_SELECTED = "outputs/strong_motion_qc_product_window_selector/selected_windows.csv"
DEFAULT_OUTDIR = "outputs/strong_motion_qc_product_impact"
DEFAULT_POLICY = "shortest_stable_no_catalog"
BASELINES = ["feature_onset_fixed", "energy_onset_fixed", "catalog_p_fixed", "feature_onset_to_energy_end"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window-stability", default=DEFAULT_STABILITY)
    parser.add_argument("--selected-windows", default=DEFAULT_SELECTED)
    parser.add_argument("--policy", default=DEFAULT_POLICY)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    return parser.parse_args()


def to_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin(["true", "1", "yes", "y"])


def prepare_table(df: pd.DataFrame) -> pd.DataFrame:
    work = df.copy()
    if "window_unstable" in work:
        work["window_unstable_bool"] = to_bool(work["window_unstable"])
    for column in ["energy_retention", "pga_retention", "window_duration_sec"]:
        if column in work:
            work[column] = pd.to_numeric(work[column], errors="coerce")
    return work


def failure_flag(series: pd.Series, token: str) -> pd.Series:
    return series.fillna("").astype(str).str.contains(token, regex=False)


def compare_baseline_to_selector(stability: pd.DataFrame, selected: pd.DataFrame, policy: str) -> pd.DataFrame:
    base = prepare_table(stability)
    chosen = prepare_table(selected[selected["policy"].eq(policy)].copy())
    if chosen.empty:
        raise ValueError(f"selected windows do not include policy: {policy}")
    chosen = chosen.set_index("record_uid", drop=False)
    rows = []
    for candidate in BASELINES:
        cand = base[base["candidate"].eq(candidate)].copy()
        if cand.empty:
            continue
        merged = cand.join(
            chosen[
                [
                    "record_uid",
                    "selected_candidate",
                    "selection_status",
                    "window_unstable_bool",
                    "energy_retention",
                    "pga_retention",
                    "window_duration_sec",
                ]
            ].rename(
                columns={
                    "window_unstable_bool": "selector_unstable",
                    "energy_retention": "selector_energy_retention",
                    "pga_retention": "selector_pga_retention",
                    "window_duration_sec": "selector_window_duration_sec",
                }
            ).set_index("record_uid"),
            on="record_uid",
            how="inner",
        )
        if merged.empty:
            continue
        merged["energy_gain"] = merged["selector_energy_retention"] - merged["energy_retention"]
        merged["pga_gain"] = merged["selector_pga_retention"] - merged["pga_retention"]
        merged["duration_change_sec"] = merged["selector_window_duration_sec"] - merged["window_duration_sec"]
        fixed_unstable = merged["window_unstable_bool"].astype(bool)
        selector_stable = ~merged["selector_unstable"].astype(bool)
        rescued = fixed_unstable & selector_stable
        for keys, group in merged.groupby(["dataset", "priority_group"], dropna=False):
            rows.append(summary_row(candidate, keys[0], keys[1], group, policy))
        for dataset, group in merged.groupby("dataset", dropna=False):
            rows.append(summary_row(candidate, dataset, "ALL", group, policy))
        rows.append(summary_row(candidate, "ALL", "ALL", merged, policy))
    return pd.DataFrame(rows)


def summary_row(candidate: str, dataset: str, priority_group: str, group: pd.DataFrame, policy: str) -> dict[str, object]:
    fixed_unstable = group["window_unstable_bool"].astype(bool)
    selector_unstable = group["selector_unstable"].astype(bool)
    rescued = fixed_unstable & ~selector_unstable
    failure_reason = group.get("failure_reason", pd.Series([""] * len(group), index=group.index))
    return {
        "dataset": dataset,
        "priority_group": priority_group,
        "baseline_candidate": candidate,
        "selector_policy": policy,
        "records": int(len(group)),
        "baseline_unstable_records": int(fixed_unstable.sum()),
        "baseline_unstable_pct": 100.0 * float(fixed_unstable.mean()) if len(group) else 0.0,
        "rescued_records": int(rescued.sum()),
        "rescued_pct_of_records": 100.0 * float(rescued.mean()) if len(group) else 0.0,
        "rescued_pct_of_baseline_failures": 100.0 * float(rescued.sum() / fixed_unstable.sum()) if fixed_unstable.sum() else 0.0,
        "baseline_peak_outside_records": int(failure_flag(failure_reason, "peak_outside").sum()),
        "baseline_pga_loss_records": int(failure_flag(failure_reason, "pga_loss").sum()),
        "baseline_energy_loss_records": int(failure_flag(failure_reason, "energy_loss").sum()),
        "median_energy_gain": float(group["energy_gain"].median()),
        "p05_energy_gain": float(group["energy_gain"].quantile(0.05)),
        "median_pga_gain": float(group["pga_gain"].median()),
        "median_duration_change_sec": float(group["duration_change_sec"].median()),
        "selector_full_record_fallback_records": int(group["selection_status"].astype(str).eq("full_record_fallback").sum()),
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


def write_report(outdir: Path, summary: pd.DataFrame, policy: str) -> None:
    display = summary[summary["priority_group"].eq("ALL")].sort_values(["dataset", "baseline_candidate"]).copy()
    lines = [
        "# StrongMotion-QC Product Impact",
        "",
        f"Selector policy: `{policy}`.",
        "",
        "This report compares fixed/adaptive candidate windows with the selected product-stable windows.",
        "",
        "## Dataset-Level Summary",
        "",
        markdown_table(display),
        "",
        "## Interpretation Boundary",
        "",
        "Recovered records are records where a baseline window fails the product-retention audit and the selected window passes it. This is an offline product-processing metric, not a manual quality label or a real-time detection metric.",
    ]
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def run_product_impact(stability: pd.DataFrame, selected: pd.DataFrame, outdir: Path, policy: str = DEFAULT_POLICY) -> dict[str, Path]:
    summary = compare_baseline_to_selector(stability, selected, policy=policy)
    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "summary": outdir / "product_impact_summary.csv",
        "report": outdir / "README.md",
    }
    summary.to_csv(outputs["summary"], index=False)
    write_report(outdir, summary, policy)
    return outputs


def main() -> None:
    args = parse_args()
    stability = pd.read_csv(args.window_stability, low_memory=False)
    selected = pd.read_csv(args.selected_windows, low_memory=False)
    outputs = run_product_impact(stability, selected, Path(args.outdir), policy=args.policy)
    for path in outputs.values():
        print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
