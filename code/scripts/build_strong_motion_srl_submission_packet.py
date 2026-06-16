#!/usr/bin/env python3
"""Build the StrongMotion-QC SRL submission-review packet."""

from __future__ import annotations

import argparse
import csv
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path


DEFAULT_OUTDIR = "outputs/strong_motion_qc_srl_submission_packet_current"
DEFAULT_MANUSCRIPT_DIR = "manuscripts/strong_motion_qc_srl"
DEFAULT_FIGURE_DIR = "outputs/strong_motion_qc_figures_knet22119_hp1_inst3000"
DEFAULT_AUDIT_DIR = "outputs/strong_motion_qc_srl_draft_audit_knet22119_hp1_inst3000"
DEFAULT_READINESS_DIR = "outputs/strong_motion_qc_srl_readiness"
DEFAULT_REPRO_RELEASE_DIR = "outputs/strong_motion_qc_srl_reproducibility_release_current"
DEFAULT_REPRO_RELEASE_ZIP = "outputs/strong_motion_qc_srl_reproducibility_release_current.zip"
DEFAULT_COMPLIANCE_DIR = "outputs/strong_motion_qc_srl_compliance"
DEFAULT_METADATA_TEMPLATE = "docs/strong_motion_qc_srl_submission_metadata_template.csv"
DEFAULT_METADATA_DIR = "outputs/strong_motion_qc_srl_submission_metadata"
DEFAULT_PGV_RETENTION_DIR = "outputs/strong_motion_qc_pgv_retention_knet22119_hp1_inst3000"
DEFAULT_RECORD_AUDIT_DIR = "outputs/strong_motion_qc_record_audit_packet_knet22119_hp1_inst3000"
DEFAULT_CHINESE_MARKDOWN = "docs/strong_motion_qc_srl_manuscript_zh.md"
DEFAULT_CHINESE_MANUSCRIPT_DIR = "manuscripts/strong_motion_qc_srl_zh"


@dataclass(frozen=True)
class PacketFile:
    source: Path
    target: Path
    role: str
    required: bool = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    parser.add_argument("--manuscript-dir", default=DEFAULT_MANUSCRIPT_DIR)
    parser.add_argument("--figure-dir", default=DEFAULT_FIGURE_DIR)
    parser.add_argument("--audit-dir", default=DEFAULT_AUDIT_DIR)
    parser.add_argument("--readiness-dir", default=DEFAULT_READINESS_DIR)
    parser.add_argument("--repro-release-dir", default=DEFAULT_REPRO_RELEASE_DIR)
    parser.add_argument("--repro-release-zip", default=DEFAULT_REPRO_RELEASE_ZIP)
    parser.add_argument("--compliance-dir", default=DEFAULT_COMPLIANCE_DIR)
    parser.add_argument("--metadata-template", default=DEFAULT_METADATA_TEMPLATE)
    parser.add_argument("--metadata-dir", default=DEFAULT_METADATA_DIR)
    parser.add_argument("--pgv-retention-dir", default=DEFAULT_PGV_RETENTION_DIR)
    parser.add_argument("--record-audit-dir", default=DEFAULT_RECORD_AUDIT_DIR)
    parser.add_argument("--chinese-markdown", default=DEFAULT_CHINESE_MARKDOWN)
    parser.add_argument("--chinese-manuscript-dir", default=DEFAULT_CHINESE_MANUSCRIPT_DIR)
    return parser.parse_args()


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n")


def metadata_value(metadata_path: Path, field_id: str, default: str = "") -> str:
    if not metadata_path.exists():
        return default
    with metadata_path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("field_id") == field_id:
                return row.get("value", "").strip() or default
    return default


