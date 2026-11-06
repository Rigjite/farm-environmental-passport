#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль 2 симуляции фермы (вода и питание растений): единый блок данных,
все производные числа считаются из него; балансы проверяются assert-ами;
6 фигур fig2_*.png (150 dpi) пишутся в папку скрипта.

Ферма — та же, что в FARM-PFAS-SIMULATION-2026-10-31.md (модуль 1, PFAS).
Все лабораторные значения синтетические; нормативные якоря реальны.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse, FancyArrowPatch, Polygon

OUT = os.path.dirname(os.path.abspath(__file__))
plt.rcParams.update({"font.size": 10, "axes.titlesize": 12,
                     "axes.labelsize": 11, "figure.dpi": 150})

# ============================ DATA BLOCK ============================
ACRE_HA = 0.4046856
FIELDS_AC = {  # акры; история осадка — из модуля 1
    "F1 (осадок с 2016)": 15.0,
    "F2 (осадок с 2019)": 15.0,
    "F3 (осадок с 2021)": 12.0,
    "F4 (осадок с 2023)": 13.0,
}
PASTURE_AC, F5_AC, FOREST_AC = 20.0, 25.0, 20.0

COWS = 80                       # синтетическое допущение модуля 2 (в модуле 1 размер стада не фиксировался)
RATION_DM_KG_DAY = 22.0         # кг сухого вещества / корову / сутки (модуль 1)
OWN_FORAGE_SHARE = 0.60         # доля собственного корма (модуль 1)
MILK_YIELD_KG = 10_500.0        # кг молока / корову / год (синтетика)
MILK_N_FRAC, MILK_P_FRAC = 0.0052, 0.00095   # доли N и P в молоке

BIOSOLIDS_T_PER_AC = 3.0        # сухие тонны / акр / год (модуль 1)
BIOSOLIDS_N_FRAC, BIOSOLIDS_P_FRAC = 0.032, 0.015   # валовые N и P осадка (синтетический анализ продукта)

FEED_N_FRAC, FEED_P_FRAC = 0.021, 0.0034     # покупной корм, доли в сухом веществе
MINERAL_N_KG, MINERAL_P_KG = 600.0, 0.0      # минеральные удобрения, кг/год (P не вносится)
FIXATION_HA, FIXATION_RATE = 8.0, 100.0      # бобово-злаковые угодья: га × кг N/га/год
DEPOSITION_N_KG_HA, DEPOSITION_P_KG_HA = 8.0, 0.25

CULLS, CULL_LW_KG = 24, 640.0                # выбраковка: голов × живая масса, кг
HEIFERS_SOLD, HEIFER_LW_KG = 16, 480.0       # проданные тёлки
LW_N_FRAC, LW_P_FRAC = 0.028, 0.0075         # доли N и P в живой массе
CROPS_SOLD_DM_KG = 45_000.0                  # проданное сено, кг сухого вещества
CROPS_N_FRAC, CROPS_P_FRAC = 0.022, 0.0028

WELL_NO3N = [8.9, 11.4, 7.2, 6.8]            # мг/л как N, кварталы I–IV (синтетические пробы)
NO3N_MCL = 10.0                              # EPA MCL для питьевой воды, мг/л как N

STREAM_TP = [24, 19, 58, 74, 46, 38, 31, 28, 36, 118, 64, 33]  # мкг/л, месяцы (синтетические пробы)
ECOLI_EVENT, ECOLI_REF = 410.0, 235.0        # КОЕ/100 мл: событийная проба после ливня / EPA, единичная проба

EXPORT_TN = {"biosolids": 24.0, "pasture": 11.0, "f5": 14.0, "forest": 3.5}   # кг/га/год, модель
EXPORT_TP = {"biosolids": 2.6, "pasture": 0.8, "f5": 1.1, "forest": 0.25}     # кг/га/год, модель
DELIVERY_RATIO = 0.15                        # доля полевого выноса, достигающая водотока (допущение модели)
RUNOFF_DEPTH_M = 0.45                        # годовой сток с территории фермы, м (модель)

