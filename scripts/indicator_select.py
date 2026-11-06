#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Farm indicator catalogue: loading, selection by farm profile, gap registry,
NASA request for the data agent, pixel-fit check (v0.3.0). Standard library only. Apache-2.0.

Selection discipline (shared with the Ecosystem Digital Twin catalogue, §18–§19):
  core          — selected whenever the component is present (applies_if)
  conditional   — selected when the component is present AND a trigger is present
  research      — selected only on request
A flag in the profile is true, false or "unknown". Unknown never silently drops an
indicator: it is selected with "confirm" so the first action is to establish the fact.
Every unselected indicator carries the reason, so "the catalogue includes everything"
stays true while the measured set stays small.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

LIST_FIELDS = ("applies_if", "trigger", "anchor", "twin", "aei", "nasa")
COST_ORDER = {"desk": 0, "remote": 1, "field": 2, "lab": 3}
TIER_ORDER = {"core": 0, "conditional": 1, "research": 2}
PURE_PIXELS_MIN = 9          # skill convention: 3 × 3 pure pixels for an object-level proxy
# Panel order follows the sampling-plan priority stated in SKILL.md: the drinking well, the product, feed,
# soil of application and control fields, standing water — then the remaining water and manure panels.
# Field visits: the cheap walkover first. Unlisted panels go last, alphabetically.
PANEL_ORDER = ["records", "nasa", "walkover", "welfare-visit", "scouting", "biodiversity",
               "well", "milk", "feed", "soil", "soil-nitrate", "pond", "stream", "drain", "irrigation-water", "manure"]


def load_catalogue(path: str | Path) -> list[dict]:
    lines = Path(path).read_text(encoding="utf-8").strip().splitlines()
    head = lines[0].split("|")
    out = []
    for n, line in enumerate(lines[1:], start=2):
        cells = line.split("|")
        if len(cells) != len(head):
            raise ValueError(f"line {n}: {len(cells)} fields, expected {len(head)}")
        row = dict(zip(head, (c.strip() for c in cells)))
        for f in LIST_FIELDS:
            row[f] = [] if row[f] in ("", "-") else [x.strip() for x in row[f].split(",")]
        out.append(row)
    return out


def _state(profile: dict, flags: list[str]) -> str:
    """'true' if any flag is true, 'unknown' if none true but one unknown, else 'false'."""
    vals = [profile.get(f, "unknown") for f in flags]
    if any(v is True for v in vals):
        return "true"
    if any(v == "unknown" for v in vals):
        return "unknown"
    return "false"


def _unknown(profile: dict, flags: list[str]) -> list[str]:
    return [f for f in flags if profile.get(f, "unknown") == "unknown"]


def select(profile: dict, catalogue: list[dict], research_ids: tuple = ()) -> tuple[list[dict], list[dict]]:
    """Returns (chosen, skipped). A chosen row carries `confirm` and, when true, `unknown_flags`: the facts
    the farm (or a desk record) must confirm before the indicator is measured or interpreted."""
    chosen, skipped = [], []
    for ind in catalogue:
        present = "true" if not ind["applies_if"] else _state(profile, ind["applies_if"])
        if present == "false":
            skipped.append({**ind, "reason": f"component absent ({', '.join(ind['applies_if'])})"})
            continue
        unknown = _unknown(profile, ind["applies_if"]) if present == "unknown" else []
        why = "core" if not ind["applies_if"] else f"component: {', '.join(ind['applies_if'])}"
        if ind["tier"] == "research":
            if ind["id"] in research_ids:
                chosen.append({**ind, "reason": "research — requested", "confirm": bool(unknown), "unknown_flags": unknown})
            else:
                skipped.append({**ind, "reason": "research tier — on request"})
            continue
        if ind["tier"] == "conditional":
            t = _state(profile, ind["trigger"])
            if t == "false":
                skipped.append({**ind, "reason": f"trigger absent ({', '.join(ind['trigger'])})"})
                continue
            if t == "unknown":
                unknown += [f for f in _unknown(profile, ind["trigger"]) if f not in unknown]
            why = f"trigger: {', '.join(f for f in ind['trigger'] if profile.get(f, 'unknown') in (True, 'unknown'))}"
        chosen.append({**ind, "reason": why, "confirm": bool(unknown), "unknown_flags": unknown})
    return chosen, skipped


