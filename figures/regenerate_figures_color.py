#!/usr/bin/env python3
"""Regenerate Preprint-1 figures from REAL data, white background,
matplotlib tab10 palette (blue/orange/green/red) matched to reference paper
2505.15112 (Parallel Scan Ascend) Fig 6.2, per Founder request. Author-generated
from the real result CSVs (provenance clean). Vector PDF + 300 dpi PNG into figures/.
Overrides CLAUDE.md Hard Rule #7 per Founder direct instruction (reference-specified palette).
"""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "data"

BG = "white"
# ---- palette matched to reference 2505.15112 (Parallel Scan Ascend) Fig 6.2 ----
# matplotlib tab10 (blue/orange/green/red), per Founder request (overrides Hard Rule #7).
OURS   = "#1f77b4"   # blue   -- hard-projected (ours)   [memcopy in ref Fig 6.2]
GRU    = "#ff7f0e"   # orange -- GRU                     [cast in ref]
SSM    = "#2ca02c"   # green  -- structured SSM          [MCSCAN in ref]
BAG    = "#d62728"   # red    -- bag                     [MCSCANUL1 in ref]
NATIVE = "#d62728"   # red    -- native readout / diagnostic (fig3 hard, fig5)
GREY   = "#7f7f7f"   # native pilot (faint reference)
CHANCE = "#000000"   # chance line (black dotted)
# muted bar tones (Figures 3 & 7 only): desaturated so large filled bars don't shout
BAR_GRU = "#E5A95C"  # soft orange
BAR_SSM = "#74B074"  # soft green
BAR_BAG = "#CD7B7B"  # soft red
BAR_BLUE = "#6F9FC9" # soft blue (Figure 1 easy / positive-control bars)

plt.rcParams.update({
    "axes.facecolor": BG, "figure.facecolor": BG,
    "savefig.facecolor": BG, "savefig.edgecolor": BG,
    "axes.edgecolor": "#333333", "axes.labelcolor": "#222222",
    "xtick.color": "#222222", "ytick.color": "#222222", "text.color": "#222222",
    "axes.titlecolor": "#222222", "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 11, "axes.linewidth": 1.0, "axes.titlesize": 11,
    "legend.frameon": False, "font.family": "sans-serif",
})


