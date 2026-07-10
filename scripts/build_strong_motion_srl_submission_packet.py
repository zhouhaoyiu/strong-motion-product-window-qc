#!/usr/bin/env python3
"""Build the current StrongMotion-QC SRL submission-review packet."""

from __future__ import annotations

import argparse
import csv
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path


DEFAULT_OUTDIR = "outputs/strong_motion_qc_srl_submission_packet_current"
DEFAULT_MANUSCRIPT_DIR = "manuscripts/strong_motion_qc_srl"
DEFAULT_FIGURE_DIR = "outputs/strong_motion_qc_figures_accel44674_hp0p1"
DEFAULT_EVIDENCE_DIR = "outputs/strong_motion_qc_revised_evidence_audit"
DEFAULT_METADATA_TEMPLATE = "docs/strong_motion_qc_srl_submission_metadata_template.csv"
DEFAULT_METADATA_DIR = "outputs/strong_motion_qc_srl_submission_metadata"
DEFAULT_CHINESE_MARKDOWN = "docs/strong_motion_qc_srl_manuscript_zh.md"
DEFAULT_CHINESE_MANUSCRIPT_DIR = "manuscripts/strong_motion_qc_srl_zh"


SOURCE_DATA_FILES = [
    ("outputs/strong_motion_qc_dataset_table_accel44674_hp0p1/dataset_summary.csv", "dataset_summary.csv", "Dataset summary"),
    ("outputs/strong_motion_qc_dataset_table_accel44674_hp0p1/priority_strata_summary.csv", "magnitude_strata.csv", "Magnitude-strata summary"),
    ("outputs/strong_motion_qc_window_stability_accel44674_hp0p1/summary.csv", "main_window_stability.csv", "Main fixed-window stability"),
    ("outputs/strong_motion_qc_window_stability_pnw_accel6107_hp0p1/summary.csv", "pnw_window_stability.csv", "PNW fixed-window stability"),
    ("outputs/strong_motion_qc_product_window_selector_accel44674_hp0p1/summary.csv", "main_primary_selector.csv", "Main first-stage selector"),
    ("outputs/strong_motion_qc_product_window_selector_pnw_accel6107_hp0p1/summary.csv", "pnw_primary_selector.csv", "PNW first-stage selector"),
    ("outputs/strong_motion_qc_response_spectrum_accel44674_hp0p1/summary.csv", "main_psa_retention.csv", "Main PSA retention"),
    ("outputs/strong_motion_qc_response_spectrum_pnw_accel6107_hp0p1/summary.csv", "pnw_psa_retention.csv", "PNW PSA retention"),
    ("outputs/strong_motion_qc_spectral_safeguard_accel44674_hp0p1/summary.csv", "main_final_routing_0p95.csv", "Main final routing at 0.95"),
    ("outputs/strong_motion_qc_spectral_safeguard_accel44674_hp0p1/spectrum_summary.csv", "main_final_psa_0p95.csv", "Main final PSA check at 0.95"),
    ("outputs/strong_motion_qc_spectral_safeguard_accel44674_hp0p1_thr0p90/summary.csv", "main_final_routing_0p90.csv", "Main routing at 0.90"),
    ("outputs/strong_motion_qc_spectral_safeguard_accel44674_hp0p1_thr0p98/summary.csv", "main_final_routing_0p98.csv", "Main routing at 0.98"),
    ("outputs/strong_motion_qc_spectral_safeguard_pnw_accel6107_hp0p1/summary.csv", "pnw_final_routing_0p95.csv", "PNW final routing at 0.95"),
    ("outputs/strong_motion_qc_spectral_safeguard_pnw_accel6107_hp0p1_thr0p90/summary.csv", "pnw_final_routing_0p90.csv", "PNW routing at 0.90"),
    ("outputs/strong_motion_qc_spectral_safeguard_pnw_accel6107_hp0p1_thr0p98/summary.csv", "pnw_final_routing_0p98.csv", "PNW routing at 0.98"),
    ("outputs/strong_motion_qc_spectral_safeguard_filter_sensitivity_e2e_hp0p05_sample1521/summary.csv", "filter_0p05_final_routing.csv", "End-to-end 0.05 Hz routing"),
    ("outputs/strong_motion_qc_spectral_safeguard_filter_sensitivity_e2e_hp0p1_sample1521/summary.csv", "filter_0p10_final_routing.csv", "End-to-end 0.10 Hz routing"),
    ("outputs/strong_motion_qc_response_spectrum_filter_sensitivity_e2e_hp0p05_sample1521/summary.csv", "filter_0p05_psa.csv", "End-to-end 0.05 Hz PSA"),
    ("outputs/strong_motion_qc_response_spectrum_filter_sensitivity_e2e_hp0p1_sample1521/summary.csv", "filter_0p10_psa.csv", "End-to-end 0.10 Hz PSA"),
    ("outputs/strong_motion_qc_pnw_snr_accel6107_hp0p1/summary.csv", "pnw_snr_summary.csv", "PNW SNR-stratified audit"),
]


