#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Farm Environmental Passport — from an input folder to the answer card (since v0.3.8).

One command takes a farm's input folder (farm.json + measurements.csv, format in
references/input-format.md), checks it, and writes two files beside it:

  passport.json    the machine-readable passport: status per object with the reference
                   rows that set it, flags, the dose block, indicator selection, work plan
                   and gap registry, and the run record (skill version, threshold pack and
                   dates, sha256 of every input and core file)
  answer-card.md   the farm's answer card, rendered from passport.json — it changes no number

Every number comes from scripts/passport_calc.py and scripts/indicator_select.py; the
statuses follow references/status-rules.md. With no arguments it runs the synthetic
farm of the worked examples.

Usage:
  python3 scripts/demo.py                                   # examples/synthetic-farm
  python3 scripts/demo.py --farm FOLDER [--out FOLDER] [--date YYYY-MM-DD]
  python3 scripts/demo.py --check                           # outputs equal the committed files?
Exit 0 = written (or in sync), 1 = input errors (nothing written) or out of sync.

Standard library only. License: Apache-2.0 (code).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import passport_calc as pc       # noqa: E402
import indicator_select as isel   # noqa: E402
import validate_input as vi       # noqa: E402

PASSPORT_FORMAT = "farm-environmental-passport/passport@1"
DEFAULT_FARM = ROOT / "examples" / "synthetic-farm"
LEGAL_WEIGHT = {"in_force": 6, "future": 5, "guidance": 4, "proposed": 3, "orientation": 2, "superseded": 1, "requirement": 0}
LEGAL_WORD = {"in_force": "in force", "future": "future", "guidance": "guidance", "proposed": "proposed",
              "orientation": "orientation", "superseded": "superseded", "requirement": "requirement"}
ORDER = {pc.GREY: -1, pc.GREEN: 0, pc.WATCH: 1, pc.YELLOW: 2, pc.RED: 3}
CORE_FILES = ["core/thresholds/ny-us.json", "core/screening-map.json", "core/indicators/farm-indicators.psv",
              "core/remote-sensing/nasa-layer.json"]