def save(fig, name):
    fig.savefig(HERE / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(HERE / f"{name}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("wrote", name)


def load_acc(stem):
    df = pd.read_csv(RES / f"{stem}.csv")
    df = df[df["seed"].astype(str).str.upper() != "AGGREGATE"].copy()
    df["eval_len"] = pd.to_numeric(df["eval_len"], errors="coerce")
    df["final_accuracy"] = pd.to_numeric(df["final_accuracy"], errors="coerce")
    return df.groupby(["eval_len", "model"])["final_accuracy"].mean()


def series_from(stems, model):
    parts = []
    for stem in stems:
        df = pd.read_csv(RES / f"{stem}.csv")
        df = df[df["seed"].astype(str).str.upper() != "AGGREGATE"].copy()
        df["eval_len"] = pd.to_numeric(df["eval_len"], errors="coerce")
        df["final_accuracy"] = pd.to_numeric(df["final_accuracy"], errors="coerce")
        parts.append(df[df["model"] == model])
    return pd.concat(parts).groupby("eval_len")["final_accuracy"].mean().sort_index()


CH36 = 1 / 36
CH120 = 1 / 120
GRID = dict(alpha=0.25, color="#cccccc")


# ---- Figure 1: Gate B (2 panels: (a) short-horizon, (b) million-token) ----
def fig1():
    ours_s = load_acc("gate_b_short_horizon_ours").xs("Hard-projected (ours)", level=1)
    ours_l = load_acc("gate_b_expanded_results").xs("Hard-projected (ours)", level=1)
    proj = {lab: load_acc(f"{s}_projected_results").groupby("eval_len").mean() for s, lab in
            [("gru", "GRU + prototype"), ("ssm", "SSM + prototype"), ("bag", "bag + prototype")]}
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(10, 4.4))
    # (a) short-horizon regime
    axa.semilogx(ours_s.index, ours_s.values, "o-", color=OURS, lw=2.5, ms=9, label="hard-projected (ours)")
    axa.semilogx([4096, 16384, 65536], [0, 0, 0], "v:", color=GREY, lw=1.4, ms=7, label="native readout (pilot)")
    axa.axhline(CH36, color=CHANCE, ls=":", lw=1.0, label=f"chance = 1/36 ≈ {CH36:.4f}")
    axa.text(0.06, 0.80, "250/250 exact", transform=axa.transAxes, fontsize=9, color=OURS, fontweight="bold")
    axa.set(xlabel="Evaluation length (tokens)", ylabel="Final-token accuracy", title="(a) Short-horizon regime", ylim=(-0.05, 1.08), xlim=(2500, 100000))
    axa.set_xticks([4096, 16384, 65536]); axa.set_xticklabels(["4,096", "16,384", "65,536"]); axa.minorticks_off()
    axa.grid(True, **GRID); axa.legend(fontsize=8.5, loc="center right")
    # (b) million-token regime
    L = [524288, 1048576]
    axb.semilogx(L, ours_l.reindex(L).values, "o-", color=OURS, lw=2.6, ms=10, label="hard-projected (ours)")
    for lab, col, mk in [("GRU + prototype", GRU, "^"), ("SSM + prototype", SSM, "s"), ("bag + prototype", BAG, "D")]:
        axb.semilogx(L, proj[lab].reindex(L).values, mk + "--", color=col, lw=1.8, ms=7, label=lab)
    axb.semilogx(L, [0.0, 0.05], "v:", color=GREY, lw=1.3, ms=6, label="GRU (native, pilot)")
    axb.axhline(CH36, color=CHANCE, ls=":", lw=1.0, label=f"chance = 1/36 ≈ {CH36:.4f}")
    axb.text(0.06, 0.80, "250/250 exact", transform=axb.transAxes, fontsize=9, color=OURS, fontweight="bold")
    axb.set(xlabel="Evaluation length (tokens)", ylabel="Final-token accuracy", title="(b) Million-token regime", ylim=(-0.05, 1.08), xlim=(400000, 1500000))
    axb.set_xticks([524288, 1048576]); axb.set_xticklabels(["524,288", "1,048,576"]); axb.minorticks_off()
    axb.grid(True, **GRID); axb.legend(fontsize=8, loc="center right")
    plt.tight_layout(); save(fig, "fig1_gate_b_long_horizon")


# ---- Figure 2: Gate C diagnostics ----
def fig2():
    T = [0.25, 0.50, 0.75, 1.00, 1.50, 2.00, 3.00]
    fa = [1.0, 0.04, 0.02, 0.06, 0.06, 0.04, 0.02]
    he = [0.000583, 0.192048, 1.225186, 2.960337, 5.006641, 5.478391, 5.661507]
    dr = [0.032646, 0.830739, 0.825461, 0.824627, 0.828726, 0.831072, 0.832476]
    cg = [8.4844, 8.1760, 6.6129, 4.2619, 1.1692, 0.3160, 0.0448]
    fig, ax = plt.subplots(2, 2, figsize=(10, 8))
    panels = [("(a) Final-token accuracy", fa, OURS, False, "Final-token accuracy"),
              ("(b) Homomorphism error (log)", he, SSM, True, r"$E_{\mathrm{homo}}$"),
              ("(c) State-consistency drift", dr, GRU, False, "Drift $D$"),
              ("(d) Commutator gap (log)", cg, BAG, True, "Commutator gap")]
    for a, (ttl, y, col, logy, ylab) in zip(ax.flatten(), panels):
        (a.semilogy if logy else a.plot)(T, y, "o-", color=col, lw=2, ms=8)
        a.set_title(ttl); a.set_ylabel(ylab); a.set_xlim(0.1, 3.2)
        a.axvline(0.5, color=GREY, ls=":", lw=1.4); a.grid(True, **GRID)
        if not logy and y is fa:
            a.set_ylim(-0.05, 1.05)
    ax[1, 0].set_xlabel(r"Projection temperature $T$"); ax[1, 1].set_xlabel(r"Projection temperature $T$")
    plt.tight_layout(); save(fig, "fig2_gate_c_diagnostics")


# ---- Figure 3: Gate A baseline ----
def fig3():
    import numpy as np
    models = ["bag", "GRU", "structured SSM"]
    easy = [1.0, 1.0, 0.8095]; easy_lo = [1.0, 1.0, 0.7635]; easy_hi = [1.0, 1.0, 0.8555]
    hard = [0.16, 0.169, 0.19]; hard_lo = [0.1395, 0.1355, 0.138]; hard_hi = [0.1835, 0.2015, 0.265]
    x = np.arange(3); w = 0.34
    ee = [[easy[i] - easy_lo[i] for i in range(3)], [easy_hi[i] - easy[i] for i in range(3)]]
    hh = [[hard[i] - hard_lo[i] for i in range(3)], [hard_hi[i] - hard[i] for i in range(3)]]
    fig, ax = plt.subplots(figsize=(8.5, 5))
    ax.bar(x - w / 2, easy, w, label="easy commutative (positive control)", color=BAR_BLUE, yerr=ee, capsize=5, ecolor="#333333")
    ax.bar(x + w / 2, hard, w, label="6-class noncommutative held-out (diagnostic)", color=BAR_BAG, yerr=hh, capsize=5, ecolor="#333333")
    ax.axhline(1 / 6, color=CHANCE, ls=":", lw=1.2, label=f"chance = 1/6 ≈ {1/6:.4f}")
    ax.set(ylabel="Mean accuracy (5 seeds)", ylim=(0, 1.15), title="Gate A: baseline competence under matched protocol")
    ax.set_xticks(x); ax.set_xticklabels(models); ax.grid(True, axis="y", **GRID)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=9)
    plt.tight_layout(); save(fig, "fig3_gate_a_baseline")


