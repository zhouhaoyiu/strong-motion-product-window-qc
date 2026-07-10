#!/usr/bin/env python3
"""Escalate product windows that fail tested PSA-retention checks."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evaluate_strong_motion_response_spectrum_retention import summarize as summarize_spectra


PRIMARY_POLICY = "shortest_stable_no_catalog"
ARIAS_POLICY = "arias_1_99_padded"
FULL_POLICY = "full_record"
OUTPUT_POLICY = "product_spectral_safeguard"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selected-windows", required=True)
    parser.add_argument("--response-spectrum", required=True)
    parser.add_argument("--outdir", required=True)
    parser.add_argument("--periods", nargs="+", type=float, default=[0.2, 1.0, 3.0])
    parser.add_argument("--retention-threshold", type=float, default=0.95)
    return parser.parse_args()


def spectrum_checks(
    response: pd.DataFrame,
    periods: list[float],
    retention_threshold: float,
) -> dict[tuple[str, str], tuple[bool, float, str]]:
    required = {float(period) for period in periods}
    checks: dict[tuple[str, str], tuple[bool, float, str]] = {}
    for keys, group in response.groupby(["record_uid", "policy"], sort=False):
        period_values = pd.to_numeric(group["period_sec"], errors="coerce")
        retention = pd.to_numeric(group["psa_retention"], errors="coerce")
        by_period = {
            float(period): float(value)
            for period, value in zip(period_values, retention)
            if np.isfinite(period) and np.isfinite(value)
        }
        missing = required - set(by_period)
        failed = sorted(period for period in required if by_period.get(period, -np.inf) < retention_threshold)
        minimum = min((by_period[period] for period in required if period in by_period), default=float("nan"))
        checks[(str(keys[0]), str(keys[1]))] = (
            not missing and not failed,
            float(minimum),
            ";".join(f"{period:g}" for period in sorted(missing | set(failed))),
        )
    return checks


def window_lookup(selected: pd.DataFrame) -> dict[tuple[str, str], pd.Series]:
    return {
        (str(row["record_uid"]), str(row["policy"])): row
        for _, row in selected.iterrows()
        if str(row.get("policy", "")) in {PRIMARY_POLICY, ARIAS_POLICY, FULL_POLICY}
    }


def apply_safeguard(
    selected: pd.DataFrame,
    response: pd.DataFrame,
    periods: list[float],
    retention_threshold: float = 0.95,
) -> pd.DataFrame:
    checks = spectrum_checks(response, periods, retention_threshold)
    windows = window_lookup(selected)
    record_ids = (
        response[response["policy"].eq(PRIMARY_POLICY)]["record_uid"]
        .astype(str)
        .drop_duplicates()
        .tolist()
    )
    rows: list[dict[str, object]] = []
    for record_uid in record_ids:
        primary = checks.get((record_uid, PRIMARY_POLICY), (False, np.nan, "missing"))
        arias = checks.get((record_uid, ARIAS_POLICY), (False, np.nan, "missing"))
        if primary[0]:
            source_policy, stage, check = PRIMARY_POLICY, "primary", primary
        elif arias[0]:
            source_policy, stage, check = ARIAS_POLICY, "arias_escalation", arias
        else:
            source_policy, stage, check = FULL_POLICY, "full_record_fallback", (True, 1.0, "")
        chosen = windows.get((record_uid, source_policy))
        if chosen is None:
            raise ValueError(f"missing {source_policy} window for {record_uid}")
        out = chosen.to_dict()
        out.update(
            {
                "policy": OUTPUT_POLICY,
                "source_policy": source_policy,
                "spectral_stage": stage,
                "spectral_audit_pass": bool(check[0]),
                "spectral_min_retention": float(check[1]),
                "spectral_failed_or_missing_periods": str(check[2]),
                "retention_threshold": float(retention_threshold),
            }
        )
        rows.append(out)
    return pd.DataFrame(rows)


def selected_spectra(
    safeguarded: pd.DataFrame,
    response: pd.DataFrame,
    periods: list[float],
    retention_threshold: float,
) -> pd.DataFrame:
    source = response.copy()
    source["record_uid"] = source["record_uid"].astype(str)
    source["policy"] = source["policy"].astype(str)
    mapping = safeguarded[["record_uid", "source_policy"]].copy()
    mapping["record_uid"] = mapping["record_uid"].astype(str)
    picked = source.merge(mapping, on="record_uid", how="inner")
    picked = picked[
        picked["policy"].eq(picked["source_policy"])
        & picked["source_policy"].ne(FULL_POLICY)
        & picked["period_sec"].isin(periods)
    ].copy()
    picked["policy"] = OUTPUT_POLICY
    picked = picked.drop(columns="source_policy")

    full_selected = safeguarded[safeguarded["source_policy"].eq(FULL_POLICY)].copy()
    if full_selected.empty:
        return picked.reset_index(drop=True)
    full_selected["record_uid"] = full_selected["record_uid"].astype(str)
    period_table = pd.DataFrame({"period_sec": [float(period) for period in periods]})
    full_rows = full_selected.merge(period_table, how="cross")
    full_psa = source[["record_uid", "period_sec", "full_psa"]].drop_duplicates(["record_uid", "period_sec"])
    full_rows = full_rows.merge(full_psa, on=["record_uid", "period_sec"], how="left")
    full_rows["policy"] = OUTPUT_POLICY
    full_rows["selection_status"] = "full_record_fallback"
    full_rows["damping"] = 0.05
    full_rows["window_psa"] = full_rows["full_psa"]
    full_rows["psa_retention"] = 1.0
    full_rows["spectrum_unstable"] = False
    full_rows["retention_threshold"] = float(retention_threshold)
    response_columns = list(source.columns)
    for column in response_columns:
        if column not in full_rows:
            full_rows[column] = np.nan
    return pd.concat([picked[response_columns], full_rows[response_columns]], ignore_index=True)


def summarize_windows(selected: pd.DataFrame) -> pd.DataFrame:
    rows = []
    groups = list(selected.groupby(["dataset", "priority_group"], dropna=False))
    groups += [((dataset, "ALL"), group) for dataset, group in selected.groupby("dataset", dropna=False)]
    groups += [(('ALL', 'ALL'), selected)]
    for keys, group in groups:
        stage = group["spectral_stage"].astype(str)
        duration = pd.to_numeric(group["window_duration_sec"], errors="coerce")
        rows.append(
            {
                "dataset": keys[0],
                "priority_group": keys[1],
                "records": int(len(group)),
                "primary_pct": 100.0 * float(stage.eq("primary").mean()),
                "arias_escalation_pct": 100.0 * float(stage.eq("arias_escalation").mean()),
                "full_record_fallback_pct": 100.0 * float(stage.eq("full_record_fallback").mean()),
                "median_window_duration_sec": float(duration.median()),
                "p75_window_duration_sec": float(duration.quantile(0.75)),
            }
        )
    return pd.DataFrame(rows)


def write_report(outdir: Path, summary: pd.DataFrame, spectra_summary: pd.DataFrame) -> None:
    focus = summary[summary["priority_group"].eq("ALL")]
    spectrum_focus = spectra_summary[
        spectra_summary["priority_group"].eq("ALL")
        & spectra_summary["policy"].eq(OUTPUT_POLICY)
    ]
    lines = [
        "# StrongMotion-QC Spectral Safeguard",
        "",
        "The safeguard retains the shortest PGA-and-energy-stable window when all tested PSA retentions pass. It escalates failures to the padded 1%-99% Arias window, then to the full record.",
        "",
        "## Window Summary",
        "",
        "```csv",
        focus.to_csv(index=False).strip(),
        "```",
        "",
        "## PSA Summary",
        "",
        "```csv",
        spectrum_focus.to_csv(index=False).strip(),
        "```",
    ]
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def run_safeguard(
    selected: pd.DataFrame,
    response: pd.DataFrame,
    outdir: Path,
    periods: list[float],
    retention_threshold: float,
) -> dict[str, Path]:
    safeguarded = apply_safeguard(selected, response, periods, retention_threshold)
    spectra = selected_spectra(safeguarded, response, periods, retention_threshold)
    summary = summarize_windows(safeguarded)
    spectra_summary = summarize_spectra(spectra)
    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "selected_windows": outdir / "selected_windows.csv",
        "response_spectrum": outdir / "response_spectrum_retention.csv",
        "summary": outdir / "summary.csv",
        "spectrum_summary": outdir / "spectrum_summary.csv",
        "report": outdir / "README.md",
    }
    safeguarded.to_csv(outputs["selected_windows"], index=False)
    spectra.to_csv(outputs["response_spectrum"], index=False)
    summary.to_csv(outputs["summary"], index=False)
    spectra_summary.to_csv(outputs["spectrum_summary"], index=False)
    write_report(outdir, summary, spectra_summary)
    return outputs


def main() -> None:
    args = parse_args()
    outputs = run_safeguard(
        pd.read_csv(args.selected_windows, low_memory=False),
        pd.read_csv(args.response_spectrum, low_memory=False),
        Path(args.outdir),
        args.periods,
        args.retention_threshold,
    )
    for path in outputs.values():
        print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
