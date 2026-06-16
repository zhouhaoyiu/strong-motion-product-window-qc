#!/usr/bin/env python3
"""Evaluate product-stable strong-motion window selection policies."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_STABILITY = "outputs/strong_motion_qc_window_stability_full/window_stability.csv"
DEFAULT_OUTDIR = "outputs/strong_motion_qc_product_window_selector"
FIXED_POLICIES = {
    "feature_onset_fixed": "feature_onset_fixed",
    "energy_onset_fixed": "energy_onset_fixed",
    "catalog_p_fixed": "catalog_p_fixed",
    "adaptive_energy_end": "feature_onset_to_energy_end",
    "full_record": "full_record",
}
NO_CATALOG_CANDIDATES = ["feature_onset_fixed", "energy_onset_fixed", "feature_onset_to_energy_end"]
ALL_NONFULL_CANDIDATES = ["feature_onset_fixed", "energy_onset_fixed", "catalog_p_fixed", "feature_onset_to_energy_end"]
POLICIES = [
    *FIXED_POLICIES.keys(),
    "shortest_stable_no_catalog",
    "shortest_stable_all",
    "energy_first_then_adaptive",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window-stability", default=DEFAULT_STABILITY)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    return parser.parse_args()


def to_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin(["true", "1", "yes", "y"])


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def prepare_stability(stability: pd.DataFrame) -> pd.DataFrame:
    required = {"record_uid", "dataset", "priority_group", "candidate", "window_unstable", "window_duration_sec"}
    missing = required - set(stability.columns)
    if missing:
        raise ValueError(f"window stability table missing columns: {sorted(missing)}")
    work = stability.copy()
    work = work[work["candidate"].ne("load_error")].copy()
    work["window_unstable_bool"] = to_bool(work["window_unstable"])
    for column in [
        "window_duration_sec",
        "pga_retention",
        "energy_retention",
        "window_start_sample",
        "window_end_sample",
    ]:
        if column in work:
            work[column] = numeric(work[column])
    return work


def first_candidate(group: pd.DataFrame, candidate: str) -> pd.Series | None:
    rows = group[group["candidate"].eq(candidate)]
    if rows.empty:
        return None
    return rows.iloc[0]


def choose_shortest_stable(group: pd.DataFrame, candidates: list[str]) -> tuple[pd.Series | None, str]:
    subset = group[group["candidate"].isin(candidates)].copy()
    subset = subset[~subset["window_unstable_bool"]].copy()
    subset = subset[pd.to_numeric(subset["window_duration_sec"], errors="coerce").notna()]
    if subset.empty:
        return first_candidate(group, "full_record"), "full_record_fallback"
    subset = subset.sort_values(["window_duration_sec", "candidate"], kind="mergesort")
    return subset.iloc[0], "stable_candidate"


def choose_energy_first(group: pd.DataFrame) -> tuple[pd.Series | None, str]:
    for candidate in ["energy_onset_fixed", "feature_onset_to_energy_end"]:
        row = first_candidate(group, candidate)
        if row is not None and not bool(row.get("window_unstable_bool", True)):
            return row, "stable_candidate"
    return first_candidate(group, "full_record"), "full_record_fallback"


def choose_policy(group: pd.DataFrame, policy: str) -> tuple[pd.Series | None, str]:
    if policy in FIXED_POLICIES:
        row = first_candidate(group, FIXED_POLICIES[policy])
        return row, "direct_candidate" if row is not None else "missing_candidate"
    if policy == "shortest_stable_no_catalog":
        return choose_shortest_stable(group, NO_CATALOG_CANDIDATES)
    if policy == "shortest_stable_all":
        return choose_shortest_stable(group, ALL_NONFULL_CANDIDATES)
    if policy == "energy_first_then_adaptive":
        return choose_energy_first(group)
    raise ValueError(f"unknown policy: {policy}")


def selected_row(record_uid: str, group: pd.DataFrame, policy: str) -> dict[str, object]:
    chosen, status = choose_policy(group, policy)
    base = group.iloc[0]
    if chosen is None:
        return {
            "record_uid": record_uid,
            "dataset": base.get("dataset", ""),
            "priority_group": base.get("priority_group", ""),
            "split": base.get("split", ""),
            "policy": policy,
            "selection_status": status,
            "selected_candidate": "",
            "window_unstable": True,
            "failure_reason": "missing_candidate",
        }
    out = chosen.to_dict()
    out.update(
        {
            "policy": policy,
            "selection_status": status,
            "selected_candidate": chosen.get("candidate", ""),
            "window_unstable": bool(chosen.get("window_unstable_bool", True)),
        }
    )
    return out


def evaluate_policies(stability: pd.DataFrame, policies: list[str] | None = None) -> pd.DataFrame:
    work = prepare_stability(stability)
    selected = []
    active_policies = policies or POLICIES
    for record_uid, group in work.groupby("record_uid", sort=False):
        for policy in active_policies:
            selected.append(selected_row(str(record_uid), group, policy))
    return pd.DataFrame(selected)


def summarize(selected: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, group in selected.groupby(["dataset", "priority_group", "policy"], dropna=False):
        rows.append(summary_row(keys, group))
    for keys, group in selected.groupby(["dataset", "policy"], dropna=False):
        rows.append(summary_row((keys[0], "ALL", keys[1]), group))
    for policy, group in selected.groupby("policy", dropna=False):
        rows.append(summary_row(("ALL", "ALL", policy), group))
    return pd.DataFrame(rows)


def summary_row(keys, group: pd.DataFrame) -> dict[str, object]:
    unstable = to_bool(group["window_unstable"])
    duration = numeric(group.get("window_duration_sec", pd.Series(dtype=float)))
    energy = numeric(group.get("energy_retention", pd.Series(dtype=float)))
    pga = numeric(group.get("pga_retention", pd.Series(dtype=float)))
    full_fallback = group["selection_status"].astype(str).eq("full_record_fallback") if "selection_status" in group else False
    return {
        "dataset": keys[0],
        "priority_group": keys[1],
        "policy": keys[2],
        "records": int(len(group)),
        "unstable_records": int(unstable.sum()),
        "unstable_pct": 100.0 * float(unstable.mean()) if len(group) else 0.0,
        "median_window_duration_sec": float(duration.median()),
        "p25_window_duration_sec": float(duration.quantile(0.25)),
        "p75_window_duration_sec": float(duration.quantile(0.75)),
        "p05_energy_retention": float(energy.quantile(0.05)),
        "median_energy_retention": float(energy.median()),
        "p05_pga_retention": float(pga.quantile(0.05)),
        "full_record_fallback_records": int(full_fallback.sum()) if hasattr(full_fallback, "sum") else 0,
        "full_record_fallback_pct": 100.0 * float(full_fallback.mean()) if hasattr(full_fallback, "mean") and len(group) else 0.0,
    }


def candidate_usage(selected: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, group in selected.groupby(["dataset", "policy", "selected_candidate"], dropna=False):
        rows.append(
            {
                "dataset": keys[0],
                "policy": keys[1],
                "selected_candidate": keys[2],
                "records": int(len(group)),
                "pct": 100.0 * float(len(group) / len(selected[selected["dataset"].eq(keys[0]) & selected["policy"].eq(keys[1])]))
                if len(group)
                else 0.0,
            }
        )
    return pd.DataFrame(rows).sort_values(["dataset", "policy", "records"], ascending=[True, True, False])


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


def write_report(outdir: Path, summary: pd.DataFrame, usage: pd.DataFrame) -> None:
    display = summary[summary["priority_group"].eq("ALL")].sort_values(["dataset", "policy"]).copy()
    usage_display = usage[usage["dataset"].isin(["InstanceGM", "K-NET"])].copy()
    lines = [
        "# StrongMotion-QC Product Window Selector",
        "",
        "This evaluation selects waveform windows by product retention: PGA retention, relative energy retention, and peak inclusion.",
        "",
        "The selector uses waveform-derived product checks. It is not a human-label classifier and it is not a learned model result.",
        "",
        "## Dataset-Level Summary",
        "",
        markdown_table(display),
        "",
        "## Candidate Usage",
        "",
        markdown_table(usage_display),
        "",
        "## Interpretation Boundary",
        "",
        "`shortest_stable_*` policies are retrospective product-stability selectors computed from available waveform records. They are valid for offline strong-motion processing audits and as upper-bound baselines for learned selectors. They should not be described as real-time phase picking or as evidence that a neural model has solved window selection.",
    ]
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def run_selector_evaluation(stability: pd.DataFrame, outdir: Path) -> dict[str, Path]:
    selected = evaluate_policies(stability)
    summary = summarize(selected)
    usage = candidate_usage(selected)
    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "selected_windows": outdir / "selected_windows.csv",
        "summary": outdir / "summary.csv",
        "candidate_usage": outdir / "candidate_usage.csv",
        "report": outdir / "README.md",
    }
    selected.to_csv(outputs["selected_windows"], index=False)
    summary.to_csv(outputs["summary"], index=False)
    usage.to_csv(outputs["candidate_usage"], index=False)
    write_report(outdir, summary, usage)
    return outputs


def main() -> None:
    args = parse_args()
    stability = pd.read_csv(args.window_stability, low_memory=False)
    outputs = run_selector_evaluation(stability, Path(args.outdir))
    for path in outputs.values():
        print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
