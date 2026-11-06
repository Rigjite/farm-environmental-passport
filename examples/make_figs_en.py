#!/usr/bin/env python3
"""English figures for the worked examples (Modules 1–3) of the synthetic farm.

All values are synthetic and come from the texts in force:
- Module 1 (PFAS): FARM-PFAS-SIMULATION-2026-10-31-r7.en.md; dose bands are the
  output of uncertainty.py (seed 20261105, 2 of 4 EFSA PFAS — lower bound).
- Modules 2–3 (water, nutrients): numbers are computed by executing the DATA BLOCK
  and COMPUTATIONS of the unchanged original make_figs2.py, so the figures cannot
  drift from the original calculation.

Series colours are neutral: in the passport red, yellow and green mean status only.
Status is shown by outline and caption. Output: examples/figures/en/*.png
Run: python3 make_figs_en.py
"""
import contextlib
import io
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch, Patch, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "figures", "en")
os.makedirs(OUT, exist_ok=True)

SER1 = "#1f3a5f"     # primary series
SER2 = "#8fa9bf"     # secondary series
SER3 = "#5b7a99"     # third series
REF = "#4a235a"      # reference lines
REF2 = "#6e2c00"
GREY = "#5d6d7e"
STATUS_YELLOW = "#d4ac0d"
plt.rcParams.update({"font.size": 10.5, "axes.titlesize": 12, "axes.labelsize": 11})


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


# ------------------------------------------------------------- Module 2 data
def module2_numbers():
    src = open(os.path.join(HERE, "make_figs2.py"), encoding="utf-8").read()
    head = src.split("# ============================ FIGURES")[0]
    ns = {"__file__": os.path.join(HERE, "make_figs2.py")}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(head, "make_figs2.py (data block)", "exec"), ns)
    return ns


# ------------------------------------------------------------- Module 1
def fig_zone_map():
    fig, ax = plt.subplots(figsize=(10, 7.2))
    ax.set_xlim(0, 100); ax.set_ylim(0, 74); ax.axis("off")
    shade = {10: "#1f3a5f", 7: "#3e5f82", 5: "#6f8eae", 3: "#a9bfd4"}
    def zone(x, y, w, h, title, sub, fc, tc="white"):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor="#333333", lw=1))
        ax.text(x + w / 2, y + h * 0.58, title, ha="center", va="center", fontsize=13, fontweight="bold", color=tc)
        ax.text(x + w / 2, y + h * 0.36, sub, ha="center", va="center", fontsize=9.5, color=tc)
    zone(3, 40, 28, 28, "F1 · 15 acres", "biosolids since 2016 · 10 seasons", shade[10])
    zone(33, 40, 28, 28, "F2 · 15 acres", "biosolids since 2019 · 7 seasons", shade[7])
    zone(63, 40, 20, 28, "F3 · 12 acres", "since 2021 · 5 seasons", shade[5])
    zone(85, 40, 12, 28, "Forest", "20 acres*", "#d5dbdb", "#1b2631")
    zone(3, 12, 28, 26, "F4 · 13 acres", "biosolids since 2023 · 3 seasons", shade[3], "#1b2631")
    zone(33, 12, 30, 26, "Pasture · 20 acres", "no biosolids", "#eaeded", "#1b2631")
    zone(65, 12, 32, 26, "F5 · 25 acres", "forage, no biosolids (control)", "#f4f6f6", "#1b2631")
    ax.add_patch(Rectangle((34.5, 31), 11, 5, facecolor="#7b7d7d", edgecolor="#333333"))
    ax.text(40, 33.5, "Farmstead", ha="center", va="center", fontsize=9.5, color="white", fontweight="bold")
    ax.plot(59, 32, marker="v", ms=13, color="#154360")
    ax.text(57.6, 30.6, "Well, 35 m", ha="right", va="center", fontsize=9.5, color="#154360")
    ax.add_patch(FancyArrowPatch((30, 41.5), (58.4, 33.2), arrowstyle="->", mutation_scale=15, color="#154360", lw=1.6, ls="--"))
    ax.text(47, 42.6, "groundwater flow F1–F2 → well", ha="center", fontsize=9, color="white")
    ax.add_patch(Rectangle((0, 8), 100, 2.6, facecolor="#e8eef3", edgecolor="none"))
    ax.text(88, 9.3, "buffer 30 m", ha="center", va="center", fontsize=8.5, color=GREY)
    ax.add_patch(Rectangle((0, 3), 100, 5, facecolor="#aed6f1", edgecolor="#2e86c1", lw=0.8))
    ax.text(50, 5.5, "Unnamed creek — tributary of the West Branch Delaware River  →", ha="center", va="center", fontsize=10, color="#154360")
    ax.text(97, 71, "N ↑", ha="center", fontsize=12, fontweight="bold")
    ax.set_title("Zone sketch of the synthetic farm (not a map; proportions and orientation are schematic)\n"
                 "*Forest is part of the remainder «farmstead, forest, roads — 20 acres»; total 120 acres. "
                 "Shading = years of biosolids, not status.", fontsize=11)
    save(fig, "fig_zone_map.png")