def cover_letter(metadata_path: Path) -> str:
    authors = metadata_value(metadata_path, "author_order", "Haoyu Zhou; Qiang Ma").replace("; ", " and ")
    ai_disclosure = metadata_value(metadata_path, "ai_tool_disclosure")
    return f"""
# Cover Letter Draft

Dear Editor,

We submit the manuscript "Auditable Product-Stable Window Selection for Strong-Motion Records" for consideration as a Regular Article in *Seismological Research Letters*.

The manuscript addresses a practical strong-motion processing problem: fixed processing windows can preserve peak motion, waveform energy, and response-spectrum quantities unevenly across archives. We evaluate this problem on 53,463 three-component records from InstanceGM and K-NET, identify energy truncation as the dominant fixed-window failure mechanism, and test an offline waveform-derived selector that chooses the shortest candidate window passing explicit product-retention checks.

The main contribution is an auditable product-window policy for strong-motion product preparation. Only 0.84% of records are assigned to full-record processing under the default criteria, and the selected-window duration differs by archive: 84.94 s for InstanceGM and 24.66 s for K-NET. A 5% damping response-spectrum audit shows that overall 3.0 s PSA-retention failures drop from 32.28% for feature-onset fixed windows to 5.56% for selected windows.

The manuscript is framed as a quality-control method for strong-motion product generation. The scope is offline archive and batch product preparation: processing-window selection is evaluated against full-record products before product tables are exported. The submission does not claim phase-picking performance, real-time warning capability, learned-model superiority, or replacement of human review.

All figures, tables, audit outputs, reproducibility instructions, the public GitHub release URL, access dates, and release-license text are included in the review packet.

AI-tool use is disclosed in the manuscript Data and Resources section. Current disclosure draft: {ai_disclosure}

Sincerely,

{authors}
"""


def data_resources_statement(metadata_path: Path) -> str:
    ai_disclosure = metadata_value(metadata_path, "ai_tool_disclosure")
    return """
# Data and Resources Statement Draft

Waveforms from the InstanceGM/INSTANCE data family and K-NET were used in this study. K-NET waveforms were converted with explicit UD -> Z, NS -> N, and EW -> E component mapping, and K-NET waveform features were computed after 1 Hz high-pass preprocessing.

The public reproducibility release is archived at https://github.com/zhouhaoyiu/strong-motion-product-window-qc/releases/tag/v0.1.0. The release contains source code, focused tests, manifest and worklist files, waveform-feature summaries, window-stability summaries, selector summaries, product-impact summaries, threshold-sensitivity summaries, response-spectrum audits, record-level audit cases, figure sources, checksums, and command logs. InstanceGM/INSTANCE data were accessed through https://doi.org/10.13127/INSTANCE on 2026-06-16. K-NET/NIED data were accessed through https://doi.org/10.17598/NIED.0004 on 2026-06-16. Raw waveform archives are not redistributed and remain subject to provider terms. Code and focused tests are released under the MIT License; derived summaries, figures, record-audit plots, manuscript-support metadata, and documentation are released under CC BY 4.0.

{ai_disclosure}
""".format(ai_disclosure=ai_disclosure)


def author_metadata_todo(metadata_path: Path) -> str:
    authors = metadata_value(metadata_path, "author_order", "Haoyu Zhou; Qiang Ma")
    corresponding = metadata_value(metadata_path, "corresponding_author_name", "Qiang Ma")
    email = metadata_value(metadata_path, "corresponding_author_email", "maqiang@iem.ac.cn")
    funding = metadata_value(metadata_path, "funding_statement", "This research received no external funding.")
    acknowledgments = metadata_value(metadata_path, "data_provider_acknowledgments")
    ai_disclosure = metadata_value(metadata_path, "ai_tool_disclosure")
    return """
# Submission Metadata To Finalize

Completed in the current metadata file:

- Authors: {authors}
- Corresponding author: {corresponding}; {email}
- Funding statement: {funding}
- Data-provider acknowledgments: {acknowledgments}
- Conflict-of-interest statement.
- AI-tool disclosure: {ai_disclosure}
- All-author approval.
- SRL classification keywords, standard publication route, editor background statement, and supplemental-material decision.

These fields still require completion before formal submission:

- Final public code/archive URL and access dates.

The fuller StrongMotion-QC-specific worksheet is included as
`statements/metadata_worksheet_zh.md` and
`statements/title_page_and_statements_draft.md` in this packet.
""".format(
        authors=authors,
        corresponding=corresponding,
        email=email,
        funding=funding,
        acknowledgments=acknowledgments,
        ai_disclosure=ai_disclosure,
    )


