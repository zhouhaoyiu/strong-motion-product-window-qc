"""Tests for the current StrongMotion-QC SRL packet builder."""

from __future__ import annotations

import os
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts import build_strong_motion_srl_submission_packet as packet


def touch(path: Path, value: str | bytes = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, bytes):
        path.write_bytes(value)
    else:
        path.write_text(value)


class BuildStrongMotionSrlSubmissionPacketTests(unittest.TestCase):
    def test_packet_contains_only_current_evidence_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manuscript = root / "manuscript"
            figures = root / "figures"
            evidence = root / "evidence"
            metadata_dir = root / "metadata"
            chinese = root / "chinese"
            chinese_markdown = root / "docs/chinese.md"
            metadata = root / "docs/metadata.csv"

            touch(manuscript / "qc.pdf", b"%PDF")
            touch(manuscript / "main.tex", "\\includegraphics{figures/smqc_figure_01_workflow.pdf}\n")
            touch(manuscript / "strong_motion_qc_srl_draft.md")
            touch(manuscript / "latex_build_report.md")
            touch(manuscript / "tables/table_01.tex")
            touch(figures / "figure_manifest.csv")
            touch(figures / "smqc_figure_01_workflow.pdf", b"%PDF")
            touch(evidence / "README.md", "Result: 42 PASS, 0 FAIL.\n")
            touch(evidence / "checks.csv")
            touch(
                metadata,
                "field_id,value\n"
                "author_order,Haoyu Zhou; Qiang Ma\n"
                'ai_tool_disclosure,"OpenAI Codex version X assisted with editing; the authors validated all outputs."\n',
            )
            touch(metadata_dir / "metadata_worksheet_zh.md")
            touch(metadata_dir / "title_page_and_statements_draft.md")
            touch(chinese_markdown)
            touch(chinese / "qc_chinese.pdf", b"%PDF")
            touch(chinese / "main.tex")
            touch(chinese / "latex_build_report.md")
            touch(root / "docs/strong_motion_qc_srl_reference_verification.md")
            for source, _, _ in packet.SOURCE_DATA_FILES:
                touch(root / source)

            old_cwd = Path.cwd()
            os.chdir(root)
            try:
                result = packet.build_packet(
                    root / "packet",
                    manuscript,
                    figures,
                    evidence,
                    metadata,
                    metadata_dir,
                    chinese_markdown,
                    chinese,
                )
            finally:
                os.chdir(old_cwd)

            with zipfile.ZipFile(result["zip"]) as archive:
                names = set(archive.namelist())
                cover = archive.read("packet/statements/cover_letter.md").decode()

        self.assertEqual(result["missing"], 0)
        self.assertIn("44,674", cover)
        self.assertNotIn("53,463", cover)
        self.assertIn("packet/manuscript/qc.pdf", names)
        self.assertIn("packet/chinese_review/qc_chinese.pdf", names)
        self.assertIn("packet/evidence/evidence_checks.csv", names)
        self.assertIn("packet/source_data/pnw_snr_summary.csv", names)
        self.assertIn("packet/manuscript_flat/smqc_figure_01_workflow.pdf", names)
        self.assertNotIn("packet/evidence/production_case_report.md", names)


if __name__ == "__main__":
    unittest.main()
