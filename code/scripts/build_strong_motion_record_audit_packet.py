#!/usr/bin/env python3
"""Build representative record-level audit material for StrongMotion-QC."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evaluate_strong_motion_response_spectrum_retention import (  # noqa: E402
    DEFAULT_FEATURES,
    DEFAULT_KNET_WAVEFORMS,
    DEFAULT_SELECTED,
    load_record_waveform,
    load_waveform_handles,
)
from scripts.compute_strong_motion_qc_features import standardize_channels  # noqa: E402
from strong_motion_qc.features import vector_amplitude  # noqa: E402


DEFAULT_OUTDIR = "outputs/strong_motion_qc_record_audit_packet_knet22119_hp1_inst3000"
CASE_CATEGORIES = [
    "instance_fixed_failure_rescued",
    "knet_fixed_failure_rescued",
    "knet_compact_stable_window",
    "full_record_fallback_boundary",
]
PLOT_POLICIES = ["feature_onset_fixed", "energy_onset_fixed", "shortest_stable_no_catalog"]
POLICY_LABELS = {
    "feature_onset_fixed": "Feature fixed",
    "energy_onset_fixed": "Energy fixed",
    "shortest_stable_no_catalog": "Shortest stable",
}
CASE_LABELS = {
    "instance_fixed_failure_rescued": "InstanceGM fixed-window failure",
    "knet_fixed_failure_rescued": "K-NET fixed-window failure",
    "knet_compact_stable_window": "K-NET compact stable window",
    "full_record_fallback_boundary": "Full-record fallback boundary",
}
GROUP_LABELS = {
    "low_magnitude_background": "low magnitude",
    "m3_to_m4_small_event": "M3-M4",
    "m4plus_strong_motion": "M4+",
    "other": "other",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--features", default=DEFAULT_FEATURES)
    parser.add_argument("--selected-windows", default=DEFAULT_SELECTED)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    parser.add_argument("--knet-waveforms", default=DEFAULT_KNET_WAVEFORMS)
    parser.add_argument("--knet-highpass-hz", type=float, default=1.0)
    parser.add_argument("--cases-per-category", type=int, default=2)
    parser.add_argument("--formats", nargs="+", default=["png", "pdf"])
    return parser.parse_args()


def as_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series
    return series.astype(str).str.lower().isin(["true", "1", "yes"])


def prepare_policy_pair(selected: pd.DataFrame, baseline_policy: str = "feature_onset_fixed") -> pd.DataFrame:
    baseline = selected[selected["policy"].eq(baseline_policy)].copy()
    main = selected[selected["policy"].eq("shortest_stable_no_catalog")].copy()
    common = ["record_uid", "dataset", "priority_group", "split", "magnitude"]
    keep = common + [
        "selected_candidate",
        "selection_status",
        "window_duration_sec",
        "window_unstable_bool",
        "failure_reason",
        "pga_retention",
        "energy_retention",
        "peak_inside_window",
        "peak_time_sec",
        "candidate_start_sec",
        "candidate_end_sec",
        "window_start_sample",
        "window_end_sample",
    ]
    pair = baseline[keep].merge(main[keep], on=common, suffixes=("_baseline", "_selected"))
    pair["baseline_unstable"] = as_bool(pair["window_unstable_bool_baseline"])
    pair["selected_unstable"] = as_bool(pair["window_unstable_bool_selected"])
    pair["energy_gain"] = pd.to_numeric(pair["energy_retention_selected"], errors="coerce") - pd.to_numeric(
        pair["energy_retention_baseline"], errors="coerce"
    )
    pair["pga_gain"] = pd.to_numeric(pair["pga_retention_selected"], errors="coerce") - pd.to_numeric(
        pair["pga_retention_baseline"], errors="coerce"
    )
    return pair


def select_top(group: pd.DataFrame, n: int, category: str, rationale: str, sort_cols: list[str]) -> pd.DataFrame:
    if group.empty or n <= 0:
        return group.iloc[0:0].copy()
    out = group.sort_values(sort_cols, ascending=[False] * len(sort_cols)).head(n).copy()
    out["case_category"] = category
    out["case_rationale"] = rationale
    return out


def select_representative_cases(selected: pd.DataFrame, cases_per_category: int = 2) -> pd.DataFrame:
    pair = prepare_policy_pair(selected)
    rescued = pair[pair["baseline_unstable"] & ~pair["selected_unstable"]].copy()

    cases: list[pd.DataFrame] = []
    cases.append(
        select_top(
            rescued[rescued["dataset"].eq("InstanceGM")],
            cases_per_category,
            "instance_fixed_failure_rescued",
            "InstanceGM feature-onset fixed window fails product checks; shortest-stable selection restores retention.",
            ["energy_gain", "pga_gain", "magnitude"],
        )
    )
    cases.append(
        select_top(
            rescued[rescued["dataset"].eq("K-NET")],
            cases_per_category,
            "knet_fixed_failure_rescued",
            "K-NET rare fixed-window failure; shortest-stable selection restores retention under the same checks.",
            ["energy_gain", "pga_gain", "magnitude"],
        )
    )

    main = selected[selected["policy"].eq("shortest_stable_no_catalog")].copy()
    main["selected_unstable"] = as_bool(main["window_unstable_bool"])
    compact = main[
        main["dataset"].eq("K-NET")
        & ~main["selected_unstable"]
        & main["selection_status"].eq("stable_candidate")
        & pd.to_numeric(main["window_duration_sec"], errors="coerce").le(25.0)
    ].copy()
    compact = compact.sort_values(["window_duration_sec", "energy_retention", "magnitude"], ascending=[True, False, False]).head(
        cases_per_category
    )
    if not compact.empty:
        compact = pair[pair["record_uid"].isin(compact["record_uid"])].copy()
        compact["case_category"] = "knet_compact_stable_window"
        compact["case_rationale"] = "K-NET record where a compact selected window retains the product checks."
        cases.append(compact.head(cases_per_category))

    fallback = main[main["selection_status"].eq("full_record_fallback")].copy()
    fallback_cases = []
    for dataset, group in fallback.groupby("dataset", dropna=False):
        take = group.sort_values(["window_duration_sec", "magnitude"], ascending=[True, False]).head(1)
        fallback_cases.append(take)
    if fallback_cases:
        fallback_records = pd.concat(fallback_cases, ignore_index=True)
        fallback_pair = pair[pair["record_uid"].isin(fallback_records["record_uid"])].copy()
        fallback_pair["case_category"] = "full_record_fallback_boundary"
        fallback_pair["case_rationale"] = "No shorter candidate passes the product checks; the selector uses the full record."
        cases.append(fallback_pair.head(cases_per_category))

    out = pd.concat([case for case in cases if not case.empty], ignore_index=True) if cases else pd.DataFrame()
    if out.empty:
        return out
    out = out.drop_duplicates("record_uid").copy()
    out.insert(0, "case_id", [f"case_{idx:02d}" for idx in range(1, len(out) + 1)])
    return out


def case_summary_rows(cases: pd.DataFrame) -> pd.DataFrame:
    if cases.empty:
        return pd.DataFrame()
    columns = [
        "case_id",
        "case_category",
        "record_uid",
        "dataset",
        "priority_group",
        "split",
        "magnitude",
        "case_rationale",
        "failure_reason_baseline",
        "selected_candidate_selected",
        "selection_status_selected",
        "window_duration_sec_baseline",
        "window_duration_sec_selected",
        "pga_retention_baseline",
        "pga_retention_selected",
        "energy_retention_baseline",
        "energy_retention_selected",
        "energy_gain",
        "pga_gain",
        "peak_time_sec_baseline",
        "peak_inside_window_baseline",
        "peak_inside_window_selected",
    ]
    present = [column for column in columns if column in cases.columns]
    return cases[present].copy()


def normalize_trace(waveform: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    arr = standardize_channels(waveform)
    amp = vector_amplitude(arr)
    max_amp = float(np.nanmax(amp)) if amp.size else 0.0
    if np.isfinite(max_amp) and max_amp > 0:
        amp = amp / max_amp
    z = arr[0].astype(float)
    max_z = float(np.nanmax(np.abs(z))) if z.size else 0.0
    if np.isfinite(max_z) and max_z > 0:
        z = z / max_z
    return amp, z


def plot_case(
    case: pd.Series,
    windows: pd.DataFrame,
    waveform: np.ndarray,
    outdir: Path,
    formats: list[str],
) -> list[Path]:
    import matplotlib.pyplot as plt

    sampling_rate = float(case["sampling_rate_hz"])
    amp, z = normalize_trace(waveform)
    n_samples = waveform.shape[-1]
    time = np.arange(n_samples) / sampling_rate
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 3.6), sharex=True, gridspec_kw={"height_ratios": [1.0, 1.2]})
    axes[0].plot(time, z, color="#333333", linewidth=0.55)
    axes[0].set_ylabel("Z norm.")
    axes[1].plot(time, amp, color="#111111", linewidth=0.75)
    axes[1].set_ylabel("Vector norm.")
    axes[1].set_xlabel("Record time (s)")

    colors = {
        "feature_onset_fixed": "#8a8a8a",
        "energy_onset_fixed": "#bdbdbd",
        "shortest_stable_no_catalog": "#111111",
    }
    for _, row in windows[windows["policy"].isin(PLOT_POLICIES)].iterrows():
        start = float(row["window_start_sample"]) / sampling_rate
        end = float(row["window_end_sample"]) / sampling_rate
        label = POLICY_LABELS.get(str(row["policy"]), str(row["policy"]))
        for ax in axes:
            if row["policy"] == "shortest_stable_no_catalog":
                ax.axvspan(start, end, facecolor="none", edgecolor=colors[row["policy"]], linewidth=1.1, label=label)
            else:
                ax.axvspan(start, end, color=colors[row["policy"]], alpha=0.16, label=label)

    peak_time = pd.to_numeric(case.get("peak_time_sec_selected", np.nan), errors="coerce")
    if np.isfinite(peak_time):
        for ax in axes:
            ax.axvline(float(peak_time), color="#a00000", linestyle="--", linewidth=0.9, label="Full-record peak")

    case_label = CASE_LABELS.get(str(case["case_category"]), str(case["case_category"]).replace("_", " "))
    group_label = GROUP_LABELS.get(str(case["priority_group"]), str(case["priority_group"]).replace("_", " "))
    title = f"{case['case_id']} | {case['dataset']} | {group_label} | M{float(case['magnitude']):.1f} | {case_label}"
    axes[0].set_title(title, fontsize=8.8)
    handles, labels = axes[1].get_legend_handles_labels()
    unique = dict(zip(labels, handles))
    axes[1].legend(unique.values(), unique.keys(), loc="upper right", frameon=False, fontsize=7.2, ncol=2)
    for ax in axes:
        ax.grid(True, alpha=0.2, linewidth=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    outdir.mkdir(parents=True, exist_ok=True)
    paths = []
    for fmt in formats:
        path = outdir / f"{case['case_id']}_{case['record_uid'].replace(':', '_')}.{fmt}"
        fig.savefig(path, bbox_inches="tight", dpi=300)
        paths.append(path)
    plt.close(fig)
    return paths


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


def write_readme(outdir: Path, cases: pd.DataFrame, load_errors: pd.DataFrame, plot_manifest: pd.DataFrame) -> None:
    compact = cases[
        [
            "case_id",
            "case_category",
            "record_uid",
            "dataset",
            "priority_group",
            "magnitude",
            "window_duration_sec_baseline",
            "window_duration_sec_selected",
            "energy_retention_baseline",
            "energy_retention_selected",
            "pga_retention_baseline",
            "pga_retention_selected",
        ]
    ].copy()
    lines = [
        "# StrongMotion-QC Record-Level Audit Packet",
        "",
        "This packet provides representative record-level traces for checking how fixed windows and the shortest-stable selector behave on individual records.",
        "",
        "## Scope",
        "",
        "- The cases are explanatory examples selected from the current 53,463-record audit.",
        "- The packet supports reviewability; it is not a separate statistical experiment.",
        "- Window metrics come from `selected_windows.csv` under the same product-retention rules used by the manuscript.",
        "",
        "## Case Summary",
        "",
        markdown_table(compact),
        "",
        "## Outputs",
        "",
        "- `cases.csv`: selected case-level metrics and rationale.",
        "- `case_windows.csv`: all plotted policy windows for the selected records.",
        "- `plot_manifest.csv`: generated case figure files.",
        "- `figures/`: per-record waveform plots with fixed and selected windows.",
    ]
    if not load_errors.empty:
        lines.extend(
            [
                "- `load_errors.csv`: records selected for the packet but unavailable to the waveform loader.",
                "",
                "## Load Errors",
                "",
                markdown_table(load_errors),
            ]
        )
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def build_record_audit_packet(
    features: pd.DataFrame,
    selected_windows: pd.DataFrame,
    outdir: Path,
    knet_waveforms: Path = Path(DEFAULT_KNET_WAVEFORMS),
    knet_highpass_hz: float | None = 1.0,
    cases_per_category: int = 2,
    formats: list[str] | None = None,
) -> dict[str, Path | int]:
    output_formats = formats or ["png", "pdf"]
    cases = select_representative_cases(selected_windows, cases_per_category=cases_per_category)
    case_table = case_summary_rows(cases)
    record_ids = set(case_table["record_uid"].astype(str)) if not case_table.empty else set()
    windows = selected_windows[
        selected_windows["record_uid"].astype(str).isin(record_ids) & selected_windows["policy"].isin(PLOT_POLICIES)
    ].copy()
    record_table = features[features["record_uid"].astype(str).isin(record_ids)].copy()
    cases_with_features = case_table.merge(
        record_table[["record_uid", "sampling_rate_hz", "units", "waveform_qc_status"]],
        on="record_uid",
        how="left",
    )

    if outdir.exists():
        import shutil

        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)
    case_table.to_csv(outdir / "cases.csv", index=False)
    windows.to_csv(outdir / "case_windows.csv", index=False)

    load_errors: list[dict[str, object]] = []
    plot_rows: list[dict[str, object]] = []
    instance_data, h5, keys = load_waveform_handles(record_table, knet_waveforms)
    try:
        for _, case in cases_with_features.iterrows():
            record_uid = str(case["record_uid"])
            record_rows = record_table[record_table["record_uid"].astype(str).eq(record_uid)]
            if record_rows.empty:
                load_errors.append(
                    {
                        "case_id": case["case_id"],
                        "record_uid": record_uid,
                        "dataset": case["dataset"],
                        "error": "record missing from waveform feature table",
                    }
                )
                continue
            try:
                waveform = load_record_waveform(record_rows.iloc[0], instance_data, h5, keys, knet_highpass_hz)
                paths = plot_case(
                    case,
                    windows[windows["record_uid"].astype(str).eq(record_uid)],
                    waveform,
                    outdir / "figures",
                    output_formats,
                )
                for path in paths:
                    plot_rows.append(
                        {
                            "case_id": case["case_id"],
                            "record_uid": record_uid,
                            "format": path.suffix.lstrip("."),
                            "path": str(path.relative_to(outdir)),
                        }
                    )
            except Exception as exc:
                load_errors.append(
                    {
                        "case_id": case["case_id"],
                        "record_uid": record_uid,
                        "dataset": case["dataset"],
                        "error": str(exc),
                    }
                )
    finally:
        if h5 is not None:
            h5.close()

    plot_manifest = pd.DataFrame(plot_rows)
    load_error_table = pd.DataFrame(load_errors)
    plot_manifest.to_csv(outdir / "plot_manifest.csv", index=False)
    if not load_error_table.empty:
        load_error_table.to_csv(outdir / "load_errors.csv", index=False)
    write_readme(outdir, case_table, load_error_table, plot_manifest)
    return {
        "outdir": outdir,
        "cases": outdir / "cases.csv",
        "case_windows": outdir / "case_windows.csv",
        "plot_manifest": outdir / "plot_manifest.csv",
        "report": outdir / "README.md",
        "case_count": int(len(case_table)),
        "plot_count": int(len(plot_manifest)),
        "load_error_count": int(len(load_error_table)),
    }


def main() -> None:
    args = parse_args()
    features = pd.read_csv(args.features, low_memory=False)
    selected = pd.read_csv(args.selected_windows, low_memory=False)
    result = build_record_audit_packet(
        features=features,
        selected_windows=selected,
        outdir=Path(args.outdir),
        knet_waveforms=Path(args.knet_waveforms),
        knet_highpass_hz=args.knet_highpass_hz,
        cases_per_category=args.cases_per_category,
        formats=args.formats,
    )
    print(f"Wrote {Path(result['outdir']).resolve()}")
    print(f"Cases: {result['case_count']}; plots: {result['plot_count']}; load errors: {result['load_error_count']}")


if __name__ == "__main__":
    main()
