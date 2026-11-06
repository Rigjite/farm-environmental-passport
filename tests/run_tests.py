#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Executable tests for farm-environmental-passport v0.3.x (T1–T34 in tests/TESTS.md).

Expected values come from the two worked examples (the task's key numbers) and from
hand calculations written next to each check — never from the code under test.
Writes a dated pass/fail protocol to tests/RUN-LOG.md and exits non-zero on any failure.

Usage: python3 tests/run_tests.py [--date YYYY-MM-DD]
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import passport_calc as pc  # noqa: E402

TODAY = date.fromisoformat(sys.argv[sys.argv.index("--date") + 1]) if "--date" in sys.argv else date.today()
SIM1 = json.loads((ROOT / "tests/fixtures/sim1_pfas.json").read_text(encoding="utf-8"))
SIM2 = json.loads((ROOT / "tests/fixtures/sim2_water_nutrients.json").read_text(encoding="utf-8"))
NYUS = pc.load_pack(ROOT / "core/thresholds/ny-us.json")
EU = pc.load_pack(ROOT / "core/thresholds/eu.json")

# sha256 of the files as received on 2026-11-01 (intake record; these files are never edited)
INTAKE_SHA256 = {
    "examples/FARM-PFAS-SIMULATION-2026-10-31.md": "9bbf103ec9ce7a922f749d6eb4fd56ba3ff4dd47d994d1ff3dde8c38fb49de3b",
    "examples/FARM-WATER-NUTRIENTS-SIMULATION-2026-10-31.md": "547b5debc284c39df54c4780ced2fd11eec7e091f73768d485ffaeef44879440",
    "examples/make_figs2.py": "26b8ec1803890bb91ec642c3d63ad4e706ed89de7752b7b4f1c21e5600c7a1e9",
    "archive/v0.1.0/SKILL.md": "3a306e21c071460dd6fd9c91b9ebdffd159ff9ccb67b5c279d62819e57e3211f",
}

RESULTS: list[tuple[str, str, bool, list[str]]] = []


def r(x: float, nd: int) -> float:
    """Round half-up on the decimal representation, as the documents print numbers."""
    q = Decimal(1).scaleb(-nd)
    return float(Decimal(repr(x)).quantize(q, rounding=ROUND_HALF_UP))


class Check:
    def __init__(self):
        self.lines: list[str] = []
        self.ok = True

    def eq(self, label, got, expected):
        ok = got == expected
        self.ok &= ok
        self.lines.append(f"{'ok ' if ok else 'XX '} {label}: got {got!r}, expected {expected!r}")

    def true(self, label, cond, detail=""):
        self.ok &= bool(cond)
        self.lines.append(f"{'ok ' if cond else 'XX '} {label}" + (f" — {detail}" if detail else ""))


def test(tid, title):
    def deco(fn):
        c = Check()
        try:
            fn(c)
        except Exception as e:  # a crash is a failure, recorded with its message
            c.ok = False
            c.lines.append(f"XX exception: {type(e).__name__}: {e}")
        RESULTS.append((tid, title, c.ok, c.lines))
        return fn
    return deco


# ------------------------------------------------------------------ farm model (Modules 2–3)
def farm2():
    d = SIM2
    fields_ha = sum(d["FIELDS_AC"].values()) * d["ACRE_HA"]
    pasture_ha, f5_ha, forest_ha = (d[k] * d["ACRE_HA"] for k in ("PASTURE_AC", "F5_AC", "FOREST_AC"))
    farm_ha = fields_ha + pasture_ha + f5_ha + forest_ha
    ration = d["COWS"] * d["RATION_DM_KG_DAY"] * 365
    feed = ration * (1 - d["OWN_FORAGE_SHARE"])
    biosolids_t = sum(d["FIELDS_AC"].values()) * d["BIOSOLIDS_T_PER_AC"]
    milk = d["COWS"] * d["MILK_YIELD_KG"]
    lw = d["CULLS"] * d["CULL_LW_KG"] + d["HEIFERS_SOLD"] * d["HEIFER_LW_KG"]
    n_in = {"mineral": d["MINERAL_N_KG"], "biosolids": biosolids_t * 1000 * d["BIOSOLIDS_N_FRAC"],
            "feed": feed * d["FEED_N_FRAC"], "fixation": d["FIXATION_HA"] * d["FIXATION_RATE"],
            "deposition": round(farm_ha * d["DEPOSITION_N_KG_HA"])}
    n_out = {"milk": milk * d["MILK_N_FRAC"], "livestock": lw * d["LW_N_FRAC"], "crops": d["CROPS_SOLD_DM_KG"] * d["CROPS_N_FRAC"]}
    p_in = {"mineral": d["MINERAL_P_KG"], "biosolids": biosolids_t * 1000 * d["BIOSOLIDS_P_FRAC"],
            "feed": feed * d["FEED_P_FRAC"], "deposition": farm_ha * d["DEPOSITION_P_KG_HA"]}
    p_out = {"milk": milk * d["MILK_P_FRAC"], "livestock": lw * d["LW_P_FRAC"], "crops": d["CROPS_SOLD_DM_KG"] * d["CROPS_P_FRAC"]}
    return dict(farm_ha=farm_ha, fields_ha=fields_ha, pasture_ha=pasture_ha, f5_ha=f5_ha, forest_ha=forest_ha,
                milk_kg=milk, N=pc.farm_gate_balance(n_in, n_out, farm_ha), P=pc.farm_gate_balance(p_in, p_out, farm_ha))


def pond():
    d = SIM2
    load_kg = d["POND_CATCH_HA"] * d["EXPORT_TP"]["biosolids"] * d["DELIVERY_RATIO"]
    area_m2 = d["POND_AREA_HA"] * 1e4
    areal = load_kg * 1e6 / area_m2
    qs = d["POND_CATCH_HA"] * 1e4 * d["POND_RUNOFF_M"] / area_m2
    z = d["POND_DEPTH_M"]
    perm = pc.vollenweider_critical_load(z, qs, d["VOLL_PERM_CONC"])
    dang = pc.vollenweider_critical_load(z, qs, d["VOLL_DANG_CONC"])
    return dict(areal=areal, qs=qs, perm=perm, dang=dang, pred=pc.vollenweider_predicted_tp(areal, z, qs),
                tau_days=area_m2 * z / (qs * area_m2) * 365)


# ======================================================================= tests
@test("T1", "Dose milk + well water vs EFSA TWI (Module 1)")
def t1(c):
    a = SIM1["dose_assumptions"]
    milk = SIM1["milk_tank_ng_l"]["PFOS"]
    water = SIM1["well_ng_l"]["PFOS"] + SIM1["well_ng_l"]["PFOA"]
    m_lo, m_hi = (pc.weekly_dose(milk, x, a["bw_kg"]) for x in a["milk_l_per_day"])
    w = pc.weekly_dose(water, a["water_l_per_day"], a["bw_kg"])
    e = SIM1["expected_from_text"]
    c.eq("milk only, ng/kg/wk", [r(m_lo, 2), r(m_hi, 2)], e["milk_only_ng_kg_wk"])
    c.eq("water only, ng/kg/wk", r(w, 2), e["water_only_ng_kg_wk"])
    c.eq("milk + water, ng/kg/wk", [r(m_lo + w, 2), r(m_hi + w, 2)], e["milk_plus_water_ng_kg_wk"])
    twi = pc.row(NYUS, "NYUS-10")["value"]
    c.eq("TWI from the pack", twi, e["efsa_twi_ng_kg_wk"])
    c.true("upper bound below TWI (adult scenario)", m_hi + w < twi, f"{m_hi + w:.3f} < {twi}")


@test("T2", "Nitrogen farm-gate surplus (Module 3)")
def t2(c):
    f = farm2()
    e = SIM2["expected_from_text"]
    c.eq("N surplus, kg/yr", int(r(f["N"]["surplus"], 0)), e["N_surplus_kg_yr"])
    c.eq("N surplus, kg/ha/yr", int(r(f["N"]["surplus_per_ha"], 0)), e["N_surplus_kg_ha_yr"])
    c.eq("N input total (text: 12 464)", int(r(f["N"]["in"], 0)), 12464)
    c.eq("N output with products (text: 6 003)", int(r(f["N"]["out"], 0)), 6003)


@test("T3", "Phosphorus farm-gate surplus (Module 3)")
def t3(c):
    f = farm2()
    e = SIM2["expected_from_text"]
    c.eq("P surplus, kg/yr", int(r(f["P"]["surplus"], 0)), e["P_surplus_kg_yr"])
    c.eq("P surplus, kg/ha/yr (≈47)", int(r(f["P"]["surplus_per_ha"], 0)), e["P_surplus_kg_ha_yr"])
    c.eq("P surplus, one decimal", r(f["P"]["surplus_per_ha"], 1), 46.6)


@test("T4", "Pond phosphorus loading vs Vollenweider criteria (Module 3)")
def t4(c):
    p = pond()
    e = SIM2["expected_from_text"]
    c.eq("areal load, mg/m2/yr", int(r(p["areal"], 0)), e["pond_load_mg_m2_yr"])
    c.eq("permissible, mg/m2/yr", int(r(p["perm"], 0)), e["pond_perm_mg_m2_yr"])
    c.eq("dangerous, mg/m2/yr", int(r(p["dang"], 0)), e["pond_dang_mg_m2_yr"])
    c.eq("load / dangerous", r(p["areal"] / p["dang"], 1), e["pond_over_dangerous"])
    c.eq("load / permissible (text: 7 times)", int(r(p["areal"] / p["perm"], 0)), 7)
    c.eq("predicted TP, µg/L", int(r(p["pred"], 0)), e["pond_tp_pred_ug_l"])
    c.eq("hydraulic load qs, m/yr (text 16.8)", r(p["qs"], 1), 16.8)
    c.eq("residence time, days (text ≈39)", int(r(p["tau_days"], 0)), 39)
    c.true("prediction within ±10 % of synthetic measurement 68", abs(p["pred"] - SIM2["POND_TP"]) / SIM2["POND_TP"] < 0.10)


@test("T5", "Well nitrate: annual mean and quarterly maximum (Module 2)")
def t5(c):
    v = SIM2["WELL_NO3N"]
    mean = float(sum(Decimal(str(x)) for x in v) / len(v))
    e = SIM2["expected_from_text"]
    c.eq("mean NO3-N, mg/L", r(mean, 1), e["well_no3n_mean"])
    c.eq("max NO3-N, mg/L", max(v), e["well_no3n_max"])
    c.eq("quarter of the max", ["I", "II", "III", "IV"][v.index(max(v))], e["well_no3n_max_quarter"])


@test("T6", "Stream total phosphorus mean (Module 2)")
def t6(c):
    v = SIM2["STREAM_TP"]
    c.eq("mean TP, µg/L", r(sum(v) / len(v), 1), SIM2["expected_from_text"]["stream_tp_mean"])


@test("T7", "Independent implementation: original make_figs2.py agrees with passport_calc")
def t7(c):
    src = ROOT / "examples/make_figs2.py"
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(src, tmp)
        env = dict(os.environ, MPLBACKEND="Agg")
        out = subprocess.run([sys.executable, "-I", str(Path(tmp) / "make_figs2.py")], capture_output=True,
                             text=True, env=env, timeout=300, cwd=tmp).stdout
    c.true("script finished (DONE printed)", "DONE" in out)
    num = lambda s: float(s.replace(",", ""))
    n = re.search(r"N: профицит ([\d,]+) кг/год = ([\d.]+)", out)
    p = re.search(r"P: профицит ([\d,]+) кг/год = ([\d.]+)", out)
    v = re.search(r"Фолленвайдер: допустимая ([\d,]+), опасная ([\d,]+).*?в ([\d.]+) раза; прогноз TP (\d+)", out)
    w = re.search(r"Скважина NO3-N: среднее ([\d.]+)", out)
    s = re.search(r"Ручей TP: среднее арифметическое ([\d.]+)", out)
    f, pd = farm2(), pond()
    c.eq("N surplus (script vs core)", (num(n.group(1)), num(n.group(2))), (r(f["N"]["surplus"], 0), r(f["N"]["surplus_per_ha"], 1)))
    c.eq("P surplus (script vs core)", (num(p.group(1)), num(p.group(2))), (r(f["P"]["surplus"], 0), r(f["P"]["surplus_per_ha"], 1)))
    c.eq("Vollenweider (script vs core)", (num(v.group(1)), num(v.group(2)), float(v.group(3)), float(v.group(4))),
         (r(pd["perm"], 0), r(pd["dang"], 0), r(pd["areal"] / pd["dang"], 1), r(pd["pred"], 0)))
    c.eq("well mean, 2 dp (script)", w.group(1), "8.57")   # script prints 8.57 (binary 8.575 rounds down); text prints 8.6
    c.eq("stream mean (script)", float(s.group(1)), 47.4)


@test("T8", "Synthetic values unchanged; model–measurement discrepancy kept")
def t8(c):
    for rel, h in INTAKE_SHA256.items():
        got = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        c.true(f"sha256 unchanged: {rel}", got == h)
    tree = ast.parse((ROOT / "examples/make_figs2.py").read_text(encoding="utf-8"))
    consts = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            try:
                val = ast.literal_eval(node.value)
            except Exception:
                continue
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            tuples = [t for t in node.targets if isinstance(t, ast.Tuple)]
            for nm in names:
                consts[nm] = val
            for t in tuples:
                for el, vv in zip(t.elts, val):
                    consts[el.id] = vv
    mismatched = []
    for k, v in SIM2.items():
        if k.startswith("_") or k in ("source_file", "expected_from_text"):
            continue
        sv = consts.get(k)
        if k == "FIELDS_AC":
            sv = {key.split()[0]: val for key, val in sv.items()}
        if sv != v:
            mismatched.append(k)
    c.true("fixture = DATA BLOCK of make_figs2.py", not mismatched, f"mismatched: {mismatched}" if mismatched else "all constants equal")
    text = (ROOT / "examples/FARM-PFAS-SIMULATION-2026-10-31.md").read_text(encoding="utf-8")
    for needle in ["PFOS 12 мкг/кг", "PFOS 6,5 нг/л, PFOA 3,8 нг/л", "PFOS 18 нг/л", "4–17 нг/л", "2,51–3,21", "0,90 | 0,40"]:
        c.true(f"simulation text still contains '{needle}'", needle in text)
    lo, hi = SIM1["milk_model_range_ng_l"]
    c.true("milk 18 ng/L stays above the model range 4–17 (discrepancy kept, not smoothed)", SIM1["milk_tank_ng_l"]["PFOS"] > hi)


@test("T9", "Statuses of both worked examples reproduced by the v0.2 decision table")
def t9(c):
    S = pc.screening_status
    bio = pc.worst(S([SIM1["biosolids_ug_kg_dw"]["PFOS"]], pc.row(NYUS, "NYUS-07"))["status"],
                   S([SIM1["biosolids_ug_kg_dw"]["PFOA"]], pc.row(NYUS, "NYUS-07"))["status"])
    soil = pc.worst(*[S([f["PFOS"]], pc.row(NYUS, "NYUS-16"))["status"] for f in SIM1["soil_0_20cm_ug_kg"].values()])
    wl = SIM1["well_ng_l"]
    well = pc.worst(S([wl["PFOS"]], pc.row(NYUS, "NYUS-02"))["status"], S([wl["PFOA"]], pc.row(NYUS, "NYUS-01"))["status"],
                    S([wl["PFOS"]], pc.row(NYUS, "NYUS-04"))["status"], S([wl["PFOA"]], pc.row(NYUS, "NYUS-03"))["status"])
    milk = S([SIM1["milk_tank_ng_l"]["PFOS"]], pc.row(NYUS, "NYUS-14"))["status"]
    got1 = {"biosolids": bio, "soil": soil, "well": well, "milk": milk}
    c.eq("Module 1 statuses", got1, SIM1["expected_from_text"]["statuses"])
    nitrate = S(SIM2["WELL_NO3N"], pc.row(NYUS, "NYUS-06"))["status"]
    tp = SIM2["STREAM_TP"]
    stream = pc.worst(S([sum(tp) / len(tp)], pc.row(NYUS, "NYUS-19"))["status"],
                      S([SIM2["ECOLI_EVENT"]], pc.row(NYUS, "NYUS-12"))["status"])
    pond_s = pc.worst(S([SIM2["POND_TP"]], pc.row(NYUS, "NYUS-19"))["status"], S([SIM2["POND_CHLA"]], pc.row(NYUS, "NYUS-20"))["status"])
    f = farm2()
    nb = S([f["N"]["surplus_per_ha"]], pc.row(NYUS, "NYUS-17"))["status"]
    pb = S([f["P"]["surplus_per_ha"]], pc.row(NYUS, "NYUS-18"))["status"]
    got2 = {"well_nitrate": nitrate, "stream": stream, "pond": pond_s, "N_balance": nb, "P_balance": pb}
    c.eq("Modules 2–3 statuses", got2, SIM2["expected_from_text"]["statuses"])
    c.eq("OECD class of the pond (TP 68, chl-a 21)", (pc.oecd_class(68, pc.OECD_TP), pc.oecd_class(21, pc.OECD_CHLA)), ("eutrophic", "eutrophic"))
    c.eq("OECD class of the stream mean (47.4)", pc.oecd_class(47.4, pc.OECD_TP), "eutrophic")


@test("T10", "Red only on a sustained exceedance")
def t10(c):
    mcl = pc.row(NYUS, "NYUS-06")      # in force, 10 mg/L as N
    fut = pc.row(NYUS, "NYUS-04")      # future, 4.0 ng/L
    S = lambda v, ref, d=None: pc.screening_status(v, ref, d)["status"]
    c.eq("single sample 11.4 above in-force MCL", S([11.4], mcl), "yellow")
    c.eq("one quarter above, mean below [8.9, 11.4, 7.2, 6.8]", S([8.9, 11.4, 7.2, 6.8], mcl), "yellow")
    c.eq("two consecutive events above [11.4, 10.6]", S([11.4, 10.6], mcl), "red")
    c.eq("non-consecutive [11.4, 9.0, 10.6]", S([11.4, 9.0, 10.6], mcl), "yellow")
    c.eq("source rule met (e.g. RAA) on a single reported value", S([12.0], mcl, "exceeded"), "red")
    c.eq("sustained above a FUTURE reference stays yellow", S([6.5, 6.8, 7.0], fut), "yellow")
    c.eq("no measurement -> grey", S([], mcl), "grey")
    c.eq("7.6 = 76 % of 10 -> green-watch", S([7.6], mcl), "green-watch")
    c.eq("7.4 = 74 % of 10 -> green", S([7.4], mcl), "green")


@test("T11", "Censored values: bounds, sums, flag; never-measured is a gap")
def t11(c):
    ref = pc.row(NYUS, "NYUS-04")  # 4.0 ng/L
    nd = pc.Result("PFNA", None, "ng/L", censored=True, rl=2.0)
    c.eq("ND bounds", nd.bounds(), (0.0, 2.0))
    s = pc.sum_bounds([pc.Result("PFOS", 6.5, "ng/L"), pc.Result("PFOA", 3.8, "ng/L"), nd,
                       pc.Result("PFHxS", None, "ng/L", censored=True, rl=2.0)])
    c.eq("sum of 4 with two ND, [LB, UB]", (r(s[0], 2), r(s[1], 2)), (10.3, 14.3))
    nd5 = pc.Result("PFOS", None, "ng/L", censored=True, rl=5.0)
    cs = pc.censored_status(nd5, ref)
    c.eq("ND with RL 5 vs reference 4 -> worse bound reported", cs["status"], "yellow")
    c.true("flag 'depends on censored values' raised", cs["depends_on_censoring"])
    try:
        pc.Result("PFHxS", None, "ng/L", cls="never_measured").bounds()
        c.true("never-measured raises (must be a gap, not a number)", False)
    except ValueError:
        c.true("never-measured raises (must be a gap, not a number)", True)


@test("T12", "Completeness of the EFSA four-PFAS sum")
def t12(c):
    n, missing = pc.efsa_sum_completeness(set(SIM1["measured_pfas"]))
    c.eq("measured of 4", n, 2)
    c.eq("missing analytes", missing, ["PFNA", "PFHxS"])
    c.true("dose must be printed as a lower bound", n < 4)


@test("T13", "Sensitive-group dose scenarios (new in v0.2)")
def t13(c):
    water = SIM1["well_ng_l"]["PFOS"] + SIM1["well_ng_l"]["PFOA"]   # 10.3 ng/L, 2 of 4 PFAS
    milk = SIM1["milk_tank_ng_l"]["PFOS"]
    twi = 4.4
    # ATSDR 2023 Exposure Dose Guidance for Water Ingestion, Table 1 (EPA EFH 2019): mean / 95th, body weight
    inf_m, inf_95 = pc.weekly_dose(water, 0.595, 7.8), pc.weekly_dose(water, 1.106, 7.8)
    ch_m, ch_95 = pc.weekly_dose(water, 0.245, 11.4), pc.weekly_dose(water, 0.658, 11.4)
    c.eq("infant formula with well water, mean (hand: 10.3*0.595*7/7.8)", r(inf_m, 2), 5.50)
    c.eq("infant, 95th percentile (hand: 10.3*1.106*7/7.8)", r(inf_95, 2), 10.22)
    c.true("infant mean already above the TWI with 2 of 4 PFAS", inf_m > twi, f"{inf_m:.2f} > {twi}")
    c.eq("child 1–<2 y water only, mean / 95th", (r(ch_m, 2), r(ch_95, 2)), (1.55, 4.16))
    be_m = pc.break_even_intake(twi - ch_m, milk, 11.4)
    be_95 = pc.break_even_intake(twi - ch_95, milk, 11.4)
    c.eq("break-even farm milk for the child, L/day (mean / 95th water)", (r(be_m, 2), r(be_95, 3)), (0.26, 0.022))
    c.true("adult-only conclusion 'no exceedance in any scenario' is not general", inf_m > twi)


@test("T14", "EU pack applied to the synthetic farm (second jurisdiction)")
def t14(c):
    S = lambda v, ref: pc.screening_status(v, ref)["status"]
    no3 = [pc.no3n_to_no3(x) for x in SIM2["WELL_NO3N"]]
    c.eq("Q2 nitrate as NO3, mg/L (11.4 × 4.427)", r(no3[1], 1), 50.5)
    c.eq("well nitrate vs EU 50 mg/L NO3", S(no3, pc.row(EU, "EU-03")), "yellow")
    c.eq("EU 50 as NO3 = 11.3 as N", r(pc.no3_to_no3n(50), 1), 11.3)
    lb = SIM1["well_ng_l"]["PFOS"] + SIM1["well_ng_l"]["PFOA"]
    c.eq("well vs EU groundwater sum-of-4 (future, partial sum = lower bound)", S([lb], pc.row(EU, "EU-04")), "yellow")
    c.eq("well vs EU drinking water 'Sum of PFAS' 100 ng/L (2 of 20 = lower bound)", S([lb], pc.row(EU, "EU-01")), "green")
    milk_ugkg = pc.milk_ng_per_l_to_ug_per_kg(SIM1["milk_tank_ng_l"]["PFOS"])
    c.eq("milk PFOS, µg/kg (18 / 1000 / 1.03)", r(milk_ugkg, 4), 0.0175)
    c.eq("milk PFOS vs EU indicative 0.020 µg/kg -> watch (87 %)", S([milk_ugkg], pc.row(EU, "EU-21")), "green-watch")
    c.true("EU has no numeric PFAS value for agricultural soil (row EU-17 value null)", pc.row(EU, "EU-17")["value"] is None)
    c.true("EU sludge waiting period before grazing ≥ 3 weeks present (EU-16)", pc.row(EU, "EU-16")["value"] == 3)
    c.true("same object, two packs, different binding reference — both printed",
           pc.row(NYUS, "NYUS-04")["legal_status"] == "future" and pc.row(EU, "EU-04")["legal_status"] == "future")


@test("T15", "Threshold packs: structure, rendered table in sync, freshness")
def t15(c):
    need = {"id", "matrix", "analyte", "value", "unit", "legal_status", "applies_from", "applicability",
            "determination_rule", "source_doc", "source_org", "url", "checked", "verified", "note"}
    ls = {"in_force", "future", "guidance", "orientation", "superseded", "requirement", "proposed"}
    vf = {"verified", "verified-secondary", "corrected", "not-verified"}
    for pack in (NYUS, EU):
        bad = [x["id"] for x in pack["rows"] if not need <= set(x) or x["legal_status"] not in ls or x["verified"] not in vf]
        c.true(f"{pack['pack']}: all {len(pack['rows'])} rows complete, vocabulary valid", not bad, str(bad) if bad else "")
        c.eq(f"{pack['pack']}: stale rows on {TODAY}", pc.stale_rows(pack, TODAY, pack["max_age_days"]), [])
        c.true(f"{pack['pack']}: every row stale on 2027-06-01 (mechanism works)",
               len(pc.stale_rows(pack, date(2027, 6, 1), pack["max_age_days"])) == len(pack["rows"]))
    rc = subprocess.run([sys.executable, str(ROOT / "scripts/render_thresholds.py"), "--check"]).returncode
    c.true("core/thresholds.md equals a fresh render of the JSON packs", rc == 0)
    c.true("EU pack covers drinking water, EFSA, soil", all(any(k in x["matrix"] for x in EU["rows"]) for k in ("human consumption", "consumer dose", "soil")))
    c.true("Maine milk line present and verified", pc.row(NYUS, "NYUS-14")["value"] == 210 and pc.row(NYUS, "NYUS-14")["verified"] == "verified")


@test("T16", "Line-by-line verification covers every v0.1 threshold line")
def t16(c):
    v01 = (ROOT / "archive/v0.1.0/SKILL.md").read_text(encoding="utf-8")
    block = v01.split("## Thresholds")[1].split("## Sampling plan")[0]
    lines = [l for l in block.splitlines() if l.startswith("- ")]
    c.eq("threshold lines in v0.1.0", len(lines), 6)
    ver = (ROOT / "references/threshold-verification-2026-11-01.md").read_text(encoding="utf-8")
    table = ver.split("## 1.")[1].split("## 2.")[0]
    rows = [l for l in table.splitlines() if re.match(r"\| (\d|6[ab]) \|", l)]
    c.eq("rows in the verification table (6 lines, nitrate/E. coli split)", len(rows), 7)
    c.true("each row carries a result mark", all(re.search(r"\*\*(verified|corrected[^*]*)\*\*", l) for l in rows))
    unconfirmed = re.findall(r"^\d+\. ", ver.split("## 3.")[1], flags=re.M)
    c.eq("items in the unconfirmed / corrected list", len(unconfirmed), 11)
    marks = [x["verified"] for x in NYUS["rows"] + EU["rows"]]
    c.true("pack marks counted", True, ", ".join(f"{m}: {marks.count(m)}" for m in sorted(set(marks))))


@test("T17", "Analytical method by matrix")
def t17(c):
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    meth = (ROOT / "references/methods.md").read_text(encoding="utf-8")
    c.true("SKILL names EPA 533 or 537.1 for drinking water", "EPA 533 or 537.1" in skill)
    c.true("SKILL names EPA 1633 for non-drinking matrices", "EPA 1633" in skill)
    c.true("SKILL names a food method for milk (FDA C-010.03)", "FDA C-010.03" in skill)
    c.true("v0.1 phrase 'EPA 1633 or the current analogue' removed", "EPA 1633 or the current analogue" not in skill)
    c.true("methods.md has the matrix table", "| Matrix | Method |" in meth)


@test("T18", "Nutrient balance against the Cornell NY feasible benchmark (new)")
def t18(c):
    f = farm2()
    S = lambda v, ref: pc.screening_status(v, ref)["status"]
    nref, pref = pc.row(NYUS, "NYUS-17"), pc.row(NYUS, "NYUS-18")
    c.eq("105 lb/acre in kg/ha", r(105 * pc.LB_PER_ACRE_TO_KG_PER_HA, 1), 117.7)
    c.eq("12 lb/acre in kg/ha", r(12 * pc.LB_PER_ACRE_TO_KG_PER_HA, 2), 13.45)
    n_milk = f["N"]["surplus"] / (f["milk_kg"] / 1000)
    p_milk = f["P"]["surplus"] / (f["milk_kg"] / 1000)
    c.eq("N per Mg milk (feasible ≤ 8.8)", r(n_milk, 2), 7.69)
    c.eq("P per Mg milk (feasible ≤ 1.1)", r(p_milk, 2), 2.70)
    c.eq("N per ha whole farm -> status", S([f["N"]["surplus_per_ha"]], nref), "yellow")
    c.eq("P per ha / feasible upper bound", r(f["P"]["surplus_per_ha"] / pref["value"], 1), 3.5)
    tillable = f["fields_ha"] + f["pasture_ha"] + f["f5_ha"]
    c.eq("per tillable ha N / P", (r(f["N"]["surplus"] / tillable, 1), r(f["P"]["surplus"] / tillable, 1)), (159.7, 55.9))
    c.true("conclusion robust to denominator (both above feasible)",
           f["N"]["surplus"] / tillable > nref["value"] and f["P"]["surplus"] / f["farm_ha"] > pref["value"])


@test("T19", "E. coli event sample against the verified references")
def t19(c):
    S = lambda v, ref: pc.screening_status(v, ref)["status"]
    c.eq("410 vs EPA 2012 STV 410 (equal, not above)", S([SIM2["ECOLI_EVENT"]], pc.row(NYUS, "NYUS-12")), "green-watch")
    c.eq("410 vs superseded 235 -> yellow at most, row marked superseded", S([SIM2["ECOLI_EVENT"]], pc.row(NYUS, "NYUS-13")), "yellow")
    c.eq("legal status of the 235 row", pc.row(NYUS, "NYUS-13")["legal_status"], "superseded")
    tp = SIM2["STREAM_TP"]
    c.eq("stream stays yellow on phosphorus (orientation)", S([sum(tp) / len(tp)], pc.row(NYUS, "NYUS-19")), "yellow")


@test("T20", "Package structure; v0.1.0 untouched")
def t20(c):
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    c.true("frontmatter version 0.3.6", re.search(r"^version: 0\.3\.6$", skill, flags=re.M) is not None)
    refs = set(re.findall(r"`((?:references|scripts|assets|tests|examples|core)/[^`]+)`", skill)) - {"tests/RUN-LOG.md"}  # output of this run
    def present(p):
        p = p.split(" ")[0]
        return any(ROOT.glob(p)) if "*" in p else (ROOT / p).exists()
    missing = [p for p in refs if not present(p)]
    c.true(f"all {len(refs)} paths named in SKILL.md exist", not missing, str(missing) if missing else "")
    c.true("CHANGELOG.md present", (ROOT / "CHANGELOG.md").exists())
    v01 = hashlib.sha256((ROOT / "archive/v0.1.0/SKILL.md").read_bytes()).hexdigest()
    c.true("v0.1.0 SKILL.md unchanged", v01 == INTAKE_SHA256["archive/v0.1.0/SKILL.md"])


# ============================================ v0.3: farm catalogue, NASA, core
import indicator_select as isel  # noqa: E402

CATALOGUE = isel.load_catalogue(ROOT / "core/indicators/farm-indicators.psv")
LAYER = json.loads((ROOT / "core/remote-sensing/nasa-layer.json").read_text(encoding="utf-8"))
PROFILE = json.loads((ROOT / "tests/fixtures/sim_farm_profile.json").read_text(encoding="utf-8"))
MEASURED = {k: v for k, v in json.loads((ROOT / "tests/fixtures/sim_measured.json").read_text(encoding="utf-8")).items() if not k.startswith("_")}
OBJECTS = {k: v for k, v in json.loads((ROOT / "tests/fixtures/sim_objects.json").read_text(encoding="utf-8")).items() if not k.startswith("_")}
BYID = {r["id"]: r for r in CATALOGUE}
# Eurostat agri-environmental indicators (KS-RA-11-022, Table 3.1.1): 28 AEIs, 32 with sub-indicators
AEI = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10.1", "10.2", "11.1", "11.2", "11.3", "12", "13", "14", "15", "16",
       "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27.1", "27.2", "28"]
