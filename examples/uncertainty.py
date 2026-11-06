"""Uncertainty and sensitivity block for FARM-PFAS-SIMULATION (Delaware, synthetic farm).
2026-11-05. Reproduces every number of section 4.1 of redaction 4.

Design: reducible UNCERTAINTY (what sampling can narrow) is propagated by Monte Carlo;
VARIABILITY between people (intake, body weight) is kept as fixed exposure profiles.
Every distribution below is an ASSUMPTION of this analysis, labelled as such in the report.
Run: python3 uncertainty.py   (seed fixed; numpy only)
"""
import numpy as np

RNG = np.random.default_rng(20261105)
N = 400_000
TWI = 4.4  # ng/kg bw/week, EFSA 2020 (sum of PFOA, PFNA, PFHxS, PFOS)

# ---- point inputs from the simulation (synthetic values, unchanged) ----
WELL_PFOS, WELL_PFOA = 6.5, 3.8   # ng/L, one sample
MILK_MEAS = 18.0                   # ng/L PFOS, one bulk-tank sample
SOIL_MEAN = 0.60                   # ug/kg PFOS, mean of F1-F4 (feed fields)
OWN_FEED = 22.0 * 0.60             # kg DM/day from own fields
COW_WATER = 100.0                  # L/day from the same well
MILK_YIELD = 10500 / 365           # kg/day per cow

# ---- exposure profiles (variability, fixed) ----
PROFILES = {
    # name: (water L/kg bw/day, milk L/kg bw/day)
    "Взрослый, молоко 0,25 л/сут": (2.0 / 70, 0.25 / 70),
    "Взрослый, молоко 0,64 л/сут": (2.0 / 70, 0.64 / 70),
    "Младенец, вода — средняя норма": (0.595 / 7.8, 0.0),  # ATSDR 2023, табл. 1: 595 мл/сут, 7,8 кг
    "Младенец, вода — 95-й перцентиль": (1.106 / 7.8, 0.0),  # ATSDR 2023: 1 106 мл/сут (RME)
    "Ребёнок 1–2 лет, вода средняя, молоко 0,25 л/сут": (0.245 / 11.4, 0.25 / 11.4),  # ATSDR 2023: 245 мл/сут, 11,4 кг
    "Ребёнок 1–2 лет, вода P95, молоко 0,25 л/сут": (0.658 / 11.4, 0.25 / 11.4),  # ATSDR 2023: 658 мл/сут (RME)
}


def lognorm(gsd, size):
    return np.exp(RNG.normal(0.0, np.log(gsd), size))


def draw(gsd_well=1.4):
    """Draw the reducible-uncertainty inputs (all ASSUMPTIONS, see report table)."""
    return {
        "well": lognorm(gsd_well, N),            # annual mean / single sample, PFOS and PFOA together
        "addon_w": RNG.uniform(0.0, 0.5, N),     # PFNA+PFHxS in water, share of PFOS+PFOA (illustrative)
        "milk": lognorm(1.3, N),                 # single bulk-tank sample -> annual mean
        "addon_m": RNG.uniform(0.0, 0.5, N),     # PFOA, PFNA, PFHxS in milk, share of PFOS (illustrative)
        "TF": np.exp(RNG.uniform(np.log(0.026), np.log(0.37), N)),  # literature range, log-uniform
        "transfer": RNG.uniform(0.07, 0.21, N),  # 14 % +/- 50 %
        "soil": lognorm(1.2, N),                 # mean field soil around 0.60
    }


def dose(x, water_lkg, milk_lkg, with_addon):
    w = (WELL_PFOS + WELL_PFOA) * x["well"]
    m = MILK_MEAS * x["milk"]
    if with_addon:
        w = w * (1 + x["addon_w"])
        m = m * (1 + x["addon_m"])
    return 7 * (w * water_lkg + m * milk_lkg)


def milk_model(x):
    feed = SOIL_MEAN * x["soil"] * 1000 * x["TF"] * OWN_FEED
    water = COW_WATER * WELL_PFOS * x["well"]
    return (feed + water) * x["transfer"] / MILK_YIELD, water / (feed + water)


