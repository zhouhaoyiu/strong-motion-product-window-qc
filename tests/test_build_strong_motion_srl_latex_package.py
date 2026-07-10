"""Tests for the StrongMotion-QC SRL LaTeX package builder."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts import build_strong_motion_srl_latex_package as latex_builder


class BuildStrongMotionSrlLatexPackageTests(unittest.TestCase):
    def test_display_items_are_inserted_into_body_near_mentions(self) -> None:
        body = "\n\n".join(
            [
                "Figure 1 summarizes the two-stage audit.",
                "The analyzed population contains 44,674 acceleration records (Table 1).",
                "The magnitude strata are listed in Table 2.",
                "Figure 2 reports the fixed-duration sensitivity.",
                "Figure 4 shows the corresponding PSA failures.",
                "Figure 3 reports the final routing and duration.",
                "Table 3 lists the routing percentages.",
                "Figure 5 reports this preprocessing sensitivity.",
                "Figure 6 reports the SNR-stratified results.",
            ]
        )
        tables = ["TABLE ONE", "TABLE TWO", "TABLE THREE"]

        updated = latex_builder.insert_display_items(body, tables)

        self.assertIn("TABLE ONE", updated)
        self.assertIn("TABLE TWO", updated)
        self.assertIn("TABLE THREE", updated)
        self.assertIn(r"\includegraphics[width=0.95\textwidth]{figures/smqc_figure_01_workflow.pdf}", updated)
        self.assertIn(r"\includegraphics[width=0.95\textwidth]{figures/smqc_figure_06_response_spectrum_retention.pdf}", updated)

    def test_title_page_uses_submission_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            metadata = Path(tmp) / "metadata.csv"
            metadata.write_text(
                "\n".join(
                    [
                        "field_id,value",
                        "author_order,Haoyu Zhou; Qiang Ma",
                        '"author_emails","Haoyu Zhou: zhouhaoyiu@gmail.com; Qiang Ma: maqiang@iem.ac.cn"',
                        '"author_affiliations","Haoyu Zhou: Institute of Engineering Mechanics, China Earthquake Administration, Harbin, Heilongjiang, China; Qiang Ma: Institute of Engineering Mechanics, China Earthquake Administration, Harbin, Heilongjiang, China"',
                        "corresponding_author_name,Qiang Ma",
                        "corresponding_author_email,maqiang@iem.ac.cn",
                        '"corresponding_author_mailing_address","Institute of Engineering Mechanics, China Earthquake Administration, 29 Xuefu Road, Nangang District, Harbin, Heilongjiang, China"',
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            authors = latex_builder.author_block(metadata)
            tex = latex_builder.build_latex("Example Title", authors, "Body", "Tables", "Figures")

        self.assertIn("Haoyu Zhou", tex)
        self.assertIn("Qiang Ma", tex)
        self.assertIn("zhouhaoyiu@gmail.com", tex)
        self.assertIn("maqiang@iem.ac.cn", tex)
        self.assertIn("29 Xuefu Road", tex)
        self.assertNotIn("Author names and affiliations to be finalized", tex)


if __name__ == "__main__":
    unittest.main()
