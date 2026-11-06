#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render the farm indicator catalogue (core/indicators/farm-indicators.psv) into JSON, CSV
(for spreadsheets), a readable table, the crosswalk to the Ecosystem Digital Twin catalogue,
and the worked selection for the synthetic farm. `--check` exits 1 if any output is stale."""
import csv
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import indicator_select as s  # noqa: E402

CAT = ROOT / "core/indicators/farm-indicators.psv"
BLOCKS = {"A": "Agronomy — crops and soil", "L": "Livestock — herd, feed, health, welfare, product safety",
          "E": "Farm ecosystem — water, nutrients, habitat, climate", "X": "Cross-cutting — contaminant sources, AMR, governance"}
TWIN = {"1": "Climate and weather drivers", "2": "Air quality and deposition", "3": "Hydrology and hydrometry",
        "4": "Surface-water quality", "5": "Nutrients and eutrophication", "6": "Contaminants and ecotoxicology",
        "8": "Groundwater", "9": "Soil and land quality", "10": "Landscape and habitat", "11": "Flora and vegetation",
        "12": "Microalgae and phytoplankton", "13": "Microbiology", "14": "Invertebrates", "15": "Fish, wildlife and fauna",
        "16": "Ecosystem functions", "17": "Pressures and management", "18": "Domain quick sets", "23": "Livestock farm as an ecosystem"}


def j(xs):
    return ", ".join(xs) if xs else "—"


def outputs() -> dict[str, str]:
    cat = s.load_catalogue(CAT)
    out = {}
    out["core/indicators/farm-indicators.json"] = json.dumps(cat, ensure_ascii=False, indent=1) + "\n"
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    cols = list(cat[0].keys())
    w.writerow(cols)
    for r in cat:
        w.writerow([", ".join(r[c]) if isinstance(r[c], list) else r[c] for c in cols])
    out["core/indicators/farm-indicators.csv"] = buf.getvalue()

    md = ["# Farm indicator catalogue — rendered", "",
          "Generated from `core/indicators/farm-indicators.psv` by `scripts/render_catalogue.py`; do not edit by hand.",
          "Tier: core = always when the component is present; conditional = when a trigger is present; research = on request.",
          "Anchor = threshold row in `core/thresholds.md` (— = no anchor: a named gap of the packs, never a borrowed number).",
          "Twin § = section of the Ecosystem Digital Twin `references/indicators.md`; *new* = not covered there.",
          f"Indicators: {len(cat)}.", ""]
    for b, title in BLOCKS.items():
        rows = [r for r in cat if r["block"] == b]
        md += [f"## {title} ({len(rows)})", "",
               "| ID | Indicator | Unit | Tier | Present if / trigger | Cost | Panel | Method | Anchor | NASA | Twin § | AEI | Welfare Quality |",
               "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            cond = j(r["applies_if"]) + (f" / {j(r['trigger'])}" if r["trigger"] else "")
            md.append("| " + " | ".join([r["id"], r["indicator"], r["unit"], r["tier"], cond, r["cost"], r.get("panel", "—") or "—",
                                          r["method"], j(r["anchor"]), j(r["nasa"]), j(r["twin"]), j(r["aei"]),
                                          r["wq"] if r["wq"] != "-" else "—"]) + " |")
        md.append("")
    out["core/indicators/farm-indicators.md"] = "\n".join(md)

    # crosswalk to the twin
    new = [r for r in cat if r["twin"] == ["new"]]
    cw = ["# Crosswalk: farm catalogue ↔ Ecosystem Digital Twin catalogue", "",
          "Generated. Twin section titles from the twin's `references/indicators.md` (v2.8, read 2026-11-01).", "",
          "| Twin § | Title | Farm indicators |", "|---|---|---|"]
    for sec, title in TWIN.items():
        ids = [r["id"] for r in cat if sec in r["twin"]]
        cw.append(f"| {sec} | {title} | {j(ids)} |")
    cw += ["", f"## Not covered by the twin catalogue ({len(new)}) — proposed extension of twin §23 or a new section", "",
           "The twin's §23 states that it does not cover animal health, disease, breeding or feeding rations. These farm indicators fill that gap and would be referenced from the shared core, not copied:", ""]
    groups = {}
    for r in new:
        groups.setdefault(r["group"], []).append(f"{r['id']} {r['indicator']}")
    for g, items in groups.items():
        cw.append(f"- **{g}:** " + "; ".join(items))
    out["core/crosswalk-twin.md"] = "\n".join(cw) + "\n"

    # worked selection for the synthetic farm
    prof = json.loads((ROOT / "tests/fixtures/sim_farm_profile.json").read_text(encoding="utf-8"))
    meas = json.loads((ROOT / "tests/fixtures/sim_measured.json").read_text(encoding="utf-8"))
    objs = json.loads((ROOT / "tests/fixtures/sim_objects.json").read_text(encoding="utf-8"))
    meas = {k: v for k, v in meas.items() if not k.startswith("_")}
    objs = {k: v for k, v in objs.items() if not k.startswith("_")}
    layer = json.loads((ROOT / "core/remote-sensing/nasa-layer.json").read_text(encoding="utf-8"))
    ch, sk = s.select(prof, cat)
    gaps = s.gap_registry(ch, meas)
    req = s.nasa_request(ch, layer, objs, aoi={"farm": "synthetic dairy farm of examples/", "coordinates": "none — synthetic"},
                         period={"from": "2016-01-01", "to": "2026-10-31"})
    panels = s.lab_panels(ch)
    plan = s.work_plan(gaps, ch)
    ex = ["# Synthetic farm — indicator selection, gap registry and NASA request", "",
          "Generated by `scripts/render_catalogue.py` from `tests/fixtures/sim_*.json`. The farm and every laboratory value are synthetic (examples/).", "",
          f"- Catalogue: {len(cat)} indicators. Selected: {len(ch)} (of which {sum(r['confirm'] for r in ch)} wait for a fact to be confirmed). Not selected: {len(sk)}, each with its reason.",
          f"- Measured in the examples: {len(meas)} indicators ({sum(1 for v in meas.values() if v.get('partial'))} only partly).",
          f"- Gap registry: {len(gaps)} rows."]
    ex.append(f"- Laboratory work for the selected indicators (confirmed facts only) groups into {len(panels)} sampling panels: " + "; ".join(f"{k} ({len(v)})" for k, v in panels.items()) + ".")
    ex.append(f"- The {len(gaps)} gaps collapse into {len(plan)} actions (one records interview, one NASA request, field visits, laboratory panels) — see the work plan.")
    ex += ["", "## Not selected", "", "| ID | Indicator | Reason |", "|---|---|---|"]
    ex += [f"| {r['id']} | {r['indicator']} | {r['reason']} |" for r in sk]
    ex += ["", "## Work plan (value-of-information order)", "", "| Step | Action | Cost | Indicators |", "|---|---|---|---|"]
    ex += [f"| {i} | {a['action']}" + (f" — {len(a['facts'])} facts: {', '.join(a['facts'])}" if a['facts'] else "") + f" | {a['cost']} | {', '.join(a['indicators'])} |" for i, a in enumerate(plan, 1)]
    ex += ["", "## Gap registry (consent → confirm facts → desk → remote → field → laboratory, grouped by panel)", "",
           "| # | ID | Indicator | Tier | Cost | Panel | Gap | Closing action | Frequency |", "|---|---|---|---|---|---|---|---|---|"]
    ex += [f"| {i} | {g['id']} | {g['indicator']} | {g['tier']} | {g['cost']} | {g['panel']} | {g['gap']} | {g['closing']} | {g['frequency']} |" for i, g in enumerate(gaps, 1)]
    ex += ["", "## NASA data request for the data agent", "", "```json", json.dumps(req, ensure_ascii=False, indent=1), "```", ""]
    out["examples/sim-farm-indicator-selection.md"] = "\n".join(ex)
    return out


if __name__ == "__main__":
    outs = outputs()
    stale = [p for p, t in outs.items() if not (ROOT / p).exists() or (ROOT / p).read_text(encoding="utf-8") != t]
    if "--check" in sys.argv:
        print("stale:", stale) if stale else None
        sys.exit(1 if stale else 0)
    for p, t in outs.items():
        (ROOT / p).write_text(t, encoding="utf-8")
        print("wrote", p)
