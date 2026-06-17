#!/usr/bin/env python3
"""Build a product-production routing case from StrongMotion-QC audit outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_SELECTED = [
    "outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/selected_windows.csv",
    "outputs/strong_motion_qc_product_window_selector_pnw_external/selected_windows.csv",
]
DEFAULT_RESPONSE = [
    "outputs/strong_motion_qc_response_spectrum_knet22119_hp1_inst3000/response_spectrum_retention.csv",
    "outputs/strong_motion_qc_response_spectrum_pnw_external/response_spectrum_retention.csv",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selected-windows", nargs="+", default=DEFAULT_SELECTED)
    parser.add_argument("--response-retention", nargs="+", default=DEFAULT_RESPONSE)
    parser.add_argument("--outdir", default="outputs/strong_motion_qc_product_production_case")
    parser.add_argument("--policy", default="shortest_stable_no_catalog")
    parser.add_argument("--long-period-sec", type=float, default=3.0)
    return parser.parse_args()


def read_many(paths: list[str]) -> pd.DataFrame:
    frames = [pd.read_csv(path, low_memory=False) for path in paths]
    return pd.concat(frames, ignore_index=True)


def to_bool(series: pd.Series) -> pd.Series:
    if series.dtype == bool:
        return series.fillna(False)
    return series.astype(str).str.lower().isin(["true", "1", "yes", "y"])


def build_case(selected: pd.DataFrame, response: pd.DataFrame, policy: str, long_period_sec: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    windows = selected[selected["policy"].eq(policy)].copy()
    response_focus = response[
        response["policy"].eq(policy) & pd.to_numeric(response["period_sec"], errors="coerce").eq(long_period_sec)
    ].copy()
    keep_response = ["record_uid", "period_sec", "psa_retention", "spectrum_unstable"]
    case = windows.merge(response_focus[keep_response], on="record_uid", how="left")
    case["full_record_required"] = case["selection_status"].astype(str).eq("full_record_fallback")
    case["long_period_psa_review"] = to_bool(case.get("spectrum_unstable", pd.Series(False, index=case.index)))
    case["production_route"] = "stable_window_accept"
    case.loc[case["long_period_psa_review"], "production_route"] = "long_period_psa_review"
    case.loc[case["full_record_required"], "production_route"] = "full_record_required"
    case["review_priority"] = case["full_record_required"].astype(int) * 2 + case["long_period_psa_review"].astype(int)
    case["review_priority"] = case["review_priority"].where(case["review_priority"].gt(0), 0)
    case = case.sort_values(
        ["review_priority", "psa_retention", "window_duration_sec"],
        ascending=[False, True, False],
        kind="mergesort",
    )
    summary = summarize(case)
    return case, summary


def summarize(case: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for keys, group in case.groupby(["dataset", "production_route"], dropna=False):
        rows.append(summary_row(keys[0], keys[1], group))
    for dataset, group in case.groupby("dataset", dropna=False):
        rows.append(summary_row(dataset, "ALL", group))
    for route, group in case.groupby("production_route", dropna=False):
        rows.append(summary_row("ALL", route, group))
    rows.append(summary_row("ALL", "ALL", case))
    return pd.DataFrame(rows).sort_values(["dataset", "production_route"])


def summary_row(dataset: str, route: str, group: pd.DataFrame) -> dict[str, object]:
    return {
        "dataset": dataset,
        "production_route": route,
        "records": int(len(group)),
        "pct": float("nan"),
        "full_record_required": int(group["full_record_required"].sum()),
        "long_period_psa_review": int(group["long_period_psa_review"].sum()),
        "median_window_duration_sec": float(pd.to_numeric(group["window_duration_sec"], errors="coerce").median()),
        "median_psa_retention_3s": float(pd.to_numeric(group["psa_retention"], errors="coerce").median()),
    }


def add_percent(summary: pd.DataFrame) -> pd.DataFrame:
    out = summary.copy()
    totals = out[out["production_route"].eq("ALL")].set_index("dataset")["records"].to_dict()
    out["pct"] = [100.0 * row.records / totals.get(row.dataset, row.records) if totals.get(row.dataset, 0) else 0.0 for row in out.itertuples()]
    return out


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


def write_report(outdir: Path, case: pd.DataFrame, summary: pd.DataFrame, policy: str, long_period_sec: float) -> None:
    review_queue = case[case["production_route"].ne("stable_window_accept")].copy()
    lines = [
        "# StrongMotion-QC Product-Production Routing Case",
        "",
        "This is a retrospective product-production case built from the same audit outputs used by the manuscript.",
        "",
        f"- Selected-window policy: `{policy}`.",
        f"- Long-period review trigger: PSA retention failure at {long_period_sec:g} s.",
        "- `stable_window_accept`: selected window passes the product audit and the long-period PSA check.",
        "- `full_record_required`: no shorter candidate passes the product audit; process and store the full record.",
        "- `long_period_psa_review`: selected window passes PGA, energy, and peak-time checks, but the 3.0 s PSA retention check remains below threshold.",
        "",
        "The case is an operational routing example. It does not measure human review time.",
        "",
        "## Batch Summary",
        "",
        markdown_table(summary),
        "",
        "## Review Queue",
        "",
        f"Records routed away from direct acceptance: {len(review_queue)}.",
        "",
        "## Outputs",
        "",
        "- `production_routes.csv`: one row per record with route flags and selected-window metrics.",
        "- `production_route_summary.csv`: route counts by dataset.",
        "- `review_queue.csv`: records requiring full-record processing or long-period PSA review.",
    ]
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def build_product_production_case(
    selected_paths: list[str],
    response_paths: list[str],
    outdir: Path,
    policy: str = "shortest_stable_no_catalog",
    long_period_sec: float = 3.0,
) -> dict[str, Path]:
    selected = read_many(selected_paths)
    response = read_many(response_paths)
    case, summary = build_case(selected, response, policy=policy, long_period_sec=long_period_sec)
    summary = add_percent(summary)
    review_queue = case[case["production_route"].ne("stable_window_accept")].copy()
    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "routes": outdir / "production_routes.csv",
        "summary": outdir / "production_route_summary.csv",
        "review_queue": outdir / "review_queue.csv",
        "report": outdir / "README.md",
    }
    case.to_csv(outputs["routes"], index=False)
    summary.to_csv(outputs["summary"], index=False)
    review_queue.to_csv(outputs["review_queue"], index=False)
    write_report(outdir, case, summary, policy=policy, long_period_sec=long_period_sec)
    return outputs


def main() -> None:
    args = parse_args()
    outputs = build_product_production_case(
        selected_paths=args.selected_windows,
        response_paths=args.response_retention,
        outdir=Path(args.outdir),
        policy=args.policy,
        long_period_sec=args.long_period_sec,
    )
    for path in outputs.values():
        print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