def reviewer_risk_answers_zh() -> str:
    return """
# 潜在审稿问题回答要点

## 1. 固定窗口已经广泛使用，本文新意在哪里？

固定窗口广泛使用说明它适合批量归档、索引和复用。本文的新意在于把固定窗从经验处理参数转化为记录级产品保持审计对象，并量化固定窗失败的主导机制。审计同时报告窗长、PGA 保持、相对能量保持、峰值时刻包含、候选来源和全记录处理状态。这样可以判断固定窗在哪些资料集中可靠、哪些记录需要更长窗口或全记录处理。

## 2. 为什么这个审计对强震动产品生产有实际意义？

强震动资料生产最终交付的是 PGA、反应谱、能量和持续时间等产品。处理窗提前结束会改变这些产品，处理窗过长会增加存储、计算和复核成本。本文给出每条记录可追溯的窗口接受或全记录处理原因，适合用于离线归档、批量产品生成、异常记录复查和资料更新后的再审计。

## 3. InstanceGM 和 K-NET 的差异是否来自资料集机制，而不是方法本身？

差异主要反映资料集记录机制、记录时长、强震段持续时间和尾波尺度。本文将这种差异作为审计对象处理：同一套候选、阈值和产品保持判据同时应用于 InstanceGM 与 K-NET。结果显示，42.00 s 固定窗失败主要由能量截断驱动；InstanceGM 中 25,468 条特征起点固定窗失败记录均存在能量保留不足，K-NET 中 917 条对应失败记录里有 916 条存在能量保留不足。方法的作用是暴露并量化这种资料集依赖性。

## 4. 反应谱保持是不是足够支撑工程意义？

反应谱保持可以支撑本文的工程产品意义，边界需要写清楚。本文证明所选处理窗相对于固定窗显著降低 0.2 s、1.0 s 和 3.0 s PSA 保持失败率，说明窗口审计影响工程常用谱值产品。3.0 s PSA 仍有 5.56% 总体剩余失败，其中 InstanceGM 为 6.42%，这是长周期谱值产品需要单独报告和保守处理的风险。论文主张的是产品保持质控，不扩展为完整结构响应安全评估。

## 5. 公开代码、数据清单、访问日期和复现包是否完整？

当前投稿包已经包含复现命令、源数据清单、图表源文件、审计输出、轻量复现包、许可声明模板和公开归档元数据模板。正式投稿前仍需填入最终 public code/data archive URL 和 data/resource access dates。第三方原始波形不打包进复现包，复现包记录数据来源、筛选清单、特征表、审计摘要和生成命令，符合公开资料复现的边界。
"""


