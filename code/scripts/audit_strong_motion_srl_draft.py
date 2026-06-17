#!/usr/bin/env python3
"""Audit the StrongMotion-QC SRL draft for numbers, style risks, and scope."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd


DEFAULT_DRAFT = "manuscripts/strong_motion_qc_srl/strong_motion_qc_srl_draft.md"
DEFAULT_DATASET_SUMMARY = "outputs/strong_motion_qc_dataset_table_knet22119_hp1_inst3000/dataset_summary.csv"
DEFAULT_SELECTOR_SUMMARY = "outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/summary.csv"
DEFAULT_SELECTOR_USAGE = "outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/candidate_usage.csv"
DEFAULT_PRODUCT_IMPACT = "outputs/strong_motion_qc_product_impact_knet22119_hp1_inst3000/product_impact_summary.csv"
DEFAULT_SENSITIVITY = "outputs/strong_motion_qc_selector_sensitivity_knet22119_hp1_inst3000/sensitivity_summary.csv"
DEFAULT_KEY_METRICS = "outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/summary.csv"
DEFAULT_RESPONSE_SPECTRUM = "outputs/strong_motion_qc_response_spectrum_knet22119_hp1_inst3000/summary.csv"
DEFAULT_PNW_SELECTOR = "outputs/strong_motion_qc_product_window_selector_pnw_external/summary.csv"
DEFAULT_PNW_RESPONSE_SPECTRUM = "outputs/strong_motion_qc_response_spectrum_pnw_external/summary.csv"
DEFAULT_PRODUCTION_ROUTES = "outputs/strong_motion_qc_product_production_case/production_route_summary.csv"
DEFAULT_OUTDIR = "outputs/strong_motion_qc_srl_draft_audit"

STYLE_PATTERNS = [
    ("rather than", r"\brather than\b", 0),
    ("however", r"\bhowever\b", 0),
    ("therefore", r"\btherefore\b", 0),
    ("not only", r"\bnot only\b", 0),
    ("but also", r"\bbut also\b", 0),
    ("not-x-but-y", r"\bnot\b[^.]{0,120}\bbut\b", 0),
    ("does not", r"\bdoes not\b", 0),
    ("do not", r"\bdo not\b", 0),
    ("not used", r"\bnot used\b", 0),
    ("not by", r"\bnot by\b", 0),
]

SCOPE_PATTERNS = [
    ("real-time claim", r"\breal[- ]time\b", 0),
    ("early-warning claim", r"\bearly warning\b|\bEEW\b", 0),
    ("human-QC replacement", r"\bhuman QC replacement\b|\breplace human\b", 0),
    ("phase-picking accuracy", r"\bphase[- ]picking accuracy\b", 0),
    ("neural superiority", r"\bneural[- ]model superiority\b|\bsuperior neural\b", 0),
    ("threshold-free claim", r"\bthreshold[- ]free\b", 0),
]

UNRESOLVED_PATTERNS = [
    ("References To Verify", r"References To Verify", 0),
    ("TODO", r"\bTODO\b", 0),
    ("TBD", r"\bTBD\b", 0),
    ("placeholder citation", r"\[\?\]|\bcitation needed\b", 0),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", default=DEFAULT_DRAFT)
    parser.add_argument("--dataset-summary", default=DEFAULT_DATASET_SUMMARY)
    parser.add_argument("--selector-summary", default=DEFAULT_SELECTOR_SUMMARY)
    parser.add_argument("--selector-usage", default=DEFAULT_SELECTOR_USAGE)
    parser.add_argument("--product-impact", default=DEFAULT_PRODUCT_IMPACT)
    parser.add_argument("--sensitivity", default=DEFAULT_SENSITIVITY)
    parser.add_argument("--key-metrics", default=DEFAULT_KEY_METRICS)
    parser.add_argument("--response-spectrum", default=DEFAULT_RESPONSE_SPECTRUM)
    parser.add_argument("--pnw-selector-summary", default=DEFAULT_PNW_SELECTOR)
    parser.add_argument("--pnw-response-spectrum", default=DEFAULT_PNW_RESPONSE_SPECTRUM)
    parser.add_argument("--production-routes", default=DEFAULT_PRODUCTION_ROUTES)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    return parser.parse_args()


def fmt_int(value: float | int) -> str:
    return f"{int(round(float(value))):,}"


def fmt_pct(value: float) -> str:
    return f"{float(value):.2f}%"


def fmt_sec(value: float) -> str:
    return f"{float(value):.2f} s"


def row_by(df: pd.DataFrame, **filters: object) -> pd.Series:
    rows = df.copy()
    for key, value in filters.items():
        rows = rows[rows[key].eq(value)]
    if rows.empty:
        joined = ", ".join(f"{key}={value}" for key, value in filters.items())
        raise ValueError(f"missing row for {joined}")
    return rows.iloc[0]


def add_metric(rows: list[dict[str, object]], metric_id: str, expected: str, text: str, source: str) -> None:
    rows.append(
        {
            "metric_id": metric_id,
            "expected_text": expected,
            "found": expected in text,
            "source": source,
        }
    )


def build_number_audit(
    text: str,
    dataset: pd.DataFrame,
    selector: pd.DataFrame,
    usage: pd.DataFrame,
    impact: pd.DataFrame,
    sensitivity: pd.DataFrame,
    response_spectrum: pd.DataFrame,
    pnw_selector: pd.DataFrame | None = None,
    pnw_response_spectrum: pd.DataFrame | None = None,
    production_routes: pd.DataFrame | None = None,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    total_records = int(dataset["records"].sum())
    add_metric(rows, "all_records", fmt_int(total_records), text, DEFAULT_DATASET_SUMMARY)
    for ds in ["InstanceGM", "K-NET"]:
        ds_row = row_by(dataset, dataset=ds)
        add_metric(rows, f"{ds}_records", fmt_int(ds_row["records"]), text, DEFAULT_DATASET_SUMMARY)
        add_metric(rows, f"{ds}_events", fmt_int(ds_row["events"]), text, DEFAULT_DATASET_SUMMARY)
        add_metric(rows, f"{ds}_stations", fmt_int(ds_row["stations"]), text, DEFAULT_DATASET_SUMMARY)
        add_metric(rows, f"{ds}_median_duration", fmt_sec(ds_row["median_duration_sec"]), text, DEFAULT_DATASET_SUMMARY)

    fixed_methods = ["feature_onset_fixed", "energy_onset_fixed", "catalog_p_fixed"]
    for ds in ["InstanceGM", "K-NET"]:
        for method in fixed_methods:
            fixed = row_by(selector, dataset=ds, priority_group="ALL", policy=method)
            add_metric(rows, f"{ds}_{method}_unstable", fmt_pct(fixed["unstable_pct"]), text, DEFAULT_SELECTOR_SUMMARY)
        adaptive = row_by(selector, dataset=ds, priority_group="ALL", policy="adaptive_energy_end")
        selected = row_by(selector, dataset=ds, priority_group="ALL", policy="shortest_stable_no_catalog")
        add_metric(rows, f"{ds}_adaptive_unstable", fmt_pct(adaptive["unstable_pct"]), text, DEFAULT_SELECTOR_SUMMARY)
        add_metric(rows, f"{ds}_adaptive_duration", fmt_sec(adaptive["median_window_duration_sec"]), text, DEFAULT_SELECTOR_SUMMARY)
        add_metric(rows, f"{ds}_selector_fallback", fmt_pct(selected["full_record_fallback_pct"]), text, DEFAULT_SELECTOR_SUMMARY)
        add_metric(rows, f"{ds}_selector_duration", fmt_sec(selected["median_window_duration_sec"]), text, DEFAULT_SELECTOR_SUMMARY)

    selected_all = row_by(selector, dataset="ALL", priority_group="ALL", policy="shortest_stable_no_catalog")
    add_metric(rows, "selector_all_fallback", fmt_pct(selected_all["full_record_fallback_pct"]), text, DEFAULT_SELECTOR_SUMMARY)
    add_metric(rows, "selector_all_fallback_records", fmt_int(selected_all["full_record_fallback_records"]), text, DEFAULT_SELECTOR_SUMMARY)

    for ds in ["InstanceGM", "K-NET"]:
        for candidate in ["feature_onset_to_energy_end", "energy_onset_fixed"]:
            usage_row = row_by(usage, dataset=ds, policy="shortest_stable_no_catalog", selected_candidate=candidate)
            add_metric(rows, f"{ds}_{candidate}_usage", fmt_pct(usage_row["pct"]), text, DEFAULT_SELECTOR_USAGE)

    for ds in ["InstanceGM", "K-NET"]:
        for baseline in ["feature_onset_fixed", "energy_onset_fixed"]:
            impact_row = row_by(impact, dataset=ds, priority_group="ALL", baseline_candidate=baseline)
            add_metric(rows, f"{ds}_{baseline}_rescued", fmt_int(impact_row["rescued_records"]), text, DEFAULT_PRODUCT_IMPACT)
    inst_feature = row_by(impact, dataset="InstanceGM", priority_group="ALL", baseline_candidate="feature_onset_fixed")
    knet_feature = row_by(impact, dataset="K-NET", priority_group="ALL", baseline_candidate="feature_onset_fixed")
    add_metric(rows, "InstanceGM_feature_energy_gain", f"{float(inst_feature['median_energy_gain']):.3f}", text, DEFAULT_PRODUCT_IMPACT)
    add_metric(rows, "InstanceGM_feature_duration_change", fmt_sec(inst_feature["median_duration_change_sec"]), text, DEFAULT_PRODUCT_IMPACT)
    add_metric(rows, "K-NET_feature_duration_change", fmt_sec(knet_feature["median_duration_change_sec"]), text, DEFAULT_PRODUCT_IMPACT)
    add_metric(rows, "InstanceGM_feature_energy_loss_records", fmt_int(inst_feature["baseline_energy_loss_records"]), text, DEFAULT_PRODUCT_IMPACT)
    add_metric(rows, "InstanceGM_feature_pga_loss_records", fmt_int(inst_feature["baseline_pga_loss_records"]), text, DEFAULT_PRODUCT_IMPACT)
    add_metric(rows, "K-NET_feature_energy_loss_records", fmt_int(knet_feature["baseline_energy_loss_records"]), text, DEFAULT_PRODUCT_IMPACT)
    add_metric(rows, "K-NET_feature_pga_loss_records", fmt_int(knet_feature["baseline_pga_loss_records"]), text, DEFAULT_PRODUCT_IMPACT)

    for ds in ["ALL", "InstanceGM", "K-NET"]:
        for energy in [0.95, 0.98]:
            sens = row_by(sensitivity, dataset=ds, priority_group="ALL", pga_threshold=0.99, energy_threshold=energy)
            add_metric(rows, f"{ds}_fallback_energy_{energy}", fmt_pct(sens["full_record_fallback_pct"]), text, DEFAULT_SENSITIVITY)

    response_checks = [
        ("ALL", "feature_onset_fixed", 0.2),
        ("ALL", "feature_onset_fixed", 1.0),
        ("ALL", "feature_onset_fixed", 3.0),
        ("ALL", "shortest_stable_no_catalog", 0.2),
        ("ALL", "shortest_stable_no_catalog", 1.0),
        ("ALL", "shortest_stable_no_catalog", 3.0),
        ("InstanceGM", "feature_onset_fixed", 3.0),
        ("InstanceGM", "shortest_stable_no_catalog", 3.0),
        ("K-NET", "feature_onset_fixed", 3.0),
        ("K-NET", "shortest_stable_no_catalog", 3.0),
    ]
    for ds, method, period in response_checks:
        spectrum = row_by(
            response_spectrum,
            dataset=ds,
            priority_group="ALL",
            policy=method,
            period_sec=period,
        )
        add_metric(
            rows,
            f"{ds}_{method}_{period:g}s_spectrum_unstable",
            fmt_pct(spectrum["spectrum_unstable_pct"]),
            text,
            DEFAULT_RESPONSE_SPECTRUM,
        )
        if ds == "ALL" and method == "shortest_stable_no_catalog":
            add_metric(
                rows,
                f"ALL_selector_{period:g}s_spectrum_records",
                fmt_int(spectrum["spectrum_unstable_records"]),
                text,
                DEFAULT_RESPONSE_SPECTRUM,
            )

    for ds in ["InstanceGM", "K-NET"]:
        for method in ["feature_onset_fixed", "energy_onset_fixed", "shortest_stable_no_catalog"]:
            strata = row_by(selector, dataset=ds, priority_group="m3_to_m4_small_event", policy=method)
            if method == "shortest_stable_no_catalog":
                add_metric(rows, f"{ds}_m3m4_selector_fallback", fmt_pct(strata["full_record_fallback_pct"]), text, DEFAULT_SELECTOR_SUMMARY)
                add_metric(rows, f"{ds}_m3m4_selector_duration", fmt_sec(strata["median_window_duration_sec"]), text, DEFAULT_SELECTOR_SUMMARY)
            else:
                add_metric(rows, f"{ds}_m3m4_{method}_unstable", fmt_pct(strata["unstable_pct"]), text, DEFAULT_SELECTOR_SUMMARY)

    if pnw_selector is not None:
        pnw_feature = row_by(pnw_selector, dataset="PNWAccelerometers", priority_group="ALL", policy="feature_onset_fixed")
        pnw_energy = row_by(pnw_selector, dataset="PNWAccelerometers", priority_group="ALL", policy="energy_onset_fixed")
        pnw_catalog = row_by(pnw_selector, dataset="PNWAccelerometers", priority_group="ALL", policy="catalog_p_fixed")
        pnw_selected = row_by(pnw_selector, dataset="PNWAccelerometers", priority_group="ALL", policy="shortest_stable_no_catalog")
        add_metric(rows, "PNW_records", fmt_int(pnw_feature["records"]), text, DEFAULT_PNW_SELECTOR)
        add_metric(rows, "PNW_feature_fixed_unstable", fmt_pct(pnw_feature["unstable_pct"]), text, DEFAULT_PNW_SELECTOR)
        add_metric(rows, "PNW_energy_fixed_unstable", fmt_pct(pnw_energy["unstable_pct"]), text, DEFAULT_PNW_SELECTOR)
        add_metric(rows, "PNW_catalog_fixed_unstable", fmt_pct(pnw_catalog["unstable_pct"]), text, DEFAULT_PNW_SELECTOR)
        add_metric(rows, "PNW_selector_fallback", fmt_pct(pnw_selected["full_record_fallback_pct"]), text, DEFAULT_PNW_SELECTOR)
        add_metric(rows, "PNW_selector_duration", fmt_sec(pnw_selected["median_window_duration_sec"]), text, DEFAULT_PNW_SELECTOR)

    if pnw_response_spectrum is not None:
        for method in ["feature_onset_fixed", "shortest_stable_no_catalog"]:
            for period in [0.2, 1.0, 3.0]:
                row = row_by(
                    pnw_response_spectrum,
                    dataset="PNWAccelerometers",
                    priority_group="ALL",
                    policy=method,
                    period_sec=period,
                )
                add_metric(
                    rows,
                    f"PNW_{method}_{period:g}s_spectrum_unstable",
                    fmt_pct(row["spectrum_unstable_pct"]),
                    text,
                    DEFAULT_PNW_RESPONSE_SPECTRUM,
                )

    if production_routes is not None:
        route_all = row_by(production_routes, dataset="ALL", production_route="ALL")
        route_accept = row_by(production_routes, dataset="ALL", production_route="stable_window_accept")
        route_full = row_by(production_routes, dataset="ALL", production_route="full_record_required")
        route_review = row_by(production_routes, dataset="ALL", production_route="long_period_psa_review")
        pnw_full = row_by(production_routes, dataset="PNWAccelerometers", production_route="full_record_required")
        pnw_review = row_by(production_routes, dataset="PNWAccelerometers", production_route="long_period_psa_review")
        add_metric(rows, "production_total_records", fmt_int(route_all["records"]), text, DEFAULT_PRODUCTION_ROUTES)
        add_metric(rows, "production_accept_records", fmt_int(route_accept["records"]), text, DEFAULT_PRODUCTION_ROUTES)
        add_metric(rows, "production_accept_pct", fmt_pct(route_accept["pct"]), text, DEFAULT_PRODUCTION_ROUTES)
        add_metric(rows, "production_full_records", fmt_int(route_full["records"]), text, DEFAULT_PRODUCTION_ROUTES)
        add_metric(rows, "production_full_pct", fmt_pct(route_full["pct"]), text, DEFAULT_PRODUCTION_ROUTES)
        add_metric(rows, "production_review_records", fmt_int(route_review["records"]), text, DEFAULT_PRODUCTION_ROUTES)
        add_metric(rows, "production_review_pct", fmt_pct(route_review["pct"]), text, DEFAULT_PRODUCTION_ROUTES)
        add_metric(rows, "production_pnw_full_records", fmt_int(pnw_full["records"]), text, DEFAULT_PRODUCTION_ROUTES)
        add_metric(rows, "production_pnw_review_records", fmt_int(pnw_review["records"]), text, DEFAULT_PRODUCTION_ROUTES)

    return pd.DataFrame(rows)


def text_before_references(text: str) -> str:
    marker = re.search(r"^## References\b", text, flags=re.IGNORECASE | re.MULTILINE)
    if marker:
        return text[: marker.start()]
    return text


def count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, flags=re.IGNORECASE | re.DOTALL))


def build_pattern_audit(text: str, patterns: list[tuple[str, str, int]], audit_type: str) -> pd.DataFrame:
    rows = []
    for label, pattern, allowed in patterns:
        count = count_pattern(text, pattern)
        rows.append(
            {
                "audit_type": audit_type,
                "pattern": label,
                "count": count,
                "allowed_count": allowed,
                "passed": count <= allowed,
            }
        )
    return pd.DataFrame(rows)


def build_display_audit(text: str) -> pd.DataFrame:
    rows = []
    for idx in range(1, 7):
        label = f"Figure {idx}"
        count = count_pattern(text, rf"\b{label}\b")
        rows.append({"item": label, "count": count, "passed": count >= 1})
    for idx in range(1, 4):
        label = f"Table {idx}"
        count = count_pattern(text, rf"\b{label}\b")
        rows.append({"item": label, "count": count, "passed": count >= 1})
    return pd.DataFrame(rows)


def write_report(
    outdir: Path,
    number_audit: pd.DataFrame,
    pattern_audit: pd.DataFrame,
    display_audit: pd.DataFrame,
) -> None:
    missing_numbers = number_audit[~number_audit["found"]]
    pattern_failures = pattern_audit[~pattern_audit["passed"]]
    display_failures = display_audit[~display_audit["passed"]]
    lines = [
        "# StrongMotion-QC SRL Draft Audit",
        "",
        f"Number checks passed: {int(number_audit['found'].sum())}/{len(number_audit)}",
        f"Pattern checks passed: {int(pattern_audit['passed'].sum())}/{len(pattern_audit)}",
        f"Display-item checks passed: {int(display_audit['passed'].sum())}/{len(display_audit)}",
        "",
        "## Blocking Items",
        "",
    ]
    if missing_numbers.empty and pattern_failures.empty and display_failures.empty:
        lines.append("No blocking audit items found.")
    else:
        if not missing_numbers.empty:
            lines.append("Missing number strings:")
            for _, row in missing_numbers.iterrows():
                lines.append(f"- {row['metric_id']}: expected `{row['expected_text']}`")
        if not pattern_failures.empty:
            lines.append("Pattern risks:")
            for _, row in pattern_failures.iterrows():
                lines.append(f"- {row['pattern']}: count {row['count']} exceeds {row['allowed_count']}")
        if not display_failures.empty:
            lines.append("Missing display references:")
            for _, row in display_failures.iterrows():
                lines.append(f"- {row['item']}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This audit checks manuscript consistency against the current evidence packet. Passing the audit is a submission-risk control, not a standalone science validation.",
        ]
    )
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def run_audit(
    draft_path: Path,
    dataset_summary: Path,
    selector_summary: Path,
    selector_usage: Path,
    product_impact: Path,
    sensitivity: Path,
    key_metrics: Path,
    response_spectrum: Path,
    pnw_selector_summary: Path,
    pnw_response_spectrum: Path,
    production_routes: Path,
    outdir: Path,
) -> dict[str, Path]:
    text = draft_path.read_text()
    claim_text = text_before_references(text)
    dataset = pd.read_csv(dataset_summary)
    selector = pd.read_csv(selector_summary)
    usage = pd.read_csv(selector_usage)
    impact = pd.read_csv(product_impact)
    sens = pd.read_csv(sensitivity)
    spectrum = pd.read_csv(response_spectrum)
    pnw_selector = pd.read_csv(pnw_selector_summary) if pnw_selector_summary.exists() else None
    pnw_spectrum = pd.read_csv(pnw_response_spectrum) if pnw_response_spectrum.exists() else None
    production = pd.read_csv(production_routes) if production_routes.exists() else None
    number_audit = build_number_audit(
        text,
        dataset,
        selector,
        usage,
        impact,
        sens,
        spectrum,
        pnw_selector=pnw_selector,
        pnw_response_spectrum=pnw_spectrum,
        production_routes=production,
    )
    pattern_audit = pd.concat(
        [
            build_pattern_audit(claim_text, STYLE_PATTERNS, "style"),
            build_pattern_audit(claim_text, SCOPE_PATTERNS, "scope"),
            build_pattern_audit(text, UNRESOLVED_PATTERNS, "unresolved"),
        ],
        ignore_index=True,
    )
    display_audit = build_display_audit(text)
    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "number_audit": outdir / "number_audit.csv",
        "pattern_audit": outdir / "pattern_audit.csv",
        "display_audit": outdir / "display_audit.csv",
        "report": outdir / "README.md",
    }
    number_audit.to_csv(outputs["number_audit"], index=False)
    pattern_audit.to_csv(outputs["pattern_audit"], index=False)
    display_audit.to_csv(outputs["display_audit"], index=False)
    write_report(outdir, number_audit, pattern_audit, display_audit)
    return outputs


def main() -> None:
    args = parse_args()
    outputs = run_audit(
        draft_path=Path(args.draft),
        dataset_summary=Path(args.dataset_summary),
        selector_summary=Path(args.selector_summary),
        selector_usage=Path(args.selector_usage),
        product_impact=Path(args.product_impact),
        sensitivity=Path(args.sensitivity),
        key_metrics=Path(args.key_metrics),
        response_spectrum=Path(args.response_spectrum),
        pnw_selector_summary=Path(args.pnw_selector_summary),
        pnw_response_spectrum=Path(args.pnw_response_spectrum),
        production_routes=Path(args.production_routes),
        outdir=Path(args.outdir),
    )
    for path in outputs.values():
        print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