POND_AREA_HA, POND_DEPTH_M = 0.2, 1.8        # пруд: площадь и средняя глубина
POND_CATCH_HA, POND_RUNOFF_M = 8.0, 0.42     # суббассейн F2/F3 и его сток, м/год
POND_TP, POND_CHLA = 68.0, 21.0              # мкг/л (синтетические сезонные средние)
VOLL_PERM_CONC, VOLL_DANG_CONC = 10.0, 20.0  # граничные концентрации Фолленвайдера, мкг/л

# ============================ COMPUTATIONS ============================
area_ha = {k: v * ACRE_HA for k, v in FIELDS_AC.items()}
fields_ha = sum(area_ha.values())
pasture_ha, f5_ha, forest_ha = PASTURE_AC * ACRE_HA, F5_AC * ACRE_HA, FOREST_AC * ACRE_HA
farm_ha = fields_ha + pasture_ha + f5_ha + forest_ha
assert abs(farm_ha - 120 * ACRE_HA) < 0.01

ration_dm_yr = COWS * RATION_DM_KG_DAY * 365
imported_feed_dm = ration_dm_yr * (1 - OWN_FORAGE_SHARE)
biosolids_t = sum(FIELDS_AC.values()) * BIOSOLIDS_T_PER_AC
milk_kg_yr = COWS * MILK_YIELD_KG
livestock_lw = CULLS * CULL_LW_KG + HEIFERS_SOLD * HEIFER_LW_KG

N_IN = {
    "Минеральные удобрения": MINERAL_N_KG,
    "Осадок (валовый N)": biosolids_t * 1000 * BIOSOLIDS_N_FRAC,
    "Покупной корм": imported_feed_dm * FEED_N_FRAC,
    "Фиксация бобовыми": FIXATION_HA * FIXATION_RATE,
    "Атмосферное осаждение": round(farm_ha * DEPOSITION_N_KG_HA),  # целое по ферме: иначе сумма компонентов расходится с итогом на округлении
}
N_OUT = {
    "Молоко": milk_kg_yr * MILK_N_FRAC,
    "Продажа скота (живая масса)": livestock_lw * LW_N_FRAC,
    "Проданные корма (сено)": CROPS_SOLD_DM_KG * CROPS_N_FRAC,
}
P_IN = {
    "Минеральные удобрения": MINERAL_P_KG,
    "Осадок (валовый P)": biosolids_t * 1000 * BIOSOLIDS_P_FRAC,
    "Покупной корм": imported_feed_dm * FEED_P_FRAC,
    "Атмосферное осаждение": farm_ha * DEPOSITION_P_KG_HA,
}
P_OUT = {
    "Молоко": milk_kg_yr * MILK_P_FRAC,
    "Продажа скота (живая масса)": livestock_lw * LW_P_FRAC,
    "Проданные корма (сено)": CROPS_SOLD_DM_KG * CROPS_P_FRAC,
}
for name, din, dout in (("N", N_IN, N_OUT), ("P", P_IN, P_OUT)):
    assert all(v >= 0 for v in din.values()) and all(v >= 0 for v in dout.values()), name
N_in_tot, N_out_tot = sum(N_IN.values()), sum(N_OUT.values())
P_in_tot, P_out_tot = sum(P_IN.values()), sum(P_OUT.values())
N_surplus, P_surplus = N_in_tot - N_out_tot, P_in_tot - P_out_tot
assert N_surplus > 0 and P_surplus > 0
N_surplus_ha, P_surplus_ha = N_surplus / farm_ha, P_surplus / farm_ha
assert 80 <= N_surplus_ha <= 140, f"N surplus/ha out of band: {N_surplus_ha:.1f}"

well_mean = float(np.mean(WELL_NO3N))
stream_tp_mean = float(np.mean(STREAM_TP))
assert 45 <= stream_tp_mean <= 55

