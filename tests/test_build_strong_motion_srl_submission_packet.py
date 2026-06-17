"""Unit tests for the StrongMotion-QC SRL submission packet builder."""

from __future__ import annotations

import os
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts import build_strong_motion_srl_submission_packet as packet


def touch(path: Path, payload: bytes | str = "x\n") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(payload, bytes):
        path.write_bytes(payload)
    else:
        path.write_text(payload, encoding="utf-8")


class BuildStrongMotionSrlSubmissionPacketTests(unittest.TestCase):
    def test_packet_includes_strong_motion_metadata_worksheet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manuscript = root / "manuscript"
            figures = root / "figures"
            audit = root / "audit"
            readiness = root / "readiness"
            release = root / "release"
            compliance = root / "compliance"
            metadata = root / "metadata"
            metadata_template = root / "strong_motion_metadata.csv"
            pgv = root / "pgv"
            record_audit = root / "record_audit"
            pnw_selector = root / "pnw_selector"
            pnw_response = root / "pnw_response"
            production_case = root / "production_case"
            chinese_markdown = root / "docs/strong_motion_qc_srl_manuscript_zh.md"
            chinese_manuscript = root / "chinese_manuscript"
            outdir = root / "packet"

            touch(manuscript / "main.pdf", b"%PDF")
            touch(manuscript / "main.tex")
            touch(manuscript / "strong_motion_qc_srl_draft.md")
            touch(manuscript / "latex_build_report.md")
            touch(manuscript / "tables/table_01.tex")
            touch(figures / "figure_manifest.csv", "figure_id,png,pdf\n1,a.png,a.pdf\n")
            touch(figures / "smqc_figure_01_workflow.pdf", b"%PDF")
            for name in ["README.md", "number_audit.csv", "pattern_audit.csv", "display_audit.csv"]:
                touch(audit / name)
            touch(readiness / "report.md")
            touch(readiness / "readiness_checks.csv")
            touch(release / "README.md")
            touch(release / "REPRODUCTION_COMMANDS.md")
            touch(release / "LICENSE")
            touch(release / "ARCHIVE_METADATA_TEMPLATE.md")
            touch(release / "metadata/file_checksums.csv")
            touch(release / "metadata/data_source_manifest.csv")
            touch(root / "release.zip", b"PK")
            touch(compliance / "report.md")
            touch(compliance / "compliance_checks.csv")
            touch(
                metadata_template,
                "\n".join(
                    [
                        "field_id,value",
                        "srl_classification_terms,strong-motion records",
                        "author_order,Haoyu Zhou; Qiang Ma",
                        "corresponding_author_name,Qiang Ma",
                        "corresponding_author_email,maqiang@iem.ac.cn",
                        "funding_statement,This research received no external funding.",
                        '"data_provider_acknowledgments","The authors thank the data providers."',
                    ]
                )
                + "\n",
            )
            touch(metadata / "submission_metadata_checks.csv")
            touch(metadata / "report.md")
            touch(metadata / "metadata_worksheet_items.csv")
            touch(metadata / "metadata_worksheet_zh.md", "# 投稿元数据中英双语工作表\n")
            touch(metadata / "title_page_and_statements_draft.md")
            touch(pgv / "summary.csv", "dataset,policy,records\nALL,shortest_stable_no_catalog,1\n")
            touch(pgv / "README.md", "# Relative PGV retention\n")
            touch(pgv / "load_errors.csv", "record_uid,dataset,priority_group,error\n")
            touch(record_audit / "README.md", "# Record audit\n")
            touch(record_audit / "cases.csv", "case_id,record_uid\ncase_01,r1\n")
            touch(record_audit / "case_windows.csv", "case_id,policy\ncase_01,shortest_stable_no_catalog\n")
            touch(record_audit / "plot_manifest.csv", "case_id,path\ncase_01,figures/case_01.pdf\n")
            touch(record_audit / "figures/case_01.pdf", b"%PDF")
            touch(record_audit / "figures/case_01.png", b"PNG")
            touch(pnw_selector / "summary.csv", "dataset,policy,records\nPNWAccelerometers,shortest_stable_no_catalog,6107\n")
            touch(pnw_selector / "candidate_usage.csv", "dataset,policy,selected_candidate,records\nPNWAccelerometers,shortest_stable_no_catalog,full_record,1\n")
            touch(pnw_response / "summary.csv", "dataset,policy,period_sec,records\nPNWAccelerometers,shortest_stable_no_catalog,3.0,6107\n")
            touch(production_case / "README.md", "# Production case\n")
            touch(production_case / "production_route_summary.csv", "dataset,production_route,records\nALL,ALL,1\n")
            touch(production_case / "production_routes.csv", "record_uid,dataset,production_route\nr1,PNWAccelerometers,stable_window_accept\n")
            touch(production_case / "review_queue.csv", "record_uid,dataset,production_route\nr2,PNWAccelerometers,long_period_psa_review\n")
            touch(chinese_markdown, "# 中文论文稿\n")
            touch(chinese_manuscript / "main.pdf", b"%PDF")
            touch(chinese_manuscript / "main.tex")
            touch(chinese_manuscript / "latex_build_report.md")

            source_paths = [
                "outputs/strong_motion_qc_dataset_table_knet22119_hp1_inst3000/dataset_summary.csv",
                "outputs/strong_motion_qc_dataset_table_knet22119_hp1_inst3000/priority_strata_summary.csv",
                "outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/summary.csv",
                "outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/candidate_usage.csv",
                "outputs/strong_motion_qc_product_impact_knet22119_hp1_inst3000/product_impact_summary.csv",
                "outputs/strong_motion_qc_selector_sensitivity_knet22119_hp1_inst3000/sensitivity_summary.csv",
                "outputs/strong_motion_qc_response_spectrum_knet22119_hp1_inst3000/summary.csv",
            ]
            for relpath in source_paths:
                touch(root / relpath)
            touch(root / "docs/strong_motion_qc_srl_reference_verification.md", "# Reference verification\n")

            old_cwd = Path.cwd()
            os.chdir(root)
            try:
                result = packet.build_packet(
                    outdir=outdir,
                    manuscript_dir=manuscript,
                    figure_dir=figures,
                    audit_dir=audit,
                    readiness_dir=readiness,
                    repro_release_dir=release,
                    repro_release_zip=root / "release.zip",
                    compliance_dir=compliance,
                    metadata_template=metadata_template,
                    metadata_dir=metadata,
                    pgv_retention_dir=pgv,
                    record_audit_dir=record_audit,
                    pnw_selector_dir=pnw_selector,
                    pnw_response_dir=pnw_response,
                    production_case_dir=production_case,
                    chinese_markdown=chinese_markdown,
                    chinese_manuscript_dir=chinese_manuscript,
                )
            finally:
                os.chdir(old_cwd)

            with zipfile.ZipFile(result["zip"]) as archive:
                names = set(archive.namelist())
                cover_letter = archive.read("packet/statements/cover_letter_draft.md").decode()

        self.assertEqual(result["missing"], 0)
        self.assertIn("Haoyu Zhou and Qiang Ma", cover_letter)
        self.assertNotIn("Author names to be finalized", cover_letter)
        self.assertIn("packet/statements/metadata_worksheet_zh.md", names)
        self.assertIn("packet/statements/title_page_and_statements_draft.md", names)
        self.assertIn("packet/evidence/submission_metadata_report.md", names)
        self.assertIn("packet/evidence/reference_verification.md", names)
        self.assertIn("packet/evidence/srl_format_checklist.md", names)
        self.assertIn("packet/manuscript_flat/main.tex", names)
        self.assertIn("packet/manuscript_flat/smqc_figure_01_workflow.pdf", names)
        self.assertIn("packet/statements/strong_motion_qc_srl_submission_metadata_template.csv", names)
        self.assertIn("packet/reproducibility/release_LICENSE", names)
        self.assertIn("packet/reproducibility/release_ARCHIVE_METADATA_TEMPLATE.md", names)
        self.assertIn("packet/source_data/pgv_retention_summary.csv", names)
        self.assertIn("packet/evidence/pgv_retention_report.md", names)
        self.assertIn("packet/evidence/pgv_retention_load_errors.csv", names)
        self.assertIn("packet/evidence/record_audit_report.md", names)
        self.assertIn("packet/source_data/pnw_product_window_selector_summary.csv", names)
        self.assertIn("packet/source_data/pnw_response_spectrum_summary.csv", names)
        self.assertIn("packet/evidence/production_case_report.md", names)
        self.assertIn("packet/source_data/production_route_summary.csv", names)
        self.assertIn("packet/source_data/production_review_queue.csv", names)
        self.assertIn("packet/source_data/record_audit_cases.csv", names)
        self.assertIn("packet/figures/record_audit/case_01.pdf", names)
        self.assertIn("packet/figures/record_audit/case_01.png", names)
        self.assertIn("packet/chinese_review/main.pdf", names)
        self.assertIn("packet/chinese_review/strong_motion_qc_srl_manuscript_zh.md", names)


if __name__ == "__main__":
    unittest.main()
