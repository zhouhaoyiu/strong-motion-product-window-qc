#!/usr/bin/env python3
"""Build the StrongMotion-QC SRL review manuscript package."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path

import pandas as pd


DEFAULT_DRAFT = "manuscripts/strong_motion_qc_srl/strong_motion_qc_srl_draft.md"
DEFAULT_OUTDIR = "manuscripts/strong_motion_qc_srl"
DEFAULT_FIGURE_DIR = "outputs/strong_motion_qc_figures_accel44674_hp0p1"
DEFAULT_DATASET_SUMMARY = "outputs/strong_motion_qc_dataset_table_accel44674_hp0p1/dataset_summary.csv"
DEFAULT_PRIORITY_SUMMARY = "outputs/strong_motion_qc_dataset_table_accel44674_hp0p1/priority_strata_summary.csv"
DEFAULT_SAFEGUARD_SUMMARY = "outputs/strong_motion_qc_spectral_safeguard_accel44674_hp0p1/summary.csv"
DEFAULT_PNW_SAFEGUARD_SUMMARY = "outputs/strong_motion_qc_spectral_safeguard_pnw_accel6107_hp0p1/summary.csv"
DEFAULT_METADATA = "docs/strong_motion_qc_srl_submission_metadata_template.csv"

FIGURES = [
    (
        "smqc_figure_01_workflow.pdf",
        "Two-stage processing-window audit. The first stage retains the shortest candidate that preserves every component peak acceleration, relative three-component energy, and component peak times. The second stage checks 5%-damped PSA at 0.2, 1.0, and 3.0 s and escalates failures to the padded 1%-99% cumulative-energy window or the full record.",
        "Workflow from candidate windows through component-level amplitude and energy checks, PSA checks, and three possible output routes.",
    ),
    (
        "smqc_figure_02_fixed_window_failure.pdf",
        "Fixed-duration sensitivity for InstanceGM, K-NET, and PNWAccelerometers. Values are instability rates for feature-onset windows ending 20, 40, 60, or 90 s after onset; each window also includes 2 s before onset.",
        "Line plot comparing fixed-window instability across four post-onset durations and three archives.",
    ),
    (
        "smqc_figure_03_selector_duration_fallback.pdf",
        "Final processing routes and window durations after the spectral safeguard. Records retain the primary window, escalate to the padded 1%-99% cumulative-energy window, or fall back to the full record. Error bars show the 75th percentile above the median duration.",
        "Stacked bars show three audit routes and adjacent bars show median and 75th-percentile output durations for three archives.",
    ),
    (
        "smqc_figure_04_product_impact_recovery.pdf",
        "PSA-retention failures at 0.2, 1.0, and 3.0 s for the 42 s fixed window, the primary amplitude-energy window, and the final safeguarded output. The safeguarded output meets the 0.95 threshold at every tested period by construction, with full-record fallback retained in the denominator.",
        "Grouped bars compare PSA-retention failures before and after the spectral safeguard for all records and each primary archive.",
    ),
    (
        "smqc_figure_05_filter_sensitivity.pdf",
        "High-pass-filter sensitivity on the same stratified 1,521-record sample. Panels compare primary-window 3.0 s PSA failures and final full-record fallback under 0.05 and 0.10 Hz preprocessing.",
        "Paired bars compare long-period PSA failures and conservative fallback rates at two high-pass corners.",
    ),
    (
        "smqc_figure_06_response_spectrum_retention.pdf",
        "PNWAccelerometers results by a result-blind RMS signal-to-noise ratio computed from catalog-timed pre-event and signal intervals. Panels show fixed-window instability, primary-window 3.0 s PSA failure, and final full-record fallback.",
        "Three bar charts compare fixed-window, primary-spectrum, and final-fallback behavior across three PNW signal-to-noise groups.",
    ),
]
PRIORITY_GROUP_LABELS = {
    "low_magnitude_background": "Low magnitude",
    "m3_to_m4_small_event": "M3-M4",
    "m4plus_strong_motion": "M4+",
    "other": "Other timing",
}
PRIORITY_GROUP_ORDER = [
    "low_magnitude_background",
    "m3_to_m4_small_event",
    "m4plus_strong_motion",
    "other",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", default=DEFAULT_DRAFT)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    parser.add_argument("--figure-dir", default=DEFAULT_FIGURE_DIR)
    parser.add_argument("--dataset-summary", default=DEFAULT_DATASET_SUMMARY)
    parser.add_argument("--priority-summary", default=DEFAULT_PRIORITY_SUMMARY)
    parser.add_argument("--spectral-safeguard", default=DEFAULT_SAFEGUARD_SUMMARY)
    parser.add_argument("--pnw-spectral-safeguard", default=DEFAULT_PNW_SAFEGUARD_SUMMARY)
    parser.add_argument("--metadata", default=DEFAULT_METADATA)
    parser.add_argument("--compile", action="store_true")
    return parser.parse_args()


def tex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def fmt_int(value: object) -> str:
    return f"{int(round(float(value))):,}"


def fmt_pct(value: object) -> str:
    return f"{float(value):.2f}"


def fmt_num(value: object, digits: int = 2) -> str:
    return f"{float(value):.{digits}f}"


def fmt_duration_range(row: pd.Series) -> str:
    return (
        f"{float(row['median_duration_sec']):.2f} "
        f"[{float(row['p05_duration_sec']):.2f}-{float(row['p95_duration_sec']):.2f}]"
    )


def row_by(df: pd.DataFrame, **filters: object) -> pd.Series:
    rows = df.copy()
    for key, value in filters.items():
        rows = rows[rows[key].eq(value)]
    if rows.empty:
        raise ValueError(f"missing row for {filters}")
    return rows.iloc[0]


def metadata_value(metadata_path: Path, field_id: str, default: str = "") -> str:
    if not metadata_path.exists():
        return default
    df = pd.read_csv(metadata_path).fillna("")
    rows = df[df["field_id"].eq(field_id)]
    if rows.empty:
        return default
    value = str(rows.iloc[0]["value"]).strip()
    return value or default


def author_block(metadata_path: Path) -> list[str]:
    authors = metadata_value(metadata_path, "author_order", "Haoyu Zhou; Qiang Ma")
    affiliations = metadata_value(
        metadata_path,
        "author_affiliations",
        "Haoyu Zhou: Institute of Engineering Mechanics, China Earthquake Administration, Harbin, Heilongjiang, China; Qiang Ma: Institute of Engineering Mechanics, China Earthquake Administration, Harbin, Heilongjiang, China",
    )
    author_emails = metadata_value(
        metadata_path,
        "author_emails",
        "Haoyu Zhou: zhouhaoyiu@gmail.com; Qiang Ma: maqiang@iem.ac.cn",
    )
    corresponding_name = metadata_value(metadata_path, "corresponding_author_name", "Qiang Ma")
    corresponding_email = metadata_value(metadata_path, "corresponding_author_email", "maqiang@iem.ac.cn")
    corresponding_address = metadata_value(
        metadata_path,
        "corresponding_author_mailing_address",
        "Institute of Engineering Mechanics, China Earthquake Administration, 29 Xuefu Road, Nangang District, Harbin, Heilongjiang, China",
    )
    return [
        tex_escape(authors).replace("; ", r"\\") + r"\\",
        r"\vspace{0.35em}",
        tex_escape(affiliations).replace("; ", r"\\") + r"\\",
        r"\vspace{0.35em}",
        tex_escape(author_emails).replace("; ", r"\\") + r"\\",
        r"\vspace{0.35em}",
        "Corresponding author: "
        + tex_escape(corresponding_name)
        + "; "
        + tex_escape(corresponding_email)
        + r"\\"
        + tex_escape(corresponding_address)
        + r"\\",
    ]


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


def split_draft(text: str) -> tuple[str, str]:
    title_match = re.match(r"#\s+(.+?)\n", text)
    if not title_match:
        raise ValueError("draft must start with a level-1 title")
    title = title_match.group(1).strip()
    body = text[title_match.end() :]
    manuscript = re.split(r"\n## Figure Captions\n", body, maxsplit=1)[0]
    ref_match = re.search(
        r"\n## (?:Working )?References\n(.+)$", manuscript, flags=re.DOTALL
    )
    if ref_match:
        manuscript = (
            manuscript[: ref_match.start()].rstrip()
            + "\n\n## References\n\n"
            + ref_match.group(1).strip()
        )
    return title, manuscript.strip()


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


def make_dataset_table(dataset_path: Path) -> str:
    dataset = pd.read_csv(dataset_path)
    analyzed_total = int(dataset["records"].sum())
    rows = [
        r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrrrlr@{}}",
        r"\toprule",
        r"Dataset & Candidates & Analyzed & Load errors & Events & Stations & Duration (s) & Median M \\",
        r"\midrule",
    ]
    for _, item in dataset.iterrows():
        rows.append(
            " & ".join(
                [
                    tex_escape(item["dataset"]),
                    fmt_int(item["candidate_records"]),
                    fmt_int(item["records"]),
                    fmt_int(item["load_error_records"]),
                    fmt_int(item["events"]),
                    fmt_int(item["stations"]),
                    tex_escape(fmt_duration_range(item)),
                    fmt_num(item["median_magnitude"], 1),
                ]
            )
            + r" \\"
        )
    rows.extend([r"\bottomrule", r"\end{tabular*}"])
    return table_environment(
        "tab:dataset",
        f"Dataset flow for the {analyzed_total:,}-record acceleration audit. Duration is median [5th-95th percentile].",
        "\n".join(rows),
    )


def make_priority_table(dataset_path: Path, priority_path: Path) -> str:
    dataset = pd.read_csv(dataset_path)
    priority = pd.read_csv(priority_path)
    rows = [
        r"\begin{tabular*}{0.82\textwidth}{@{\extracolsep{\fill}}llrrr@{}}",
        r"\toprule",
        r"Dataset & Stratum & Records & Median duration (s) & Median M \\",
        r"\midrule",
    ]
    for dataset_name in dataset["dataset"]:
        strata = priority[priority["dataset"].eq(dataset_name)].copy()
        strata["sort_key"] = strata["priority_group"].map({label: idx for idx, label in enumerate(PRIORITY_GROUP_ORDER)})
        for _, stratum in strata.sort_values("sort_key").iterrows():
            label = PRIORITY_GROUP_LABELS.get(str(stratum["priority_group"]), str(stratum["priority_group"]))
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
        "Priority-stratum summary used in the waveform audit.",
        "\n".join(rows),
    )


def make_table_2(safeguard_path: Path, pnw_safeguard_path: Path) -> str:
    summary = pd.concat([pd.read_csv(safeguard_path), pd.read_csv(pnw_safeguard_path)], ignore_index=True)
    summary = summary[summary["priority_group"].eq("ALL") & summary["dataset"].ne("ALL")].copy()
    summary["dataset"] = summary["dataset"].replace({"PNWAccelerometers": "PNW"})
    rows = [
        r"\begin{tabular}{lrrrrrr}",
        r"\toprule",
        r"Dataset & Records & Primary (\%) & Energy window (\%) & Full record (\%) & Median (s) & p75 (s) \\",
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
    return table_environment(
        "tab:stability",
        "Final routes after component-level peak, energy, and response-spectrum audits.",
        "\n".join(rows),
    )


def make_table_3(response_path: Path) -> str:
    response = pd.read_csv(response_path)
    policies = [("feature_onset_fixed", "Feature fixed"), ("shortest_stable_no_catalog", "Shortest stable")]
    periods = [0.2, 1.0, 3.0]
    rows = [
        r"\begin{tabular}{llrrr}",
        r"\toprule",
        r"Dataset & Policy & 0.2 s failure (\%) & 1.0 s failure (\%) & 3.0 s failure (\%) \\",
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
    return table_environment(
        "tab:response",
        "Response-spectrum retention summary. Values are 5% damping PSA-retention failure percentages relative to the full record.",
        "\n".join(rows),
    )


def copy_figures(source_dir: Path, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    for filename, _caption, _alt_text in FIGURES:
        src = source_dir / filename
        if not src.exists():
            raise FileNotFoundError(src)
        shutil.copy2(src, target_dir / filename)


def figure_latex() -> str:
    chunks = [r"\clearpage", r"\section*{Figures}"]
    for index, (filename, caption, alt_text) in enumerate(FIGURES, start=1):
        if index > 1:
            chunks.append(r"\clearpage")
        chunks.extend(
            [
                r"\begin{center}",
                r"\begin{minipage}{0.98\textwidth}",
                r"\centering",
                rf"\includegraphics[width=0.95\textwidth]{{figures/{filename}}}",
                r"\captionof{figure}{" + tex_escape(caption) + r"}",
                r"\noindent\textbf{Alt text:} " + tex_escape(alt_text),
                rf"\label{{fig:{index}}}",
                r"\end{minipage}",
                r"\end{center}",
                "",
            ]
        )
    return "\n".join(chunks)


def figure_environment(index: int, filename: str, caption: str, alt_text: str) -> str:
    return "\n".join(
        [
            r"\begin{center}",
            r"\begin{minipage}{0.98\textwidth}",
            r"\centering",
            rf"\includegraphics[width=0.95\textwidth]{{figures/{filename}}}",
            r"\captionof{figure}{" + tex_escape(caption) + r"}",
            r"\noindent\textbf{Alt text:} " + tex_escape(alt_text),
            rf"\label{{fig:{index}}}",
            r"\end{minipage}",
            r"\end{center}",
            "",
        ]
    )


def insert_display_items(body_md: str, table_chunks: list[str]) -> str:
    figures = {
        f"FIGURE_{index}": figure_environment(index, filename, caption, alt_text)
        for index, (filename, caption, alt_text) in enumerate(FIGURES, start=1)
    }
    displays = {
        "TABLE_1": table_chunks[0],
        "TABLE_2": table_chunks[1],
        "TABLE_3": table_chunks[2],
        **figures,
    }
    anchors = [
        ("Figure 1 summarizes the two-stage audit.", ["FIGURE_1"]),
        ("The analyzed population contains 44,674 acceleration records (Table 1).", ["TABLE_1"]),
        ("The magnitude strata are listed in Table 2.", ["TABLE_2"]),
        ("Figure 2 reports the fixed-duration sensitivity.", ["FIGURE_2"]),
        ("Figure 4 shows the corresponding PSA failures.", ["FIGURE_4"]),
        ("Figure 3 reports the final routing and duration.", ["FIGURE_3"]),
        ("Table 3 lists the routing percentages.", ["TABLE_3"]),
        ("Figure 5 reports this preprocessing sensitivity.", ["FIGURE_5"]),
        ("Figure 6 reports the SNR-stratified results.", ["FIGURE_6"]),
    ]
    updated = body_md
    for anchor, keys in anchors:
        pattern = re.compile(re.escape(anchor).replace(r"\ ", r"\s+"))
        match = pattern.search(updated)
        if not match:
            raise ValueError(f"missing display insertion anchor: {anchor}")
        block = "\n\n" + "\n".join(displays[key] for key in keys)
        updated = updated[: match.end()] + block + updated[match.end() :]
    return updated


def build_latex(
    title: str,
    authors: list[str],
    body_latex: str,
    tables: str = "",
    figures: str = "",
) -> str:
    legacy_appendix = ""
    if tables or figures:
        legacy_appendix = "\n".join(
            [
                r"\clearpage",
                r"\section*{Tables}",
                tables,
                figures,
            ]
        )
    return "\n".join(
        [
            r"\pdfoutput=1",
            r"\documentclass[12pt,letterpaper]{article}",
            r"\usepackage[margin=1in]{geometry}",
            r"\usepackage{setspace}",
            r"\usepackage{lineno}",
            r"\usepackage{graphicx}",
            r"\usepackage{booktabs}",
            r"\usepackage{caption}",
            r"\usepackage{amsmath}",
            r"\usepackage{array}",
            r"\usepackage{xurl}",
            r"\usepackage[hidelinks]{hyperref}",
            r"\usepackage[T1]{fontenc}",
            r"\usepackage[utf8]{inputenc}",
            r"\usepackage{lmodern}",
            r"\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}",
            r"\captionsetup{font=small,labelfont=bf}",
            r"\setcounter{secnumdepth}{0}",
            r"\setlength{\parindent}{0.25in}",
            r"\setlength{\parskip}{0pt}",
            r"\setlength{\emergencystretch}{3em}",
            r"\doublespacing",
            r"\linenumbers",
            r"\modulolinenumbers[1]",
            r"\begin{document}",
            r"\begin{center}",
            r"{\Large\bfseries " + tex_escape(title) + r"}\\[1.5em]",
            *authors,
            r"\end{center}",
            r"\thispagestyle{plain}",
            "",
            body_latex,
            legacy_appendix,
            r"\end{document}",
            "",
        ]
    )


def compile_pdf(outdir: Path) -> str:
    proc = subprocess.run(
        ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        cwd=outdir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc.stdout


def clean_latex_aux(outdir: Path) -> None:
    for name in ["main.aux", "main.fdb_latexmk", "main.fls", "main.log"]:
        path = outdir / name
        if path.exists():
            path.unlink()


def write_report(outdir: Path, compiled: bool, compile_log: str | None) -> None:
    lines = [
        "# StrongMotion-QC SRL LaTeX Build Report",
        "",
        f"- Main TeX: `{outdir / 'main.tex'}`",
        f"- Main PDF: `{outdir / 'main.pdf'}`",
        f"- Compiled: {'yes' if compiled else 'no'}",
        "- Format target: SRL initial-review PDF style, with letter paper, 1 inch margins, 12 pt text, double spacing, line numbers, page numbers, 6 figures, and 3 main tables.",
    ]
    (outdir / "latex_build_report.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    args = parse_args()
    draft = Path(args.draft)
    outdir = Path(args.outdir)
    figure_source = Path(args.figure_dir)
    tables_dir = outdir / "tables"
    figures_dir = outdir / "figures"
    outdir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    for stale_table in tables_dir.glob("table_*.tex"):
        stale_table.unlink()

    title, body_md = split_draft(draft.read_text())
    table_chunks = [
        make_dataset_table(Path(args.dataset_summary)),
        make_priority_table(Path(args.dataset_summary), Path(args.priority_summary)),
        make_table_2(Path(args.spectral_safeguard), Path(args.pnw_spectral_safeguard)),
    ]
    for idx, table in enumerate(table_chunks, start=1):
        (tables_dir / f"table_{idx:02d}.tex").write_text(table.rstrip() + "\n")
    copy_figures(figure_source, figures_dir)
    body_latex = md_to_latex(insert_display_items(body_md, table_chunks))
    authors = author_block(Path(args.metadata))
    latex = build_latex(title, authors, body_latex)
    (outdir / "main.tex").write_text(latex)

    compile_log = None
    compiled = False
    if args.compile:
        compile_log = compile_pdf(outdir)
        compiled = (outdir / "main.pdf").exists() and "Fatal error" not in compile_log
        if not compiled:
            (outdir / "latexmk.log").write_text(compile_log)
            write_report(outdir, False, compile_log)
            raise SystemExit("LaTeX compilation failed; see latexmk.log")
        shutil.copy2(outdir / "main.pdf", outdir / "qc.pdf")
        clean_latex_aux(outdir)
    write_report(outdir, compiled, compile_log)
    print(f"Wrote {(outdir / 'main.tex').resolve()}")
    if compiled:
        print(f"Wrote {(outdir / 'main.pdf').resolve()}")
        print(f"Wrote {(outdir / 'qc.pdf').resolve()}")
    print(f"Wrote {(outdir / 'latex_build_report.md').resolve()}")


if __name__ == "__main__":
    main()