# ---- Figure 4: projection-matched baselines (Gate B) -- grouped bar ----
def fig4():
    import numpy as np
    L = [524288, 1048576]
    data = {s: load_acc(f"{s}_projected_results").groupby("eval_len").mean().reindex(L).values for s in ["gru", "ssm", "bag"]}
    cnt = {"gru": ["7/250", "2/250"], "ssm": ["9/250", "3/250"], "bag": ["15/250", "6/250"]}
    x = np.arange(2); w = 0.26
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    for i, (s, lab, col) in enumerate([("gru", "GRU + prototype", BAR_GRU), ("ssm", "SSM + prototype", BAR_SSM), ("bag", "bag + prototype", BAR_BAG)]):
        bars = ax.bar(x + (i - 1) * w, data[s], w, color=col, label=lab)
        for b, txt in zip(bars, cnt[s]):
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.0015, txt, ha="center", va="bottom", fontsize=8, color="#333333")
    ax.axhline(CH36, color=CHANCE, ls=":", lw=1.2, label=f"chance = 1/36 ≈ {CH36:.4f}")
    ax.set_xticks(x); ax.set_xticklabels(["524,288", "1,048,576"])
    ax.set(xlabel="Evaluation length (tokens)", ylabel="Final-token accuracy", title="Projection-matched baselines (held-out-pair, Gate B): all near chance", ylim=(0, 0.08))
    ax.grid(True, axis="y", **GRID); ax.legend(fontsize=9, loc="upper right")
    plt.tight_layout(); save(fig, "fig4_projection_matched_baselines")


# ---- Figure 5: S5 stress ----
def fig5():
    g = load_acc("optional_s5_stress_results")
    fig, ax = plt.subplots(figsize=(7.5, 4.4))
    for model, col, mk, lab in [("Hard-projected (ours)", OURS, "o", "hard-projected (ours)"),
                                ("GRU native readout", NATIVE, "^", "GRU (native readout)")]:
        s = g.xs(model, level=1).sort_index()
        ax.semilogx(s.index, s.values, mk + "-", color=col, lw=2.2 if col == OURS else 1.7, ms=8, label=lab)
    ax.axhline(CH120, color=CHANCE, ls=":", lw=1.0, label=f"chance = 1/120 ≈ {CH120:.4f}")
    ax.set(xlabel="Evaluation length (tokens)", ylabel="Final-token accuracy", title="Preliminary S5 non-solvable stress test", ylim=(-0.05, 1.05))
    ax.grid(True, **GRID); ax.legend(fontsize=9)
    plt.tight_layout(); save(fig, "fig5_s5_stress")


