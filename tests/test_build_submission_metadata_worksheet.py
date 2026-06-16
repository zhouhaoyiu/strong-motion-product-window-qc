"""Unit tests for submission metadata worksheet generation."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from scripts import build_submission_metadata_worksheet as worksheet


class BuildSubmissionMetadataWorksheetTests(unittest.TestCase):
    def test_worksheet_items_add_bilingual_guidance(self) -> None:
        df = pd.DataFrame(
            [
                {
                    "field_id": "author_order",
                    "section": "authors",
                    "label": "Author order",
                    "required_before_submission": "yes",
                    "status": "pending",
                    "value": "",
                }
            ]
        )

        items = worksheet.worksheet_items(df)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].chinese_label, "作者顺序")
        self.assertIn("最终投稿顺序", items[0].question_zh)

    def test_classification_guidance_matches_strong_motion_route(self) -> None:
        df = pd.DataFrame(
            [
                {
                    "field_id": "srl_classification_terms",
                    "section": "journal",
                    "label": "SRL classification terms",
                    "required_before_submission": "yes",
                    "status": "pending",
                    "value": "",
                }
            ]
        )

        items = worksheet.worksheet_items(df)

        self.assertIn("strong-motion records", items[0].suggested_format)
        self.assertNotIn("phase picking", items[0].suggested_format)

    def test_outputs_include_pending_title_page_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            metadata = pd.DataFrame(
                [
                    {
                        "field_id": "journal_target",
                        "section": "journal",
                        "label": "Target journal",
                        "required_before_submission": "yes",
                        "allowed_final_statuses": "complete",
                        "status": "complete",
                        "value": "Seismological Research Letters regular article",
                        "notes": "",
                    },
                    {
                        "field_id": "author_order",
                        "section": "authors",
                        "label": "Author order",
                        "required_before_submission": "yes",
                        "allowed_final_statuses": "complete",
                        "status": "pending",
                        "value": "",
                        "notes": "",
                    },
                    {
                        "field_id": "competing_interests",
                        "section": "statements",
                        "label": "Declaration of competing interests",
                        "required_before_submission": "yes",
                        "allowed_final_statuses": "complete",
                        "status": "complete",
                        "value": "The authors declare no competing interests.",
                        "notes": "",
                    },
                ]
            )
            outdir = root / "out"
            items = worksheet.worksheet_items(metadata)
            worksheet.write_worksheet(items, outdir)
            worksheet.write_title_page_and_statements(metadata, "Example Title", outdir)

            report = (outdir / "metadata_worksheet_zh.md").read_text(encoding="utf-8")
            title_page = (outdir / "title_page_and_statements_draft.md").read_text(encoding="utf-8")

        self.assertIn("投稿元数据中英双语工作表", report)
        self.assertIn("作者顺序", report)
        self.assertIn("[PENDING: Author order]", title_page)
        self.assertIn("Declaration of Competing Interests", title_page)
        self.assertIn("Example Title", title_page)
        self.assertIn("offline processing-window audit", title_page)
        self.assertNotIn("external stress test and limitation", title_page)


if __name__ == "__main__":
    unittest.main()