CONSENT_ID = "X-07"          # nothing is sampled, requested or stored before the farm's consent record


def _voi_rank(ind: dict) -> int:
    """Value-of-information order: 0 consent; 1 confirm an unknown fact (a phone call can open or close
    several indicators); 2 everything else, then by cost (desk < remote < field < lab), tier and panel."""
    if ind["id"] == CONSENT_ID:
        return 0
    return 1 if ind.get("confirm") else 2


def gap_registry(chosen: list[dict], measured: dict) -> list[dict]:
    """Selected indicators without a (complete) measurement -> gap rows in value-of-information order:
    consent first, then confirmation of unknown facts, then desk, remote, field and laboratory work,
    laboratory rows grouped by sampling panel so one visit closes several gaps."""
    rows = []
    for ind in chosen:
        m = measured.get(ind["id"])
        if m and not m.get("partial"):
            continue
        rows.append({
            "id": ind["id"], "indicator": ind["indicator"], "tier": ind["tier"], "cost": ind["cost"],
            "panel": ind.get("panel", ""), "confirm": bool(ind.get("confirm")), "rank": _voi_rank(ind),
            "gap": ("partial: " + m["missing"]) if m else ("confirm the fact first" if ind.get("confirm") else "never measured"),
            "closing": ("confirm with the farm or its records: " + ", ".join(ind.get("unknown_flags", []))) if ind.get("confirm") and not m else ind["method"],
            "frequency": ind["frequency"]})
    # a panel is as expensive as its most expensive member: field checks done on a laboratory sampling
    # visit (soil compaction, stream flow, pond profile) travel with that panel
    pcost = {}
    for r in rows:
        if r["rank"] == 2:
            pcost[r["panel"]] = max(pcost.get(r["panel"], 0), COST_ORDER[r["cost"]])
    po = lambda pn: (PANEL_ORDER.index(pn), "") if pn in PANEL_ORDER else (len(PANEL_ORDER), pn)
    rows.sort(key=lambda r: (r["rank"], pcost.get(r["panel"], COST_ORDER[r["cost"]]) if r["rank"] == 2 else COST_ORDER[r["cost"]],
                             po(r["panel"]) if r["rank"] == 2 else (0, ""),
                             not r["gap"].startswith("partial"),          # complete what was started first
                             TIER_ORDER[r["tier"]], COST_ORDER[r["cost"]], r["id"]))
    return rows


def lab_panels(chosen: list[dict], include_confirm: bool = False) -> dict[str, list[str]]:
    """Laboratory sampling panels for the selected indicators: one sampling visit / shipment per panel."""
    out: dict[str, list[str]] = {}
    for ind in chosen:
        if ind["cost"] != "lab" or (ind.get("confirm") and not include_confirm):
            continue
        out.setdefault(ind.get("panel") or ind["id"], []).append(ind["id"])
    return dict(sorted(out.items(), key=lambda kv: (PANEL_ORDER.index(kv[0]) if kv[0] in PANEL_ORDER else len(PANEL_ORDER), kv[0])))