groups_ha = {"biosolids": fields_ha, "pasture": pasture_ha, "f5": f5_ha, "forest": forest_ha}
exp_TN = {k: groups_ha[k] * EXPORT_TN[k] for k in groups_ha}
exp_TP = {k: groups_ha[k] * EXPORT_TP[k] for k in groups_ha}
exp_TN_tot, exp_TP_tot = sum(exp_TN.values()), sum(exp_TP.values())
runoff_m3 = farm_ha * 1e4 * RUNOFF_DEPTH_M
stream_TP_delivered = exp_TP_tot * DELIVERY_RATIO
stream_TP_flowweighted = stream_TP_delivered * 1e9 / (runoff_m3 * 1000)  # кг→мкг / м³→л

pond_catch_export = POND_CATCH_HA * EXPORT_TP["biosolids"]
pond_load_kg = pond_catch_export * DELIVERY_RATIO
pond_area_m2 = POND_AREA_HA * 1e4
pond_areal_mg = pond_load_kg * 1e6 / pond_area_m2            # мг/м²/год
pond_Q = POND_CATCH_HA * 1e4 * POND_RUNOFF_M                 # м³/год
pond_qs = pond_Q / pond_area_m2                              # гидравлическая нагрузка, м/год
pond_tau_yr = (pond_area_m2 * POND_DEPTH_M) / pond_Q         # время пребывания, годы
def vollenweider(depth_m, conc_ug_l):
    return conc_ug_l * pond_qs * (1 + np.sqrt(depth_m / pond_qs))   # мг/м²/год
pond_L_perm = vollenweider(POND_DEPTH_M, VOLL_PERM_CONC)
pond_L_dang = vollenweider(POND_DEPTH_M, VOLL_DANG_CONC)
pond_TP_pred = pond_areal_mg / (pond_qs * (1 + np.sqrt(POND_DEPTH_M / pond_qs)))

print("=== КЛЮЧЕВЫЕ ЧИСЛА МОДУЛЯ 2 ===")
print(f"Площадь фермы: {farm_ha:.2f} га (поля с осадком {fields_ha:.2f}, пастбище {pasture_ha:.2f}, "
      f"F5 {f5_ha:.2f}, лес/усадьба {forest_ha:.2f})")
print(f"Стадо {COWS} коров; рацион {ration_dm_yr:,.0f} кг СВ/год, покупной корм {imported_feed_dm:,.0f} кг СВ/год; "
      f"молоко {milk_kg_yr:,.0f} кг/год; осадок {biosolids_t:.0f} сухих т/год")
print(f"N: поступление {N_in_tot:,.0f} = " + " + ".join(f"{k} {v:,.0f}" for k, v in N_IN.items()))
print(f"N: вынос с продукцией {N_out_tot:,.0f} = " + " + ".join(f"{k} {v:,.0f}" for k, v in N_OUT.items()))
print(f"N: профицит {N_surplus:,.0f} кг/год = {N_surplus_ha:.1f} кг/га/год")
print(f"P: поступление {P_in_tot:,.0f} = " + " + ".join(f"{k} {v:,.0f}" for k, v in P_IN.items()))
print(f"P: вынос с продукцией {P_out_tot:,.0f} = " + " + ".join(f"{k} {v:,.0f}" for k, v in P_OUT.items()))
print(f"P: профицит {P_surplus:,.0f} кг/год = {P_surplus_ha:.1f} кг/га/год")
print(f"Скважина NO3-N: среднее {well_mean:.2f} мг/л, максимум {max(WELL_NO3N)} (квартал II), MCL {NO3N_MCL}")
print(f"Ручей TP: среднее арифметическое {stream_tp_mean:.1f} мкг/л; вынос с полей TN {exp_TN_tot:,.0f} кг/год, "
      f"TP {exp_TP_tot:,.0f} кг/год; доставлено в ручей TP {stream_TP_delivered:.1f} кг/год, "
      f"средневзвешенная по стоку {stream_TP_flowweighted:.1f} мкг/л")
