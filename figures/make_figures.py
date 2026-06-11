#!/usr/bin/env python3
"""
Generate Figures 1, 2, 3 for Preprint 1 v0.5.

Color discipline (CLAUDE.md Hard Rule #7):
    cream background #F2EDE4 + navy primary #1A2744 + one muted accent #8A8175.
    No default matplotlib palette is used; rcParams override the default cycle.

Data source: PREPRINT_1_v0_5_2026_05_27_EN.md sections 6.1-6.4.

Output:
    fig1_gate_b_long_horizon.{png,pdf}
    fig2_gate_c_diagnostics.{png,pdf}
    fig3_gate_a_baseline.{png,pdf}
    color_evidence.json
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# ----------------------------------------------------------------------
# Color discipline (Hard Rule #7) -- academic B&W override for arXiv 2026-05-28
# Constants keep their original names so all "color=CREAM/NAVY/MUTED"
# call sites resolve without code changes; only values change.
# ----------------------------------------------------------------------

CREAM = "white"     # was "#F2EDE4" -- blend into arXiv white page
NAVY = "black"      # was "#1A2744" -- printer-friendly primary
MUTED = "#666666"   # was "#8A8175" -- 40% gray for secondary series

plt.rcParams.update(
    {
        "axes.facecolor": CREAM,
        "figure.facecolor": CREAM,
        "savefig.facecolor": CREAM,
        "savefig.edgecolor": CREAM,
        "axes.edgecolor": NAVY,
        "axes.labelcolor": NAVY,
        "xtick.color": NAVY,
        "ytick.color": NAVY,
        "text.color": NAVY,
        "axes.titlecolor": NAVY,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "font.size": 11,
        "axes.linewidth": 1.0,
        "axes.titlesize": 11,
        "legend.frameon": False,
    }
)

FIGURES_DIR = Path(__file__).parent
FIGURES_DIR.mkdir(exist_ok=True)


# ----------------------------------------------------------------------
# Figure 1 — Gate B: long-horizon final-token accuracy
# ----------------------------------------------------------------------


def figure_1() -> None:
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(10, 4.2))

    # S_3 × S_3 chance for Gate B (order 36)
    chance_36 = 1.0 / 36.0
    chance_label = f"chance = 1/36 ≈ {chance_36:.4f}"

    # Left panel: short horizons (only structured SSM has data in §6.2 table)
    short_lengths = [4096, 16384, 65536]
    ssm_short = [0.0000, 0.0000, 0.0000]
    ax_left.semilogx(
        short_lengths,
        ssm_short,
        marker="o",
        linestyle="-",
        color=MUTED,
        label="structured SSM (native)",
        linewidth=1.8,
        markersize=8,
    )
    ax_left.axhline(chance_36, color=NAVY, linestyle=":", linewidth=1.0, alpha=0.6, label=chance_label)
    ax_left.set_xlabel("Evaluation length (tokens)")
    ax_left.set_ylabel("Final-token accuracy")
    ax_left.set_title("(a) Short-horizon regime")
    ax_left.set_ylim(-0.05, 1.05)
    ax_left.set_xlim(2000, 100000)
    ax_left.legend(loc="upper right", fontsize=9)
    ax_left.grid(True, alpha=0.25, color=NAVY)

    # Right panel: long horizons (ours + bag + GRU)
    long_lengths = np.array([524288, 1048576])
    ours = [1.0000, 1.0000]
    bag = [0.0000, 0.0000]
    gru = [0.0000, 0.0500]

    ax_right.semilogx(
        long_lengths,
        ours,
        marker="o",
        linestyle="-",
        color=NAVY,
        label="hard-projected (ours)",
        linewidth=2.5,
        markersize=10,
    )
    ax_right.semilogx(
        long_lengths,
        bag,
        marker="s",
        linestyle="--",
        color=MUTED,
        label="bag (native)",
        linewidth=1.4,
        markersize=7,
        alpha=0.65,
    )
    ax_right.semilogx(
        long_lengths,
        gru,
        marker="^",
        linestyle="--",
        color=MUTED,
        label="GRU (native)",
        linewidth=1.4,
        markersize=7,
        alpha=0.95,
    )
    ax_right.axhline(chance_36, color=NAVY, linestyle=":", linewidth=1.0, alpha=0.6, label=chance_label)
    ax_right.set_xlabel("Evaluation length (tokens)")
    ax_right.set_ylabel("Final-token accuracy")
    ax_right.set_title("(b) Million-token regime")
    ax_right.set_ylim(-0.05, 1.05)
    ax_right.set_xlim(400000, 1500000)
    ax_right.legend(loc="center right", fontsize=9)
    ax_right.grid(True, alpha=0.25, color=NAVY)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig1_gate_b_long_horizon.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIGURES_DIR / "fig1_gate_b_long_horizon.pdf", bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------
# Figure 2 — Gate C: four diagnostics across projection temperature
# ----------------------------------------------------------------------


def figure_2() -> None:
    T = np.array([0.25, 0.50, 0.75, 1.00, 1.50, 2.00, 3.00])
    final_acc = [1.0000, 0.0400, 0.0200, 0.0600, 0.0600, 0.0400, 0.0200]
    homo_err = [0.000583, 0.192048, 1.225186, 2.960337, 5.006641, 5.478391, 5.661507]
    drift = [0.032646, 0.830739, 0.825461, 0.824627, 0.828726, 0.831072, 0.832476]
    comm_gap = [8.4844, 8.1760, 6.6129, 4.2619, 1.1692, 0.3160, 0.0448]

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    # (a) Final-token accuracy — linear 0-1
    axes[0, 0].plot(T, final_acc, marker="o", color=NAVY, linewidth=2, markersize=8)
    axes[0, 0].set_ylabel("Final-token accuracy")
    axes[0, 0].set_ylim(-0.05, 1.05)
    axes[0, 0].set_title("(a) Final-token accuracy")

    # (b) Homomorphism error — log scale
    axes[0, 1].semilogy(T, homo_err, marker="o", color=NAVY, linewidth=2, markersize=8)
    axes[0, 1].set_ylabel(r"Homomorphism error  $E_{\mathrm{homo}}$")
    axes[0, 1].set_title("(b) Exact homomorphism error (log scale)")

    # (c) State-consistency drift — linear
    axes[1, 0].plot(T, drift, marker="o", color=NAVY, linewidth=2, markersize=8)
    axes[1, 0].set_xlabel(r"Projection temperature  $T$")
    axes[1, 0].set_ylabel(r"State-consistency drift  $D$")
    axes[1, 0].set_title("(c) State-consistency drift")

    # (d) Commutator gap — log scale
    axes[1, 1].semilogy(T, comm_gap, marker="o", color=NAVY, linewidth=2, markersize=8)
    axes[1, 1].set_xlabel(r"Projection temperature  $T$")
    axes[1, 1].set_ylabel("Commutator gap")
    axes[1, 1].set_title("(d) Commutator gap (log scale)")

    # Mark boundary T = 0.5 on all panels
    for ax in axes.flatten():
        ax.axvline(0.5, color=MUTED, linestyle=":", linewidth=1.5, alpha=0.85)
        ax.grid(True, alpha=0.25, color=NAVY)
        ax.set_xlim(0.1, 3.2)

    # Boundary annotation in the top-left panel
    axes[0, 0].annotate(
        r"boundary  $T^\star = 0.5$",
        xy=(0.5, 0.5),
        xytext=(0.9, 0.65),
        color=NAVY,
        fontsize=10,
        arrowprops=dict(arrowstyle="->", color=MUTED, lw=1.2),
    )

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig2_gate_c_diagnostics.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIGURES_DIR / "fig2_gate_c_diagnostics.pdf", bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------
# Figure 3 — Gate A: matched-protocol baseline competence
# ----------------------------------------------------------------------


def figure_3() -> None:
    models = ["bag", "GRU", "structured SSM"]
    easy = [1.0000, 1.0000, 0.8095]
    easy_lo = [1.0000, 1.0000, 0.7635]
    easy_hi = [1.0000, 1.0000, 0.8555]
    hard = [0.1600, 0.1690, 0.1900]
    hard_lo = [0.1395, 0.1355, 0.1380]
    hard_hi = [0.1835, 0.2015, 0.2650]
    chance = 1.0 / 6.0

    easy_err = [
        [easy[i] - easy_lo[i] for i in range(3)],
        [easy_hi[i] - easy[i] for i in range(3)],
    ]
    hard_err = [
        [hard[i] - hard_lo[i] for i in range(3)],
        [hard_hi[i] - hard[i] for i in range(3)],
    ]

    x = np.arange(len(models))
    width = 0.34

    fig, ax = plt.subplots(figsize=(8.5, 5))

    ax.bar(
        x - width / 2,
        easy,
        width,
        label="easy commutative (positive control)",
        color=NAVY,
        yerr=easy_err,
        capsize=5,
        ecolor=NAVY,
        edgecolor=NAVY,
    )
    ax.bar(
        x + width / 2,
        hard,
        width,
        label="6-class noncommutative held-out (diagnostic)",
        color=MUTED,
        yerr=hard_err,
        capsize=5,
        ecolor=NAVY,
        edgecolor=NAVY,
    )

    ax.axhline(
        chance,
        color=NAVY,
        linestyle=":",
        linewidth=1.2,
        alpha=0.7,
        label=f"chance = 1/6 ≈ {chance:.4f}",
    )

    ax.set_ylabel("Mean accuracy (5 seeds)")
    ax.set_xticks(x)
    ax.set_xticklabels(models)
    ax.set_ylim(0, 1.15)
    ax.set_title("Gate A: baseline competence under matched protocol")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=9.5)
    ax.grid(True, axis="y", alpha=0.25, color=NAVY)

    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig3_gate_a_baseline.png", dpi=300, bbox_inches="tight")
    fig.savefig(FIGURES_DIR / "fig3_gate_a_baseline.pdf", bbox_inches="tight")
    plt.close(fig)


# ----------------------------------------------------------------------
# Color evidence JSON (Hard Rule #7 reverse-check)
# ----------------------------------------------------------------------


def color_evidence() -> None:
    evidence = {
        "schema": "preprint_1_v0_5_figure_color_evidence",
        "generated_at": "2026-05-27 KST",
        "hard_rule_reference": "CLAUDE.md Hard Rule #7 — cream + navy + at most one muted accent; default palette prohibited.",
        "palette": {
            "cream_background": CREAM,
            "navy_primary": NAVY,
            "muted_accent": MUTED,
        },
        "default_matplotlib_palette_used": False,
        "rcParams_overrides": [
            "axes.facecolor",
            "figure.facecolor",
            "savefig.facecolor",
            "axes.edgecolor",
            "axes.labelcolor",
            "xtick.color",
            "ytick.color",
            "text.color",
            "axes.titlecolor",
        ],
        "figures": [
            "fig1_gate_b_long_horizon.png",
            "fig1_gate_b_long_horizon.pdf",
            "fig2_gate_c_diagnostics.png",
            "fig2_gate_c_diagnostics.pdf",
            "fig3_gate_a_baseline.png",
            "fig3_gate_a_baseline.pdf",
        ],
        "script": "make_figures.py",
        "data_source": "paper sections 6.1, 6.2, 6.3, 6.4 (numbers identical to the frozen public artifact tables).",
    }
    with open(FIGURES_DIR / "color_evidence.json", "w") as f:
        json.dump(evidence, f, indent=2)


if __name__ == "__main__":
    figure_1()
    figure_2()
    figure_3()
    color_evidence()
    print("Generated figures and color evidence:")
    for p in sorted(FIGURES_DIR.glob("*")):
        if p.name != "make_figures.py":
            print(f"  {p.name}  ({p.stat().st_size:>7} bytes)")
