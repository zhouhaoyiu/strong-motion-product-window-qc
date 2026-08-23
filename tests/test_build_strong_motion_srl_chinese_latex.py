"""Tests for the formal Chinese StrongMotion-QC manuscript builder."""

from __future__ import annotations

import unittest

from scripts import build_strong_motion_srl_chinese_latex as latex_builder


class BuildStrongMotionSrlChineseLatexTests(unittest.TestCase):
    def test_explicit_chinese_section_numbers_are_not_duplicated(self) -> None:
        markdown = "## 摘要\n\n## 1 引言\n\n### 1.1 研究背景\n"

        updated = latex_builder.mark_headings_unnumbered(markdown)

        self.assertIn("## 摘要 {.unnumbered}", updated)
        self.assertIn("## 1 引言 {.unnumbered}", updated)
        self.assertIn("### 1.1 研究背景 {.unnumbered}", updated)

    def test_filter_sensitivity_figure_uses_current_filename(self) -> None:
        figure_names = [filename for filename, _caption in latex_builder.FIGURES]

        self.assertIn("smqc_figure_05_filter_sensitivity.pdf", figure_names)
        self.assertNotIn("smqc_figure_05_threshold_sensitivity.pdf", figure_names)


if __name__ == "__main__":
    unittest.main()