@dataclass(frozen=True)
class PacketFile:
    source: Path
    target: Path
    role: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    parser.add_argument("--manuscript-dir", default=DEFAULT_MANUSCRIPT_DIR)
    parser.add_argument("--figure-dir", default=DEFAULT_FIGURE_DIR)
    parser.add_argument("--evidence-dir", default=DEFAULT_EVIDENCE_DIR)
    parser.add_argument("--metadata-template", default=DEFAULT_METADATA_TEMPLATE)
    parser.add_argument("--metadata-dir", default=DEFAULT_METADATA_DIR)
    parser.add_argument("--chinese-markdown", default=DEFAULT_CHINESE_MARKDOWN)
    parser.add_argument("--chinese-manuscript-dir", default=DEFAULT_CHINESE_MANUSCRIPT_DIR)
    return parser.parse_args()


def metadata_value(path: Path, field_id: str, default: str = "") -> str:
    if not path.exists():
        return default
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("field_id") == field_id:
                return row.get("value", "").strip() or default
    return default


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.strip() + "\n")


def copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def cover_letter(metadata_path: Path) -> str:
    authors = metadata_value(metadata_path, "author_order", "Haoyu Zhou; Qiang Ma").replace("; ", " and ")
    ai_disclosure = metadata_value(metadata_path, "ai_tool_disclosure")
    return f"""
# Cover Letter

Dear Editor,

We submit "A Two-Stage Product Audit for Strong-Motion Processing Windows" for consideration as a Regular Article in *Seismological Research Letters*.

Fixed processing windows simplify archive production, but their product adequacy can vary among strong-motion archives. We analyze 44,674 three-component acceleration records from InstanceGM and K-NET and evaluate the same procedure on 6,107 PNWAccelerometers records. The audit first selects the shortest waveform-derived interval that preserves component peaks and three-component squared motion. It then checks minimum component-wise 5%-damped pseudo-spectral acceleration retention at 0.2, 1.0, and 3.0 s, escalating failed records to a padded cumulative-energy interval or the full record.

The results quantify a production problem that fixed duration alone cannot resolve. A window ending 40 s after feature onset fails the first-stage criteria for 67.55% of InstanceGM records, 4.15% of K-NET records, and 86.56% of PNW records. The first stage reduces the main-set median duration to 34.25 s, while 37.16% of records still lose more than 5% of 3.0 s PSA in at least one component. The spectral safeguard routes 60.08% of the main set to the primary interval, 19.96% to the energy-percentile interval, and 19.96% to the full record. An end-to-end 0.05/0.10 Hz comparison and the independent PNW archive test the sensitivity and transfer of this behavior.

The contribution is a record-level quality-control method for offline strong-motion product production. It links each output window to explicit amplitude, energy, peak-time, spectral, and fallback evidence. The evaluated scope is archive and batch-product preparation; phase picking, real-time warning, and measured operator-time reduction are outside the claims.

The manuscript is original, is not under consideration elsewhere, and has been approved by both authors. Code, tests, derived audit tables, figure source data, and reproduction commands are archived at https://github.com/zhouhaoyiu/strong-motion-product-window-qc/releases/tag/v0.2.0.

AI-tool disclosure: {ai_disclosure}

Sincerely,

{authors}
"""


