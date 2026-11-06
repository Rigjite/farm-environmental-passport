#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Фигуры симуляции 1 (PFAS, округ Делавэр).

Пересборка 2026-11-05 (v0.3.1), правки 2026-11-05 (v0.3.2):
- цвета серий нейтральные (PFOS — тёмно-синий, PFOA — серо-голубой): красный, жёлтый
  и зелёный в паспорте означают статус и для серий данных не используются;
- статус показан отдельно: обводкой и подписью (F1 — жёлтый по ориентиру DEC 0,88);
- fig_biosolids: ярусы DMM-7 по первоисточнику (NYSDEC DMM-7, выпуск 07.09.2023):
  ≤20 — действий не требуется; 20–50 — доотбор, через год ограничение использования,
  если PFOS или PFOA не снижены ниже 20; ≥50 — использование запрещено до снижения ниже 20;
- fig_dose: подпись TWI вынесена над полем графика; точечная доза — чёрный ромб;
- fig_well: подписи линий справа от столбцов, без наложений;
- десятичный разделитель — запятая во всех подписях.
Числа fig_dose — вывод uncertainty.py (зерно 20261105, 2 PFAS из 4 — оценка снизу).
Синтетические значения не изменены (фикстура tests/fixtures/sim1_pfas.json).
Запуск: python3 make_figs1.py  -> examples/figures/
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

PFOS_C = "#1f3a5f"      # серия PFOS
PFOA_C = "#8fa9bf"      # серия PFOA
REF = "#4a235a"         # линии ориентиров
REF2 = "#6e2c00"
GREY = "#5d6d7e"
STATUS_YELLOW = "#d4ac0d"

plt.rcParams["font.size"] = 11


def c(v, nd=2):
    """Число с запятой."""
    return f"{v:.{nd}f}".replace(".", ",")


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


# ---------------------------------------------------------------- fig_biosolids
def fig_biosolids():
    fig, ax = plt.subplots(figsize=(9.6, 5.2))
    ax.axhspan(0, 20, color="#eaf2f8", zorder=0)
    ax.axhspan(20, 50, color="#f2f3f4", zorder=0)
    ax.axhspan(50, 60, color="#e5e7e9", zorder=0)
    ax.bar([0, 1], [12, 5], width=0.5, color=[PFOS_C, PFOA_C], zorder=3)
    for x, v in zip([0, 1], [12, 5]):
        ax.text(x, v + 1.0, str(v), ha="center", fontweight="bold", fontsize=13)
    ax.axhline(20, color=REF2, ls="--", lw=1.4, zorder=4)
    ax.axhline(50, color=REF, ls=":", lw=1.8, zorder=4)
    kw = dict(ha="left", va="center", fontsize=10.2)
    ax.text(1.45, 10, "≤20 — действий не требуется", color="#1b2631", **kw)
    ax.text(1.45, 35, "20–50 — доотбор; если через год PFOS или PFOA\nне ниже 20 — DEC ограничивает использование",
            color="#1b2631", **kw)
    ax.text(1.45, 55, "≥50 — использование запрещено\nдо снижения ниже 20", color="#1b2631", **kw)
    ax.set_xticks([0, 1], ["PFOS", "PFOA"])
    ax.set_xlim(-0.5, 3.6)
    ax.set_ylabel("мкг/кг сухой массы")
    ax.set_ylim(0, 60)
    ax.set_title("Осадок очистных сооружений: синтетический результат (EPA 1633)\n"
                 "и ярусы политики DEC DMM-7 (выпуск 07.09.2023), по PFOS или PFOA", fontsize=12)
    ax.text(0.5, -0.12, "Статус осадка — зелёный: оба значения в нижнем ярусе.",
            transform=ax.transAxes, ha="center", fontsize=10, color=GREY)
    save(fig, "fig_biosolids.png")


# ---------------------------------------------------------------- fig_dose
# (профиль, точечная доза, медиана, низ 90 %-интервала, верх) — вывод uncertainty.py, 2 PFAS
PROFILES = [
    ("Взрослый, молоко 0,25 л/сут", 2.51, 2.53, 1.63, 4.06),
    ("Взрослый, молоко 0,64 л/сут", 3.21, 3.27, 2.24, 4.87),
    ("Ребёнок 1–2 лет, вода средняя,\nмолоко 0,25 л/сут", 4.31, 4.40, 3.12, 6.21),
    ("Ребёнок 1–2 лет, вода P95,\nмолоко 0,25 л/сут", 6.92, 7.05, 4.89, 10.37),
    ("Младенец, вода — средняя норма", 5.50, 5.51, 3.17, 9.56),
    ("Младенец, вода — 95-й перцентиль", 10.22, 10.24, 5.89, 17.77),
]


def fig_dose():
    fig, ax = plt.subplots(figsize=(10.2, 5.6))
    ys = list(range(len(PROFILES)))[::-1]
    for y, (name, point, med, lo, hi) in zip(ys, PROFILES):
        ax.plot([lo, hi], [y, y], color="#aeb6bf", lw=6, solid_capstyle="butt", zorder=2)
        ax.plot([lo, lo], [y - 0.2, y + 0.2], color=GREY, lw=1.5, zorder=2)
        ax.plot([hi, hi], [y - 0.2, y + 0.2], color=GREY, lw=1.5, zorder=2)
        ax.plot(med, y, "o", mfc="white", mec=PFOS_C, mew=1.6, ms=7, zorder=3)
        ax.plot(point, y, "D", color="#1b2631", ms=6, zorder=4)
        ax.text(max(hi + 0.35, 4.9), y, f"точка {c(point)} · 90 %: {c(lo)}–{c(hi)}", va="center", fontsize=10)
    ax.axvline(4.4, color=REF, ls="--", lw=1.8, zorder=1)
    ax.set_ylim(-0.6, len(PROFILES) - 0.4)
    ax.text(4.4, len(PROFILES) - 0.35, "TWI EFSA 4,4", color=REF, fontsize=10.5,
            ha="center", va="bottom", clip_on=False)
    ax.set_yticks(ys, [p[0] for p in PROFILES])
    ax.set_xlim(0, 24.5)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    ax.set_xlabel("нг/кг массы тела в неделю. Посчитаны PFOS и PFOA из четырёх PFAS суммы EFSA — оценка снизу.\n"
                  "Ромб — точечная доза; кружок — медиана Монте-Карло; полоса — 90 %-интервал неопределённости")
    ax.set_title("Недельная доза по профилям потребления против TWI EFSA", fontsize=12.5, pad=22)
    save(fig, "fig_dose.png")


