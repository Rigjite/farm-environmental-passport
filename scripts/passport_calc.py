#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Farm Environmental Passport — calculation core (v0.2.0).

Every number a passport prints is computed here, from inputs that carry a
class (measured / modelled / never measured) and a provenance line. The core
does not measure anything and does not decide compliance: it computes doses,
balances, loads and screening statuses under the rules in
references/status-rules.md.

Standard library only. License: Apache-2.0 (code).
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path

# ----------------------------------------------------------------- units
ACRE_HA = 0.4046856                 # 1 acre = 0.4046856 ha (exact definition)
LB_KG = 0.45359237                  # 1 lb = 0.45359237 kg (exact definition)
LB_PER_ACRE_TO_KG_PER_HA = LB_KG / ACRE_HA          # = 1.12085
LB_PER_CWT_TO_KG_PER_MG = 10.0      # 1 lb per 100 lb = 10 kg per 1000 kg
NO3_PER_N = 62.0049 / 14.0067       # nitrate ion mass per nitrogen mass = 4.4268
MILK_DENSITY_KG_PER_L = 1.03        # whole cow's milk, approximate — stated convention


def no3n_to_no3(mg_n_per_l: float) -> float:
    """Nitrate expressed as N (US convention) -> as NO3 ion (EU convention)."""
    return mg_n_per_l * NO3_PER_N


def no3_to_no3n(mg_no3_per_l: float) -> float:
    return mg_no3_per_l / NO3_PER_N


def milk_ng_per_l_to_ug_per_kg(ng_per_l: float, density: float = MILK_DENSITY_KG_PER_L) -> float:
    """Milk result reported per litre -> per kg fresh weight (EU food limits use µg/kg)."""
    return ng_per_l / 1000.0 / density


# ----------------------------------------------------- censored values
@dataclass(frozen=True)
class Result:
    """One laboratory result. Censored (below reporting limit) is never silently 0 or missing."""
    analyte: str
    value: float | None          # reported value; None when censored
    unit: str
    censored: bool = False       # True = '<RL' / ND
    rl: float | None = None      # reporting limit for censored results
    cls: str = "measured"        # measured | modelled | never_measured
    source: str = ""

    def bounds(self) -> tuple[float, float]:
        """Lower/upper bound: ND -> [0, RL] (EFSA lower-bound / upper-bound convention)."""
        if self.cls == "never_measured":
            raise ValueError(f"{self.analyte}: never measured — no bounds, register as a gap")
        if self.censored:
            if self.rl is None:
                raise ValueError(f"{self.analyte}: censored result without reporting limit")
            return 0.0, float(self.rl)
        return float(self.value), float(self.value)


def sum_bounds(results: list[Result]) -> tuple[float, float]:
    """Sum of analytes as [lower bound, upper bound]; equal when nothing is censored."""
    lo = hi = 0.0
    for r in results:
        a, b = r.bounds()
        lo += a
        hi += b
    return lo, hi


# ------------------------------------------------------------- doses
def weekly_dose(conc_per_l: float, intake_l_per_day: float, bw_kg: float) -> float:
    """ng/kg bw per week = concentration (ng/L) x intake (L/day) x 7 / body weight (kg)."""
    if bw_kg <= 0 or intake_l_per_day < 0 or conc_per_l < 0:
        raise ValueError("dose inputs must be non-negative and body weight positive")
    return conc_per_l * intake_l_per_day * 7.0 / bw_kg


def break_even_intake(remaining_ng_per_kg_wk: float, conc_per_l: float, bw_kg: float) -> float:
    """Daily intake (L/day) of a product at which the remaining headroom to a TWI is used up."""
    if conc_per_l <= 0:
        return math.inf
    return max(remaining_ng_per_kg_wk, 0.0) * bw_kg / (conc_per_l * 7.0)


def efsa_sum_completeness(measured: set[str]) -> tuple[int, list[str]]:
    """EFSA 2020 TWI covers the SUM of four PFAS. Returns (n measured of 4, missing)."""
    four = ["PFOS", "PFOA", "PFNA", "PFHxS"]
    missing = [a for a in four if a not in measured]
    return 4 - len(missing), missing


# ---------------------------------------------------- nutrient balance
def farm_gate_balance(inputs: dict[str, float], outputs: dict[str, float], area_ha: float) -> dict:
    """Farm-gate balance: surplus = inputs - outputs (kg/yr) and per hectare.

    The denominator (whole farm vs tillable land) must be named by the caller
    in the passport; it changes the per-hectare figure and the benchmark it is
    compared with.
    """
    if any(v < 0 for v in list(inputs.values()) + list(outputs.values())):
        raise ValueError("balance components must be non-negative")
    tin, tout = sum(inputs.values()), sum(outputs.values())
    return {"in": tin, "out": tout, "surplus": tin - tout, "surplus_per_ha": (tin - tout) / area_ha,
            "use_efficiency": tout / tin if tin else float("nan")}