def hr(x: float, nd: int = 2) -> str:
    """Round half-up on the decimal representation, as the worked examples print numbers."""
    return str(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def num(x: float) -> str:
    return f"{x:g}"


def pct(x: float) -> str:
    return f"{hr(100 * x, 0)} %"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def skill_version() -> str:
    m = re.search(r"^version: (\S+)$", (ROOT / "SKILL.md").read_text(encoding="utf-8"), flags=re.M)
    return m.group(1) if m else "unknown"


def worst(statuses):
    known = [s for s in statuses if s != pc.GREY]
    return max(known, key=lambda s: ORDER[s]) if known else pc.GREY


# --------------------------------------------------------------- statuses
def reference_status(rows: list, ref: dict, entry: dict) -> dict:
    """One parameter of one object against one reference row: bounds for censored results,
    the source's own single-result rule where the map says so (status-rules §3, line 4)."""
    rows = sorted(rows, key=lambda r: r.order_key)
    lo = [0.0 if r.censored else r.value for r in rows]
    hi = [r.rl if r.censored else r.value for r in rows]
    thr = float(ref["value"])

    def one(series):
        det = "exceeded" if entry.get("single_result_acts") and any(v > thr for v in series) else None
        return pc.screening_status(series, ref, det)

    s_lo, s_hi = one(lo), one(hi)
    st = worst([s_lo["status"], s_hi["status"]])
    return {"row": ref["id"], "status": st, "why": (s_hi if st == s_hi["status"] else s_lo)["why"],
            "max": max(hi), "fraction": max(hi) / thr, "events": len(rows),
            "depends_on_censoring": s_lo["status"] != s_hi["status"],
            "fit": entry.get("fit", "object"), "single_result_acts": bool(entry.get("single_result_acts"))}


def ref_line(ref: dict) -> dict:
    return {"row": ref["id"], "value": ref["value"], "unit": ref["unit"], "legal_status": ref["legal_status"],
            "matrix": ref["matrix"], "analyte": ref["analyte"], "checked": ref["checked"], "verified": ref["verified"],
            "source": ref["source_org"]}


def rank(e: dict, status: str):
    """Which reference the card names first: for yellow and red the strongest legal weight; for green and
    green-watch the reference the value comes closest to."""
    if status in (pc.YELLOW, pc.RED):
        return (-LEGAL_WEIGHT[e["legal_status"]], -e["fraction"], e["row"])
    return (-e["fraction"], -LEGAL_WEIGHT[e["legal_status"]], e["row"])


def set_by(evals: list, status: str) -> list:
    """The reference rows at the object's status, in the order the card names them."""
    return sorted([e for e in evals if e["status"] == status], key=lambda e: rank(e, status))


def object_block(ob: dict, rows: list, smap: dict, packs: dict) -> dict:
    mspec = smap["matrices"][ob["matrix"]]
    measured = [r for r in rows if r.evidence == "measured"]
    usable = [r for r in measured if r.usable]
    evals, flags = [], []
    by_param: dict = {}
    for r in usable:
        by_param.setdefault(r.parameter, []).append(r)
    for par, rs in by_param.items():
        spec = mspec["parameters"].get(par)
        if not spec:
            continue
        for entry in spec["references"]:
            ref = packs[entry["row"]]
            if not isinstance(ref.get("value"), (int, float)):
                continue
            e = reference_status(rs, ref, entry)
            e.update(parameter=par, legal_status=ref["legal_status"], value=ref["value"], unit=ref["unit"])
            evals.append(e)
            if e["depends_on_censoring"]:
                flags.append({"kind": "depends on censored values",
                              "text": f"{par}: the status against {ref['id']} depends on censored values",
                              "closing": "a laboratory with a lower reporting limit"})
    status = worst([e["status"] for e in evals]) if evals else pc.GREY
    farm_evals = [e for e in evals if e["fit"] in ("object", "farmland")]
    farm_status = worst([e["status"] for e in farm_evals]) if farm_evals else pc.GREY
    # model against measurement: printed both ways, never smoothed (status-rules §1)
    for m in (r for r in rows if r.evidence == "modelled"):
        meas = [r for r in measured if r.parameter == m.parameter and not r.censored]
        for r in meas:
            inside = m.low <= r.value <= m.high
            flags.append({"kind": "model agrees" if inside else "model disagrees",
                          "text": f"{m.parameter} measured {num(r.value)} {r.unit} is {'inside' if inside else 'outside'} "
                                  f"the modelled range {num(m.low)}–{num(m.high)} {m.unit} ({m.source})",
                          "closing": "" if inside else "a repeat measurement and a check of the model's main uncertainty; "
                                                       "the disagreement stays a gap until one explains the other"})
    # a medium that varies by season, known from one event: variation unknown, a sustained exceedance cannot be shown
    if mspec.get("series") and any(e["events"] == 1 for e in evals):
        text = "one sampling event — seasonal variation unknown"
        if status in (pc.WATCH, pc.YELLOW, pc.RED):
            text += ", and whether an exceedance is sustained cannot be shown"
        flags.append({"kind": "single event", "text": text, "closing": mspec["series"]["closing"]})
    # analytes of the EFSA sum that were never analysed in this object are gaps, not zeros
    efsa = smap["dose"]["efsa_four"]
    pfas = {r.parameter for r in measured if r.parameter in efsa}
    if pfas:
        miss = [a for a in efsa if a not in pfas]
        if miss:
            flags.append({"kind": "partial panel", "text": f"{', '.join(miss)} not analysed (EFSA four incomplete)",
                          "closing": "re-analyse the existing extract or archived sample for the missing analytes — no new field trip "
                                     "(references/methods.md §3, item 1)"})
    for r in measured:
        if not r.usable:
            flags.append({"kind": "method not valid", "text": f"{r.parameter} by '{r.method}' is not validated for this matrix — printed grey",
                          "closing": "re-analysis by a method validated for the matrix (references/methods.md)"})
    if not measured:
        meths = sorted({m for p in mspec["parameters"].values() for m in p["methods"]})
        flags.append({"kind": "never measured", "text": "no measured value — not assessed",
                      "closing": "a first sample" + (f" by {' or '.join(meths)}" if meths else "") + " (references/methods.md)"})
    top = set_by(evals, status)
    return {
        "id": ob["id"], "label": ob.get("label", ob["id"]), "matrix": ob["matrix"], "group": mspec.get("group"),
        "status": status, "status_farmland": farm_status,
        "set_by": [{"row": e["row"], "parameter": e["parameter"], "status": e["status"], "max": e["max"],
                    "fraction": round(e["fraction"], 6), "fit": e["fit"]} for e in top],
        "references": [{k: (round(v, 6) if isinstance(v, float) else v) for k, v in e.items()} for e in evals],
        "measurements": [{"parameter": r.parameter, "sampled": r.sampled, "value": r.value, "censored": r.censored,
                          "reporting_limit": r.rl, "unit": r.unit, "unit_reported": r.unit_in, "method": r.method,
                          "laboratory": r.laboratory, "evidence": r.evidence, "low": r.low, "high": r.high,
                          "source": r.source, "line": r.line, "coloured": r.usable} for r in rows],
        "flags": flags,
        "geometry": ob.get("geometry"),
    }


def group_block(name: str, objs: list) -> dict:
    """Summary of a group of fields (status-rules §3a): the summary takes the worst status against
    references written for farmland; a field whose own status is worse because of a reference
    written for another land use is printed beside the summary, by name."""
    summary = worst([o["status_farmland"] for o in objs])
    flagged = [{"object": o["id"], "status": o["status"], "set_by": o["set_by"]}
               for o in objs if ORDER[o["status"]] > ORDER[summary]]
    evals = [dict(e, object=o["id"]) for o in objs for e in o["references"] if e["fit"] in ("object", "farmland")]
    top = sorted([e for e in evals if e["status"] == summary], key=lambda e: rank(e, summary))[:1]
    return {"group": name, "objects": [o["id"] for o in objs], "status": summary,
            "set_by": [{"row": e["row"], "parameter": e["parameter"], "object": e["object"], "max": e["max"],
                        "fraction": round(e["fraction"], 6)} for e in top],
            "fields_flagged": flagged}


# ------------------------------------------------------------------ dose
def dose_block(farm: dict, rep, smap: dict, packs: dict) -> dict | None:
    efsa = smap["dose"]["efsa_four"]
    media = {}
    for ob in rep.objects.values():
        role = ob.get("dose_role")
        if not role:
            continue
        res = [pc.Result(r.parameter, None if r.censored else r.value, r.unit, censored=r.censored, rl=r.rl)
               for r in rep.rows if r.object == ob["id"] and r.evidence == "measured" and r.usable and r.parameter in efsa]
        lo, hi = pc.sum_bounds(res)
        media[role] = {"object": ob["id"], "analytes": sorted({x.analyte for x in res}, key=efsa.index),
                       "sum_lower": lo, "sum_upper": hi, "unit": "ng/L"}
    if not media:
        return None
    measured = set().union(*(set(m["analytes"]) for m in media.values()))
    n, missing = pc.efsa_sum_completeness(measured)
    twi = packs[smap["dose"]["twi_row"]]
    t = float(twi["value"])
    if not measured:
        return {"computed": False, "twi": ref_line(twi),
                "why": "no EFSA PFAS measured in the drinking-water source or the product: no dose is computed (a gap, not a zero)"}
    blank = {"sum_lower": 0.0, "sum_upper": 0.0, "analytes": []}
    water = media.get("drinking_water", blank)
    milk = media.get("product", blank)
    scen = []
    for s in farm.get("dose_scenarios", []):
        cases = []
        for c in s["cases"]:
            w_l, m_l = c.get("water_l_day", 0.0), c.get("milk_l_day", 0.0)
            d_lo = pc.weekly_dose(water["sum_lower"], w_l, s["bw_kg"]) + pc.weekly_dose(milk["sum_lower"], m_l, s["bw_kg"])
            d_hi = pc.weekly_dose(water["sum_upper"], w_l, s["bw_kg"]) + pc.weekly_dose(milk["sum_upper"], m_l, s["bw_kg"])
            # a medium that enters the case but was never measured is left out and named — never counted as zero
            excl = [name for name, med, l in (("well water", water, w_l), ("product", milk, m_l)) if l > 0 and not med["analytes"]]
            if w_l + m_l == 0:
                cases.append({"label": c["label"], "water_l_day": 0.0, "milk_l_day": 0.0, "dose": None,
                              "why": "no intake given"})
                continue
            cases.append({"label": c["label"], "water_l_day": w_l, "milk_l_day": m_l,
                          "dose": round(d_hi, 6), "dose_censored_lower": round(d_lo, 6), "share_of_twi": round(d_hi / t, 6),
                          "not_included": excl})
        item = {"role": s["role"], "label": s["label"], "bw_kg": s["bw_kg"], "source": s.get("source", ""), "cases": cases}
        if s.get("break_even") and not milk["analytes"]:
            item["break_even_note"] = "break-even intake not computed: the product was never measured"
        if s.get("break_even") and milk["sum_upper"] > 0:
            item["break_even_milk_l_day"] = [
                {"case": c["label"], "value": round(pc.break_even_intake(t - pc.weekly_dose(water["sum_upper"], c.get("water_l_day", 0.0), s["bw_kg"]),
                                                                         milk["sum_upper"], s["bw_kg"]), 6)}
                for c in s["cases"]]
        scen.append(item)
    return {"computed": True, "unit": "ng/kg body weight per week", "twi": ref_line(twi),
            "efsa_four": {"measured": n, "of": 4, "missing": missing, "lower_bound": n < 4},
            "media": media, "scenarios": scen,
            "rule": "weekly dose = concentration × daily intake × 7 ÷ body weight (scripts/passport_calc.py); an estimate with "
                    "uncertainty, not a health forecast; with fewer than four EFSA PFAS measured every dose is a lower bound"}


# ------------------------------------------------------- indicator selection
def selection_block(farm: dict) -> dict | None:
    prof = {k: v for k, v in (farm.get("profile") or {}).items() if not k.startswith("_")}
    if not prof:
        return None
    cat = isel.load_catalogue(ROOT / "core" / "indicators" / "farm-indicators.psv")
    layer = json.loads((ROOT / "core" / "remote-sensing" / "nasa-layer.json").read_text(encoding="utf-8"))
    cov = {k: v for k, v in (farm.get("coverage") or {}).items() if not k.startswith("_")}
    pix = {k: v for k, v in (farm.get("pixel_fit") or {}).items() if not k.startswith("_")}
    chosen, skipped = isel.select(prof, cat)
    gaps = isel.gap_registry(chosen, cov)
    plan = isel.work_plan(gaps, chosen)
    req = isel.nasa_request(chosen, layer, pix, aoi={"coordinates": "not given" if not farm.get("synthetic") else "none — synthetic farm"},
                            period={})
    facts = next((a["facts"] for a in plan if a["action"] == "confirm"), [])
    return {"catalogue": len(cat), "selected": len(chosen), "to_confirm": sum(1 for c in chosen if c["confirm"]),
            "left_out": [{"id": s["id"], "reason": s["reason"]} for s in skipped],
            "facts_to_confirm": facts,
            "work_plan": [{"action": a["action"], "cost": a["cost"], "indicators": a["indicators"], "facts": a["facts"]} for a in plan],
            "lab_panels": isel.lab_panels(chosen),
            "gap_registry": [{k: g[k] for k in ("id", "indicator", "panel", "cost", "gap", "closing")} for g in gaps],
            "nasa_request": {"products": [p["id"] for p in req["products"]],
                             "excluded": [{"indicator": e["indicator"], "product": e["product"], "reason": e["reason"]} for e in req["excluded"]],
                             "rule": req["rule"], "consent": req["consent"]}}


# --------------------------------------------------------------- passport
def build(farm_dir: Path, today: date) -> tuple[dict | None, object]:
    smap = vi.load_map()
    packs = vi.load_pack_rows(smap)
    rep = vi.validate(farm_dir, today, smap)
    if rep.errors:
        return None, rep
    farm = rep.farm
    pack_meta = json.loads((ROOT / "core" / "thresholds" / "ny-us.json").read_text(encoding="utf-8"))
    objects = [object_block(ob, [r for r in rep.rows if r.object == ob["id"]], smap, packs) for ob in farm["objects"]]
    groups = {}
    for o in objects:
        if o["group"]:
            groups.setdefault(o["group"], []).append(o)
    used = sorted({e["row"] for o in objects for e in o["references"]} | {smap["dose"]["twi_row"]},
                  key=lambda x: int(x.split("-")[1]))
    stale = pc.stale_rows({"rows": [packs[x] for x in used]}, today, pack_meta["max_age_days"])
    shown = vi.merged(rep.messages)
    passport = {
        "passport_format": PASSPORT_FORMAT,
        "synthetic": farm["synthetic"],
        "farm": {"farm_id": farm["farm_id"], "name": farm.get("name", ""), "jurisdiction": farm["jurisdiction"],
                 "consent": farm.get("consent")},
        "objects": objects,
        "groups": [group_block(k, v) for k, v in groups.items()],
        "dose": dose_block(farm, rep, smap, packs),
        "indicators": selection_block(farm),
        "references_used": [ref_line(packs[x]) for x in used],
        "limits": "Screening and expert opinion — not a compliance determination, a laboratory report or medical advice. "
                  "Only measured values carry a colour; red only for a sustained exceedance of an in-force reference under its own rule.",
        "run_record": {
            "skill": "farm-environmental-passport", "skill_version": skill_version(), "run_date": today.isoformat(),
            "command": f"python3 scripts/demo.py --farm {rel(farm_dir)} --date {today.isoformat()}",
            "python": sys.version.split()[0],
            "threshold_pack": {"pack": pack_meta["pack"], "version": pack_meta["version"], "max_age_days": pack_meta["max_age_days"]},
            "screening_map": {"version": smap["version"]},
            "rows_used": [{"row": x, "checked": packs[x]["checked"], "verified": packs[x]["verified"]} for x in used],
            "stale_rows": stale,
            "inputs": [{"path": rel(farm_dir / f), "sha256": sha256(farm_dir / f)} for f in ("farm.json", "measurements.csv")],
            "core": [{"path": f, "sha256": sha256(ROOT / f)} for f in CORE_FILES],
            "checks": {"errors": 0, "warnings": [{"code": m.code, "where": m.place, "text": m.text} for m in shown if m.level == "warning"]},
        },
    }
    return passport, rep


# ------------------------------------------------------------------- card
def unit_of(r: dict) -> str:
    return r["unit"].split(" (")[0]


def ref_text(row: str, packs: dict) -> str:
    r = packs[row]
    mark = {"verified-secondary": ", verified via a secondary source [provisional]", "not-verified": ", NOT verified"}.get(r["verified"], "")
    return f"{row} — {r['value']} {unit_of(r)}, {LEGAL_WORD[r['legal_status']]}, checked {r['checked']}{mark}"


def why_text(o: dict, packs: dict) -> str:
    """Status-rules §6 wording: the value, its share of the reference that set the status, and — for a
    yellow or red object — the in-force reference it stays below, so both are on the card."""
    if o["status"] == pc.GREY:
        return "not assessed: no measured value that can carry a colour"
    shown = o["set_by"][: (1 if o["status"] in (pc.GREEN, pc.WATCH) else 3)]
    by_par: dict = {}
    for s in shown:
        by_par.setdefault((s["parameter"], s["max"]), []).append(s)
    parts = []
    for (par, mx), ss in by_par.items():
        unit = unit_of(packs[ss[0]["row"]])
        word = "above" if o["status"] in (pc.YELLOW, pc.RED) else "below"
        parts.append(f"{par} {num(mx)} {unit} — {word} " + ", ".join(f"{s['row']} ({pct(s['fraction'])})" for s in ss))
    if o["status"] in (pc.YELLOW, pc.RED):
        below = sorted((e for e in o["references"] if e["legal_status"] == "in_force" and e["status"] in (pc.GREEN, pc.WATCH)),
                       key=lambda e: (-e["fraction"], e["row"]))
        if below:
            parts.append("below the in-force " + " and ".join(f"{e['row']} ({e['parameter']}, {pct(e['fraction'])})" for e in below))
    tail = {pc.YELLOW: "; screening, not a compliance finding",
            pc.RED: "; sustained exceedance of an in-force reference under its own rule"}.get(o["status"], "")
    return "; ".join(parts) + tail


def short(ids: list, groups: dict) -> str:
    """Object ids for a flag line, in the farm's order; a whole group of fields is written as its range."""
    out, skip = [], set()
    for x in ids:
        if x in skip:
            continue
        g = next((m for m in groups.values() if x in m and len(m) > 1 and all(y in ids for y in m)), None)
        if g:
            out.append(f"{g[0]}–{g[-1]}")
            skip.update(g)
        else:
            out.append(x)
    return ", ".join(out)


def card(p: dict) -> str:
    packs = vi.load_pack_rows(vi.load_map())
    rr = p["run_record"]
    out = ["# Farm environmental passport — answer card", ""]
    if p["synthetic"]:
        out += ["> **SYNTHETIC FARM.** Every laboratory value is invented and labelled as such; the thresholds, the rules and "
                "the calculations are real. This card was generated by `scripts/demo.py` from the input folder named in the run "
                "record — it changes no number.", ""]
    c = p["farm"]["consent"] or {}
    consent = ("not applicable — synthetic farm" if p["synthetic"]
               else f"recorded {c.get('date')}, scope: {c.get('scope')}")
    out += [f"Farm: {p['farm']['farm_id']} — {p['farm']['name']}  ",
            f"Jurisdiction pack: {rr['threshold_pack']['pack']}, version {rr['threshold_pack']['version']} · "
            f"Skill {rr['skill_version']} · Run {rr['run_date']}  ",
            f"Consent: {consent}", "",
            "## Status by object", "",
            "| Object | Status | Reference that set it | Why |", "|---|---|---|---|"]
    grouped = {g["group"]: g for g in p["groups"]}
    done = set()
    for o in p["objects"]:
        g = o["group"]
        if g and g in grouped:
            if g in done:
                continue
            done.add(g)
            gb = grouped[g]
            members = [x for x in p["objects"] if x["group"] == g]
            names = f"fields {members[0]['id']}–{members[-1]['id']}" if len(members) > 1 else f"field {members[0]['id']}"
            st = gb["status"] + "".join(f"; {f['object']} {f['status']}" for f in gb["fields_flagged"])
            refs = "; ".join(ref_text(s["row"], packs) for s in gb["set_by"])
            why = [] if gb["status"] != pc.GREY else ["not assessed: no measured value that can carry a colour"]
            why += [f"all fields below the references written for farmland; closest: {s['parameter']} {num(s['max'])} "
                   f"{unit_of(packs[s['row']])} on {s['object']} — {pct(s['fraction'])} of {s['row']}" for s in gb["set_by"]]
            for f in gb["fields_flagged"]:
                fb = f["set_by"][0]
                r = packs[fb["row"]]
                why.append(f"{f['object']}: {fb['parameter']} {num(fb['max'])} {unit_of(r)} — {pct(fb['fraction'])} of {fb['row']}, "
                           f"a {LEGAL_WORD[r['legal_status']]} value for {r['matrix']} — not a farmland standard, so {f['status']} at most")
            out.append(f"| {g.capitalize()}, {names} | {st} | {refs or '—'} | {'; '.join(why)} |")
            continue
        fl = [f for f in o["flags"] if f["kind"] == "model disagrees"]
        st = o["status"] + (", with a flag" if fl else "")
        refs = "; ".join(ref_text(s["row"], packs) for s in o["set_by"][: (1 if o["status"] in (pc.GREEN, pc.WATCH) else 3)])
        why = why_text(o, packs) + (f"; flag: {fl[0]['text']}" if fl else "")
        out.append(f"| {o['label']} ({o['id']}) | {st} | {refs or '—'} | {why} |")
    out += ["", "Only measured values carry a colour. Grey means not assessed. Red is kept for a sustained exceedance of an "
                "in-force reference under its own rule (`references/status-rules.md`).", ""]
    d = p["dose"]
    if d and not d["computed"]:
        out += ["## Dose — screening, not a health forecast", "", f"Not computed: {d['why']}.", ""]
    if d and d["computed"]:
        e = d["efsa_four"]
        out += ["## Dose — screening, not a health forecast", "",
                f"Reference: {d['twi']['row']} — EFSA tolerable weekly intake, {d['twi']['value']} ng/kg body weight per week "
                f"({LEGAL_WORD[d['twi']['legal_status']]}, checked {d['twi']['checked']}). "
                f"EFSA PFAS measured: {e['measured']} of 4" + (f" — missing {', '.join(e['missing'])}: **every dose is a lower bound**." if e["lower_bound"] else "."),
                "", "| Scenario | Case | Dose, ng/kg bw/week | Share of the TWI |", "|---|---|---|---|"]
        for s in d["scenarios"]:
            for i, cs in enumerate(s["cases"]):
                if cs["dose"] is None:
                    out.append(f"| {s['label'] if i == 0 else ''} | {cs['label']} — not computed: {cs['why']} | — | — |")
                    continue
                note = f" — without {', '.join(cs['not_included'])} (never measured)" if cs["not_included"] else ""
                out.append(f"| {s['label'] if i == 0 else ''} | {cs['label']}{note} | {hr(cs['dose'])} | {pct(cs['share_of_twi'])} |")
            if s.get("break_even_note"):
                out.append(f"| | {s['break_even_note']} | — | — |")
            for b in s.get("break_even_milk_l_day", []):
                out.append(f"| | break-even farm milk ({b['case'].split(',')[0]}) | {hr(b['value'], 2 if b['value'] >= 0.1 else 3)} L/day | — |")
        out += ["", "Point values from `scripts/passport_calc.py`. Uncertainty intervals are not computed by this command; "
                    "`examples/uncertainty.py` shows the method on the synthetic farm (PFAS example §4.1).", ""]
    merged_flags: dict = {}
    for o in p["objects"]:
        for f in o["flags"]:
            if f["kind"] != "model agrees":
                merged_flags.setdefault((f["kind"], f["text"], f["closing"]), []).append(o["id"])
    if merged_flags:
        gmap = {g["group"]: g["objects"] for g in p["groups"]}
        out += ["## What the measurements leave open", ""]
        out += [f"- **{short(ids, gmap)}** — {text}." + (f" Closing: {closing}." if closing else "")
                for (kind, text, closing), ids in merged_flags.items()]
        out.append("")
    ind = p["indicators"]
    if ind:
        out += ["## Indicators and work plan", "",
                f"Catalogue {ind['catalogue']} · selected {ind['selected']} · to confirm {ind['to_confirm']} "
                f"(waiting on {len(ind['facts_to_confirm'])} facts) · left out {len(ind['left_out'])}, each with its reason · "
                f"gap registry {len(ind['gap_registry'])} rows (full list in `passport.json`).", "",
                "Work plan, in value-of-information order:", ""]
        for i, a in enumerate(ind["work_plan"], 1):
            extra = f" — facts: {', '.join(a['facts'])}" if a["facts"] else ""
            out.append(f"{i}. {a['action']} ({a['cost']}) — {len(a['indicators'])} indicator(s){extra}")
        nr = ind["nasa_request"]
        out += ["", f"NASA request to the data agent: {', '.join(nr['products'])}; excluded by the pixel-fit check: "
                    + ("; ".join(f"{x['indicator']} from {x['product']}" for x in nr["excluded"]) or "none") + ". " + nr["rule"] + ".", ""]
    out += ["## Run record", "",
            f"Skill {rr['skill_version']} · run {rr['run_date']} · `{rr['command']}`  ",
            f"Threshold pack {rr['threshold_pack']['pack']} {rr['threshold_pack']['version']} (rows expire after {rr['threshold_pack']['max_age_days']} days); "
            f"rows used: {', '.join(x['row'] for x in rr['rows_used'])}; stale on the run date: {', '.join(rr['stale_rows']) or 'none'}  ",
            "Inputs (sha256): " + "; ".join(f"`{x['path']}` {x['sha256'][:12]}…" for x in rr["inputs"]) + "  ",
            "Input checks: 0 errors; " + (f"{len(rr['checks']['warnings'])} warning(s): "
                                          + "; ".join(f"{w['code']} ({w['where']})" for w in rr["checks"]["warnings"])
                                          if rr["checks"]["warnings"] else "no warnings"), "",
            "## Limits", "", p["limits"], ""]
    return "\n".join(out)


# ------------------------------------------------------------------- main
def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    def opt(name, default=None):
        if name in argv:
            return argv[argv.index(name) + 1]
        return default
    farm_dir = Path(opt("--farm", str(DEFAULT_FARM)))
    out_dir = Path(opt("--out", str(farm_dir)))
    check = "--check" in argv
    committed = None
    if check and (out_dir / "passport.json").exists():
        committed = json.loads((out_dir / "passport.json").read_text(encoding="utf-8"))
    d = opt("--date")
    if d:
        today = date.fromisoformat(d)
    elif committed:
        today = date.fromisoformat(committed["run_record"]["run_date"])
    else:
        today = datetime.now(timezone.utc).date()
    passport, rep = build(farm_dir, today)
    if passport is None:
        for m in vi.merged(rep.messages):
            print(m.line())
        print(f"\n{len(rep.errors)} error(s) — nothing written. Fix the input and run again.")
        return 1
    text = json.dumps(passport, ensure_ascii=False, indent=1) + "\n"
    md = card(passport)
    if check:
        if committed is None or not (out_dir / "answer-card.md").exists():
            print("no committed passport.json / answer-card.md to compare with")
            return 1
        a = dict(committed["run_record"]); b = dict(passport["run_record"])
        a.pop("python", None); b.pop("python", None)
        same_json = {**committed, "run_record": a} == {**json.loads(text), "run_record": b}
        same_md = (out_dir / "answer-card.md").read_text(encoding="utf-8") == md
        print(f"passport.json {'in sync' if same_json else 'DIFFERS'}; answer-card.md {'in sync' if same_md else 'DIFFERS'}")
        return 0 if same_json and same_md else 1
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "passport.json").write_text(text, encoding="utf-8")
    (out_dir / "answer-card.md").write_text(md, encoding="utf-8")
    nw = sum(1 for m in vi.merged(rep.messages) if m.level == "warning")
    print(f"wrote {rel(out_dir / 'passport.json')} and {rel(out_dir / 'answer-card.md')} ({nw} input warning(s), printed in the run record)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