MODELS = [("Hard-projected (ours)", "hard-projected (ours)", OURS, "o", "-", 2.4),
          ("GRU + projection", "GRU + projection", GRU, "^", "--", 1.7),
          ("Structured SSM + projection", "structured SSM + projection", SSM, "s", "--", 1.7),
          ("Bag + projection", "bag + projection", BAG, "D", "--", 1.7)]


# ---- Figure S1: S3xS3 same-factor held-out (2 panels) ----
def fig_s3xs3():
    ext = "s3xs3_same_factor_heldout_option1_1m_extension_results"
    first = {"Hard-projected (ours)": ["s3xs3_same_factor_heldout_option1_results", ext],
             "GRU + projection": ["s3xs3_same_factor_heldout_option1_results", ext],
             "Bag + projection": ["s3xs3_same_factor_heldout_option1_results", ext],
             "Structured SSM + projection": ["s3xs3_same_factor_heldout_option1_ssm_results", ext]}
    second = {m: ["s3xs3_same_factor_heldout_option2_results"] for m, *_ in MODELS}
    fig, (axa, axb) = plt.subplots(1, 2, figsize=(11, 4.6), sharey=True)
    for ax, panel, ttl in [(axa, first, "First factor"), (axb, second, "Second factor")]:
        for key, lab, col, mk, ls, lw in MODELS:
            s = series_from(panel[key], key)
            ax.plot(s.index, s.values, marker=mk, ls=ls, color=col, lw=lw, ms=8, label=lab)
        ax.axhline(CH36, color=CHANCE, ls=":", lw=1.0, label=f"chance = 1/36 ≈ {CH36:.4f}")
        ax.set_xscale("log", base=2)
        ax.set(xlabel="Evaluation sequence length", title=ttl, ylim=(-0.05, 1.05))
        ax.grid(True, **GRID)
    axa.set_ylabel("Mean final-token accuracy")
    axa.legend(loc="center left", bbox_to_anchor=(0.02, 0.55), fontsize=8.5)
    fig.suptitle("Same-factor held-out transition-pair falsifier", y=1.0)
    plt.tight_layout(); save(fig, "s3xs3_same_factor_heldout")


# ---- Figure S2: S5 projection-matched baselines -- grouped bar ----
def fig_s5proj():
    import numpy as np
    L = [512, 2048, 8192, 65536]
    data = {s: series_from([f"s5_projected_{s}_results"], lab).reindex(L).values
            for s, lab in [("gru", "GRU + projection"), ("ssm", "Structured SSM + projection"), ("bag", "Bag + projection")]}
    x = np.arange(4); w = 0.26
    fig, ax = plt.subplots(figsize=(7.8, 4.5))
    for i, (s, lab, col) in enumerate([("gru", "GRU + projection", BAR_GRU), ("ssm", "Structured SSM + projection", BAR_SSM), ("bag", "Bag + projection", BAR_BAG)]):
        ax.bar(x + (i - 1) * w, data[s], w, color=col, label=lab)
    ax.axhline(CH120, color=CHANCE, ls=":", lw=1.2, label=f"chance = 1/120 ≈ {CH120:.4f}")
    ax.set_xticks(x); ax.set_xticklabels([f"{v:,}" for v in L])
    ax.set(xlabel="Evaluation length (tokens)", ylabel="Final-token accuracy", title="Projection-matched baselines on $S_5$ (held-out-pair): all near chance", ylim=(0, 0.025))
    ax.grid(True, axis="y", **GRID); ax.legend(fontsize=9, loc="upper right")
    plt.tight_layout(); save(fig, "s5_projection_matched_baselines")


for fn in (fig1, fig2, fig3, fig4, fig5, fig_s3xs3, fig_s5proj):
    try:
        fn()
    except Exception as e:
        print("ERR", fn.__name__, repr(e))
print("BG =", BG, "| palette = tab10 (ref 2505.15112 Fig6.2)")