def fig_pathway():
    fig, ax = plt.subplots(figsize=(14, 6.4))
    ax.set_xlim(0, 100); ax.set_ylim(0, 46); ax.axis("off")
    def node(x, y, w, h, title, body, fc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3", facecolor=fc, edgecolor="#4d5656", lw=1.2))
        ax.text(x + w / 2, y + h * 0.72, title, ha="center", va="center", fontsize=11, fontweight="bold")
        ax.text(x + w / 2, y + h * 0.32, body, ha="center", va="center", fontsize=9.8)
    top, bot, h = 27, 4, 11
    node(1, top, 16, h, "Treatment plants", "small municipal;\nclass B biosolids", "#eef2f6")
    node(21, top, 15, h, "Biosolids", "PFOS 12 µg/kg\nPFOA 5 µg/kg", "#eef2f6")
    node(40, top, 15, h, "Field soil 0–20 cm", "PFOS 0.15–0.90 µg/kg", "#eef2f6")
    node(59, top, 15, h, "Forage (grass,\nlegumes)", "TF 0.026–0.37", "#eef2f6")
    node(78, top, 20, h, "Cow", "ration 22 kg DM/day;\nwater 100 L/day", "#eef2f6")
    node(4, bot, 28, h, "Consumer", "milk only: 0.45–1.15\nwater + milk: 2.51–3.21\nng/kg bw per week (adult)", "#f4f1f8")
    node(40, bot, 15, h, "Well, 35 m", "PFOS 6.5 ng/L\nPFOA 3.8 ng/L", "#e8f0f8")
    node(78, bot, 20, h, "Milk (bulk tank)", "PFOS 18 ng/L (measured)\nmodel: 4–17 ng/L", "#eef6f1")
    arrow = dict(arrowstyle="->", color="#333333", lw=1.6)
    for x0, x1, lab in ((17.3, 20.7, ""), (36.3, 39.7, "3 dry t/acre/yr"), (55.3, 58.7, "model"), (74.3, 77.7, "60 % of ration")):
        ax.annotate("", xy=(x1, top + h / 2), xytext=(x0, top + h / 2), arrowprops=arrow)
        if lab:
            ax.text((x0 + x1) / 2, top + h + 1.2, lab, ha="center", fontsize=9, color=GREY)
    ax.annotate("", xy=(88, bot + h + 0.4), xytext=(88, top - 0.4), arrowprops=arrow)
    ax.text(89.5, 21.5, "secreted into milk:\n14 % of the dose (PFOS)", fontsize=9, color=GREY)
    ax.annotate("", xy=(18, bot + h + 0.5), xytext=(47.5, bot + h + 0.5),
                arrowprops=dict(arrowstyle="->", color="#2e86c1", lw=1.6, connectionstyle="arc3,rad=0"))
    ax.text(33, 17.3, "drinking water from the well: cows and residents", ha="center", fontsize=9.3, color="#2e86c1")
    ax.annotate("", xy=(32.4, bot + 3), xytext=(77.6, bot + 3),
                arrowprops=dict(arrowstyle="->", color="#6c3483", lw=1.5, connectionstyle="arc3,rad=0.25"))
    ax.text(62, 1.2, "milk as a product", ha="center", fontsize=9.3, color="#6c3483")
    ax.set_title("PFAS pathways on the synthetic farm: source → soil → forage → cow → milk → consumer.\n"
                 "Values from the report tables (synthetic measurements and model estimates are labelled in the text).", fontsize=12)
    save(fig, "fig_pathway.png")


def fig_timeline():
    fields = ["F1 (15 acres)", "F2 (15 acres)", "F3 (12 acres)", "F4 (13 acres)", "F5 — control (25 acres)"]
    start = [2016, 2019, 2021, 2023, None]
    years = list(range(2016, 2026))
    fig, ax = plt.subplots(figsize=(10, 4.2))
    for i, (f, s) in enumerate(zip(fields, start)):
        y = len(fields) - 1 - i
        for yr in years:
            on = s is not None and yr >= s
            ax.add_patch(Rectangle((yr - 0.5, y - 0.5), 1, 1, facecolor=SER1 if on else "#eceff1", edgecolor="white", lw=1.5))
            if on:
                ax.text(yr, y, "applied", ha="center", va="center", fontsize=7.5, color="white")
    ax.set_xlim(2015.5, 2025.5); ax.set_ylim(-0.5, len(fields) - 0.5)
    ax.set_xticks(years); ax.set_yticks(range(len(fields))[::-1], fields)
    ax.set_title("Biosolids application by field, 2016–2025 (synthetic history; 25 field-seasons in total)")
    for s in ax.spines.values():
        s.set_visible(False)
    save(fig, "fig_timeline.png")


def fig_biosolids():
    fig, ax = plt.subplots(figsize=(9.6, 5.2))
    ax.axhspan(0, 20, color="#eaf2f8", zorder=0); ax.axhspan(20, 50, color="#f2f3f4", zorder=0); ax.axhspan(50, 60, color="#e5e7e9", zorder=0)
    ax.bar([0, 1], [12, 5], width=0.5, color=[SER1, SER2], zorder=3)
    for x, v in zip([0, 1], [12, 5]):
        ax.text(x, v + 1.0, str(v), ha="center", fontweight="bold", fontsize=13)
    ax.axhline(20, color=REF2, ls="--", lw=1.4, zorder=4); ax.axhline(50, color=REF, ls=":", lw=1.8, zorder=4)
    kw = dict(ha="left", va="center", fontsize=10.2, color="#1b2631")
    ax.text(1.45, 10, "≤ 20 — no action required", **kw)
    ax.text(1.45, 35, "> 20 and < 50 — additional sampling; DEC restricts\nuse if PFOS or PFOA is not below 20 after one year", **kw)
    ax.text(1.45, 55, "≥ 50 — use prohibited\nuntil below 20", **kw)
    ax.set_xticks([0, 1], ["PFOS", "PFOA"]); ax.set_xlim(-0.5, 3.8); ax.set_ylim(0, 60)
    ax.set_ylabel("µg/kg dry weight")
    ax.set_title("Biosolids: synthetic result (EPA 1633) and the tiers of NYSDEC policy DMM-7\n(issued 2023-09-07), by PFOS or PFOA")
    ax.text(0.5, -0.12, "Biosolids status — green: both values in the lowest tier.", transform=ax.transAxes, ha="center", fontsize=10, color=GREY)
    save(fig, "fig_biosolids.png")


PROFILES = [  # (profile, point, median, low, high) — uncertainty.py, 2 of 4 EFSA PFAS
    ("Adult, milk 0.25 L/day", 2.51, 2.53, 1.63, 4.06),
    ("Adult, milk 0.64 L/day", 3.21, 3.27, 2.24, 4.87),
    ("Child 1–<2 y, mean water,\nmilk 0.25 L/day", 4.31, 4.40, 3.12, 6.21),
    ("Child 1–<2 y, 95th-pct water,\nmilk 0.25 L/day", 6.92, 7.05, 4.89, 10.37),
    ("Infant, formula, mean water", 5.50, 5.51, 3.17, 9.56),
    ("Infant, formula, 95th-pct water", 10.22, 10.24, 5.89, 17.77),
]


def fig_dose():
    fig, ax = plt.subplots(figsize=(10.2, 5.6))
    ys = list(range(len(PROFILES)))[::-1]
    for y, (name, point, med, lo, hi) in zip(ys, PROFILES):
        ax.plot([lo, hi], [y, y], color="#aeb6bf", lw=6, solid_capstyle="butt", zorder=2)
        for xv in (lo, hi):
            ax.plot([xv, xv], [y - 0.2, y + 0.2], color=GREY, lw=1.5, zorder=2)
        ax.plot(med, y, "o", mfc="white", mec=SER1, mew=1.6, ms=7, zorder=3)
        ax.plot(point, y, "D", color="#1b2631", ms=6, zorder=4)
        ax.text(max(hi + 0.35, 4.9), y, f"point {point:.2f} · 90 %: {lo:.2f}–{hi:.2f}", va="center", fontsize=10)
    ax.axvline(4.4, color=REF, ls="--", lw=1.8, zorder=1)
    ax.set_ylim(-0.6, len(PROFILES) - 0.4)
    ax.text(4.4, len(PROFILES) - 0.35, "EFSA TWI 4.4", color=REF, fontsize=10.5, ha="center", va="bottom", clip_on=False)
    ax.set_yticks(ys, [p[0] for p in PROFILES]); ax.set_xlim(0, 24.5)
    ax.set_xlabel("ng/kg body weight per week. PFOS and PFOA only, of the four PFAS in the EFSA sum — a lower bound.\n"
                  "Diamond — point dose; circle — Monte Carlo median; bar — 90 % uncertainty interval")
    ax.set_title("Weekly dose by consumption profile against the EFSA TWI (synthetic farm)", fontsize=12.5, pad=22)
    save(fig, "fig_dose.png")


def fig_well():
    fig, ax = plt.subplots(figsize=(10.0, 5.2))
    ax.bar([0, 1], [6.5, 3.8], width=0.5, color=[SER1, SER2], zorder=3)
    for x, v in zip([0, 1], [6.5, 3.8]):
        ax.text(x, v - 0.75, f"{v:.1f}", ha="center", fontweight="bold", fontsize=13, color="white", zorder=5)
    lines = [
        (10.0, "#1b4f72", "--", "New York State MCL — 10 ng/L (PFOS, PFOA, each)"),
        (6.7, REF, "-.", "DEC groundwater guidance (class GA): PFOA 6.7 ng/L"),
        (4.0, REF2, ":", "EPA MCL — 4.0 ng/L (2024 rule; compliance 2029;\nextension to 2031 proposed, not final)"),
        (2.7, REF, "-.", "DEC groundwater guidance (class GA): PFOS 2.7 ng/L"),
    ]
    for yv, col, ls, label in lines:
        ax.axhline(yv, color=col, ls=ls, lw=1.5, zorder=4)
        ax.text(1.42, yv + 0.12, label, color=col, ha="left", va="bottom", fontsize=10)
    ax.set_xticks([0, 1], ["PFOS", "PFOA"]); ax.set_xlim(-0.5, 4.1); ax.set_ylim(0, 12)
    ax.set_ylabel("ng/L")
    ax.set_title("Drinking-water well: synthetic result of one sample (October 2025)")
    ax.text(0.5, -0.12, "Well status — yellow: PFOS above the EPA MCL and the DEC guidance value, below the state MCL.",
            transform=ax.transAxes, ha="center", fontsize=10, color=GREY)
    save(fig, "fig_well.png")


def fig_soil():
    fields = ["F1", "F2", "F3", "F4", "F5\n(control)"]
    pfos = [0.90, 0.65, 0.50, 0.35, 0.15]
    pfoa = [0.40, 0.30, 0.22, 0.18, 0.08]
    fig, ax = plt.subplots(figsize=(9.4, 5.4))
    ax.axhspan(0.3, 1.1, facecolor="none", edgecolor="#bfc9ca", hatch="///", lw=0, zorder=0)
    x = list(range(len(fields))); w = 0.38
    bars = ax.bar([i - w / 2 for i in x], pfos, width=w, color=SER1, zorder=3)
    ax.bar([i + w / 2 for i in x], pfoa, width=w, color=SER2, zorder=3)
    bars[0].set_edgecolor(STATUS_YELLOW); bars[0].set_linewidth(3.2)
    for i, (a, b) in enumerate(zip(pfos, pfoa)):
        ax.text(i - w / 2, a + 0.025, f"{a:.2f}", ha="center", fontsize=10)
        ax.text(i + w / 2, b + 0.025, f"{b:.2f}", ha="center", fontsize=10)
    ax.annotate("F1 — yellow status:\n102 % of the 0.88 guidance", xy=(-w / 2 + 0.08, 0.90), xytext=(0.55, 1.25),
                fontsize=10, color="#7d6608", arrowprops=dict(arrowstyle="->", color="#7d6608", lw=1.2))
    ax.axhline(0.88, color=REF2, ls="--", lw=1.5, zorder=4)
    ax.text(4.45, 0.84, "DEC: PFOS 0.88 — unrestricted use", ha="right", va="top", fontsize=9.8, color=REF2)
    ax.axhline(1.0, color=REF, ls=":", lw=1.8, zorder=4)
    ax.text(4.45, 1.02, "DEC: PFOS 1.0 — protection of groundwater", ha="right", va="bottom", fontsize=9.8, color=REF)
    ax.set_xticks(x, fields); ax.set_ylabel("µg/kg, 0–20 cm layer"); ax.set_ylim(0, 1.45)
    handles = [Patch(color=SER1, label="PFOS"), Patch(color=SER2, label="PFOA"),
               Patch(facecolor="none", edgecolor="#bfc9ca", hatch="///", label="model for a 10-season field: PFOS 0.3–1.1"),
               Patch(facecolor="none", edgecolor=STATUS_YELLOW, lw=2.5, label="status: yellow")]
    ax.legend(handles=handles, loc="upper right", framealpha=0.95, fontsize=9.5)
    ax.set_title("Field soil: synthetic measurements (EPA 1633), 0–20 cm")
    save(fig, "fig_soil.png")


# ------------------------------------------------------------- Modules 2–3
def module2_figures(d):
    # (a) water sketch
    fig, ax = plt.subplots(figsize=(9, 6.4))
    ax.set_xlim(0, 100); ax.set_ylim(0, 72); ax.axis("off")
    def box(x, y, w, h, label, fc):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor="#4d5656", lw=1.1))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=9.5)
    box(2, 46, 30, 24, "F1\nbiosolids since 2016", "#d6dee6"); box(34, 46, 30, 24, "F2\nbiosolids since 2019", "#d6dee6")
    box(66, 46, 32, 24, "Forest", "#e5e8e8"); box(2, 28, 30, 16, "F3\nbiosolids since 2021", "#e3e9ef")
    box(34, 28, 30, 16, "F4\nbiosolids since 2023", "#e3e9ef"); box(66, 28, 32, 16, "Pasture\nno biosolids", "#f0f3f4")
    box(2, 10, 44, 16, "F5 — control, no biosolids", "#f7f9f9"); box(48, 10, 16, 16, "", "#e5e7e9")
    ax.text(56, 21.5, "Farmstead", ha="center", va="center", fontsize=9.5)
    ax.add_patch(Ellipse((82, 17), 17, 10, facecolor="#aed6f1", edgecolor="#2e86c1", lw=1.3))
    ax.text(82, 17, "Pond\n0.2 ha", ha="center", va="center", fontsize=9, color="#154360")
    ax.add_patch(Rectangle((34, 46.5), 30, 7.5, fill=False, edgecolor="#2e86c1", ls="--", lw=1.2))
    ax.add_patch(Rectangle((4, 28.5), 26, 4.5, fill=False, edgecolor="#2e86c1", ls="--", lw=1.2))
    ax.text(82, 25.2, "pond subcatchment ~8 ha (parts of F2, F3)", fontsize=7.8, color="#2e86c1", ha="center")
    ax.add_patch(Rectangle((0, 3.4), 100, 2.2, facecolor="#e8eef3", edgecolor="none"))
    ax.add_patch(Rectangle((0, 0.6), 100, 2.8, facecolor="#aed6f1", edgecolor="#2e86c1", lw=0.8))
    ax.annotate("", xy=(97, 2.0), xytext=(60, 2.0), arrowprops=dict(arrowstyle="->", color="#154360", lw=1.6))
    ax.text(32, 1.9, "Creek — southern boundary, flow →", ha="center", va="center", fontsize=9.5, color="#154360")
    ax.text(50, 4.6, "buffer 30 m", ha="center", fontsize=8.5, color=GREY)
    ax.plot(56, 14, marker="o", ms=9, mfc="#154360", mec="white", mew=1.2)
    ax.text(56, 11.3, "Well 35 m (W)", ha="center", fontsize=8.5, color="#154360")
    for x, lab in ((6, "S1 — creek, inflow"), (93, "S2 — creek, outflow")):
        ax.plot(x, 2.0, marker="s", ms=8, mfc="#1b2631", mec="white", mew=1.1)
        ax.text(x, 7.6, lab, fontsize=8.5, color="#1b2631", ha="center")
    ax.plot(89, 20, marker="s", ms=8, mfc="#1b2631", mec="white", mew=1.1)
    ax.text(82, 9.4, "P — pond", fontsize=8.5, color="#1b2631", ha="center")
    ax.add_patch(FancyArrowPatch((30, 45), (55, 15.5), arrowstyle="->", mutation_scale=15, color="#154360", lw=1.6, ls="--"))
    ax.text(36, 29.2, "groundwater flow F1–F2 → well", fontsize=8, color="#154360")
    ax.add_patch(FancyArrowPatch((70, 27.5), (79, 22.6), arrowstyle="->", mutation_scale=15, color="#2e86c1", lw=1.6))
    ax.text(96.3, 67.6, "N", fontsize=12, fontweight="bold", ha="center")
    ax.set_title("Water sketch of the synthetic farm: Module 2 objects and sampling points (squares)")
    save(fig, "fig2_water_map.png")

    # (b) well nitrate
    q = d["WELL_NO3N"]; mcl = d["NO3N_MCL"]
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    bars = ax.bar(["Q1", "Q2", "Q3", "Q4"], q, color=SER1, edgecolor="#333333", zorder=3)
    bars[1].set_edgecolor(STATUS_YELLOW); bars[1].set_linewidth(3)
    ax.axhline(mcl, color=REF2, lw=1.6, ls="--", label="EPA MCL 10 mg/L (as N)")
    for i, v in enumerate(q):
        ax.text(i, v + 0.3, f"{v:.1f}", ha="center", fontsize=10)
    ax.set_ylim(0, 13.2); ax.set_ylabel("NO$_3$-N, mg/L")
    ax.set_title(f"Well: nitrate by quarter (synthetic samples)\nannual mean {d['well_mean']:.1f} mg/L — below the MCL; Q2 above (yellow outline)")
    ax.legend(loc="lower left"); ax.grid(axis="y", alpha=0.3)
    save(fig, "fig2_well_nitrate.png")

    # (c) creek total phosphorus
    tp = d["STREAM_TP"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    ax.plot(months, tp, "o-", color=SER1, lw=1.8, ms=5)
    for y, lab in ((10, "10 — oligo/mesotrophic boundary (OECD)"), (35, "35 — meso/eutrophic"), (100, "100 — eu/hypertrophic")):
        ax.axhline(y, color=REF, lw=1.0, ls="--")
        ax.text(11.45, y + 2.5, lab, fontsize=8, ha="right", color=REF)
    ax.annotate("storm peak 118", xy=(9, 118), xytext=(6.6, 128), arrowprops=dict(arrowstyle="->", lw=1.0), fontsize=9)
    ax.set_ylim(0, 145); ax.set_ylabel("Total phosphorus, µg/L")
    ax.set_title(f"Creek: total phosphorus by month (synthetic samples), mean {d['stream_tp_mean']:.0f} µg/L")
    ax.grid(axis="y", alpha=0.3)
    save(fig, "fig2_stream_tp.png")

    # (d, e) farm-gate balances
    names = {"Минеральные удобрения": "Mineral fertiliser", "Осадок (валовый N)": "Biosolids (total N)",
             "Осадок (валовый P)": "Biosolids (total P)", "Покупной корм": "Purchased feed",
             "Фиксация бобовыми": "Legume fixation", "Атмосферное осаждение": "Atmospheric deposition",
             "Молоко": "Milk", "Продажа скота (живая масса)": "Livestock sold (live weight)",
             "Проданные корма (сено)": "Crops sold (hay)"}
    def balance(din, dout, surplus, surplus_ha, title, fname):
        din = {names[k]: v for k, v in din.items() if v > 0}
        dout = {names[k]: v for k, v in dout.items()}
        labels = list(din) + list(dout) + ["Surplus (stays on the farm)"]
        values = list(din.values()) + [-v for v in dout.values()] + [surplus]
        cols = [SER1] * len(din) + [SER2] * len(dout) + [SER3]
        fig, ax = plt.subplots(figsize=(8.8, 4.9))
        ypos = np.arange(len(labels))[::-1]
        ax.barh(ypos, values, color=cols, edgecolor="#333333", lw=0.5)
        off = 0.04 * max(abs(v) for v in values)
        ax.set_xlim(min(0, min(values)) * 1.42, max(0, max(values)) * 1.30)
        for y, v in zip(ypos, values):
            ax.text(v + (off if v >= 0 else -off), y, f"{abs(v):,.0f}", va="center", ha="left" if v >= 0 else "right", fontsize=9.5)
        ax.axvline(0, color="#333333", lw=0.9)
        ax.set_yticks(ypos, labels, fontsize=9.5)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f"{x:,.0f}"))
        ax.set_xlabel("kg/yr: inputs → / ← exports in products")
        ax.set_title(f"{title}\nsurplus {surplus:,.0f} kg/yr = {surplus_ha:.1f} kg/ha/yr")
        ax.grid(axis="x", alpha=0.3)
        save(fig, fname)
    balance(d["N_IN"], d["N_OUT"], d["N_surplus"], d["N_surplus_ha"], "Farm-gate nitrogen balance (synthetic components)", "fig2_n_balance.png")
    balance(d["P_IN"], d["P_OUT"], d["P_surplus"], d["P_surplus_ha"], "Farm-gate phosphorus balance (synthetic components)", "fig2_p_balance.png")

    # (f) Vollenweider diagram
    voll = d["vollenweider"]; depth = d["POND_DEPTH_M"]; load = d["pond_areal_mg"]
    depths = np.logspace(np.log10(0.3), np.log10(30), 200)
    fig, ax = plt.subplots(figsize=(7.6, 5.4))
    ax.plot(depths, voll(depths, d["VOLL_PERM_CONC"]), color=SER1, lw=1.6, label="permissible load ([P] = 10 µg/L)")
    ax.plot(depths, voll(depths, d["VOLL_DANG_CONC"]), color=REF, lw=1.6, ls="--", label="dangerous load ([P] = 20 µg/L)")
    ax.plot(depth, load, "o", ms=10, mfc="#1b2631", mec=STATUS_YELLOW, mew=2.2, zorder=5)
    ax.annotate(f"farm pond: {depth} m; {load:,.0f} mg/m²/yr\n{load / d['pond_L_dang']:.1f}× the dangerous line (yellow status)",
                xy=(depth, load), xytext=(3.2, 5200), arrowprops=dict(arrowstyle="->", lw=1.1), fontsize=9.5)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(30, 30000)
    ax.set_xlabel("Mean depth, m"); ax.set_ylabel("Phosphorus load, mg/m²/yr")
    ax.set_title(f"Vollenweider diagram: farm pond at a hydraulic load of {d['pond_qs']:.1f} m/yr")
    ax.legend(loc="lower right", fontsize=9); ax.grid(alpha=0.3, which="both")
    save(fig, "fig2_vollenweider.png")


if __name__ == "__main__":
    fig_zone_map(); fig_pathway(); fig_timeline()
    fig_biosolids(); fig_dose(); fig_well(); fig_soil()
    module2_figures(module2_numbers())
    print("DONE")