print(f"Доля полей с осадком в выносе: TN {exp_TN['biosolids']/exp_TN_tot*100:.0f}%, TP {exp_TP['biosolids']/exp_TP_tot*100:.0f}% "
      f"при {fields_ha/farm_ha*100:.0f}% площади")
print(f"Пруд: валовый вынос суббассейна {pond_catch_export:.1f} кг P/год, нагрузка {pond_load_kg:.2f} кг/год = "
      f"{pond_areal_mg:,.0f} мг/м²/год; qs {pond_qs:.1f} м/год, τ {pond_tau_yr:.3f} года ({pond_tau_yr*365:.0f} сут)")
print(f"Фолленвайдер: допустимая {pond_L_perm:,.0f}, опасная {pond_L_dang:,.0f} мг/м²/год; "
      f"фактическая выше опасной в {pond_areal_mg/pond_L_dang:.1f} раза; прогноз TP {pond_TP_pred:.0f} мкг/л "
      f"при синтетическом измерении {POND_TP:.0f} мкг/л")

# ============================ FIGURES ============================
def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)

# (a) Водная схема фермы
fig, ax = plt.subplots(figsize=(9, 6.4))
ax.set_xlim(0, 100); ax.set_ylim(0, 72); ax.axis("off")
def box(x, y, w, h, label, fc, ec="#4a6741", fs=9.5):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, lw=1.1))
    ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs)
box(2, 46, 30, 24, "F1\nосадок с 2016", "#cfe3c0")
box(34, 46, 30, 24, "F2\nосадок с 2019", "#cfe3c0")
box(66, 46, 32, 24, "Лес", "#a9c69a")
box(2, 28, 30, 16, "F3\nосадок с 2021", "#dcebcf")
box(34, 28, 30, 16, "F4\nосадок с 2023", "#dcebcf")
box(66, 28, 32, 16, "Пастбище\nбез осадка", "#e6f0da")
box(2, 10, 44, 16, "F5 — контроль, без осадка", "#eef5e4")
box(48, 10, 16, 16, "Усадьба", "#e8ddc8")
ax.add_patch(Ellipse((82, 17), 17, 10, facecolor="#7fb2dd", edgecolor="#2b5f8a", lw=1.3))
ax.text(82, 17, "Пруд\n0,2 га", ha="center", va="center", fontsize=9, color="#08306b")
ax.add_patch(Rectangle((34, 46.5), 30, 7.5, fill=False, edgecolor="#2b5f8a", ls="--", lw=1.2))
ax.add_patch(Rectangle((4, 28.5), 26, 4.5, fill=False, edgecolor="#2b5f8a", ls="--", lw=1.2))
ax.text(84, 24.9, "суббассейн пруда ~8 га\n(части F2 и F3)", fontsize=8.5, color="#2b5f8a", ha="center")
ax.add_patch(Rectangle((0, 3.4), 100, 2.2, facecolor="#cfe6f7", edgecolor="none"))
ax.add_patch(Rectangle((0, 0.6), 100, 2.8, facecolor="#7fb2dd", edgecolor="#2b5f8a", lw=0.8))
ax.annotate("", xy=(97, 2.0), xytext=(60, 2.0),
            arrowprops=dict(arrowstyle="->", color="#08306b", lw=1.6))
ax.text(50, 1.9, "Ручей — южная граница, течение →", ha="center", fontsize=9.5, color="#08306b")
ax.text(50, 4.6, "буфер 30 м", ha="center", fontsize=8.5, color="#2b5f8a")
ax.plot(56, 18, marker="o", ms=9, mfc="#08306b", mec="white", mew=1.2)
ax.text(57.5, 21.5, "Скважина 35 м (W)", fontsize=9.5, color="#08306b")
for x, lab in ((6, "S1 — ручей, вход"), (93, "S2 — ручей, выход")):
    ax.plot(x, 2.0, marker="s", ms=8, mfc="#c1272d", mec="white", mew=1.1)
    ax.text(x, 7.6, lab, fontsize=8.5, color="#c1272d", ha="center")