# ---------------------------------------------------------------- fig_well
def fig_well():
    fig, ax = plt.subplots(figsize=(10.0, 5.2))
    ax.bar([0, 1], [6.5, 3.8], width=0.5, color=[PFOS_C, PFOA_C], zorder=3)
    for x, v in zip([0, 1], [6.5, 3.8]):
        ax.text(x, v - 0.75, c(v, 1), ha="center", fontweight="bold", fontsize=13, color="white", zorder=5)
    lines = [
        (10.0, "#1b4f72", "--", "MCL штата Нью-Йорк — 10 нг/л (PFOS, PFOA, каждый)"),
        (6.7, REF, "-.", "DEC, подземные воды класса GA: PFOA 6,7 нг/л"),
        (4.0, REF2, ":", "MCL EPA — 4,0 нг/л (правило 2024 г.; срок соблюдения 2029;\nпродление до 2031 предложено, не принято)"),
        (2.7, REF, "-.", "DEC, подземные воды класса GA: PFOS 2,7 нг/л"),
    ]
    for yv, col, ls, label in lines:
        ax.axhline(yv, color=col, ls=ls, lw=1.5, zorder=4)
        ax.text(1.42, yv + 0.12, label, color=col, ha="left", va="bottom", fontsize=10)
    ax.set_xticks([0, 1], ["PFOS", "PFOA"])
    ax.set_xlim(-0.5, 3.9)
    ax.set_ylabel("нг/л")
    ax.set_ylim(0, 12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ",")))
    ax.set_title("Скважина питьевой воды: синтетический результат одной пробы (октябрь 2025 г.)", fontsize=12)
    ax.text(0.5, -0.12, "Статус скважины — жёлтый: PFOS выше MCL EPA и ориентира DEC, ниже MCL штата.",
            transform=ax.transAxes, ha="center", fontsize=10, color=GREY)
    save(fig, "fig_well.png")


# ---------------------------------------------------------------- fig_soil
def fig_soil():
    fields = ["F1", "F2", "F3", "F4", "F5\n(контроль)"]
    pfos = [0.90, 0.65, 0.50, 0.35, 0.15]
    pfoa = [0.40, 0.30, 0.22, 0.18, 0.08]
    fig, ax = plt.subplots(figsize=(9.4, 5.4))
    ax.axhspan(0.3, 1.1, facecolor="none", edgecolor="#bfc9ca", hatch="///", lw=0, zorder=0)
    x = list(range(len(fields)))
    w = 0.38
    bars = ax.bar([i - w / 2 for i in x], pfos, width=w, color=PFOS_C, zorder=3)
    ax.bar([i + w / 2 for i in x], pfoa, width=w, color=PFOA_C, zorder=3)
    bars[0].set_edgecolor(STATUS_YELLOW)
    bars[0].set_linewidth(3.2)
    for i, (a, b) in enumerate(zip(pfos, pfoa)):
        ax.text(i - w / 2, a + 0.025, c(a), ha="center", fontsize=10)
        ax.text(i + w / 2, b + 0.025, c(b), ha="center", fontsize=10)
    ax.annotate("F1 — жёлтый статус:\n102 % ориентира 0,88", xy=(-w / 2 + 0.08, 0.90), xytext=(0.55, 1.25),
                fontsize=10, color="#7d6608",
                arrowprops=dict(arrowstyle="->", color="#7d6608", lw=1.2))
    ax.axhline(0.88, color=REF2, ls="--", lw=1.5, zorder=4)
    ax.text(4.45, 0.84, "DEC: PFOS 0,88 — неограниченное использование", ha="right", va="top",
            fontsize=9.8, color=REF2)
    ax.axhline(1.0, color=REF, ls=":", lw=1.8, zorder=4)
    ax.text(4.45, 1.02, "DEC: PFOS 1,0 — защита подземных вод", ha="right", va="bottom",
            fontsize=9.8, color=REF)
    ax.set_xticks(x, fields)
    ax.set_ylabel("мкг/кг, слой 0–20 см")
    ax.set_ylim(0, 1.45)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1f}".replace(".", ",")))
    handles = [Patch(color=PFOS_C, label="PFOS"), Patch(color=PFOA_C, label="PFOA"),
               Patch(facecolor="none", edgecolor="#bfc9ca", hatch="///",
                     label="модель для поля с 10 сезонами: PFOS 0,3–1,1"),
               Patch(facecolor="none", edgecolor=STATUS_YELLOW, lw=2.5, label="статус «жёлтый»")]
    ax.legend(handles=handles, loc="upper right", framealpha=0.95, fontsize=9.5)
    ax.set_title("Почва полей: синтетические измерения (EPA 1633), 0–20 см", fontsize=12.5)
    save(fig, "fig_soil.png")


if __name__ == "__main__":
    fig_biosolids()
    fig_dose()
    fig_well()
    fig_soil()
    print("DONE")