AEI_SCOPED_OUT = {"14": "risk of farmland abandonment is a regional indicator, not a property of one farm"}
# Welfare Quality: 4 principles, 12 criteria (as listed by NMBU, Welfare Quality Norway)
WQ = ["absence of prolonged hunger", "absence of prolonged thirst", "comfort around resting", "thermal comfort",
      "ease of movement", "absence of injuries", "absence of disease", "absence of pain induced by management procedures",
      "expression of social behaviours", "expression of other behaviours", "good human-animal relationship", "positive emotional state"]


@test("T21", "Farm catalogue: schema, vocabulary, links to packs, NASA layer and twin")
def t21(c):
    ids = [r["id"] for r in CATALOGUE]
    c.eq("indicators in the catalogue", len(ids), 113)
    c.true("IDs unique", len(ids) == len(set(ids)))
    c.eq("blocks", sorted({r["block"] for r in CATALOGUE}), ["A", "E", "L", "X"])
    c.true("tiers valid", all(r["tier"] in ("core", "conditional", "research") for r in CATALOGUE))
    c.true("cost classes valid", all(r["cost"] in isel.COST_ORDER for r in CATALOGUE))
    c.true("every conditional row has a trigger", all(r["trigger"] for r in CATALOGUE if r["tier"] == "conditional"))
    rows = {x["id"] for x in NYUS["rows"] + EU["rows"]}
    bad = [(r["id"], a) for r in CATALOGUE for a in r["anchor"] if a not in rows]
    c.true("every anchor is an existing threshold row", not bad, str(bad) if bad else f"{sum(bool(r['anchor']) for r in CATALOGUE)} anchored rows")
    prods = {p["id"] for p in LAYER["products"]}
    c.true("every NASA product exists in the layer", all(p in prods for r in CATALOGUE for p in r["nasa"]))
    c.true("every twin reference is a section number or 'new'", all(t == "new" or t.isdigit() for r in CATALOGUE for t in r["twin"]))
    c.true("every row has a method and a decision it supports", all(r["method"] and r["decision"] for r in CATALOGUE))
    rc = subprocess.run([sys.executable, str(ROOT / "scripts/render_catalogue.py"), "--check"], capture_output=True, text=True).returncode
    c.true("rendered catalogue, CSV, JSON, crosswalk and worked selection are in sync", rc == 0)