def reproducibility_note() -> str:
    return """
# Reproducibility Note

Create a Python environment with `requirements.txt`, or use an equivalent local
environment that provides the listed packages.

Core rebuild commands:

```bash
python scripts/make_strong_motion_qc_figures.py \\
  --selector-summary outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/summary.csv \\
  --product-impact outputs/strong_motion_qc_product_impact_knet22119_hp1_inst3000/product_impact_summary.csv \\
  --sensitivity outputs/strong_motion_qc_selector_sensitivity_knet22119_hp1_inst3000/sensitivity_summary.csv \\
  --response-spectrum outputs/strong_motion_qc_response_spectrum_knet22119_hp1_inst3000/summary.csv \\
  --outdir outputs/strong_motion_qc_figures_knet22119_hp1_inst3000

python scripts/audit_strong_motion_srl_draft.py \\
  --draft manuscripts/strong_motion_qc_srl/strong_motion_qc_srl_draft.md \\
  --dataset-summary outputs/strong_motion_qc_dataset_table_knet22119_hp1_inst3000/dataset_summary.csv \\
  --selector-summary outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/summary.csv \\
  --selector-usage outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/candidate_usage.csv \\
  --product-impact outputs/strong_motion_qc_product_impact_knet22119_hp1_inst3000/product_impact_summary.csv \\
  --sensitivity outputs/strong_motion_qc_selector_sensitivity_knet22119_hp1_inst3000/sensitivity_summary.csv \\
  --key-metrics outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/summary.csv \\
  --response-spectrum outputs/strong_motion_qc_response_spectrum_knet22119_hp1_inst3000/summary.csv \\
  --outdir outputs/strong_motion_qc_srl_draft_audit_knet22119_hp1_inst3000

python scripts/build_strong_motion_srl_latex_package.py --compile

python scripts/check_submission_metadata.py \\
  --metadata docs/strong_motion_qc_srl_submission_metadata_template.csv \\
  --outdir outputs/strong_motion_qc_srl_submission_metadata

python scripts/build_submission_metadata_worksheet.py \\
  --metadata docs/strong_motion_qc_srl_submission_metadata_template.csv \\
  --manuscript manuscripts/strong_motion_qc_srl/strong_motion_qc_srl_draft.md \\
  --outdir outputs/strong_motion_qc_srl_submission_metadata

python scripts/build_strong_motion_srl_readiness_report.py \\
  --audit-dir outputs/strong_motion_qc_srl_draft_audit_knet22119_hp1_inst3000 \\
  --figure-manifest outputs/strong_motion_qc_figures_knet22119_hp1_inst3000/figure_manifest.csv \\
  --dataset-summary outputs/strong_motion_qc_dataset_table_knet22119_hp1_inst3000/dataset_summary.csv \\
  --key-metrics outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/summary.csv \\
  --product-impact outputs/strong_motion_qc_product_impact_knet22119_hp1_inst3000/product_impact_summary.csv \\
  --sensitivity outputs/strong_motion_qc_selector_sensitivity_knet22119_hp1_inst3000/sensitivity_summary.csv \\
  --response-spectrum outputs/strong_motion_qc_response_spectrum_knet22119_hp1_inst3000/summary.csv \\
  --draft manuscripts/strong_motion_qc_srl/strong_motion_qc_srl_draft.md \\
  --latex-pdf manuscripts/strong_motion_qc_srl/main.pdf \\
  --outdir outputs/strong_motion_qc_srl_readiness

python scripts/evaluate_strong_motion_pgv_retention.py \\
  --outdir outputs/strong_motion_qc_pgv_retention_knet22119_hp1_inst3000

python scripts/build_strong_motion_record_audit_packet.py \\
  --outdir outputs/strong_motion_qc_record_audit_packet_knet22119_hp1_inst3000
```

Validation commands:

```bash
python -m unittest \\
  tests.test_make_strong_motion_qc_figures \\
  tests.test_audit_strong_motion_srl_draft \\
  tests.test_build_strong_motion_srl_readiness_report \\
  tests.test_build_strong_motion_srl_submission_packet \\
  tests.test_build_strong_motion_srl_reproducibility_release \\
  tests.test_build_submission_metadata_worksheet \\
  tests.test_check_submission_metadata \\
  tests.test_build_strong_motion_record_audit_packet \\
  tests.test_evaluate_strong_motion_pgv_retention \\
  tests.test_evaluate_strong_motion_response_spectrum_retention \\
  tests.test_build_strong_motion_qc_full_manifest \\
  tests.test_compute_strong_motion_qc_features \\
  tests.test_build_strong_motion_qc_worklist
```
"""


def srl_format_checklist() -> str:
    return """
# SRL Format Checklist

Checked against the Seismological Society of America SRL author instructions current on 2026-06-16.

- Main review PDF is a complete manuscript PDF with text, figures, and tables.
- English manuscript uses letter paper, 1 inch margins, 12 pt text, double spacing, line numbers, and page numbers for review.
- Section headers are unnumbered.
- Figures and tables are embedded near first discussion and cited in sequential order.
- Figure captions are below figures; table captions are above tables.
- Tables are editable LaTeX tables, not images.
- Table 1 and Table 2 are separate tables; no A/B table parts are used.
- References are arranged alphabetically by first author and restricted to cited published works or citable data resources.
- Data and Resources precedes Acknowledgments.
- Declaration of Competing Interests is present.
- Public archive URL, data/resource access dates, and release-license statement are complete.
- A flat LaTeX upload bundle is included at `manuscript_flat/`; it keeps `main.tex` and figure PDFs in one directory and avoids figure subdirectory references.
"""