ax.plot(89, 20, marker="s", ms=8, mfc="#c1272d", mec="white", mew=1.1)
ax.text(82, 9.4, "P — пруд", fontsize=8.5, color="#c1272d", ha="center")
ax.add_patch(FancyArrowPatch((30, 45), (53, 27), arrowstyle="->", mutation_scale=15,
                             color="#08306b", lw=1.6, ls="--"))
ax.text(35.5, 30.6, "фильтрация\nF1–F2 → скважина", fontsize=8.5, color="#08306b")
ax.add_patch(FancyArrowPatch((70, 27.5), (79, 22.6), arrowstyle="->", mutation_scale=15,
                             color="#2b5f8a", lw=1.6))
ax.text(96.3, 67.6, "С", fontsize=12, fontweight="bold", ha="center")
ax.set_title("Водная схема синтетической фермы: объекты модуля 2 и точки отбора")
save(fig, "fig2_water_map.png")

# (b) Нитрат скважины по кварталам
fig, ax = plt.subplots(figsize=(7.4, 4.6))
colors = ["#7fb069", "#d9a404", "#7fb069", "#7fb069"]
ax.bar(["I квартал", "II квартал", "III квартал", "IV квартал"], WELL_NO3N,
       color=colors, edgecolor="#40513a")
ax.axhline(NO3N_MCL, color="#c1272d", lw=1.6, ls="--", label="MCL EPA 10 мг/л (как N)")
for i, v in enumerate(WELL_NO3N):
    ax.text(i, v + 0.3, f"{v:.1f}", ha="center", fontsize=10)
ax.set_ylim(0, 13.2); ax.set_ylabel("NO$_3$-N, мг/л")
ax.set_title("Скважина: нитрат по кварталам (синтетические пробы)\n"
             f"среднее за год {well_mean:.1f} мг/л — ниже MCL; II квартал выше MCL")
ax.legend(loc="lower left"); ax.grid(axis="y", alpha=0.3)
save(fig, "fig2_well_nitrate.png")

# (c) Фосфор ручья по месяцам
fig, ax = plt.subplots(figsize=(8.6, 4.8))
months = ["янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек"]
ax.axhspan(35, 100, color="#f6e8a8", alpha=0.55)
ax.axhspan(100, 150, color="#f3b8a6", alpha=0.55)
ax.plot(months, STREAM_TP, "o-", color="#2b5f8a", lw=1.8, ms=5)
for y, lab in ((10, "10 — граница олиго/мезотрофии OECD"), (35, "35 — мезо/эвтрофия"),
               (100, "100 — эвтрофия/гипертрофии")):
    ax.axhline(y, color="#8a6d1a" if y < 100 else "#a63a2b", lw=1.0, ls="--")
    ax.text(11.45, y + 2.5, lab, fontsize=8, ha="right",
            color="#8a6d1a" if y < 100 else "#a63a2b")
ax.annotate("ливневый пик 118", xy=(9, 118), xytext=(6.6, 128),
            arrowprops=dict(arrowstyle="->", lw=1.0), fontsize=9)
ax.set_ylim(0, 145); ax.set_ylabel("Общий фосфор, мкг/л")
ax.set_title(f"Ручей: общий фосфор по месяцам (синтетические пробы), среднее {stream_tp_mean:.0f} мкг/л")
ax.grid(axis="y", alpha=0.3)
save(fig, "fig2_stream_tp.png")