@test("T22", "Completeness against the Eurostat agri-environmental indicators (external benchmark)")
def t22(c):
    covered = {a for r in CATALOGUE for a in r["aei"]}
    missing = [a for a in AEI if a not in covered and a not in AEI_SCOPED_OUT]
    c.eq("AEIs (incl. sub-indicators)", len(AEI), 32)
    c.true("every AEI mapped or explicitly scoped out", not missing, f"missing: {missing}" if missing else "")
    c.eq("scoped out (with reason)", sorted(AEI_SCOPED_OUT), ["14"])
    c.true("no unknown AEI codes in the catalogue", covered <= set(AEI))


@test("T23", "Completeness against the 12 Welfare Quality criteria")
def t23(c):
    got = {r["wq"] for r in CATALOGUE if r["wq"] != "-"}
    missing = [w for w in WQ if w not in got]
    c.true("all 12 criteria served by at least one livestock indicator", not missing, f"missing: {missing}" if missing else "12/12")
    c.true("welfare rows sit in the livestock block", all(r["block"] == "L" for r in CATALOGUE if r["wq"] != "-"))
    tc = [r for r in CATALOGUE if r["wq"] == "thermal comfort"]
    c.true("thermal comfort: the protocol has no measure — the THI row says it is the skill's proxy",
           tc and all("no measure for thermal comfort" in r["method"] and "proxy" in r["method"] for r in tc))


