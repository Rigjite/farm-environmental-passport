#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render references/thresholds.md from the JSON packs, so the human table and the
machine pack can never disagree. Run after any edit of core/thresholds/*.json.
Test T15 fails if the committed thresholds.md differs from a fresh render."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKS = ["ny-us.json", "eu.json"]
STATUS = {"in_force": "in force", "future": "adopted — applies from date", "guidance": "guidance / benchmark",
          "proposed": "proposed (not adopted)",
          "orientation": "orientation (not a norm)", "superseded": "superseded", "requirement": "requirement (no number)"}
MARK = {"verified": "verified", "verified-secondary": "verified via secondary [provisional]",
        "corrected": "corrected vs v0.1", "not-verified": "NOT verified"}


def cell(x):
    return "—" if x in (None, "") else str(x).replace("|", "/")


def render() -> str:
    out = ["# Threshold packs — rendered table",
           "",
           "Generated from `core/thresholds/*.json` by `scripts/render_thresholds.py`. Do not edit by hand.",
           "Every row: value, unit, legal status, date of application, the date it was checked against the source, and the verification mark.",
           "A screening comparison is never worded as compliance.",
           ""]
    for name in PACKS:
        pack = json.loads((ROOT / "core" / "thresholds" / name).read_text(encoding="utf-8"))
        out += [f"## {pack['title']}", "", f"Pack version {pack['version']}; a row older than {pack['max_age_days']} days must be re-checked before use.", "",
                "| ID | Matrix | Analyte | Value | Unit | Legal status | Applies from | Checked | Verification | Source |",
                "|---|---|---|---|---|---|---|---|---|---|"]
        for r in pack["rows"]:
            src = f"{cell(r['source_doc'])} — {cell(r['source_org'])}" + (f" <{r['url']}>" if r.get("url") else "")
            out.append("| " + " | ".join([r["id"], cell(r["matrix"]), cell(r["analyte"]), cell(r["value"]), cell(r["unit"]),
                                          STATUS[r["legal_status"]], cell(r["applies_from"]), r["checked"],
                                          MARK[r["verified"]], src]) + " |")
        notes = [r for r in pack["rows"] if r.get("note")]
        if notes:
            out += ["", "Notes:", ""]
            out += [f"- **{r['id']}** — {r['note']}" for r in notes]
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    text = render()
    target = ROOT / "core" / "thresholds.md"
    if "--check" in sys.argv:
        sys.exit(0 if target.read_text(encoding="utf-8") == text else 1)
    target.write_text(text, encoding="utf-8")
    print(f"wrote {target}")