def write_flat_latex_bundle(outdir: Path, manuscript_dir: Path, figure_dir: Path) -> list[dict[str, str]]:
    flat_dir = outdir / "manuscript_flat"
    flat_dir.mkdir(parents=True, exist_ok=True)
    source_tex = manuscript_dir / "main.tex"
    rows: list[dict[str, str]] = []
    if source_tex.exists():
        tex = source_tex.read_text()
        tex = tex.replace("figures/", "")
        target = flat_dir / "main.tex"
        target.write_text(tex)
        rows.append(
            {
                "status": "generated",
                "role": "Flat LaTeX source with no figure subdirectory references",
                "source": str(source_tex),
                "target": str(target.relative_to(outdir)),
            }
        )
    for figure in sorted(figure_dir.glob("smqc_figure_*.pdf")):
        target = flat_dir / figure.name
        copy_file(figure, target)
        rows.append(
            {
                "status": "generated",
                "role": "Flat LaTeX figure file",
                "source": str(figure),
                "target": str(target.relative_to(outdir)),
            }
        )
    return rows


def packet_files(
    manuscript_dir: Path,
    figure_dir: Path,
    audit_dir: Path,
    readiness_dir: Path,
    repro_release_dir: Path,
    repro_release_zip: Path,
    compliance_dir: Path,
    metadata_template: Path,
    metadata_dir: Path,
    pgv_retention_dir: Path,
    record_audit_dir: Path,
    chinese_markdown: Path,
    chinese_manuscript_dir: Path,
) -> list[PacketFile]:
    files = [
        PacketFile(manuscript_dir / "main.pdf", Path("manuscript/main.pdf"), "SRL-style review manuscript PDF"),
        PacketFile(manuscript_dir / "main.tex", Path("manuscript/main.tex"), "LaTeX source for review manuscript"),
        PacketFile(manuscript_dir / "strong_motion_qc_srl_draft.md", Path("manuscript/strong_motion_qc_srl_draft.md"), "Markdown source draft"),
        PacketFile(manuscript_dir / "latex_build_report.md", Path("manuscript/latex_build_report.md"), "LaTeX build report"),
        PacketFile(figure_dir / "figure_manifest.csv", Path("figures/figure_manifest.csv"), "Figure manifest"),
        PacketFile(audit_dir / "README.md", Path("evidence/draft_audit_report.md"), "Draft audit report"),
        PacketFile(audit_dir / "number_audit.csv", Path("evidence/number_audit.csv"), "Draft number audit"),
        PacketFile(audit_dir / "pattern_audit.csv", Path("evidence/pattern_audit.csv"), "Style and scope audit"),
        PacketFile(audit_dir / "display_audit.csv", Path("evidence/display_audit.csv"), "Figure and table audit"),
        PacketFile(readiness_dir / "report.md", Path("evidence/readiness_report.md"), "Internal SRL readiness report"),
        PacketFile(readiness_dir / "readiness_checks.csv", Path("evidence/readiness_checks.csv"), "Machine-readable readiness checks"),
        PacketFile(compliance_dir / "report.md", Path("evidence/srl_compliance_report.md"), "SRL compliance report"),
        PacketFile(compliance_dir / "compliance_checks.csv", Path("evidence/srl_compliance_checks.csv"), "Machine-readable SRL compliance checks"),
        PacketFile(metadata_template, Path("statements/strong_motion_qc_srl_submission_metadata_template.csv"), "StrongMotion-QC SRL metadata template"),
        PacketFile(metadata_dir / "submission_metadata_checks.csv", Path("evidence/submission_metadata_checks.csv"), "Machine-readable submission metadata checks"),
        PacketFile(metadata_dir / "report.md", Path("evidence/submission_metadata_report.md"), "Submission metadata report"),
        PacketFile(metadata_dir / "metadata_worksheet_items.csv", Path("statements/metadata_worksheet_items.csv"), "Bilingual submission metadata worksheet source table"),
        PacketFile(metadata_dir / "metadata_worksheet_zh.md", Path("statements/metadata_worksheet_zh.md"), "Bilingual submission metadata worksheet"),
        PacketFile(metadata_dir / "title_page_and_statements_draft.md", Path("statements/title_page_and_statements_draft.md"), "Title-page and statements draft"),
        PacketFile(Path("docs/strong_motion_qc_srl_reference_verification.md"), Path("evidence/reference_verification.md"), "Reference verification notes"),
        PacketFile(repro_release_zip, Path("reproducibility/strong_motion_qc_srl_reproducibility_release_current.zip"), "Lightweight reproducibility release zip"),
        PacketFile(repro_release_dir / "README.md", Path("reproducibility/release_README.md"), "Reproducibility release README"),
        PacketFile(repro_release_dir / "REPRODUCTION_COMMANDS.md", Path("reproducibility/release_REPRODUCTION_COMMANDS.md"), "Reproducibility release commands"),
        PacketFile(repro_release_dir / "LICENSE", Path("reproducibility/release_LICENSE"), "Reproducibility release license"),
        PacketFile(
            repro_release_dir / "ARCHIVE_METADATA_TEMPLATE.md",
            Path("reproducibility/release_ARCHIVE_METADATA_TEMPLATE.md"),
            "Public archive metadata template",
        ),
        PacketFile(repro_release_dir / "metadata/file_checksums.csv", Path("reproducibility/release_file_checksums.csv"), "Reproducibility release file checksums"),
        PacketFile(repro_release_dir / "metadata/data_source_manifest.csv", Path("reproducibility/release_data_source_manifest.csv"), "Reproducibility release data-source manifest"),
        PacketFile(Path("outputs/strong_motion_qc_dataset_table_knet22119_hp1_inst3000/dataset_summary.csv"), Path("source_data/dataset_summary.csv"), "Dataset summary source table"),
        PacketFile(Path("outputs/strong_motion_qc_dataset_table_knet22119_hp1_inst3000/priority_strata_summary.csv"), Path("source_data/priority_strata_summary.csv"), "Priority-strata summary source table"),
        PacketFile(Path("outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/summary.csv"), Path("source_data/product_window_selector_summary.csv"), "Product-window selector summary"),
        PacketFile(Path("outputs/strong_motion_qc_product_window_selector_knet22119_hp1_inst3000/candidate_usage.csv"), Path("source_data/selector_candidate_usage.csv"), "Selector candidate usage"),
        PacketFile(Path("outputs/strong_motion_qc_product_impact_knet22119_hp1_inst3000/product_impact_summary.csv"), Path("source_data/product_impact_summary.csv"), "Product-impact summary"),
        PacketFile(Path("outputs/strong_motion_qc_selector_sensitivity_knet22119_hp1_inst3000/sensitivity_summary.csv"), Path("source_data/selector_sensitivity_summary.csv"), "Selector sensitivity summary"),
        PacketFile(Path("outputs/strong_motion_qc_response_spectrum_knet22119_hp1_inst3000/summary.csv"), Path("source_data/response_spectrum_summary.csv"), "Response-spectrum retention summary"),
        PacketFile(pgv_retention_dir / "summary.csv", Path("source_data/pgv_retention_summary.csv"), "Relative PGV-retention summary"),
        PacketFile(pgv_retention_dir / "README.md", Path("evidence/pgv_retention_report.md"), "Relative PGV-retention audit report"),
        PacketFile(pgv_retention_dir / "load_errors.csv", Path("evidence/pgv_retention_load_errors.csv"), "Relative PGV-retention load-error boundary"),
        PacketFile(record_audit_dir / "README.md", Path("evidence/record_audit_report.md"), "Representative record-level audit report"),
        PacketFile(record_audit_dir / "cases.csv", Path("source_data/record_audit_cases.csv"), "Representative record-level audit cases"),
        PacketFile(record_audit_dir / "case_windows.csv", Path("source_data/record_audit_case_windows.csv"), "Representative record-level window metrics"),
        PacketFile(record_audit_dir / "plot_manifest.csv", Path("evidence/record_audit_plot_manifest.csv"), "Representative record-level plot manifest"),
        PacketFile(chinese_markdown, Path("chinese_review/strong_motion_qc_srl_manuscript_zh.md"), "Formal Chinese advisor-review manuscript"),
        PacketFile(chinese_manuscript_dir / "main.pdf", Path("chinese_review/main.pdf"), "Formal Chinese advisor-review PDF"),
        PacketFile(chinese_manuscript_dir / "main.tex", Path("chinese_review/main.tex"), "Chinese advisor-review LaTeX source"),
        PacketFile(chinese_manuscript_dir / "latex_build_report.md", Path("chinese_review/latex_build_report.md"), "Chinese advisor-review build report"),
    ]
    for figure in sorted((record_audit_dir / "figures").glob("case_*.*")):
        if figure.suffix.lower() in {".png", ".pdf"}:
            files.append(PacketFile(figure, Path("figures/record_audit") / figure.name, "Representative record-level audit figure"))
    for figure in sorted(figure_dir.glob("smqc_figure_*.pdf")):
        files.append(PacketFile(figure, Path("figures") / figure.name, "Figure PDF"))
    for figure in sorted((chinese_manuscript_dir / "figures").glob("smqc_figure_*.pdf")):
        files.append(PacketFile(figure, Path("chinese_review/figures") / figure.name, "Chinese advisor-review figure PDF"))
    for table in sorted((manuscript_dir / "tables").glob("table_*.tex")):
        files.append(PacketFile(table, Path("tables") / table.name, "LaTeX table source"))
    return files