@test("T24", "Her three blocks are complete: agronomy, livestock, farm ecosystem")
def t24(c):
    need = {"A": ["Soil chemistry", "Soil fertility", "Soil physics", "Soil biology", "Erosion", "Contaminants in soil", "Plant health",
                  "Inputs", "Crops and forage", "Water use", "Vegetation", "Energy", "Product safety"],
            "L": ["Herd", "Feed", "Feed safety", "Water for animals", "Welfare — feeding", "Welfare — housing", "Welfare — health",
                  "Welfare — behaviour", "Health", "Milk quality", "Antimicrobials", "Biosecurity", "Zoonoses", "Manure", "Emissions", "Product safety"],
            "E": ["Drinking water", "Surface water", "Standing water", "Nutrients", "Habitat", "Biodiversity", "Climate", "Land", "Water", "Management"],
            "X": ["Contaminant sources", "AMR", "Governance"]}
    for b, groups in need.items():
        have = {r["group"] for r in CATALOGUE if r["block"] == b}
        miss = [g for g in groups if g not in have]
        c.true(f"block {b}: {len(groups)} required groups present", not miss, f"missing {miss}" if miss else f"{sum(1 for r in CATALOGUE if r['block'] == b)} indicators")


@test("T25", "Selection on the synthetic farm")
def t25(c):
    ch, sk = isel.select(PROFILE, CATALOGUE)
    sel = {r["id"]: r for r in ch}
    for i in ["L-18", "L-19", "X-01", "A-15", "A-16", "E-01", "L-08", "L-40", "E-06", "L-13"]:
        c.true(f"{i} selected ({BYID[i]['indicator']})", i in sel)
    skipped = {r["id"]: r["reason"] for r in sk}
    c.true("L-41 raw-milk pathogens not selected: no raw-milk sales", skipped.get("L-41", "").startswith("trigger absent"))
    c.true("research rows not selected unless requested", all(r["id"] in skipped for r in CATALOGUE if r["tier"] == "research"))
    c.true("every unselected indicator carries a reason", all(r["reason"] for r in sk))
    c.true("A-26 irrigation selected only to confirm (profile: unknown)", sel.get("A-26", {}).get("confirm") is True)
    c.eq("selected / confirm / not selected", (len(ch), sum(r["confirm"] for r in ch), len(sk)), (98, 16, 15))
    req = isel.select(PROFILE, CATALOGUE, research_ids=("E-19",))[0]
    c.true("a requested research indicator is selected", any(r["id"] == "E-19" for r in req))