# (d, e) Балансы у ворот фермы
def balance_fig(din, dout, surplus, surplus_ha, title, fname, unit="кг/год"):
    labels = list(din) + list(dout) + ["Профицит (остаётся на ферме)"]
    values = list(din.values()) + [-v for v in dout.values()] + [surplus]
    cols = ["#7fb069"] * len(din) + ["#e08a3c"] * len(dout) + ["#c1272d"]
    fig, ax = plt.subplots(figsize=(8.8, 4.9))
    ypos = np.arange(len(labels))[::-1]
    ax.barh(ypos, values, color=cols, edgecolor="#333333", lw=0.5)
    off = 0.04 * max(abs(v) for v in values)
    ax.set_xlim(min(0, min(values)) * 1.42, max(0, max(values)) * 1.30)
    for y, v in zip(ypos, values):
        ax.text(v + (off if v >= 0 else -off), y, f"{abs(v):,.0f}".replace(",", " "),
                va="center", ha="left" if v >= 0 else "right", fontsize=9.5)
    ax.axvline(0, color="#333333", lw=0.9)
    ax.set_yticks(ypos); ax.set_yticklabels(labels, fontsize=9.5)
    ax.set_xlabel(f"{unit}: поступление → / ← вынос с продукцией")
    ax.set_title(f"{title}\nпрофицит {surplus:,.0f} {unit} = {surplus_ha:.1f} кг/га/год".replace(",", " "))
    ax.grid(axis="x", alpha=0.3)
    save(fig, fname)

balance_fig(N_IN, N_OUT, N_surplus, N_surplus_ha,
            "Баланс азота у ворот фермы (синтетические компоненты)", "fig2_n_balance.png")
balance_fig(P_IN, P_OUT, P_surplus, P_surplus_ha,
            "Баланс фосфора у ворот фермы (синтетические компоненты)", "fig2_p_balance.png")

# (f) Диаграмма Фолленвайдера для пруда
fig, ax = plt.subplots(figsize=(7.6, 5.4))
depths = np.logspace(np.log10(0.3), np.log10(30), 200)
Lp = vollenweider(depths, VOLL_PERM_CONC)
Ld = vollenweider(depths, VOLL_DANG_CONC)
ax.fill_between(depths, Ld, 30000, color="#f3b8a6", alpha=0.6)
ax.fill_between(depths, Lp, Ld, color="#f6e8a8", alpha=0.65)
ax.fill_between(depths, 30, Lp, color="#cfe3c0", alpha=0.7)
ax.plot(depths, Lp, color="#4a6741", lw=1.6, label="допустимая нагрузка ([P] = 10 мкг/л)")
ax.plot(depths, Ld, color="#a63a2b", lw=1.6, label="опасная нагрузка ([P] = 20 мкг/л)")
ax.plot(POND_DEPTH_M, pond_areal_mg, "o", ms=10, mfc="#c1272d", mec="white", mew=1.3, zorder=5)
ax.annotate(f"пруд фермы: {POND_DEPTH_M} м; {pond_areal_mg:,.0f} мг/м²/год\n"
            f"в {pond_areal_mg/pond_L_dang:.1f} раза выше опасной линии".replace(",", " "),
            xy=(POND_DEPTH_M, pond_areal_mg), xytext=(3.2, 5200),
            arrowprops=dict(arrowstyle="->", lw=1.1), fontsize=9.5)
ax.text(0.36, 9000, "зона эвтрофии", fontsize=9.5, color="#a63a2b")
ax.text(0.36, 272, "переходная зона", fontsize=9.5, color="#8a6d1a")
ax.text(0.36, 52, "допустимая зона", fontsize=9.5, color="#4a6741")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_ylim(30, 30000)
ax.set_xlabel("Средняя глубина, м"); ax.set_ylabel("Нагрузка фосфора, мг/м²/год")
ax.set_title(f"Диаграмма Фолленвайдера: пруд при гидравлической нагрузке {pond_qs:.1f} м/год")
ax.legend(loc="lower right", fontsize=9); ax.grid(alpha=0.3, which="both")
save(fig, "fig2_vollenweider.png")
print("DONE")