def data_resources_statement(metadata_path: Path) -> str:
    ai_disclosure = metadata_value(metadata_path, "ai_tool_disclosure")
    return f"""
# Data and Resources Statement

InstanceGM/INSTANCE data were accessed through https://doi.org/10.13127/INSTANCE on 16 June 2026. K-NET data were accessed from the National Research Institute for Earth Science and Disaster Resilience through https://doi.org/10.17598/NIED.0004 on 16 June 2026. PNWAccelerometers data were accessed through the SeisBench data interface on 18 June 2026 and are described by Ni et al. (2023), https://doi.org/10.26443/seismica.v2i1.368.

Code, tests, derived audit tables, figure source data, and reproduction commands are archived at https://github.com/zhouhaoyiu/strong-motion-product-window-qc/releases/tag/v0.2.0 (last accessed July 2026). Raw waveforms are not redistributed and remain subject to provider terms. Source code is released under the MIT License. Derived tables, figures, and documentation are released under CC BY 4.0.

{ai_disclosure}
"""


def reviewer_answers_zh() -> str:
    return """
# 潜在审稿问题回答要点

## 1. 固定窗已经广泛使用，本文的新意是什么？

固定窗解决记录长度统一和批量读取问题。本文研究产品计算阶段的另一项要求：候选窗是否保留各分量峰值、三分量平方运动积分和受检周期的反应谱。方法把固定时长从默认处理参数改为逐记录审计对象，并为每条记录保留判据、升级路径和最终窗长。三套资料在 40 s 固定窗上的不稳定率为 67.55%、4.15% 和 86.56%，说明统一窗长不能直接作为跨资料库的产品质量标准。

## 2. 为什么该审计对强震动产品生产有实际意义？

产品表中的 PGA 和 PSA 由处理窗内样本计算。窗长不足会造成未报告的产品损失，统一延长又会增加存储和计算。本文在产品输出前逐条检查保留率，合格记录采用较短初选窗，边界记录升级为能量百分位窗，仍未达标的记录保留全记录。输出字段可与产品共同归档，支持资料更新后的复算和失败原因追溯。

## 3. InstanceGM 与 K-NET 的差异会不会只是资料集机制？

差异本身就是本文要审计的对象。两套资料使用完全相同的预处理、候选窗和产品判据，结果仍显著不同。截取规则、触发停止条件、震级构成、传播路径和盆地效应都可能参与形成差异。本文量化这些因素共同作用后的产品后果；区分各机制的独立贡献需要资料库级采集和触发元数据。

## 4. 三个周期的 PSA 是否足以支撑工程意义？

0.2、1.0 和 3.0 s 覆盖短周期至较长周期的代表性谱值，能够直接检验处理窗对工程反应谱产品的影响。第一级之后主数据仍有 37.16% 的记录在 3.0 s 周期损失超过 5%，说明峰值和积分量不能替代谱产品复核。质量保证限于本文给定的预处理、5% 阻尼、三个周期和 0.95 阈值；更长周期、其他阻尼比或傅里叶谱应加入相应审计指标。

## 5. 代码、数据清单、访问日期和复现材料是否完整？

正文给出三套资料的来源和访问日期，公开仓库提供代码、测试、派生摘要、图件源数据和复现命令。原始波形遵循各提供方条款，不在仓库中重复分发。代码采用 MIT License，派生表格、图件和文档采用 CC BY 4.0。投稿前还需确认公开仓库可访问，并为最终提交版本建立不可变归档。
"""


def reproduction_note() -> str:
    return """
# Reproduction Note

The packet contains the compact summary tables used by the manuscript. From the repository root, the figures, review PDFs, and packet are rebuilt with:

```bash
python scripts/make_strong_motion_qc_figures.py
python scripts/make_strong_motion_qc_figures.py --language zh --outdir outputs/strong_motion_qc_figures_accel44674_hp0p1_zh
python scripts/build_strong_motion_srl_latex_package.py --compile
python scripts/build_strong_motion_srl_chinese_latex.py --compile
python scripts/build_strong_motion_srl_submission_packet.py
```

The full analysis and a rerun of `scripts/audit_strong_motion_qc_revised_evidence.py` require provider-authorized copies of InstanceGM, K-NET, and PNWAccelerometers plus the record-level feature, window, and response-spectrum tables. The archived evidence report verifies record counts, component-level peak and PSA definitions, tested periods, five-cycle oscillator ringdown, safeguard grain, filter-sample identity, PNW SNR summaries, manuscript key numbers, and stale-result markers.
"""