@test("T26", "Gap registry: complete vs partial, value-of-information order")
def t26(c):
    ch, _ = isel.select(PROFILE, CATALOGUE)
    gaps = isel.gap_registry(ch, MEASURED)
    gid = [g["id"] for g in gaps]
    complete = [k for k, v in MEASURED.items() if not v.get("partial")]
    partial = [k for k, v in MEASURED.items() if v.get("partial")]
    c.true("complete measurements are not gaps", not set(complete) & set(gid))
    c.true("partial measurements stay as 'partial' gaps", all(any(g["id"] == p and g["gap"].startswith("partial") for g in gaps) for p in partial))
    c.eq("first row: farm consent (nothing starts without it)", gid[0] if gid else None, "X-07")
    k = sum(1 for g in gaps if g["confirm"])
    c.true("confirmation of unknown facts comes right after consent", all(g["confirm"] for g in gaps[1:1 + k]) and not any(g["confirm"] for g in gaps[1 + k:]),
           f"rows 2–{1 + k}")
    c.true("each confirm row names the facts to confirm (only the unknown ones)",
           all(g["closing"].startswith("confirm with the farm") and "crops" not in g["closing"] for g in gaps if g["confirm"]))
    rest = [g for g in gaps if g["rank"] == 2]
    order = [isel.COST_ORDER[g["cost"]] for g in rest if g["panel"] in ("records", "nasa")]
    c.true("desk records before NASA request before field and laboratory work",
           order == sorted(order) and all(g["panel"] in ("records", "nasa") for g in rest[:len(order)]))
    soil = [i for i, g in enumerate(rest) if g["panel"] == "soil"]
    c.true("a laboratory panel stays together (compaction travels with the soil sampling visit)", soil == list(range(soil[0], soil[0] + len(soil))) and "A-08" in [rest[i]["id"] for i in soil])
    seq = []
    for g in rest:
        if g["cost"] == "lab" or g["panel"] in ("well", "milk", "feed", "soil", "pond"):
            if g["panel"] not in seq:
                seq.append(g["panel"])
    want = [x for x in ("well", "milk", "feed", "soil", "pond") if x in seq]
    c.true("laboratory panels follow the sampling-plan priority in SKILL.md: well → product → feed → soil → standing water",
           [x for x in seq if x in want] == want, " → ".join(seq))
    first = {}
    for g in rest:
        first.setdefault(g["panel"], []).append(g["gap"].startswith("partial"))
    c.true("inside a panel, partly measured indicators come first (complete what was started)",
           all(v == sorted(v, reverse=True) for v in first.values()))
    plan = isel.work_plan(gaps, ch)
    conf = next(a for a in plan if a["action"] == "confirm")
    c.true(f"{len(gaps)} gaps collapse into ≤ 15 actions; {len(conf['indicators'])} confirm rows wait on {len(conf['facts'])} facts",
           len(plan) <= 15 and len(conf["facts"]) < len(conf["indicators"]), f"{len(plan)} actions")


