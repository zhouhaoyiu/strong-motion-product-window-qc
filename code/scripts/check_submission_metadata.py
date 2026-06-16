#!/usr/bin/env python3
"""Check human submission metadata decisions for journal handoff."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "field_id",
    "section",
    "label",
    "required_before_submission",
    "allowed_final_statuses",
    "status",
    "value",
    "notes",
]

ALLOWED_STATUSES = {"pending", "complete", "deferred", "not_applicable"}

REQUIRED_FIELD_IDS = {
    "journal_target",
    "submission_issue_choice",
    "srl_classification_terms",
    "flinn_engdahl_region",
    "major_earthquake_name",
    "license_choice",
    "editor_background_information",
    "author_order",
    "author_affiliations",
    "corresponding_author_name",
    "corresponding_author_email",
    "corresponding_author_mailing_address",
    "funding_statement",
    "competing_interests",
    "author_approval",
    "code_archive_url",
    "data_access_dates",
    "supplemental_material_decision",
    "qc_review_decision",
    "knet_scope_decision",
}


@dataclass(frozen=True)
class MetadataCheck:
    field_id: str
    section: str
    label: str
    required_before_submission: str
    allowed_final_statuses: str
    metadata_status: str
    status: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", default="docs/submission_metadata_template.csv")
    parser.add_argument("--outdir", default="outputs/submission_metadata")
    return parser.parse_args()


def clean(value: object) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def truthy(value: object) -> bool:
    return clean(value).lower() in {"1", "true", "yes", "y"}


def split_statuses(value: object) -> set[str]:
    return {part.strip() for part in clean(value).split(";") if part.strip()}


def validate_table(df: pd.DataFrame) -> list[str]:
    errors = []
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing_columns:
        errors.append("missing columns: " + ", ".join(missing_columns))
        return errors
    duplicate_ids = sorted(df.loc[df["field_id"].astype(str).duplicated(), "field_id"].astype(str).unique())
    if duplicate_ids:
        errors.append("duplicate field_id values: " + ", ".join(duplicate_ids))
    missing_ids = sorted(REQUIRED_FIELD_IDS - set(df["field_id"].astype(str)))
    if missing_ids:
        errors.append("missing required field_id values: " + ", ".join(missing_ids))
    return errors


def check_row(row: pd.Series) -> MetadataCheck:
    field_id = clean(row["field_id"])
    section = clean(row["section"])
    label = clean(row["label"])
    required = truthy(row["required_before_submission"])
    allowed_final = split_statuses(row["allowed_final_statuses"])
    metadata_status = clean(row["status"]).lower()
    value = clean(row["value"])
    notes = clean(row["notes"])
    failures = []
    warnings = []

    if metadata_status not in ALLOWED_STATUSES:
        failures.append(f"invalid status `{metadata_status}`")
    if not allowed_final:
        failures.append("allowed_final_statuses is empty")
    if metadata_status == "complete" and not value:
        failures.append("complete field has empty value")
    if metadata_status in {"deferred", "not_applicable"} and not notes:
        warnings.append(f"{metadata_status} field should include an explanatory note")
    if required and metadata_status not in allowed_final:
        warnings.append(
            "required before submission but not final "
            f"(status `{metadata_status}`, allowed final: {', '.join(sorted(allowed_final))})"
        )
    elif not required and metadata_status == "pending":
        warnings.append("optional field is still pending")

    if failures:
        status = "FAIL"
        detail = "; ".join(failures)
    elif warnings:
        status = "WARN"
        detail = "; ".join(warnings)
    else:
        status = "PASS"
        detail = "metadata field is ready or explicitly finalized"

    return MetadataCheck(
        field_id=field_id,
        section=section,
        label=label,
        required_before_submission="yes" if required else "no",
        allowed_final_statuses=";".join(sorted(allowed_final)),
        metadata_status=metadata_status,
        status=status,
        detail=detail,
    )


def collect_checks(path: Path) -> tuple[list[MetadataCheck], list[str]]:
    if not path.exists():
        return [], [f"metadata file missing: {path}"]
    df = pd.read_csv(path, keep_default_na=False)
    table_errors = validate_table(df)
    if table_errors:
        return [], table_errors
    return [check_row(row) for _, row in df.iterrows()], []


def write_outputs(checks: list[MetadataCheck], table_errors: list[str], outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    rows = [check.__dict__ for check in checks]
    if table_errors:
        rows = [
            {
                "field_id": "__table__",
                "section": "metadata",
                "label": "metadata table",
                "required_before_submission": "yes",
                "allowed_final_statuses": "complete",
                "metadata_status": "invalid",
                "status": "FAIL",
                "detail": "; ".join(table_errors),
            }
        ]
    with (outdir / "submission_metadata_checks.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(MetadataCheck.__dataclass_fields__.keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    counts = {status: sum(row["status"] == status for row in rows) for status in ["PASS", "WARN", "FAIL"]}
    lines = [
        "# Submission Metadata Check",
        "",
        "This report tracks human-provided journal metadata that cannot be inferred",
        "from the computational artifacts.",
        "",
        f"- Passed: {counts['PASS']}",
        f"- Warnings: {counts['WARN']}",
        f"- Failed: {counts['FAIL']}",
        "",
    ]
    for status in ["FAIL", "WARN"]:
        subset = [row for row in rows if row["status"] == status]
        if subset:
            lines.extend([f"## {status.title()} Items", ""])
            for row in subset:
                lines.append(f"- **{row['field_id']}**: {row['detail']}")
            lines.append("")
    lines.extend(
        [
            "## All Fields",
            "",
            "| Field | Section | Required | Metadata status | Check status | Detail |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            f"| {row['field_id']} | {row['section']} | {row['required_before_submission']} | "
            f"{row['metadata_status']} | {row['status']} | {row['detail']} |"
        )
    (outdir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    checks, table_errors = collect_checks(Path(args.metadata))
    write_outputs(checks, table_errors, Path(args.outdir))
    rows = checks if not table_errors else [
        MetadataCheck("__table__", "metadata", "metadata table", "yes", "complete", "invalid", "FAIL", "; ".join(table_errors))
    ]
    counts = {status: sum(check.status == status for check in rows) for status in ["PASS", "WARN", "FAIL"]}
    print(f"Submission metadata: {counts['PASS']} PASS, {counts['WARN']} WARN, {counts['FAIL']} FAIL")
    print(f"Report written to {Path(args.outdir) / 'report.md'}")
    if counts["FAIL"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