def validate_manifest(rows: list[dict[str, str]]) -> tuple[int, int]:
    total = len(rows)
    missing = sum(1 for row in rows if row["status"] not in {"copied", "generated"})
    return total, missing


def write_manifest(outdir: Path, rows: list[dict[str, str]]) -> None:
    path = outdir / "package_manifest.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["status", "role", "source", "target"])
        writer.writeheader()
        writer.writerows(rows)


def write_readme(outdir: Path, total: int, missing: int) -> None:
    readme = f"""
# StrongMotion-QC SRL Submission Packet

This packet is for advisor review and pre-submission checking of the StrongMotion-QC SRL manuscript route.

## Status

- Manifest entries: {total}
- Missing required files: {missing}
- Manuscript PDF: `manuscript/main.pdf`
- Manuscript TeX: `manuscript/main.tex`
- Flat LaTeX upload bundle: `manuscript_flat/main.tex`
- Main evidence reports: `evidence/draft_audit_report.md`, `evidence/readiness_report.md`
- Chinese advisor-review manuscript: `chinese_review/main.pdf`
- SRL compliance report: `evidence/srl_compliance_report.md`
- Submission metadata worksheet: `statements/metadata_worksheet_zh.md`
- Potential reviewer-question answers: `evidence/reviewer_risk_answers_zh.md`
- Supplemental PGV-retention audit: `evidence/pgv_retention_report.md`
- Representative record-level audit: `evidence/record_audit_report.md`
- SRL format checklist: `evidence/srl_format_checklist.md`
- Reproducibility release: `reproducibility/strong_motion_qc_srl_reproducibility_release_current.zip`
- Final manual items: public archive URL and access dates.

## Scope

This packet supports the current offline product-stable window selection claim and its StrongMotion-QC audit artifacts.
"""
    write_text(outdir / "README.md", readme)