def work_plan(gaps: list[dict], chosen: list[dict] | None = None) -> list[dict]:
    """Collapse the gap registry into actions: consent; one call to confirm the unknown facts; one records
    interview; one NASA request; one field visit or laboratory panel per panel — in registry order."""
    flags = {c["id"]: c.get("unknown_flags", []) for c in (chosen or [])}
    plan, seen = [], {}
    for g in gaps:
        key = "consent" if g["id"] == CONSENT_ID else ("confirm" if g["rank"] == 1 else (g["panel"] or g["id"]))
        if key not in seen:
            seen[key] = {"action": key, "cost": g["cost"], "indicators": [], "facts": []}
            plan.append(seen[key])
        a = seen[key]
        a["indicators"].append(g["id"])
        if COST_ORDER[g["cost"]] > COST_ORDER[a["cost"]] and key != "confirm":
            a["cost"] = g["cost"]
        if key == "confirm":
            a["cost"] = "desk"
            a["facts"] += [f for f in flags.get(g["id"], []) if f not in a["facts"]]
    return plan


def pure_pixels(res_m: float, area_m2: float | None = None, width_m: float | None = None, length_m: float | None = None) -> int:
    """Pixels fully inside an object at random alignment (conservative): square object of the
    given area, or a strip of given width and length. (side/res - 1)^2 for squares."""
    if width_m is not None:
        across = max(math.floor(width_m / res_m - 1 + 1e-9), 0)
        along = max(math.floor(length_m / res_m - 1 + 1e-9), 0)
        return across * along
    side = math.sqrt(area_m2)
    k = max(math.floor(side / res_m - 1 + 1e-9), 0)
    return k * k


def nasa_request(chosen: list[dict], layer: dict, objects: dict, aoi: dict, period: dict, requester: str = "farm passport") -> dict:
    """Compose the data request handed to the data agent. objects: {indicator_id: {"area_m2": ..} or {"width_m":.., "length_m":..}}
    for indicators tied to a small object; field-scale products failing the pixel-fit check are excluded with a reason."""
    prods = {p["id"]: p for p in layer["products"]}
    items, excluded = {}, []
    for ind in chosen:
        for pid in ind["nasa"]:
            p = prods[pid]
            if p["scale"] == "field" and ind["id"] in objects:
                n = pure_pixels(p["resolution_m"], **objects[ind["id"]])
                if n < PURE_PIXELS_MIN:
                    excluded.append({"indicator": ind["id"], "product": pid, "pure_pixels": n,
                                     "reason": f"object too small for {p['resolution_m']} m pixels ({n} pure pixels < {PURE_PIXELS_MIN})"})
                    continue
            it = items.setdefault(pid, {"product": p["name"], "variables": p["variables"], "resolution_m": p["resolution_m"],
                                        "scale": p["scale"], "verified": p["verified"], "indicators": [], "awaiting_confirmation": []})
            it["indicators"].append(ind["id"])
            if ind.get("confirm"):
                it["awaiting_confirmation"].append(ind["id"])
    return {"to": "Data agent with NASA Earthdata access", "from": requester, "aoi": aoi, "period": period,
            "deliver": "per-field (or per-farm for farm-context products) time series as CSV with product version, granule/tile, date, quality mask, access date and licence / reuse terms (the twin's Phase 1 onboarding checklist); clipped rasters on request",
            "rule": "remote = proxy: used for triggers, targeting and context; never a status colour alone",
            "consent": f"send only after the farm consent record ({CONSENT_ID}) covers satellite data for this area",
            "verification_note": "a product marked other than 'verified' is used only after its specification is checked at the source",
            "confirm_note": "indicators under awaiting_confirmation depend on a fact the farm has not confirmed; the data agent may fetch them (cheap) but they are not interpreted until confirmed",
            "products": [dict(id=k, **v) for k, v in sorted(items.items())], "excluded": excluded}


def drought_flag(smap_rootzone_percentiles: list[float], months_needed: int = 2, cutoff: float = 20.0) -> bool:
    """Skill convention: drought_year = at least `months_needed` growing-season months with SMAP root-zone
    soil moisture at or below the 20th percentile of its climatology (aligned with the US Drought Monitor
    D1 band — not verified in this check). Drives triggers for aflatoxin (L-06, L-39) and forage nitrate (A-19)."""
    return sum(1 for p in smap_rootzone_percentiles if p <= cutoff) >= months_needed