def srl_checklist() -> str:
    return """
# SRL Format Checklist

Checked against the SRL Submission Guidelines and SSA AI Guidelines on 10 July 2026.

- Regular Article limits: 3,300-word manuscript text, 285-word abstract, 6 figures, and 3 tables; limits are 6,000 words, 300 abstract words, 10 figures, and 3 tables.
- Review PDF: U.S. letter paper, one-inch margins, 12-point double-spaced text, page numbers, and continuous line numbers.
- Unnumbered section headings; sequential figure and table callouts.
- Table captions above editable LaTeX tables; figure captions and alt text below figures.
- Data and Resources precedes Acknowledgments and contains URLs, access dates, licenses, and AI disclosure.
- Declaration of Competing Interests is present; the corresponding-author address follows the references.
- The flat LaTeX bundle removes figure-subdirectory references.
"""


def packet_files(
    manuscript_dir: Path,
    figure_dir: Path,
    evidence_dir: Path,
    metadata_template: Path,
    metadata_dir: Path,
    chinese_markdown: Path,
    chinese_manuscript_dir: Path,
) -> list[PacketFile]:
    files = [
        PacketFile(manuscript_dir / "qc.pdf", Path("manuscript/qc.pdf"), "English review PDF"),
        PacketFile(manuscript_dir / "main.tex", Path("manuscript/main.tex"), "English LaTeX source"),
        PacketFile(manuscript_dir / "strong_motion_qc_srl_draft.md", Path("manuscript/strong_motion_qc_srl_draft.md"), "English Markdown source"),
        PacketFile(manuscript_dir / "latex_build_report.md", Path("manuscript/latex_build_report.md"), "English build report"),
        PacketFile(figure_dir / "figure_manifest.csv", Path("figures/figure_manifest.csv"), "Figure manifest"),
        PacketFile(evidence_dir / "README.md", Path("evidence/evidence_audit.md"), "Evidence audit"),
        PacketFile(evidence_dir / "checks.csv", Path("evidence/evidence_checks.csv"), "Machine-readable evidence checks"),
        PacketFile(Path("docs/strong_motion_qc_srl_reference_verification.md"), Path("evidence/reference_verification.md"), "Reference verification"),
        PacketFile(metadata_template, Path("statements/submission_metadata.csv"), "Submission metadata"),
        PacketFile(metadata_dir / "metadata_worksheet_zh.md", Path("statements/metadata_worksheet_zh.md"), "Bilingual metadata worksheet"),
        PacketFile(metadata_dir / "title_page_and_statements_draft.md", Path("statements/title_page_and_statements.md"), "Title-page statements"),
        PacketFile(chinese_markdown, Path("chinese_review/strong_motion_qc_srl_manuscript_zh.md"), "Chinese advisor manuscript"),
        PacketFile(chinese_manuscript_dir / "qc_chinese.pdf", Path("chinese_review/qc_chinese.pdf"), "Chinese advisor PDF"),
        PacketFile(chinese_manuscript_dir / "main.tex", Path("chinese_review/main.tex"), "Chinese LaTeX source"),
        PacketFile(chinese_manuscript_dir / "latex_build_report.md", Path("chinese_review/latex_build_report.md"), "Chinese build report"),
    ]
    files.extend(PacketFile(Path(source), Path("source_data") / target, role) for source, target, role in SOURCE_DATA_FILES)
    files.extend(PacketFile(path, Path("figures") / path.name, "English figure PDF") for path in sorted(figure_dir.glob("smqc_figure_*.pdf")))
    files.extend(PacketFile(path, Path("tables") / path.name, "Editable LaTeX table") for path in sorted((manuscript_dir / "tables").glob("table_*.tex")))
    files.extend(PacketFile(path, Path("chinese_review/figures") / path.name, "Chinese figure PDF") for path in sorted((chinese_manuscript_dir / "figures").glob("smqc_figure_*.pdf")))
    return files