def write_package_report(outdir: Path, total: int, missing: int, zip_path: Path) -> None:
    report = f"""
# StrongMotion-QC SRL Packet Report

- Packet directory: `{outdir}`
- Zip archive: `{zip_path}`
- Manifest entries: {total}
- Missing required files: {missing}
- Ready for advisor review: {'yes' if missing == 0 else 'no'}

## Remaining Submission Fields

1. Final public code/data archive URL.
2. Final data/resource access dates.
"""
    write_text(outdir / "package_report.md", report)


def zip_packet(outdir: Path) -> Path:
    zip_path = outdir.with_suffix(".zip")
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(outdir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(outdir.parent))
    return zip_path


def build_packet(
    outdir: Path,
    manuscript_dir: Path,
    figure_dir: Path,
    audit_dir: Path,
    readiness_dir: Path,
    repro_release_dir: Path,
    repro_release_zip: Path,
    compliance_dir: Path,
    metadata_template: Path,
    metadata_dir: Path,
    pgv_retention_dir: Path,
    record_audit_dir: Path,
    chinese_markdown: Path,
    chinese_manuscript_dir: Path,
) -> dict[str, Path | int]:
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)

    rows: list[dict[str, str]] = []
    for item in packet_files(
        manuscript_dir,
        figure_dir,
        audit_dir,
        readiness_dir,
        repro_release_dir,
        repro_release_zip,
        compliance_dir,
        metadata_template,
        metadata_dir,
        pgv_retention_dir,
        record_audit_dir,
        chinese_markdown,
        chinese_manuscript_dir,
    ):
        status = "copied"
        if not item.source.exists():
            status = "missing_required" if item.required else "missing_optional"
        else:
            copy_file(item.source, outdir / item.target)
        rows.append(
            {
                "status": status,
                "role": item.role,
                "source": str(item.source),
                "target": str(item.target),
            }
        )

    generated_files = [
        (Path("statements/cover_letter_draft.md"), "Cover letter draft", cover_letter(metadata_template)),
        (Path("statements/data_and_resources_statement_draft.md"), "Data and Resources statement draft", data_resources_statement(metadata_template)),
        (Path("statements/author_metadata_todo.md"), "Author metadata completion checklist", author_metadata_todo(metadata_template)),
        (Path("reproducibility/reproduce_strong_motion_qc_srl.md"), "Reproducibility note", reproducibility_note()),
        (Path("evidence/reviewer_risk_answers_zh.md"), "Potential reviewer-question answers", reviewer_risk_answers_zh()),
        (Path("evidence/srl_format_checklist.md"), "SRL format checklist", srl_format_checklist()),
    ]
    for target, role, text in generated_files:
        write_text(outdir / target, text)
        rows.append({"status": "generated", "role": role, "source": "script", "target": str(target)})

    rows.extend(write_flat_latex_bundle(outdir, manuscript_dir, figure_dir))

    write_manifest(outdir, rows)
    total, missing = validate_manifest(rows)
    write_readme(outdir, total, missing)
    zip_path = zip_packet(outdir)
    write_package_report(outdir, total, missing, zip_path)
    zip_path = zip_packet(outdir)
    return {"outdir": outdir, "zip": zip_path, "total": total, "missing": missing}


def main() -> None:
    args = parse_args()
    result = build_packet(
        outdir=Path(args.outdir),
        manuscript_dir=Path(args.manuscript_dir),
        figure_dir=Path(args.figure_dir),
        audit_dir=Path(args.audit_dir),
        readiness_dir=Path(args.readiness_dir),
        repro_release_dir=Path(args.repro_release_dir),
        repro_release_zip=Path(args.repro_release_zip),
        compliance_dir=Path(args.compliance_dir),
        metadata_template=Path(args.metadata_template),
        metadata_dir=Path(args.metadata_dir),
        pgv_retention_dir=Path(args.pgv_retention_dir),
        record_audit_dir=Path(args.record_audit_dir),
        chinese_markdown=Path(args.chinese_markdown),
        chinese_manuscript_dir=Path(args.chinese_manuscript_dir),
    )
    print(f"Wrote {Path(result['outdir']).resolve()}")
    print(f"Wrote {Path(result['zip']).resolve()}")
    print(f"Manifest entries: {result['total']}; missing required: {result['missing']}")
    if result["missing"]:
        raise SystemExit("Submission packet has missing required files")


if __name__ == "__main__":
    main()
