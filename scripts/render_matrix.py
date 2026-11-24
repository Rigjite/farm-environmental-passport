#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render core/screening-matrix.md — parameter → reference row → unit → method — from
core/screening-map.json and the threshold pack (since v0.3.8). The human table and the
machine map can never disagree: a test fails if the committed file differs from a fresh
render. Run after any edit of the map or the pack. Standard library only. Apache-2.0."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGAL = {"in_force": "in force", "future": "future (adopted, applies from a date)", "guidance": "guidance",
         "proposed": "proposed", "orientation": "orientation", "superseded": "superseded", "requirement": "requirement"}
MARK = {"verified": "verified", "verified-secondary": "verified via secondary [provisional]",
        "corrected": "corrected vs v0.1", "not-verified": "NOT verified"}


def cell(x):
    return "—" if x in (None, "") else str(x).replace("|", "/")


def render() -> str:
    smap = json.loads((ROOT / "core" / "screening-map.json").read_text(encoding="utf-8"))
    name = {"NY-US": "ny-us.json", "EU": "eu.json"}[smap["pack"]]
    pack = json.loads((ROOT / "core" / "thresholds" / name).read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in pack["rows"]}
    out = ["# Screening matrix — parameter → reference → unit → method",
           "",
           "Generated from `core/screening-map.json` and `core/thresholds/" + name + "` by `scripts/render_matrix.py`. Do not edit by hand.",
           f"Map version {smap['version']}; pack {pack['pack']} version {pack['version']} (a row older than {pack['max_age_days']} days must be re-checked before use).",
           "",
           "Which reference rows a measured result is compared with, in which unit it must arrive and which analytical methods are "
           "validated for it. Values, legal status and dates come from the pack; the map holds row IDs only. A result by a method "
           "not listed for its matrix is printed grey (`references/methods.md`). Status rules: `references/status-rules.md`.",
           ""]
    out += ["Fit of a reference: " + "; ".join(f"**{k}** — {v}" for k, v in smap["fit_legend"].items()) + ".", ""]
    for mx, spec in smap["matrices"].items():
        out += [f"## `{mx}` — {spec['label']}", ""]
        notes = []
        if spec.get("group"):
            notes.append(f"Objects of this matrix form the group **{spec['group']}**: the card prints one summary line and names any field whose own status is worse (status-rules §3a).")
        if spec.get("series"):
            notes.append(f"Varies by season: one sampling event is flagged; closing sample — {spec['series']['closing']}.")
        if notes:
            out += notes + [""]
        out += ["| Parameter | Unit (canonical) | Validated methods | Reference row | Value | Legal status | Fit | Verification | Checked |",
                "|---|---|---|---|---|---|---|---|---|"]
        for par, p in spec["parameters"].items():
            unit = smap["unit_sets"][p["unit_set"]]["canonical"]
            methods = ", ".join(p["methods"]) or "any (none listed in references/methods.md)"
            if not p["references"]:
                out.append(f"| {par} | {unit} | {methods} | — no reference in this pack: reported, not coloured | — | — | — | — | — |")
                continue
            for e in p["references"]:
                r = rows[e["row"]]
                fit = e.get("fit", "object") + (" · acts on a single result" if e.get("single_result_acts") else "")
                out.append(f"| {par} | {unit} | {methods} | {e['row']} — {cell(r['matrix'])}, {cell(r['analyte'])} | "
                           f"{cell(r['value'])} {cell(r['unit'])} | {LEGAL[r['legal_status']]} | {fit} | {MARK[r['verified']]} | {r['checked']} |")
        out.append("")
    out += ["## Accepted units", "",
            "A result in another unit is refused with the list below; a wet-weight result for a solid is refused until it is converted to dry weight.", "",
            "| Unit set | Canonical | Accepted as written (factor to canonical) |", "|---|---|---|"]
    for k, u in smap["unit_sets"].items():
        acc = ", ".join(f"{a} (×{f:g})" for a, f in u["aliases"].items())
        extra = f"; basis {u['basis']} — a unit without 'dw' is accepted with a warning" if u.get("basis") else ""
        out.append(f"| {k} | {u['canonical']} | {acc}{extra} |")
    d = smap["dose"]
    out += ["", "## Dose", "",
            f"Reference row {d['twi_row']} — {cell(rows[d['twi_row']]['analyte'])}, {rows[d['twi_row']]['value']} {rows[d['twi_row']]['unit']}. "
            f"EFSA four: {', '.join(d['efsa_four'])}. Mandatory scenarios: {', '.join(d['mandatory_roles'])}.", ""]
    return "\n".join(out)


if __name__ == "__main__":
    text = render()
    target = ROOT / "core" / "screening-matrix.md"
    if "--check" in sys.argv:
        sys.exit(0 if target.exists() and target.read_text(encoding="utf-8") == text else 1)
    target.write_text(text, encoding="utf-8")
    print(f"wrote {target.relative_to(ROOT)}")
