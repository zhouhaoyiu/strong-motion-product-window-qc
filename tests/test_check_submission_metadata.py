"""Unit tests for submission metadata checks."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts.check_submission_metadata import collect_checks


def write_metadata(path: Path, rows: list[dict[str, str]]) -> None:
    pd.DataFrame(rows).to_csv(path, index=False)


def base_row(field_id: str, status: str = "complete", value: str = "value") -> dict[str, str]:
    return {
        "field_id": field_id,
        "section": "section",
        "label": field_id.replace("_", " "),
        "required_before_submission": "yes",
        "allowed_final_statuses": "complete",
        "status": status,
        "value": value,
        "notes": "",
    }


class CheckSubmissionMetadataTests(unittest.TestCase):
    def required_rows(self) -> list[dict[str, str]]:
        field_ids = [
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
        ]
        rows = [base_row(field_id) for field_id in field_ids]
        for row in rows:
            if row["field_id"] == "qc_review_decision":
                row["allowed_final_statuses"] = "complete;deferred"
            if row["field_id"] == "major_earthquake_name":
                row["allowed_final_statuses"] = "complete;not_applicable"
        return rows

    def test_complete_required_metadata_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.csv"
            write_metadata(path, self.required_rows())

            checks, errors = collect_checks(path)

        self.assertEqual(errors, [])
        self.assertTrue(all(check.status == "PASS" for check in checks))

    def test_pending_required_metadata_warns(self) -> None:
        rows = self.required_rows()
        author_row = next(row for row in rows if row["field_id"] == "author_order")
        author_row["status"] = "pending"
        author_row["value"] = ""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.csv"
            write_metadata(path, rows)

            checks, errors = collect_checks(path)

        self.assertEqual(errors, [])
        author_order = [check for check in checks if check.field_id == "author_order"][0]
        self.assertEqual(author_order.status, "WARN")
        self.assertIn("required before submission", author_order.detail)

    def test_complete_empty_value_fails(self) -> None:
        rows = self.required_rows()
        affiliation_row = next(row for row in rows if row["field_id"] == "author_affiliations")
        affiliation_row["value"] = ""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.csv"
            write_metadata(path, rows)

            checks, errors = collect_checks(path)

        self.assertEqual(errors, [])
        affiliations = [check for check in checks if check.field_id == "author_affiliations"][0]
        self.assertEqual(affiliations.status, "FAIL")
        self.assertIn("empty value", affiliations.detail)

    def test_missing_required_column_is_table_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "metadata.csv"
            pd.DataFrame({"field_id": ["journal_target"]}).to_csv(path, index=False)

            checks, errors = collect_checks(path)

        self.assertEqual(checks, [])
        self.assertTrue(errors)
        self.assertIn("missing columns", errors[0])


if __name__ == "__main__":
    unittest.main()