# --------------------------------------------- standing water (P loading)
def vollenweider_critical_load(depth_m: float, qs_m_per_yr: float, conc_ug_l: float) -> float:
    """Critical areal P load (mg/m2/yr) for an in-lake TP concentration (µg/L):
    L = [P] * qs * (1 + sqrt(z / qs))  — Vollenweider (1976) form, z mean depth, qs hydraulic load."""
    return conc_ug_l * qs_m_per_yr * (1.0 + math.sqrt(depth_m / qs_m_per_yr))


def vollenweider_predicted_tp(load_mg_m2_yr: float, depth_m: float, qs_m_per_yr: float) -> float:
    """Steady-state TP (µg/L) predicted from areal load — inverse of the same relation."""
    return load_mg_m2_yr / (qs_m_per_yr * (1.0 + math.sqrt(depth_m / qs_m_per_yr)))


OECD_TP = [(10.0, "oligotrophic"), (35.0, "mesotrophic"), (100.0, "eutrophic")]   # µg/L, annual/seasonal mean
OECD_CHLA = [(2.5, "oligotrophic"), (8.0, "mesotrophic"), (25.0, "eutrophic")]    # µg/L, mean


def oecd_class(value: float, bounds: list[tuple[float, str]]) -> str:
    for upper, name in bounds:
        if value < upper:
            return name
    return "hypertrophic"


# ------------------------------------------------------- threshold packs
def load_pack(path: str | Path) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def stale_rows(pack: dict, today: date, max_age_days: int) -> list[str]:
    """Rows whose last check against the primary source is older than allowed."""
    out = []
    for row in pack["rows"]:
        checked = date.fromisoformat(row["checked"])
        if (today - checked).days > max_age_days:
            out.append(row["id"])
    return out


def row(pack: dict, row_id: str) -> dict:
    for r in pack["rows"]:
        if r["id"] == row_id:
            return r
    raise KeyError(row_id)


# ------------------------------------------------------------ status
GREEN, WATCH, YELLOW, RED, GREY = "green", "green-watch", "yellow", "red", "grey"
_ORDER = {GREEN: 0, WATCH: 1, YELLOW: 2, RED: 3}
WATCH_FRACTION = 0.75   # skill convention, not a norm: >= 75 % of the lowest reference -> watch note


def worst(*statuses: str) -> str:
    known = [s for s in statuses if s != GREY]
    if not known:
        return GREY
    return max(known, key=lambda s: _ORDER[s])


def screening_status(values: list[float], ref: dict, determination: str | None = None) -> dict:
    """Status of one object against one reference row (see references/status-rules.md).

    values        — measured values in the reference's unit, in time order (one sampling event each).
    ref           — threshold row: value, legal_status, applicability, determination_rule.
    determination — optional pre-computed result of the source's own rule ('exceeded' / 'not_exceeded').

    Rules, in order:
      no measured value                         -> grey (never a colour from a model)
      no value above the reference              -> green, or green-watch at >= 75 % of it
      reference is future / guidance / orientation / superseded -> yellow at most (screening)
      in-force reference and the source's own determination rule is met
        (or, without one, >= 2 consecutive events above it)                -> red
      any other exceedance (single sample, one quarter above a mean that is below) -> yellow
    Applicability by analogy (public-water MCL vs a private well) changes the wording, not the colour.
    """
    if not values:
        return {"status": GREY, "why": "no measurement"}
    thr = float(ref["value"])
    above = [v > thr for v in values]
    peak = max(values)
    if not any(above):
        st = WATCH if peak >= WATCH_FRACTION * thr else GREEN
        return {"status": st, "why": f"max {peak:g} vs {thr:g} ({peak / thr:.0%})"}
    legal = ref["legal_status"]
    if legal != "in_force":
        return {"status": YELLOW, "why": f"above a {legal} reference — screening only"}
    consecutive = any(a and b for a, b in zip(above, above[1:]))
    if determination == "exceeded" or (determination is None and consecutive):
        return {"status": RED, "why": "sustained exceedance under the determination rule"}
    return {"status": YELLOW, "why": "exceedance not sustained (single event or mean below)"}


def censored_status(result: Result, ref: dict) -> dict:
    """Censored results: classify lower and upper bound; if they differ, report the worse with a flag."""
    lo, hi = result.bounds()
    s_lo = screening_status([lo], ref)["status"]
    s_hi = screening_status([hi], ref)["status"]
    st = worst(s_lo, s_hi)
    return {"status": st, "depends_on_censoring": s_lo != s_hi, "bounds": (lo, hi)}
