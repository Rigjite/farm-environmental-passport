#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =====================================================================
# make_figs2_v2.py — вариант v0.3.3 (v0.3.3, п. 5):
# только две фигуры балансов (fig2_n_balance, fig2_p_balance), те же данные
# и тот же расчёт, что в make_figs2.py; цвета серий нейтральные (тёмно-синий /
# серо-синий / стальной — красный, жёлтый и зелёный зарезервированы для статуса),
# десятичная запятая во всех подписях; результат — figures/fig2_*_v2.png.
# Исходный make_figs2.py и его фигуры не изменены (sha256 — T8).
# =====================================================================

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


# ============================ FIGURES (v2: балансы) ============================
FIGOUT = os.path.join(OUT, "figures")
os.makedirs(FIGOUT, exist_ok=True)

def save(fig, name):
    fig.savefig(os.path.join(FIGOUT, name), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)

def _fmt(x):
    s = f"{x:,.1f}".replace(",", " ").replace(".", ",")
    if s.endswith(",0"):
        s = s[:-2]
    return s

def balance_fig(din, dout, surplus, surplus_ha, title, fname, unit="кг/год"):
    labels = list(din) + list(dout) + ["Профицит (остаётся на ферме)"]
    values = list(din.values()) + [-v for v in dout.values()] + [surplus]
    cols = ["#1f3a5f"] * len(din) + ["#8fa9bf"] * len(dout) + ["#5b7a99"]
    fig, ax = plt.subplots(figsize=(8.8, 4.9))
    ypos = np.arange(len(labels))[::-1]
    ax.barh(ypos, values, color=cols, edgecolor="#333333", lw=0.5)
    off = 0.04 * max(abs(v) for v in values)
    ax.set_xlim(min(0, min(values)) * 1.42, max(0, max(values)) * 1.30)
    for y, v in zip(ypos, values):
        ax.text(v + (off if v >= 0 else -off), y, _fmt(abs(v)),
                va="center", ha="left" if v >= 0 else "right", fontsize=9.5)
    ax.axvline(0, color="#333333", lw=0.9)
    ax.set_yticks(ypos); ax.set_yticklabels(labels, fontsize=9.5)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: _fmt(x)))
    ax.set_xlabel(f"{unit}: поступление → / ← вынос с продукцией")
    ax.set_title(f"{title}\nпрофицит {_fmt(surplus)} {unit} = {_fmt(surplus_ha)} кг/га/год")
    ax.grid(axis="x", alpha=0.3)
    save(fig, fname)

balance_fig(N_IN, N_OUT, N_surplus, N_surplus_ha,
            "Баланс азота у ворот фермы (синтетические компоненты)", "fig2_n_balance_v2.png")
balance_fig(P_IN, P_OUT, P_surplus, P_surplus_ha,
            "Баланс фосфора у ворот фермы (синтетические компоненты)", "fig2_p_balance_v2.png")
print("DONE")