def first_order(y, xi, bins=50):
    """First-order sensitivity index Var(E[y|xi]) / Var(y) by quantile binning."""
    edges = np.quantile(xi, np.linspace(0, 1, bins + 1))
    idx = np.clip(np.searchsorted(edges, xi, side="right") - 1, 0, bins - 1)
    means = np.bincount(idx, weights=y, minlength=bins) / np.bincount(idx, minlength=bins)
    return float(np.var(means[idx]) / np.var(y))


def pct(a, q):
    return float(np.percentile(a, q))


def main():
    x = draw()
    print("=== Дозы по профилям, нг/кг/нед (TWI 4,4) ===")
    for name, (wl, ml) in PROFILES.items():
        point = 7 * ((WELL_PFOS + WELL_PFOA) * wl + MILK_MEAS * ml)
        d2 = dose(x, wl, ml, False)
        d4 = dose(x, wl, ml, True)
        print(f"{name}: точка {point:.2f} | 2 PFAS: медиана {pct(d2,50):.2f}, 90%-интервал "
              f"{pct(d2,5):.2f}–{pct(d2,95):.2f}, P(>TWI) {(d2>TWI).mean():.0%} | "
              f"с PFNA/PFHxS: медиана {pct(d4,50):.2f}, P95 {pct(d4,95):.2f}, P(>TWI) {(d4>TWI).mean():.0%}")

    print("\n=== Устойчивость к допущению о разбросе скважины (GSD) ===")
    for g in (1.2, 1.4, 1.7):
        xg = draw(g)
        for name in ("Младенец, вода — средняя норма", "Взрослый, молоко 0,64 л/сут"):
            wl, ml = PROFILES[name]
            d2 = dose(xg, wl, ml, False)
            print(f"GSD {g}: {name}: P(>TWI, 2 PFAS) {(d2>TWI).mean():.0%}, 90% {pct(d2,5):.2f}–{pct(d2,95):.2f}")

    print("\n=== Чувствительность (доля дисперсии, первого порядка) — доза с PFNA/PFHxS ===")
    for name in ("Взрослый, молоко 0,64 л/сут", "Младенец, вода — средняя норма",
                 "Ребёнок 1–2 лет, вода средняя, молоко 0,25 л/сут"):
        wl, ml = PROFILES[name]
        d4 = dose(x, wl, ml, True)
        s = {k: first_order(d4, x[k]) for k in ("well", "addon_w", "milk", "addon_m")}
        print(name, {k: f"{v:.0%}" for k, v in s.items()})

    print("\n=== Модель молока ===")
    mm, wshare = milk_model(x)
    print(f"медиана {pct(mm,50):.1f}, 90% {pct(mm,5):.1f}–{pct(mm,95):.1f} нг/л; "
          f"P(модель >= 18) {(mm>=MILK_MEAS).mean():.0%}; доля воды коров в PFOS молока: "
          f"медиана {pct(wshare,50):.0%}, 90% {pct(wshare,5):.0%}–{pct(wshare,95):.0%}")
    s = {k: first_order(mm, x[k]) for k in ("TF", "transfer", "soil", "well")}
    print("чувствительность модели молока", {k: f"{v:.0%}" for k, v in s.items()})

    print("\n=== Ценность пробы: квартальная серия скважины (4 пробы) ===")
    # averaging 4 independent quarterly samples narrows the annual-mean GSD: ln(GSD)/sqrt(4)
    g4 = float(np.exp(np.log(1.4) / 2))
    x4 = draw(g4)
    for name in ("Младенец, вода — средняя норма", "Ребёнок 1–2 лет, вода средняя, молоко 0,25 л/сут"):
        wl, ml = PROFILES[name]
        before, after = dose(x, wl, ml, False), dose(x4, wl, ml, False)
        print(f"{name}: 90%-интервал {pct(before,5):.2f}–{pct(before,95):.2f} -> "
              f"{pct(after,5):.2f}–{pct(after,95):.2f} (GSD {g4:.2f})")


if __name__ == "__main__":
    main()