@test("T27", "Economy: laboratory work grouped into sampling panels")
def t27(c):
    ch, _ = isel.select(PROFILE, CATALOGUE)
    has = "panel" in CATALOGUE[0]
    c.true("catalogue has a sampling-panel column", has)
    c.true("desk rows → records interview, remote rows → NASA request, field and lab rows → a named visit or panel",
           all((r["cost"] == "desk") == (r["panel"] == "records") and (r["cost"] == "remote") == (r["panel"] == "nasa") for r in CATALOGUE))
    if has:
        lab = [r for r in ch if r["cost"] == "lab" and not r["confirm"]]
        c.true("every selected laboratory indicator belongs to a panel", all(r["panel"] not in ("", "-") for r in lab))
        panels = isel.lab_panels(ch)
        c.true("lab panels for the synthetic farm ≤ 10 (one visit can serve many indicators)", len(panels) <= 10, f"{len(panels)}: {', '.join(panels)}")


@test("T28", "Crosswalk to the Ecosystem Digital Twin")
def t28(c):
    new = [r for r in CATALOGUE if r["twin"] == ["new"]]
    c.eq("indicators the twin does not cover", len(new), 22)
    c.true("all of them in the livestock block (the twin's §23 excludes animal health, disease, feeding)", all(r["block"] == "L" for r in new))
    c.true("every other indicator points to at least one twin section", all(r["twin"] for r in CATALOGUE))
    cw = (ROOT / "core/crosswalk-twin.md").read_text(encoding="utf-8")
    c.true("crosswalk names §23 and the proposal", "| 23 |" in cw and "proposed extension" in cw)
    core = (ROOT / "core/README.md").read_text(encoding="utf-8")
    c.true("core README states that the twin was not changed", "Nothing has been changed in the Ecosystem Digital Twin repository" in core)
    c.true("handover mapped to the twin's v2.8 stages (Object Passport, Data Inventory & QC, [НЕТ ДАННЫХ] register, public status line)",
           all(k in core for k in ("v2.8", "Stage 1 — Object Passport (Phase 0)", "Stage 2 — Data Inventory & QC (Phase 1)", "[НЕТ ДАННЫХ]", "public status line", "Tier S")))