def write_flat_bundle(outdir: Path, manuscript_dir: Path, figure_dir: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    flat = outdir / "manuscript_flat"
    flat.mkdir(parents=True, exist_ok=True)
    source_tex = manuscript_dir / "main.tex"
    target_tex = flat / "main.tex"
    target_tex.write_text(source_tex.read_text().replace("figures/", ""))
    rows.append({"status": "generated", "role": "Flat LaTeX source", "source": str(source_tex), "target": str(target_tex.relative_to(outdir))})
    for figure in sorted(figure_dir.glob("smqc_figure_*.pdf")):
        target = flat / figure.name
        copy_file(figure, target)
        rows.append({"status": "generated", "role": "Flat figure PDF", "source": str(figure), "target": str(target.relative_to(outdir))})
    return rows


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
    evidence_dir: Path,
    metadata_template: Path,
    metadata_dir: Path,
    chinese_markdown: Path,
    chinese_manuscript_dir: Path,
) -> dict[str, Path | int]:
    if outdir.exists():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)

    rows: list[dict[str, str]] = []
    for item in packet_files(manuscript_dir, figure_dir, evidence_dir, metadata_template, metadata_dir, chinese_markdown, chinese_manuscript_dir):
        status = "copied" if item.source.exists() else "missing_required"
        if status == "copied":
            copy_file(item.source, outdir / item.target)
        rows.append({"status": status, "role": item.role, "source": str(item.source), "target": str(item.target)})

    generated = [
        ("statements/cover_letter.md", "Cover letter", cover_letter(metadata_template)),
        ("statements/data_and_resources.md", "Data and Resources statement", data_resources_statement(metadata_template)),
        ("evidence/reviewer_questions_zh.md", "Reviewer-question answers", reviewer_answers_zh()),
        ("evidence/srl_format_checklist.md", "SRL format checklist", srl_checklist()),
        ("reproducibility/REPRODUCTION.md", "Reproduction note", reproduction_note()),
    ]
    for target, role, value in generated:
        write_text(outdir / target, value)
        rows.append({"status": "generated", "role": role, "source": "script", "target": target})
    rows.extend(write_flat_bundle(outdir, manuscript_dir, figure_dir))

    manifest = outdir / "package_manifest.csv"
    with manifest.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["status", "role", "source", "target"])
        writer.writeheader()
        writer.writerows(rows)
    missing = sum(row["status"] == "missing_required" for row in rows)
    write_text(
        outdir / "README.md",
        f"""
# StrongMotion-QC SRL Review Packet

- Manifest entries: {len(rows)}
- Missing required files: {missing}
- English review PDF: `manuscript/qc.pdf`
- Chinese advisor PDF: `chinese_review/qc_chinese.pdf`
- Evidence audit: `evidence/evidence_audit.md`
- Cover letter: `statements/cover_letter.md`
- Flat LaTeX upload bundle: `manuscript_flat/`

This packet contains only the current two-stage processing-window audit and its supporting evidence.
""",
    )
    zip_path = zip_packet(outdir)
    write_text(outdir / "package_report.md", f"Manifest entries: {len(rows)}\nMissing required files: {missing}\nZip: {zip_path}\n")
    zip_path = zip_packet(outdir)
    return {"outdir": outdir, "zip": zip_path, "total": len(rows), "missing": missing}


def main() -> None:
    args = parse_args()
    result = build_packet(
        Path(args.outdir),
        Path(args.manuscript_dir),
        Path(args.figure_dir),
        Path(args.evidence_dir),
        Path(args.metadata_template),
        Path(args.metadata_dir),
        Path(args.chinese_markdown),
        Path(args.chinese_manuscript_dir),
    )
    print(f"Wrote {Path(result['outdir']).resolve()}")
    print(f"Wrote {Path(result['zip']).resolve()}")
    print(f"Manifest entries: {result['total']}; missing required: {result['missing']}")
    if result["missing"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
