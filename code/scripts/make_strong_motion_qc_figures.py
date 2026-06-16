#!/usr/bin/env python3
"""Create publication-oriented StrongMotion-QC figures."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_SELECTOR_SUMMARY = "outputs/strong_motion_qc_product_window_selector/summary.csv"
DEFAULT_PRODUCT_IMPACT = "outputs/strong_motion_qc_product_impact/product_impact_summary.csv"
DEFAULT_SENSITIVITY = "outputs/strong_motion_qc_selector_sensitivity/sensitivity_summary.csv"
DEFAULT_RESPONSE_SPECTRUM = "outputs/strong_motion_qc_response_spectrum_knet22119_hp1_inst3000/summary.csv"
DEFAULT_OUTDIR = "outputs/strong_motion_qc_figures"
DATASETS = ["InstanceGM", "K-NET"]
LANGUAGE = "en"
FIXED_METHODS = ["feature_onset_fixed", "energy_onset_fixed", "catalog_p_fixed"]
CORE_METHODS = ["feature_onset_fixed", "energy_onset_fixed", "catalog_p_fixed", "adaptive_energy_end", "shortest_stable_no_catalog"]
METHOD_LABELS_EN = {
    "feature_onset_fixed": "Feature fixed",
    "energy_onset_fixed": "Energy fixed",
    "catalog_p_fixed": "Catalog-P fixed",
    "adaptive_energy_end": "Adaptive",
    "shortest_stable_no_catalog": "Shortest stable",
    "full_record": "Full record",
}
METHOD_LABELS_ZH = {
    "feature_onset_fixed": "特征起点窗",
    "energy_onset_fixed": "能量起点窗",
    "catalog_p_fixed": "目录P窗",
    "adaptive_energy_end": "适应性窗",
    "shortest_stable_no_catalog": "最短稳定窗",
    "full_record": "全记录",
}
HATCHES = ["", "///", "\\\\\\", "xxx", "...", "---"]
COLORS = {
    "feature_onset_fixed": "#4d4d4d",
    "energy_onset_fixed": "#7a7a7a",
    "catalog_p_fixed": "#a6a6a6",
    "adaptive_energy_end": "#d9d9d9",
    "shortest_stable_no_catalog": "#111111",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selector-summary", default=DEFAULT_SELECTOR_SUMMARY)
    parser.add_argument("--product-impact", default=DEFAULT_PRODUCT_IMPACT)
    parser.add_argument("--sensitivity", default=DEFAULT_SENSITIVITY)
    parser.add_argument("--response-spectrum", default=DEFAULT_RESPONSE_SPECTRUM)
    parser.add_argument("--outdir", default=DEFAULT_OUTDIR)
    parser.add_argument("--formats", nargs="+", default=["png", "pdf"])
    parser.add_argument("--language", choices=["en", "zh"], default="en")
    return parser.parse_args()


def text(en: str, zh: str) -> str:
    return zh if LANGUAGE == "zh" else en


def method_label(method: str) -> str:
    labels = METHOD_LABELS_ZH if LANGUAGE == "zh" else METHOD_LABELS_EN
    return labels[method]


def configure_matplotlib() -> None:
    import matplotlib.pyplot as plt

    font_family = "DejaVu Sans"
    if LANGUAGE == "zh":
        font_family = ["Hiragino Sans GB", "Arial Unicode MS", "DejaVu Sans"]
    plt.rcParams.update(
        {
            "figure.dpi": 120,
            "savefig.dpi": 300,
            "font.family": font_family,
            "font.size": 9.4,
            "axes.titlesize": 10.0,
            "axes.labelsize": 9.4,
            "legend.fontsize": 8.6,
            "xtick.labelsize": 8.4,
            "ytick.labelsize": 8.4,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.22,
            "grid.linewidth": 0.6,
            "axes.unicode_minus": False,
        }
    )


def save_figure(fig, outdir: Path, stem: str, formats: list[str]) -> list[Path]:
    paths = []
    for fmt in formats:
        path = outdir / f"{stem}.{fmt}"
        fig.savefig(path, bbox_inches="tight", pad_inches=0.04)
        paths.append(path)
    return paths


def dataset_policy(summary: pd.DataFrame, policy: str) -> pd.DataFrame:
    return summary[summary["dataset"].isin(DATASETS) & summary["priority_group"].eq("ALL") & summary["policy"].eq(policy)]


def figure_workflow(outdir: Path, formats: list[str]) -> list[Path]:
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

    fig, ax = plt.subplots(figsize=(7.4, 3.25), constrained_layout=True)
    ax.axis("off")

    def panel(x: float, y: float, w: float, h: float, title: str) -> None:
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.012,rounding_size=0.012",
                linewidth=0.9,
                edgecolor="#222222",
                facecolor="#f6f6f6",
            )
        )
        ax.text(x + 0.02, y + h - 0.055, title, ha="left", va="center", fontsize=8.7, fontweight="bold")

    panel(0.04, 0.54, 0.23, 0.34, text("1  Waveform record", "1  波形记录"))
    t = np.linspace(0, 1, 180)
    signal = 0.018 * np.sin(20 * np.pi * t)
    signal += 0.13 * np.exp(-((t - 0.48) ** 2) / 0.018) * np.sin(55 * np.pi * t)
    x = 0.065 + 0.18 * t
    y = 0.67 + signal
    ax.plot(x, y, color="#222222", lw=0.9)
    for xx, label in [(0.125, text("onset", "起点")), (0.185, text("peak", "峰值"))]:
        ax.plot([xx, xx], [0.585, 0.79], color="#555555", lw=0.8, ls="--")
        ax.text(xx, 0.575, label, ha="center", va="top", fontsize=7.2)

    panel(0.34, 0.54, 0.27, 0.34, text("2  Candidate windows", "2  候选处理窗"))
    ax.plot([0.375, 0.575], [0.64, 0.64], color="#222222", lw=0.8)
    candidates = [
        (text("fixed", "固定窗"), 0.39, 0.71, 0.095, "#d9d9d9"),
        (text("adaptive", "适应性窗"), 0.39, 0.66, 0.145, "#bdbdbd"),
        (text("full", "全记录"), 0.375, 0.59, 0.20, "#ffffff"),
    ]
    for label, x0, y0, width, face in candidates:
        ax.add_patch(Rectangle((x0, y0), width, 0.028, facecolor=face, edgecolor="#222222", lw=0.7))
        ax.text(x0 + width + 0.012, y0 + 0.014, label, ha="left", va="center", fontsize=7.6)
    ax.text(0.475, 0.79, text("same record, multiple windows", "同一记录，多种候选窗"), ha="center", va="center", fontsize=7.5)

    panel(0.68, 0.54, 0.26, 0.34, text("3  Product audit", "3  产品审计"))
    audit_rows = [
        (text("PGA ratio", "PGA比值"), r"$\geq$ 0.99"),
        (text("Energy ratio", "能量比值"), r"$\geq$ 0.95"),
        (text("Peak time", "峰值时刻"), text("inside", "在窗内")),
    ]
    for idx, (left, right) in enumerate(audit_rows):
        yy = 0.76 - idx * 0.065
        ax.plot([0.705, 0.915], [yy - 0.027, yy - 0.027], color="#d0d0d0", lw=0.5)
        ax.text(0.71, yy, left, ha="left", va="center", fontsize=7.9)
        ax.text(0.91, yy, right, ha="right", va="center", fontsize=7.9)

    ax.add_patch(
        FancyBboxPatch(
            (0.22, 0.18),
            0.22,
            0.17,
            boxstyle="round,pad=0.014,rounding_size=0.012",
            linewidth=0.9,
            edgecolor="#222222",
            facecolor="#ffffff",
        )
    )
    ax.text(0.33, 0.285, text("select shortest\nstable candidate", "选择最短\n稳定候选"), ha="center", va="center", fontsize=8.8)
    ax.text(0.33, 0.215, text("record selected window", "输出处理窗"), ha="center", va="center", fontsize=7.5)

    ax.add_patch(
        FancyBboxPatch(
            (0.58, 0.18),
            0.22,
            0.17,
            boxstyle="round,pad=0.014,rounding_size=0.012",
            linewidth=0.9,
            edgecolor="#222222",
            facecolor="#f0f0f0",
        )
    )
    ax.text(0.69, 0.285, text("full record", "全记录"), ha="center", va="center", fontsize=8.8, fontweight="bold")
    ax.text(0.69, 0.215, text("assigned if no\ncandidate passes", "候选均失败\n则分配全记录"), ha="center", va="center", fontsize=7.5)

    arrow_style = dict(arrowstyle="->", mutation_scale=10, lw=0.95, color="#222222")
    ax.add_patch(FancyArrowPatch((0.275, 0.71), (0.34, 0.71), **arrow_style))
    ax.add_patch(FancyArrowPatch((0.61, 0.71), (0.68, 0.71), **arrow_style))
    ax.add_patch(FancyArrowPatch((0.755, 0.54), (0.43, 0.31), connectionstyle="arc3,rad=-0.18", **arrow_style))
    ax.add_patch(FancyArrowPatch((0.815, 0.54), (0.64, 0.34), connectionstyle="arc3,rad=0.12", **arrow_style))
    ax.text(0.51, 0.39, text("pass", "通过"), ha="center", va="center", fontsize=7.7)
    ax.text(0.74, 0.39, text("none pass", "均未通过"), ha="center", va="center", fontsize=7.7)

    ax.set_xlim(-0.02, 1.04)
    ax.set_ylim(0, 1)
    return save_figure(fig, outdir, "smqc_figure_01_workflow", formats)


def figure_fixed_window_failure(selector_summary: pd.DataFrame, outdir: Path, formats: list[str]) -> list[Path]:
    import matplotlib.pyplot as plt

    data = selector_summary[
        selector_summary["dataset"].isin(DATASETS)
        & selector_summary["priority_group"].eq("ALL")
        & selector_summary["policy"].isin(CORE_METHODS)
    ].copy()
    fig, ax = plt.subplots(figsize=(7.1, 3.35), constrained_layout=True)
    x = np.arange(len(DATASETS))
    width = 0.15
    for idx, method in enumerate(CORE_METHODS):
        vals = []
        for dataset in DATASETS:
            row = data[data["dataset"].eq(dataset) & data["policy"].eq(method)].iloc[0]
            vals.append(float(row["unstable_pct"]))
        offset = (idx - (len(CORE_METHODS) - 1) / 2) * width
        bars = ax.bar(
            x + offset,
            vals,
            width=width,
            label=method_label(method),
            color=COLORS[method],
            edgecolor="black",
            linewidth=0.4,
            hatch=HATCHES[idx],
        )
        ax.bar_label(bars, fmt="%.1f", padding=1.5, fontsize=7)
    ax.set_xticks(x)
    ax.set_xticklabels(DATASETS)
    ax.set_ylabel(text("Unstable windows (%)", "不稳定率 (%)"))
    ax.set_title(text("(a) Product-window instability", "（a）处理窗不稳定率"))
    ax.set_ylim(0, max(90, data["unstable_pct"].max() + 8))
    ax.legend(ncol=3, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.16))
    return save_figure(fig, outdir, "smqc_figure_02_fixed_window_failure", formats)


def figure_selector_duration(selector_summary: pd.DataFrame, outdir: Path, formats: list[str]) -> list[Path]:
    import matplotlib.pyplot as plt

    rows = dataset_policy(selector_summary, "shortest_stable_no_catalog")
    fig, axes = plt.subplots(
        1,
        2,
        figsize=(7.0, 3.1),
        gridspec_kw={"width_ratios": [1.2, 1.0]},
        constrained_layout=True,
    )
    x = np.arange(len(DATASETS))
    med = [float(rows[rows["dataset"].eq(dataset)]["median_window_duration_sec"].iloc[0]) for dataset in DATASETS]
    p25 = [float(rows[rows["dataset"].eq(dataset)]["p25_window_duration_sec"].iloc[0]) for dataset in DATASETS]
    p75 = [float(rows[rows["dataset"].eq(dataset)]["p75_window_duration_sec"].iloc[0]) for dataset in DATASETS]
    yerr = np.vstack([np.array(med) - np.array(p25), np.array(p75) - np.array(med)])
    bars = axes[0].bar(x, med, yerr=yerr, capsize=3, color=["#555555", "#111111"], edgecolor="black", linewidth=0.5)
    axes[0].bar_label(bars, fmt="%.1f s", padding=2, fontsize=7)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(DATASETS)
    axes[0].set_ylabel(text("Selected duration (s)", "选窗时长 (s)"))
    axes[0].set_title(text("(a) Selected-window duration", "（a）选窗时长"))

    fallback = [float(rows[rows["dataset"].eq(dataset)]["full_record_fallback_pct"].iloc[0]) for dataset in DATASETS]
    bars = axes[1].bar(x, fallback, color=["#888888", "#333333"], edgecolor="black", linewidth=0.5)
    axes[1].bar_label(bars, fmt="%.2f%%", padding=2, fontsize=7)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(DATASETS)
    axes[1].set_ylabel(text("Full-record assignment (%)", "全记录处理比例 (%)"))
    axes[1].set_title(text("(b) Full-record assignment", "（b）全记录处理比例"))
    axes[1].set_ylim(0, max(2.0, max(fallback) + 0.8))
    return save_figure(fig, outdir, "smqc_figure_03_selector_duration_fallback", formats)


def figure_product_impact(product_impact: pd.DataFrame, outdir: Path, formats: list[str]) -> list[Path]:
    import matplotlib.pyplot as plt

    methods = FIXED_METHODS
    if LANGUAGE == "zh":
        labels = ["特征起点", "能量起点", "目录P"]
    else:
        labels = [method_label(m).replace(" fixed", "") for m in methods]
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.55), sharex=True, constrained_layout=True)
    x = np.arange(len(methods))
    width = 0.36
    colors = {"InstanceGM": "#7a7a7a", "K-NET": "#222222"}

    for ds_idx, dataset in enumerate(DATASETS):
        data = product_impact[
            product_impact["dataset"].eq(dataset)
            & product_impact["priority_group"].eq("ALL")
            & product_impact["baseline_candidate"].isin(methods)
        ].copy()
        offset = (ds_idx - 0.5) * width
        unstable = [
            float(data[data["baseline_candidate"].eq(method)]["baseline_unstable_pct"].iloc[0])
            for method in methods
        ]
        energy_gain = [
            float(data[data["baseline_candidate"].eq(method)]["median_energy_gain"].iloc[0])
            for method in methods
        ]
        duration_change = [
            float(data[data["baseline_candidate"].eq(method)]["median_duration_change_sec"].iloc[0])
            for method in methods
        ]
        bars = axes[0].bar(
            x + offset,
            unstable,
            width=width,
            label=dataset,
            color=colors[dataset],
            edgecolor="black",
            linewidth=0.4,
            hatch="" if dataset == "InstanceGM" else "///",
        )
        axes[0].bar_label(bars, fmt="%.1f", padding=1.5, fontsize=6.8)
        bars = axes[1].bar(
            x + offset,
            energy_gain,
            width=width,
            color=colors[dataset],
            edgecolor="black",
            linewidth=0.4,
            hatch="" if dataset == "InstanceGM" else "///",
        )
        axes[1].bar_label(bars, fmt="%.2f", padding=1.5, fontsize=6.8)
        bars = axes[2].bar(
            x + offset,
            duration_change,
            width=width,
            color=colors[dataset],
            edgecolor="black",
            linewidth=0.4,
            hatch="" if dataset == "InstanceGM" else "///",
        )
        axes[2].bar_label(bars, fmt="%.1f", padding=1.5, fontsize=6.8)

    axes[0].set_title(text("(a) Fixed-window failures", "（a）固定窗失败率"))
    axes[0].set_ylabel(text("Unstable windows (%)", "不稳定率 (%)"))
    axes[1].set_title(text("(b) Median energy gain", "（b）能量增益中位数"))
    axes[1].set_ylabel(text("Energy-retention gain", "能量保留率增益"))
    axes[2].set_title(text("(c) Median duration change", "（c）时长变化中位数"))
    axes[2].set_ylabel(text("Selected - baseline (s)", "选窗-基线 (s)"))
    axes[2].axhline(0, color="#222222", linewidth=0.7)
    for ax in axes:
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=25, ha="right")
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, frameon=False, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.06))
    return save_figure(fig, outdir, "smqc_figure_04_product_impact_recovery", formats)


def figure_threshold_sensitivity(sensitivity: pd.DataFrame, outdir: Path, formats: list[str]) -> list[Path]:
    import matplotlib.pyplot as plt

    data = sensitivity[sensitivity["dataset"].isin(DATASETS) & sensitivity["priority_group"].eq("ALL") & sensitivity["pga_threshold"].eq(0.99)].copy()
    energy_levels = sorted(data["energy_threshold"].unique())
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 2.55), constrained_layout=True)
    markers = {"InstanceGM": "o", "K-NET": "s"}
    for dataset in DATASETS:
        subset = data[data["dataset"].eq(dataset)].sort_values("energy_threshold")
        axes[0].plot(
            subset["energy_threshold"],
            subset["full_record_fallback_pct"],
            marker=markers[dataset],
            linewidth=1.4,
            label=dataset,
            color="#111111" if dataset == "K-NET" else "#666666",
        )
        axes[1].plot(
            subset["energy_threshold"],
            subset["median_window_duration_sec"],
            marker=markers[dataset],
            linewidth=1.4,
            label=dataset,
            color="#111111" if dataset == "K-NET" else "#666666",
        )
    for ax in axes:
        ax.set_xticks(energy_levels)
        ax.set_xlabel(text("Energy-retention threshold", "能量保留阈值"))
        ax.legend(frameon=False)
    axes[0].set_ylabel(text("Full-record assignment (%)", "全记录处理比例 (%)"))
    axes[0].set_title(text("(a) Assignment sensitivity", "（a）全记录处理敏感性"))
    axes[1].set_ylabel(text("Median selected duration (s)", "中位选窗时长 (s)"))
    axes[1].set_title(text("(b) Duration sensitivity", "（b）窗长敏感性"))
    return save_figure(fig, outdir, "smqc_figure_05_threshold_sensitivity", formats)


def figure_response_spectrum_retention(response_spectrum: pd.DataFrame, outdir: Path, formats: list[str]) -> list[Path]:
    import matplotlib.pyplot as plt

    datasets = ["ALL", "InstanceGM", "K-NET"]
    methods = ["feature_onset_fixed", "energy_onset_fixed", "catalog_p_fixed", "shortest_stable_no_catalog"]
    markers = {
        "feature_onset_fixed": "o",
        "energy_onset_fixed": "s",
        "catalog_p_fixed": "^",
        "shortest_stable_no_catalog": "D",
    }
    linestyles = {
        "feature_onset_fixed": "-",
        "energy_onset_fixed": "--",
        "catalog_p_fixed": ":",
        "shortest_stable_no_catalog": "-.",
    }
    colors = {
        "feature_onset_fixed": "#4d4d4d",
        "energy_onset_fixed": "#7a7a7a",
        "catalog_p_fixed": "#a6a6a6",
        "shortest_stable_no_catalog": "#111111",
    }
    data = response_spectrum[
        response_spectrum["dataset"].isin(datasets)
        & response_spectrum["priority_group"].eq("ALL")
        & response_spectrum["policy"].isin(methods)
    ].copy()
    fig, axes = plt.subplots(1, 3, figsize=(7.6, 2.55), sharey=True, constrained_layout=True)
    for ax, dataset in zip(axes, datasets):
        subset = data[data["dataset"].eq(dataset)]
        for method in methods:
            row = subset[subset["policy"].eq(method)].sort_values("period_sec")
            ax.plot(
                row["period_sec"],
                row["spectrum_unstable_pct"],
                marker=markers[method],
                linestyle=linestyles[method],
                linewidth=1.2,
                markersize=3.8,
                color=colors[method],
                label=method_label(method),
            )
        ax.set_title(dataset)
        ax.set_xlabel(text("Period (s)", "周期 (s)"))
        ax.set_xticks([0.2, 1.0, 3.0])
    axes[0].set_ylabel(text("PSA-retention failures (%)", "PSA保留失败率 (%)"))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.07))
    return save_figure(fig, outdir, "smqc_figure_06_response_spectrum_retention", formats)


def write_manifest(outdir: Path, generated: dict[str, list[Path]], source_paths: dict[str, str]) -> None:
    rows = [
        {
            "figure_id": "Fig. 1",
            "stem": "smqc_figure_01_workflow",
            "title": "Product-stable window-selection workflow",
            "source": "method schematic",
            "manuscript_role": "Defines candidate generation, product checks, selector, and full-record assignment.",
            "boundary": "Offline workflow; streaming picking is outside scope.",
        },
        {
            "figure_id": "Fig. 2",
            "stem": "smqc_figure_02_fixed_window_failure",
            "title": "Fixed-window failure by dataset",
            "source": source_paths["selector_summary"],
            "manuscript_role": "Shows dataset dependence of fixed 40 s windows.",
            "boundary": "Product-window audit, separate from manual QC labels.",
        },
        {
            "figure_id": "Fig. 3",
            "stem": "smqc_figure_03_selector_duration_fallback",
            "title": "Selected-window duration and full-record assignment",
            "source": source_paths["selector_summary"],
            "manuscript_role": "Shows selected-window duration and full-record assignment at the default threshold.",
            "boundary": "Selector is offline and product-derived.",
        },
        {
            "figure_id": "Fig. 4",
            "stem": "smqc_figure_04_product_impact_recovery",
            "title": "Product-impact recovery",
            "source": source_paths["product_impact"],
            "manuscript_role": "Quantifies records recovered from fixed-window product failures.",
            "boundary": "Recovered denotes product-retention pass, separate from human relabeling.",
        },
        {
            "figure_id": "Fig. 5",
            "stem": "smqc_figure_05_threshold_sensitivity",
            "title": "Threshold sensitivity",
            "source": source_paths["sensitivity"],
            "manuscript_role": "Shows how the energy-retention threshold changes full-record assignment.",
            "boundary": "Threshold dependence is reported explicitly.",
        },
        {
            "figure_id": "Fig. 6",
            "stem": "smqc_figure_06_response_spectrum_retention",
            "title": "Response-spectrum retention",
            "source": source_paths["response_spectrum"],
            "manuscript_role": "Connects selected windows to strong-motion engineering products.",
            "boundary": "Relative pseudo-spectral acceleration retention, separate from site-specific design spectra.",
        },
    ]
    for row in rows:
        paths = generated.get(row["stem"], [])
        for path in paths:
            row[path.suffix.lstrip("_ .")] = str(path)
    manifest = pd.DataFrame(rows)
    manifest.to_csv(outdir / "figure_manifest.csv", index=False)
    lines = [
        "# StrongMotion-QC Figures",
        "",
        "Publication-oriented figures for the SRL route.",
        "",
        "| figure_id | title | manuscript_role | source | boundary |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['figure_id']} | {row['title']} | {row['manuscript_role']} | `{row['source']}` | {row['boundary']} |"
        )
    (outdir / "README.md").write_text("\n".join(lines) + "\n")


def make_figures(
    selector_summary_path: Path,
    product_impact_path: Path,
    sensitivity_path: Path,
    response_spectrum_path: Path,
    outdir: Path,
    formats: list[str],
) -> dict[str, list[Path]]:
    configure_matplotlib()
    outdir.mkdir(parents=True, exist_ok=True)
    selector_summary = pd.read_csv(selector_summary_path)
    product_impact = pd.read_csv(product_impact_path)
    sensitivity = pd.read_csv(sensitivity_path)
    response_spectrum = pd.read_csv(response_spectrum_path)
    generated = {
        "smqc_figure_01_workflow": figure_workflow(outdir, formats),
        "smqc_figure_02_fixed_window_failure": figure_fixed_window_failure(selector_summary, outdir, formats),
        "smqc_figure_03_selector_duration_fallback": figure_selector_duration(selector_summary, outdir, formats),
        "smqc_figure_04_product_impact_recovery": figure_product_impact(product_impact, outdir, formats),
        "smqc_figure_05_threshold_sensitivity": figure_threshold_sensitivity(sensitivity, outdir, formats),
        "smqc_figure_06_response_spectrum_retention": figure_response_spectrum_retention(response_spectrum, outdir, formats),
    }
    write_manifest(
        outdir,
        generated,
        {
            "selector_summary": str(selector_summary_path),
            "product_impact": str(product_impact_path),
            "sensitivity": str(sensitivity_path),
            "response_spectrum": str(response_spectrum_path),
        },
    )
    return generated


def main() -> None:
    global LANGUAGE
    args = parse_args()
    LANGUAGE = args.language
    generated = make_figures(
        selector_summary_path=Path(args.selector_summary),
        product_impact_path=Path(args.product_impact),
        sensitivity_path=Path(args.sensitivity),
        response_spectrum_path=Path(args.response_spectrum),
        outdir=Path(args.outdir),
        formats=args.formats,
    )
    for paths in generated.values():
        for path in paths:
            print(f"Wrote {path.resolve()}")
    print(f"Wrote {(Path(args.outdir) / 'figure_manifest.csv').resolve()}")
    print(f"Wrote {(Path(args.outdir) / 'README.md').resolve()}")


if __name__ == "__main__":
    main()