@test("T29", "New livestock and feed anchors: values and verification marks")
def t29(c):
    exp = {"NYUS-22": 750000, "NYUS-23": 0.5, "NYUS-24": 20, "NYUS-25": 100000, "NYUS-26": 30000,
           "EU-26": 400000, "EU-27": 100000, "EU-28": 0.050, "EU-29": 5, "EU-30": 0.07}
    for k, v in exp.items():
        r_ = pc.row(NYUS if k.startswith("NYUS") else EU, k)
        c.true(f"{k} {r_['analyte']} = {v} {r_['unit']} [{r_['verified']}]", r_["value"] == v)
    c.true("secondary-only rows are marked provisional (EU-28, EU-30; NY milk rows read via a reproduction of 1 NYCRR §2.8)",
           all(pc.row(EU, k)["verified"] == "verified-secondary" for k in ("EU-28", "EU-30"))
           and all(pc.row(NYUS, k)["verified"] == "verified-secondary" for k in ("NYUS-22", "NYUS-25", "NYUS-26")))
    c.eq("EU-29 confirmed in Directive 2002/32/EC Annex I (consolidated text)", pc.row(EU, "EU-29")["verified"], "verified")
    c.true("bulk-tank plate count anchored for NY (Grade A producer, raw-milk sales) and the EU", BYID["L-19"]["anchor"] == ["NYUS-25", "NYUS-26", "EU-27"])
    c.true("FDA action levels classed as guidance (colour capped at yellow)", all(pc.row(NYUS, k)["legal_status"] == "guidance" for k in ("NYUS-23", "NYUS-24")))
    S = lambda v, ref: pc.screening_status(v, ref)["status"]
    c.eq("SCC 450 000 vs EU 400 000, single month", S([450000], pc.row(EU, "EU-26")), "yellow")
    c.eq("SCC 450 000 vs EU rule met (rolling 3-month geometric mean above)", pc.screening_status([450000], pc.row(EU, "EU-26"), "exceeded")["status"], "red")
    c.eq("SCC 450 000 vs US PMO 750 000", S([450000], pc.row(NYUS, "NYUS-22")), "green")


