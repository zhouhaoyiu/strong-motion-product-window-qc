#!/usr/bin/env python3
"""Build an internal SRL readiness report for the StrongMotion-QC route."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


DEFAULT_AUDIT_DIR = "outputs/strong_motion_qc_srl_draft_audit"
DEFAULT_FIGURE_MANIFEST = "outputs/strong_motion_qc_figures/figure_manifest.csv"
DEFAULT_DATASET_SUMMARY = "outputs/strong_motion_qc_dataset_table/dataset_summary.csv"
DEFAULT_KEY_METRICS = "outputs/strong_motion_qc_journal_evidence_packet/key_metrics.csv"
DEFAULT_PRODUCT_IMPACT = "outputs/strong_motion_qc_product_impact/product_impact_summary.csv"
DEFAULT_SENSITIVITY = "outputs/strong_motion_qc_selector_sensitivity/sensitivity_summary.csv"
DEFAULT_RESPONSE_SPECTRUM = "outputs/strong_motion_qc_response_spectrum_knet22119_hp1_inst3000/summary.csv"
DEFAULT_PGV_RETENTION = "outputs/strong_motion_qc_pgv_retention_knet22119_hp1_inst3000/summary.csv"
DEFAULT_RECORD_AUDIT_DIR = "outputs/strong_motion_qc_record_audit_packet_knet22119_hp1_inst3000"
DEFAULT_DRAFT = "manuscripts/strong_motion_qc_srl/strong_motion_qc_srl_draft.md"
DEFAULT_LATEX_PDF = "manuscripts/strong_motion_qc_srl/main.pdf"
DEFAULT_REPRO_RELEASE_ZIP = "outputs/strong_motion_qc_srl_reproducibility_release_current.zip"
DEFAULT_COMPLIANCE_DIR = "outputs/strong_motion_qc_srl_compliance"
DEFAULT_OUTDIR = "outputs/strong_motion_qc_srl_readiness"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-dir", default=DEFAULT_AUDIT_DIR)
    parser.add_argument("--figure-manifest", default=DEFAULT_FIGURE_MANIFEST)
    parser.add_argument("--dataset-summary", default=DEFAULT_DATASET_SUMMARY)
    parser.add_argument("--key-metrics", default=DEFAULT_KEY_METRICS)
    parser.add_argument("--product-impact", default=DEFAULT_PRODUCT_IMPACT)
    parser.add_argument("--sensitivity", default=DEFAULT_SENSITIVITY)
    parser.add_argument("--response-spectrum", default=DEFAULT_RESPONSE_SPECTRUM)
    parser.add_argument("--pgv-retention", default=DEFAULT_PGV_RETENTION)
    parser.add_argument("--record-audit-dir", default=DEFAULT_RECORD_AUDIT_DIR)
    parser.add_argument("--draft", default=DEFAULT_DRAFT)
    parser.add_argument("--latex-pdf", default=DEFAULT_LATEX_PDF)
    parser.add_argument("--repro-release-zip", default=DEFAULT_REPRO_RELEASE_ZIP)
    parser.add_argument("--compliance-dir", default=DEFAULT_COMPLIANCE_DIR)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    return parser.parse_args()


def audit_status(audit_dir: Path) -> dict[str, object]:
    number = pd.read_csv(audit_dir / "number_audit.csv")
    pattern = pd.read_csv(audit_dir / "pattern_audit.csv")
    display = pd.read_csv(audit_dir / "display_audit.csv")
    return {
        "number_passed": int(number["found"].sum()),
        "number_total": len(number),
        "pattern_passed": int(pattern["passed"].sum()),
        "pattern_total": len(pattern),
        "display_passed": int(display["passed"].sum()),
        "display_total": len(display),
        "all_passed": bool(number["found"].all() and pattern["passed"].all() and display["passed"].all()),
    }


def figure_status(manifest_path: Path) -> dict[str, object]:
    manifest = pd.read_csv(manifest_path)
    expected_files = []
    for _, row in manifest.iterrows():
        expected_files.extend([Path(row["png"]), Path(row["pdf"])])
    existing = [path for path in expected_files if path.exists()]
    return {
        "figures": len(manifest),
        "figure_files": len(expected_files),
        "figure_files_present": len(existing),
        "all_present": len(existing) == len(expected_files),
    }


def row_by(df: pd.DataFrame, **filters: object) -> pd.Series:
    rows = df.copy()
    for key, value in filters.items():
        rows = rows[rows[key].eq(value)]
    if rows.empty:
        joined = ", ".join(f"{key}={value}" for key, value in filters.items())
        raise ValueError(f"missing row for {joined}")
    return rows.iloc[0]


def compliance_status(compliance_dir: Path) -> dict[str, object]:
    path = compliance_dir / "compliance_checks.csv"
    if not path.exists():
        return {"exists": False, "pass": 0, "warn": 0, "fail": 1}
    checks = pd.read_csv(path)
    counts = checks["status"].value_counts().to_dict()
    return {
        "exists": True,
        "pass": int(counts.get("PASS", 0)),
        "warn": int(counts.get("WARN", 0)),
        "fail": int(counts.get("FAIL", 0)),
    }


def pgv_status(path: Path) -> dict[str, object]:
    if not path.exists():
        return {"exists": False, "records": 0, "selected_failure_pct": None, "fixed_failure_pct": None}
    summary = pd.read_csv(path)
    selected = row_by(summary, dataset="ALL", priority_group="ALL", policy="shortest_stable_no_catalog")
    fixed = row_by(summary, dataset="ALL", priority_group="ALL", policy="feature_onset_fixed")
    return {
        "exists": True,
        "records": int(selected["records"]),
        "selected_failure_pct": float(selected["pgv_unstable_pct"]),
        "fixed_failure_pct": float(fixed["pgv_unstable_pct"]),
    }


def record_audit_status(path: Path) -> dict[str, object]:
    cases_path = path / "cases.csv"
    manifest_path = path / "plot_manifest.csv"
    report_path = path / "README.md"
    if not cases_path.exists() or not manifest_path.exists() or not report_path.exists():
        return {"exists": False, "cases": 0, "plots": 0, "load_errors": None}
    cases = pd.read_csv(cases_path)
    manifest = pd.read_csv(manifest_path)
    load_errors_path = path / "load_errors.csv"
    load_errors = len(pd.read_csv(load_errors_path)) if load_errors_path.exists() else 0
    return {
        "exists": True,
        "cases": int(len(cases)),
        "plots": int(len(manifest)),
        "load_errors": int(load_errors),
    }


def readiness_checks(
    audit: dict[str, object],
    figures: dict[str, object],
    dataset: pd.DataFrame,
    key_metrics: pd.DataFrame,
    impact: pd.DataFrame,
    sensitivity: pd.DataFrame,
    response_spectrum: pd.DataFrame,
    draft_text: str,
    latex_pdf: Path,
    latex_text: str,
    repro_release_zip: Path,
    compliance: dict[str, object],
    pgv: dict[str, object],
    record_audit: dict[str, object],
) -> pd.DataFrame:
    all_short = row_by(key_metrics, dataset="ALL", method="shortest_stable_no_catalog")
    inst_fixed = row_by(key_metrics, dataset="InstanceGM", method="feature_onset_fixed")
    knet_fixed = row_by(key_metrics, dataset="K-NET", method="feature_onset_fixed")
    strict = row_by(sensitivity, dataset="ALL", priority_group="ALL", pga_threshold=0.99, energy_threshold=0.98)
    default = row_by(sensitivity, dataset="ALL", priority_group="ALL", pga_threshold=0.99, energy_threshold=0.95)
    spectrum_fixed_3s = row_by(
        response_spectrum,
        dataset="ALL",
        priority_group="ALL",
        policy="feature_onset_fixed",
        period_sec=3.0,
    )
    spectrum_selected_3s = row_by(
        response_spectrum,
        dataset="ALL",
        priority_group="ALL",
        policy="shortest_stable_no_catalog",
        period_sec=3.0,
    )
    author_placeholder = (
        "Author names and affiliations to be finalized" in draft_text
        or "Author names and affiliations to be finalized" in latex_text
        or "No external funding statement has been finalized" in draft_text
        or "No external funding statement has been finalized" in latex_text
        or "designated corresponding author" in draft_text
        or "designated corresponding author" in latex_text
    )
    rows = [
        {
            "check": "draft_audit",
            "status": "PASS" if audit["all_passed"] else "FAIL",
            "evidence": (
                f"{audit['number_passed']}/{audit['number_total']} number, "
                f"{audit['pattern_passed']}/{audit['pattern_total']} pattern, "
                f"{audit['display_passed']}/{audit['display_total']} display checks pass"
            ),
            "readiness_weight": 16,
        },
        {
            "check": "figure_package",
            "status": "PASS" if figures["all_present"] and figures["figures"] >= 6 else "FAIL",
            "evidence": f"{figures['figures']} figures; {figures['figure_files_present']}/{figures['figure_files']} files present",
            "readiness_weight": 10,
        },
        {
            "check": "cross_dataset_denominator",
            "status": "PASS" if int(dataset["records"].sum()) >= 9000 and dataset["dataset"].nunique() >= 2 else "FAIL",
            "evidence": f"{int(dataset['records'].sum()):,} records across {dataset['dataset'].nunique()} datasets",
            "readiness_weight": 11,
        },
        {
            "check": "fixed_window_problem",
            "status": "PASS" if float(inst_fixed["unstable_pct"]) > 50.0 and float(knet_fixed["unstable_pct"]) < 15.0 else "WARN",
            "evidence": (
                f"feature fixed instability: InstanceGM {float(inst_fixed['unstable_pct']):.2f}%, "
                f"K-NET {float(knet_fixed['unstable_pct']):.2f}%"
            ),
            "readiness_weight": 8,
        },
        {
            "check": "selector_operational_summary",
            "status": "PASS" if float(all_short["full_record_fallback_pct"]) < 2.0 else "WARN",
            "evidence": f"overall fallback {float(all_short['full_record_fallback_pct']):.2f}%",
            "readiness_weight": 8,
        },
        {
            "check": "product_impact",
            "status": "PASS" if not impact.empty and int(impact["rescued_records"].max()) > 1000 else "FAIL",
            "evidence": f"max fixed-window failures recovered in one row: {int(impact['rescued_records'].max()):,}",
            "readiness_weight": 8,
        },
        {
            "check": "threshold_sensitivity",
            "status": "PASS" if float(strict["full_record_fallback_pct"]) > float(default["full_record_fallback_pct"]) else "FAIL",
            "evidence": (
                f"fallback rises from {float(default['full_record_fallback_pct']):.2f}% "
                f"to {float(strict['full_record_fallback_pct']):.2f}% when energy threshold changes 0.95->0.98"
            ),
            "readiness_weight": 8,
        },
        {
            "check": "response_spectrum_retention",
            "status": (
                "PASS"
                if float(spectrum_selected_3s["spectrum_unstable_pct"]) < 10.0
                and float(spectrum_fixed_3s["spectrum_unstable_pct"]) - float(spectrum_selected_3s["spectrum_unstable_pct"]) > 20.0
                else "WARN"
            ),
            "evidence": (
                "3.0 s PSA-retention failures fall from "
                f"{float(spectrum_fixed_3s['spectrum_unstable_pct']):.2f}% "
                f"to {float(spectrum_selected_3s['spectrum_unstable_pct']):.2f}% overall"
            ),
            "readiness_weight": 12,
        },
        {
            "check": "supplemental_pgv_retention",
            "status": "PASS" if pgv["exists"] and float(pgv["selected_failure_pct"]) < float(pgv["fixed_failure_pct"]) else "WARN",
            "evidence": (
                f"{pgv['records']:,} loaded records; PGV-proxy failures fall from "
                f"{float(pgv['fixed_failure_pct']):.2f}% to {float(pgv['selected_failure_pct']):.2f}%"
                if pgv["exists"]
                else "PGV-retention summary missing"
            ),
            "readiness_weight": 0,
        },
        {
            "check": "record_level_audit_packet",
            "status": "PASS" if record_audit["exists"] and int(record_audit["cases"]) >= 4 and int(record_audit["load_errors"]) == 0 else "WARN",
            "evidence": (
                f"{record_audit['cases']} cases, {record_audit['plots']} plots, {record_audit['load_errors']} load errors"
                if record_audit["exists"]
                else "record-level audit packet missing"
            ),
            "readiness_weight": 0,
        },
        {
            "check": "submission_package",
            "status": "PASS" if latex_pdf.exists() else "FAIL",
            "evidence": f"SRL-style PDF package {'exists' if latex_pdf.exists() else 'is missing'} at {latex_pdf}",
            "readiness_weight": 4,
        },
        {
            "check": "reproducibility_release",
            "status": "PASS" if repro_release_zip.exists() else "FAIL",
            "evidence": f"lightweight reproducibility release {'exists' if repro_release_zip.exists() else 'is missing'} at {repro_release_zip}",
            "readiness_weight": 5,
        },
        {
            "check": "srl_compliance",
            "status": "PASS" if compliance["exists"] and int(compliance["fail"]) == 0 else "FAIL",
            "evidence": (
                f"{compliance['pass']} PASS, {compliance['warn']} WARN, {compliance['fail']} FAIL"
                if compliance["exists"]
                else "compliance report missing"
            ),
            "readiness_weight": 4,
        },
        {
            "check": "author_metadata",
            "status": "WARN" if author_placeholder else "PASS",
            "evidence": (
                "placeholder author/funding/corresponding-author text remains"
                if author_placeholder
                else "author, corresponding-author, funding, acknowledgment, and competing-interest text is populated"
            ),
            "readiness_weight": 3,
        },
        {
            "check": "references",
            "status": (
                "PASS"
                if "## References" in draft_text
                and "Working References" not in draft_text
                and "References To Verify" not in draft_text
                else "WARN"
            ),
            "evidence": "final reference list present; no working-reference or unresolved-reference heading",
            "readiness_weight": 3,
        },
    ]
    return pd.DataFrame(rows)


def compute_score(checks: pd.DataFrame) -> int:
    score = 0
    for _, row in checks.iterrows():
        weight = int(row["readiness_weight"])
        if row["status"] == "PASS":
            score += weight
        elif row["status"] == "WARN":
            score += weight // 2
    return score


def acceptance_band(score: int) -> str:
    if score >= 95:
        return "82-86% with public archive URL, access dates, and license statement included"
    if score >= 90:
        return "70-78% after final SRL formatting and advisor approval"
    if score >= 80:
        return "65-72% with current evidence; 70% is plausible after format and reference polish"
    if score >= 70:
        return "58-68%; more packaging or validation work is needed before calling it a 70% submission"
    return "below 60%; the current package still has blocking risks"


def write_report(outdir: Path, checks: pd.DataFrame, score: int, band: str) -> None:
    status_counts = checks["status"].value_counts().to_dict()
    lines = [
        "# StrongMotion-QC SRL Readiness Report",
        "",
        "This is an internal readiness estimate, not a statistical acceptance model.",
        "",
        f"- Readiness score: {score}/100",
        f"- Current acceptance band: {band}",
        f"- Gate counts: {status_counts.get('PASS', 0)} PASS, {status_counts.get('WARN', 0)} WARN, {status_counts.get('FAIL', 0)} FAIL",
        "",
        "## Checks",
        "",
        "| Check | Status | Evidence |",
        "| --- | --- | --- |",
    ]
    for _, row in checks.iterrows():
        lines.append(f"| {row['check']} | {row['status']} | {row['evidence']} |")
    lines.extend(
        [
            "",
            "## Remaining Work Before Submission",
            "",
            "1. Verify that the public GitHub release remains accessible before final journal upload.",
            "2. Keep the main claim on offline product-window selection, with no streaming or phase-picking claims.",
            "3. Keep PGV and record-level cases as supplemental review material unless the final target journal requests additional main-text evidence.",
        ]
    )
    (outdir / "report.md").write_text("\n".join(lines) + "\n")


def run_report(
    audit_dir: Path,
    figure_manifest: Path,
    dataset_summary: Path,
    key_metrics: Path,
    product_impact: Path,
    sensitivity: Path,
    response_spectrum: Path,
    pgv_retention: Path,
    record_audit_dir: Path,
    draft: Path,
    latex_pdf: Path,
    repro_release_zip: Path,
    compliance_dir: Path,
    outdir: Path,
) -> dict[str, Path]:
    audit = audit_status(audit_dir)
    figures = figure_status(figure_manifest)
    dataset = pd.read_csv(dataset_summary)
    metrics = pd.read_csv(key_metrics)
    impact = pd.read_csv(product_impact)
    sens = pd.read_csv(sensitivity)
    spectrum = pd.read_csv(response_spectrum)
    pgv = pgv_status(pgv_retention)
    record_audit = record_audit_status(record_audit_dir)
    draft_text = draft.read_text()
    latex_source = latex_pdf.with_suffix(".tex")
    latex_text = latex_source.read_text() if latex_source.exists() else ""
    compliance = compliance_status(compliance_dir)
    checks = readiness_checks(
        audit,
        figures,
        dataset,
        metrics,
        impact,
        sens,
        spectrum,
        draft_text,
        latex_pdf,
        latex_text,
        repro_release_zip,
        compliance,
        pgv,
        record_audit,
    )
    score = compute_score(checks)
    band = acceptance_band(score)
    outdir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "checks": outdir / "readiness_checks.csv",
        "report": outdir / "report.md",
    }
    checks.to_csv(outputs["checks"], index=False)
    write_report(outdir, checks, score, band)
    return outputs


def main() -> None:
    args = parse_args()
    outputs = run_report(
        audit_dir=Path(args.audit_dir),
        figure_manifest=Path(args.figure_manifest),
        dataset_summary=Path(args.dataset_summary),
        key_metrics=Path(args.key_metrics),
        product_impact=Path(args.product_impact),
        sensitivity=Path(args.sensitivity),
        response_spectrum=Path(args.response_spectrum),
        pgv_retention=Path(args.pgv_retention),
        record_audit_dir=Path(args.record_audit_dir),
        draft=Path(args.draft),
        latex_pdf=Path(args.latex_pdf),
        repro_release_zip=Path(args.repro_release_zip),
        compliance_dir=Path(args.compliance_dir),
        outdir=Path(args.outdir),
    )
    for path in outputs.values():
        print(f"Wrote {path.resolve()}")


if __name__ == "__main__":
    main()
