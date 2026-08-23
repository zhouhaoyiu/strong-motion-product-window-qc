#!/usr/bin/env python3
"""Build a formal Chinese review manuscript for the StrongMotion-QC SRL route."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_strong_motion_srl_latex_package import fmt_int, fmt_num, fmt_pct, row_by, tex_escape


DEFAULT_OUTDIR = "manuscripts/strong_motion_qc_srl_zh"
DEFAULT_MARKDOWN = "docs/strong_motion_qc_srl_manuscript_zh.md"
DEFAULT_FIGURE_DIR = "outputs/strong_motion_qc_figures_accel44674_hp0p1_zh"
DEFAULT_DATASET_SUMMARY = "outputs/strong_motion_qc_dataset_table_accel44674_hp0p1/dataset_summary.csv"
DEFAULT_PRIORITY_SUMMARY = "outputs/strong_motion_qc_dataset_table_accel44674_hp0p1/priority_strata_summary.csv"
DEFAULT_SAFEGUARD_SUMMARY = "outputs/strong_motion_qc_spectral_safeguard_accel44674_hp0p1/summary.csv"
DEFAULT_PNW_SAFEGUARD_SUMMARY = "outputs/strong_motion_qc_spectral_safeguard_pnw_accel6107_hp0p1/summary.csv"
PRIORITY_GROUP_LABELS_ZH = {
    "low_magnitude_background": "低震级背景",
    "m3_to_m4_small_event": "M3-M4",
    "m4plus_strong_motion": "M4+",
    "other": "目录计时不完整",
}
PRIORITY_GROUP_ORDER = [
    "low_magnitude_background",
    "m3_to_m4_small_event",
    "m4plus_strong_motion",
    "other",
]

FIGURES = [
    (
        "smqc_figure_01_workflow.pdf",
        "强震动处理窗的两阶段产品审计流程。第一阶段检查各分量峰值加速度、三分量总能量和分量峰值时刻，保留通过审计的最短候选窗；第二阶段检查 0.2、1.0 和 3.0 s 的 5% 阻尼 PSA，未通过时依次改用 1%-99% 累积能量窗和全记录。",
    ),
    (
        "smqc_figure_02_fixed_window_failure.pdf",
        "InstanceGM、K-NET 和 PNWAccelerometers 的固定窗敏感性。横轴为起点后 20、40、60 和 90 s，所有窗口均包含起点前 2 s。",
    ),
    (
        "smqc_figure_03_selector_duration_fallback.pdf",
        "反应谱复核后的处理分流和窗长。记录分为保留初选窗、改用 1%-99% 累积能量窗和采用全记录三类；误差线上端为处理窗时长的 75 分位。",
    ),
    (
        "smqc_figure_04_product_impact_recovery.pdf",
        "42 s 固定窗、幅值-能量初选窗和反应谱保障窗在 0.2、1.0 和 3.0 s 周期上的 PSA 保留失败率。最终输出包含全记录回退，三个周期均满足 0.95 保留阈值。",
    ),
    (
        "smqc_figure_05_filter_sensitivity.pdf",
        "同一 1,521 条分层样本上的高通滤波敏感性。图中比较 0.05 和 0.10 Hz 预处理条件下初选窗的 3.0 s PSA 失败率及最终全记录回退比例。",
    ),
    (
        "smqc_figure_06_response_spectrum_retention.pdf",
        "PNWAccelerometers 的信噪比分层结果。信噪比在结果合并前由目录到时和波形均方根幅值计算；三幅图依次给出固定窗不稳定率、初选窗 3.0 s PSA 失败率和最终全记录回退比例。",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    parser.add_argument("--markdown", default=DEFAULT_MARKDOWN)
    parser.add_argument("--figure-dir", default=DEFAULT_FIGURE_DIR)
    parser.add_argument("--dataset-summary", default=DEFAULT_DATASET_SUMMARY)
    parser.add_argument("--priority-summary", default=DEFAULT_PRIORITY_SUMMARY)
    parser.add_argument("--spectral-safeguard", default=DEFAULT_SAFEGUARD_SUMMARY)
    parser.add_argument("--pnw-spectral-safeguard", default=DEFAULT_PNW_SAFEGUARD_SUMMARY)
    parser.add_argument("--compile", action="store_true")
    return parser.parse_args()


def table_environment(label: str, caption: str, tabular: str) -> str:
    return "\n".join(
        [
            r"\begin{table}[!htbp]",
            r"\centering",
            r"\caption{" + tex_escape(caption) + r"}",
            r"\label{" + label + r"}",
            r"\begin{singlespace}",
            r"\footnotesize",
            r"\setlength{\tabcolsep}{3pt}",
            tabular,
            r"\end{singlespace}",
            r"\end{table}",
            "",
        ]
    )


def figure_environment(index: int, filename: str, caption: str) -> str:
    return "\n".join(
        [
            r"\begin{center}",
            r"\begin{minipage}{0.99\textwidth}",
            r"\centering",
            rf"\includegraphics[width=0.97\textwidth]{{figures/{filename}}}",
            r"\captionof{figure}{" + tex_escape(caption) + r"}",
            rf"\label{{fig:{index}}}",
            r"\end{minipage}",
            r"\end{center}",
            "",
        ]
    )


def make_dataset_table(dataset_path: Path) -> str:
    dataset = pd.read_csv(dataset_path)
    rows = [
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrrrlr@{}}",
        r"\toprule",
        r"资料集 & 候选数 & 分析数 & 加载失败 & 事件数 & 台站数 & 时长/s & 中位震级 \\",
        r"\midrule",
    ]
    for _, item in dataset.iterrows():
        duration = (
            f"{float(item['median_duration_sec']):.2f} "
            f"[{float(item['p05_duration_sec']):.2f}-{float(item['p95_duration_sec']):.2f}]"
        )
        rows.append(
            " & ".join(
                [
                    tex_escape(item["dataset"]),
                    fmt_int(item["candidate_records"]),
                    fmt_int(item["records"]),
                    fmt_int(item["load_error_records"]),
                    fmt_int(item["events"]),
                    fmt_int(item["stations"]),
                    tex_escape(duration),
                    fmt_num(item["median_magnitude"], 1),
                ]
            )
            + r" \\"
        )
    rows.extend([r"\bottomrule", r"\end{tabular*}"])
    return table_environment(
        "tab:dataset",
        "加速度记录样本流转。时长为中位数[5分位-95分位]。",
        "\n".join(rows),
    )


def make_priority_table(dataset_path: Path, priority_path: Path) -> str:
    dataset = pd.read_csv(dataset_path)
    priority = pd.read_csv(priority_path)
    rows = [
        r"\begin{tabular*}{0.76\textwidth}{@{\extracolsep{\fill}}llrrr@{}}",
        r"\toprule",
        r"资料集 & 分层 & 记录数 & 中位时长/s & 中位震级 \\",
        r"\midrule",
    ]
    for dataset_name in dataset["dataset"]:
        strata = priority[priority["dataset"].eq(dataset_name)].copy()
        strata["sort_key"] = strata["priority_group"].map({label: idx for idx, label in enumerate(PRIORITY_GROUP_ORDER)})
        for _, stratum in strata.sort_values("sort_key").iterrows():
            label = PRIORITY_GROUP_LABELS_ZH.get(str(stratum["priority_group"]), str(stratum["priority_group"]))
            rows.append(
                " & ".join(
                    [
                        tex_escape(dataset_name),
                        tex_escape(label),
                        fmt_int(stratum["records"]),
                        fmt_num(stratum["median_duration_sec"], 2),
                        fmt_num(stratum["median_magnitude"], 1),
                    ]
                )
                + r" \\"
            )
    rows.extend([r"\bottomrule", r"\end{tabular*}"])
    return table_environment(
        "tab:priority",
        "波形审计使用的资料集优先分层。",
        "\n".join(rows),
    )


def make_table_2(safeguard_path: Path, pnw_safeguard_path: Path) -> str:
    summary = pd.concat([pd.read_csv(safeguard_path), pd.read_csv(pnw_safeguard_path)], ignore_index=True)
    summary = summary[summary["priority_group"].eq("ALL") & summary["dataset"].ne("ALL")].copy()
    summary["dataset"] = summary["dataset"].replace({"PNWAccelerometers": "PNW"})
    rows = [
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"资料集 & 记录数 & 初选窗/\% & 能量窗/\% & 全记录/\% & 中位窗长/s & 75分位/s \\",
        r"\midrule",
    ]
    for dataset in ["InstanceGM", "K-NET", "PNW"]:
        item = summary[summary["dataset"].eq(dataset)].iloc[0]
        rows.append(
            " & ".join(
                [
                    tex_escape(dataset),
                    fmt_int(item["records"]),
                    fmt_pct(item["primary_pct"]),
                    fmt_pct(item["arias_escalation_pct"]),
                    fmt_pct(item["full_record_fallback_pct"]),
                    fmt_num(item["median_window_duration_sec"], 2),
                    fmt_num(item["p75_window_duration_sec"], 2),
                ]
            )
            + r" \\"
        )
    rows.extend([r"\bottomrule", r"\end{tabular}"])
    return table_environment("tab:stability", "逐分量峰值、能量和反应谱审计后的最终处理分流。", "\n".join(rows))


def make_table_3(response_path: Path) -> str:
    response = pd.read_csv(response_path)
    policies = [("feature_onset_fixed", "特征起点固定窗"), ("shortest_stable_no_catalog", "最短稳定窗")]
    periods = [0.2, 1.0, 3.0]
    rows = [
        r"\begin{tabular}{llrrr}",
        r"\toprule",
        r"资料集 & 策略 & 0.2 s失败率/\% & 1.0 s失败率/\% & 3.0 s失败率/\% \\",
        r"\midrule",
    ]
    for dataset in ["ALL", "InstanceGM", "K-NET"]:
        for policy, label in policies:
            values = []
            for period in periods:
                item = row_by(response, dataset=dataset, priority_group="ALL", policy=policy, period_sec=period)
                values.append(fmt_pct(item["spectrum_unstable_pct"]))
            rows.append(" & ".join([tex_escape(dataset), tex_escape(label), *values]) + r" \\")
    rows.extend([r"\bottomrule", r"\end{tabular}"])
    return table_environment("tab:response", "相对于全记录的 5% 阻尼 PSA 保留失败率。", "\n".join(rows))



def linkify_urls(markdown: str) -> str:
    return re.sub(r"(?<!<)(https://doi\.org/[^\s>)。；，]+)", r"<\1>", markdown)


def mark_headings_unnumbered(markdown: str) -> str:
    """Keep the explicit Chinese section numbers without LaTeX adding a second set."""
    return re.sub(
        r"^(#{2,6}) (.+?)(?:\s+\{\.unnumbered\})?$",
        r"\1 \2 {.unnumbered}",
        markdown,
        flags=re.MULTILINE,
    )


def insert_displays(markdown: str, tables: list[str]) -> str:
    displays = {
        "FIGURE_1": figure_environment(1, *FIGURES[0]),
        "FIGURE_2": figure_environment(2, *FIGURES[1]),
        "FIGURE_3": figure_environment(3, *FIGURES[2]),
        "FIGURE_4": figure_environment(4, *FIGURES[3]),
        "FIGURE_5": figure_environment(5, *FIGURES[4]),
        "FIGURE_6": figure_environment(6, *FIGURES[5]),
        "TABLE_1": tables[0],
        "TABLE_2": tables[1],
        "TABLE_3": tables[2],
    }
    anchors = [
        ("图 1 给出了两阶段审计流程。", ["FIGURE_1"]),
        ("主分析实际包含 44,674 条加速度记录（表 1）。", ["TABLE_1"]),
        ("各组资料见表 2。", ["TABLE_2"]),
        ("图 2 给出了固定窗时长试验。", ["FIGURE_2"]),
        ("图 4 对比了固定窗、初选窗和最终处理窗。", ["FIGURE_4"]),
        ("图 3 给出了最终分流和窗长。", ["FIGURE_3"]),
        ("三套资料的分流比例列于表 3。", ["TABLE_3"]),
        ("图 5 给出了端到端滤波灵敏度。", ["FIGURE_5"]),
        ("图 6 给出了 PNW 的信噪比分组结果。", ["FIGURE_6"]),
    ]
    updated = markdown
    for anchor, keys in anchors:
        if anchor not in updated:
            raise ValueError(f"missing Chinese display insertion anchor: {anchor}")
        updated = updated.replace(anchor, anchor + "\n\n" + "\n".join(displays[key] for key in keys), 1)
    return updated


def md_to_latex(markdown: str) -> str:
    proc = subprocess.run(
        [
            "pandoc",
            "-f",
            "markdown+raw_tex+tex_math_single_backslash+tex_math_dollars",
            "-t",
            "latex",
            "--wrap=none",
            "--shift-heading-level-by=-1",
        ],
        input=markdown,
        text=True,
        check=True,
        stdout=subprocess.PIPE,
    )
    return proc.stdout


def build_latex(body_latex: str) -> str:
    return "\n".join(
        [
            r"\documentclass[UTF8,a4paper,zihao=5]{ctexart}",
            r"\usepackage[left=2.1cm,right=2.1cm,top=2.2cm,bottom=1.8cm]{geometry}",
            r"\usepackage{graphicx}",
            r"\usepackage{booktabs}",
            r"\usepackage{caption}",
            r"\usepackage{amsmath}",
            r"\usepackage{array}",
            r"\usepackage{enumitem}",
            r"\usepackage{setspace}",
            r"\usepackage{xurl}",
            r"\usepackage{hyperref}",
            r"\hypersetup{colorlinks=true,linkcolor=black,urlcolor=blue,citecolor=black}",
            r"\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}",
            r"\captionsetup{font=small,labelfont=bf,labelsep=space}",
            r"\captionsetup[table]{position=top}",
            r"\setlength{\parindent}{2em}",
            r"\setlength{\parskip}{0pt}",
            r"\setlist[enumerate]{itemsep=0pt,topsep=2pt,parsep=0pt}",
            r"\linespread{1.25}",
            r"\ctexset{section={format=\zihao{4}\heiti},subsection={format=\zihao{5}\heiti}}",
            r"\begin{document}",
            r"\begin{center}",
            r"{\zihao{3}\heiti 面向强震动产品的两阶段处理窗质量审计方法\par}",
            r"\vspace{0.8em}",
            r"{\zihao{5} 周浩宇，马强$^{*}$\par}",
            r"\vspace{0.4em}",
            r"{\zihao{5} 中国地震局工程力学研究所，黑龙江 哈尔滨\par}",
            r"\vspace{0.4em}",
            r"{\zihao{5} $^{*}$通讯作者：maqiang@iem.ac.cn\par}",
            r"\end{center}",
            "",
            body_latex,
            r"\end{document}",
            "",
        ]
    )


def copy_figures(source_dir: Path, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    for filename, _caption in FIGURES:
        source = source_dir / filename
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, target_dir / filename)


def compile_pdf(outdir: Path) -> str:
    proc = subprocess.run(
        ["latexmk", "-xelatex", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        cwd=outdir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc.stdout


def clean_aux(outdir: Path) -> None:
    for suffix in [".aux", ".fdb_latexmk", ".fls", ".log", ".out", ".xdv"]:
        path = outdir / f"main{suffix}"
        if path.exists():
            path.unlink()


def main() -> None:
    args = parse_args()
    outdir = Path(args.outdir)
    markdown_path = Path(args.markdown)
    tables_dir = outdir / "tables"
    figures_dir = outdir / "figures"
    outdir.mkdir(parents=True, exist_ok=True)
    if not markdown_path.exists():
        raise FileNotFoundError(markdown_path)
    tables_dir.mkdir(parents=True, exist_ok=True)
    for stale_table in tables_dir.glob("table_*.tex"):
        stale_table.unlink()

    markdown = mark_headings_unnumbered(linkify_urls(markdown_path.read_text(encoding="utf-8")))
    table_chunks = [
        make_dataset_table(Path(args.dataset_summary)),
        make_priority_table(Path(args.dataset_summary), Path(args.priority_summary)),
        make_table_2(Path(args.spectral_safeguard), Path(args.pnw_spectral_safeguard)),
    ]
    for idx, table in enumerate(table_chunks, start=1):
        (tables_dir / f"table_{idx:02d}.tex").write_text(table.rstrip() + "\n", encoding="utf-8")
    copy_figures(Path(args.figure_dir), figures_dir)
    body_latex = md_to_latex(insert_displays(markdown, table_chunks))
    latex = build_latex(body_latex)
    (outdir / "main.tex").write_text(latex, encoding="utf-8")

    compiled = False
    compile_log = ""
    if args.compile:
        compile_log = compile_pdf(outdir)
        compiled = (outdir / "main.pdf").exists() and "Fatal error" not in compile_log
        if not compiled:
            (outdir / "latexmk.log").write_text(compile_log, encoding="utf-8")
            raise SystemExit("Chinese LaTeX compilation failed; see latexmk.log")
        shutil.copy2(outdir / "main.pdf", outdir / "qc_chinese.pdf")
        clean_aux(outdir)
    report = [
        "# StrongMotion-QC Chinese Manuscript Build Report",
        "",
        f"- Markdown: `{markdown_path}`",
        f"- Main TeX: `{outdir / 'main.tex'}`",
        f"- Main PDF: `{outdir / 'main.pdf'}`",
        f"- Compiled: {'yes' if compiled else 'no'}",
        "- Role: formal Chinese advisor-review manuscript synchronized with the StrongMotion-QC SRL evidence line.",
    ]
    (outdir / "latex_build_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Wrote {markdown_path.resolve()}")
    print(f"Wrote {(outdir / 'main.tex').resolve()}")
    if compiled:
        print(f"Wrote {(outdir / 'main.pdf').resolve()}")
        print(f"Wrote {(outdir / 'qc_chinese.pdf').resolve()}")
    print(f"Wrote {(outdir / 'latex_build_report.md').resolve()}")


if __name__ == "__main__":
    main()