@test("T30", "NASA layer and the request for the data agent")
def t30(c):
    c.true("every product row carries a check date and verification mark", all(p["checked"] and p["verified"] for p in LAYER["products"]))
    c.eq("products verified against NASA sources", sorted(p["id"] for p in LAYER["products"] if p["verified"] == "verified"),
         ["DSWx", "ECOSTRESS", "HLS", "IMERG", "POWER", "SMAP"])
    ch, _ = isel.select(PROFILE, CATALOGUE)
    req = isel.nasa_request(ch, LAYER, OBJECTS, aoi={"coordinates": "none — synthetic"}, period={})
    got = {p["id"] for p in req["products"]}
    c.true("request includes HLS, SMAP, IMERG, POWER", {"HLS", "SMAP", "IMERG", "POWER"} <= got, str(sorted(got)))
    ex = {(e["indicator"], e["product"]) for e in req["excluded"]}
    c.true("0.2 ha pond excluded from DSWx (pixel fit)", ("E-08", "DSWx") in ex)
    c.true("30 m buffer strip excluded from HLS (pixel fit)", ("E-14", "HLS") in ex)
    c.eq("smallest field F3 (12 acres) pure 30 m pixels", isel.pure_pixels(30, area_m2=48562), 36)
    c.true("request addressed to the data agent and states the remote = proxy rule", "data agent" in req["to"].lower() and "never a status colour alone" in req["rule"])
    by = {p["id"]: p for p in req["products"]}
    c.true("indicators that depend on an unconfirmed fact are flagged (flooding E-23 waits on 'floodplain', irrigation A-26 on 'irrigation')",
           "E-23" in by["DSWx"]["awaiting_confirmation"] and "A-26" in by["ECOSTRESS"]["awaiting_confirmation"])
    c.true("confirmed indicators are not flagged (NDVI A-28 on HLS)", "A-28" in by["HLS"]["indicators"] and "A-28" not in by["HLS"]["awaiting_confirmation"])
    c.true("every requested product carries its verification mark; unverified ones are named",
           all("verified" in p for p in req["products"]) and [p["id"] for p in req["products"] if p["verified"] != "verified"] == ["LANDSAT"])
    c.true("request is conditional on the farm consent record", "X-07" in req["consent"])
    c.true("delivery asks for what the twin's Phase 1 onboarding needs (version, date, quality mask, access date, licence)",
           all(k in req["deliver"] for k in ("product version", "quality mask", "access date", "licence")))


@test("T31", "Satellite drought signal drives triggers")
def t31(c):
    c.true("two months at ≤ 20th percentile → drought year", isel.drought_flag([15, 18, 40, 60]) is True)
    c.true("one month only → not a drought year", isel.drought_flag([25, 30, 15, 50]) is False)
    base = {"dairy": True, "livestock": True, "forage": True, "crops": True, "purchased_grain": False, "cottonseed": False,
            "biosolids": False, "manure": False, "sells_milk": True}
    on = {r["id"] for r in isel.select({**base, "drought_year": True}, CATALOGUE)[0]}
    off = {r["id"] for r in isel.select({**base, "drought_year": False}, CATALOGUE)[0]}
    c.true("drought year opens aflatoxin in feed (L-06), aflatoxin M1 (L-39), forage nitrate (A-19)", {"L-06", "L-39", "A-19"} <= on)
    c.true("without drought (and no other trigger) they stay closed", not ({"L-06", "L-39", "A-19"} & off))



@test("T32", "DEC soil guidance: F1 PFOS above the unrestricted value (new 2026-11-05)")
def t32(c):
    ref = pc.row(NYUS, "NYUS-28")   # PFOS, soil unrestricted use guidance 0.88 µg/kg (DEC, Apr 2023)
    f1 = SIM1["soil_0_20cm_ug_kg"]["F1"]["PFOS"]
    st = pc.screening_status([f1], ref)
    c.eq("F1 PFOS value from fixture", f1, 0.90)
    c.eq("F1 0.90 vs 0.88 (guidance) -> yellow", st["status"], "yellow")
    ref_pg = pc.row(NYUS, "NYUS-34")   # PFOS, protection of groundwater 1.0 µg/kg
    st2 = pc.screening_status([f1], ref_pg)
    c.eq("F1 0.90 vs 1.0 (groundwater protection) -> green-watch (90 %)", st2["status"], "green-watch")


@test("T33", "DEC groundwater guidance: well PFOS above the Class GA value (new 2026-11-05)")
def t33(c):
    ref = pc.row(NYUS, "NYUS-32")   # PFOS, Class GA groundwater guidance 2.7 ng/L (TOGS 1.1.1, 2023)
    well = SIM1["well_ng_l"]["PFOS"]
    st = pc.screening_status([well], ref)
    c.eq("well PFOS value from fixture", well, 6.5)
    c.true("well 6.5 exceeds the GA guidance value 2.7", well > float(ref["value"]))
    c.eq("exceedance of a guidance value -> yellow (screening cap)", st["status"], "yellow")


@test("T34", "DEC soil guidance: F2 PFOS below the 75 % watch fraction (new 2026-11-05)")
def t34(c):
    ref = pc.row(NYUS, "NYUS-28")   # PFOS, soil unrestricted use guidance 0.88 µg/kg
    f2 = SIM1["soil_0_20cm_ug_kg"]["F2"]["PFOS"]
    st = pc.screening_status([f2], ref)
    c.eq("F2 PFOS value from fixture", f2, 0.65)
    c.true("F2 share of the guidance value < 75 %", f2 / float(ref["value"]) < 0.75)
    c.eq("F2 0.65 vs 0.88 -> green", st["status"], "green")


# =================================================================== protocol
def main() -> int:
    passed = sum(1 for *_, ok, _ in RESULTS if ok)
    head = [f"# Test run — farm-environmental-passport v0.3.6", "",
            f"Date: {TODAY.isoformat()}  ·  Python {sys.version.split()[0]}  ·  runner: tests/run_tests.py", "",
            f"**Result: {passed} / {len(RESULTS)} PASS**" + ("" if passed == len(RESULTS) else " — FAILURES BELOW"), "",
            "| Test | Title | Result |", "|---|---|---|"]
    head += [f"| {tid} | {title} | {'PASS' if ok else 'FAIL'} |" for tid, title, ok, _ in RESULTS]
    body = ["", "## Detail", ""]
    for tid, title, ok, lines in RESULTS:
        body += [f"### {tid} — {title}: {'PASS' if ok else 'FAIL'}", "", "```"] + lines + ["```", ""]
    body += ["Behavioural tests B1–B5 (tests/TESTS.md) are not executable here: pending first live use."]
    text = "\n".join(head + body) + "\n"
    (ROOT / "tests/RUN-LOG.md").write_text(text, encoding="utf-8")
    for tid, title, ok, lines in RESULTS:
        print(f"{'PASS' if ok else 'FAIL'}  {tid}  {title}")
        if not ok:
            print("\n".join("      " + l for l in lines))
    print(f"\n{passed}/{len(RESULTS)} PASS — protocol written to tests/RUN-LOG.md")
    return 0 if passed == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
