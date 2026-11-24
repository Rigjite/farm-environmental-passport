#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Farm Environmental Passport — input check (since v0.3.8).

Reads one farm's input folder — `farm.json` (the farm, its objects, consent, dose
scenarios) and `measurements.csv` (one result per row, long format) — and checks it
before anything is computed. Every message says where the problem is and how to fix
it. Errors stop the run; warnings are printed in the passport and its run record.

The format is described in references/input-format.md; the template is in
assets/input-template/. Which parameters, units and methods are accepted for which
matrix comes from core/screening-map.json — this script holds no thresholds.

Usage:
  python3 scripts/validate_input.py examples/synthetic-farm [--date YYYY-MM-DD] [--json]
Exit 0 = no errors (warnings allowed), 1 = errors found, 2 = input could not be read.

Standard library only. License: Apache-2.0 (code).
"""
from __future__ import annotations

import csv
import difflib
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INPUT_FORMAT = "farm-environmental-passport/input@1"
COLUMNS = ["object", "parameter", "sampled", "value", "qualifier", "reporting_limit", "detection_limit",
           "unit", "uncertainty", "method", "laboratory", "evidence", "low", "high", "source"]
EVIDENCE = ("measured", "modelled", "remote")
NOT_STATED = "not stated"
CENSOR_WORDS = {"nd", "n.d.", "bdl", "<rl", "<lod", "<loq", "below rl", "not detected"}
CENSORING_QUALIFIERS = ("<", "J")          # J = estimated between detection and reporting limit
GEOMETRY_TYPES = ("Point", "MultiPoint", "LineString", "MultiLineString", "Polygon", "MultiPolygon")
PROFILE_VALUES = (True, False, "unknown")


@dataclass
class Message:
    level: str            # error | warning
    code: str             # stable identifier, used by the tests
    where: str            # file and line, or file and key
    text: str             # what is wrong
    fix: str = ""         # how to fix it
    obj: str = ""         # object id, when the message belongs to one object
    lines: list = field(default_factory=list)   # line numbers in measurements.csv
    col: str = ""         # column, when one cell is at fault

    @property
    def place(self) -> str:
        out = self.where
        if self.lines:
            out += (" line " if len(self.lines) == 1 else " lines ") + ", ".join(str(n) for n in self.lines)
        return out + (f", {self.col}" if self.col else "")

    def line(self) -> str:
        out = f"{self.level.upper():7s} {self.code:22s} {self.place}: {self.text}"
        return out + (f"\n        fix: {self.fix}" if self.fix else "")


@dataclass
class Row:
    line: int
    object: str
    matrix: str
    parameter: str
    sampled: str
    order_key: tuple
    value: float | None          # canonical unit; None when censored without an estimate or modelled without a point
    censored: bool
    qualifier: str
    rl: float | None
    dl: float | None
    uncertainty: float | None
    unit_in: str
    unit: str                    # canonical unit
    method: str
    method_valid: bool | None    # None = no method list for this parameter, or "not stated"
    laboratory: str
    evidence: str
    low: float | None
    high: float | None
    source: str
    mapped: bool                 # parameter has an entry in the screening map
    usable: bool = True          # may set a colour (measured, valid method, parsed)


@dataclass
class Report:
    folder: str
    today: str
    farm: dict | None = None
    objects: dict = field(default_factory=dict)
    rows: list = field(default_factory=list)
    messages: list = field(default_factory=list)

    @property
    def errors(self):
        return [m for m in self.messages if m.level == "error"]

    @property
    def warnings(self):
        return [m for m in self.messages if m.level == "warning"]

    def add(self, level, code, where, text, fix="", obj="", lines=None, col=""):
        self.messages.append(Message(level, code, where, text, fix, obj, list(lines or []), col))


# ----------------------------------------------------------------- helpers
def load_map(path: Path | None = None) -> dict:
    return json.loads((path or ROOT / "core" / "screening-map.json").read_text(encoding="utf-8"))


def load_pack_rows(smap: dict) -> dict:
    name = {"NY-US": "ny-us.json", "EU": "eu.json"}[smap["pack"]]
    pack = json.loads((ROOT / "core" / "thresholds" / name).read_text(encoding="utf-8"))
    return {r["id"]: r for r in pack["rows"]}


def norm_method(s: str) -> str:
    s = re.sub(r"\bmethod\b", "", s, flags=re.I)
    return re.sub(r"\s+", "", s).lower()


def method_ok(given: str, allowed: list[str]) -> bool:
    g = norm_method(given)
    return any(norm_method(a) in g for a in allowed)


def parse_date(text: str, today: date):
    """Accepts YYYY-MM-DD, YYYY-MM, YYYY or 'not stated'. Returns (order_key, problem)."""
    t = text.strip()
    if t.lower() == NOT_STATED:
        return None, None
    m = re.fullmatch(r"(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?", t)
    if not m:
        return None, "format"
    y, mo, d = int(m.group(1)), int(m.group(2) or 1), int(m.group(3) or 1)
    try:
        first = date(y, mo, d)
    except ValueError:
        return None, "format"
    if first > today:
        return None, "future"
    return (first.isoformat(), len(t)), None


def parse_number(text: str):
    """Returns (float | None, problem code | None). Empty -> (None, None)."""
    t = text.strip()
    if t == "":
        return None, None
    low = t.lower()
    if t.startswith("<") or low in CENSOR_WORDS:
        return None, "censored-as-text"
    if re.fullmatch(r"-?\d+,\d+", t):
        return None, "decimal-comma"
    try:
        v = float(t)
    except ValueError:
        return None, "not-a-number"
    if v != v or v in (float("inf"), float("-inf")):
        return None, "not-a-number"
    if v < 0:
        return None, "negative"
    return v, None


def unit_factor(unit: str, uset: dict):
    """(factor to canonical, basis_stated, wet) or (None, ..) when the unit is not accepted."""
    u = re.sub(r"\s+", " ", unit.strip())
    if u in uset.get("wet_aliases", []):
        return None, True, True
    if u in uset["aliases"]:
        basis = "dw" in u or "dry" in u or "basis" not in uset
        return float(uset["aliases"][u]), basis, False
    return None, False, False


def walk_coords(c):
    if isinstance(c, (list, tuple)) and len(c) >= 2 and all(isinstance(x, (int, float)) for x in c[:2]):
        yield c
    elif isinstance(c, (list, tuple)):
        for x in c:
            yield from walk_coords(x)


# ----------------------------------------------------------------- farm.json
def check_farm(rep: Report, farm: dict, smap: dict, catalogue_ids: set | None):
    w = "farm.json"
    if farm.get("passport_input") != INPUT_FORMAT:
        rep.add("error", "format-version", w, f"'passport_input' must be '{INPUT_FORMAT}'",
                "copy the first line of assets/input-template/farm.json")
    for key in ("farm_id", "jurisdiction", "objects"):
        if not farm.get(key):
            rep.add("error", "farm-field-missing", f"{w} → {key}", f"'{key}' is missing or empty",
                    "see references/input-format.md §1")
    if not isinstance(farm.get("synthetic"), bool):
        rep.add("error", "synthetic-flag", f"{w} → synthetic",
                "'synthetic' must be true or false", "true only for an invented farm; a real farm is false")
    synthetic = farm.get("synthetic") is True
    if farm.get("jurisdiction") and farm["jurisdiction"] != smap["pack"]:
        rep.add("error", "no-screening-map", f"{w} → jurisdiction",
                f"no screening map for '{farm['jurisdiction']}' in this version (mapped: {smap['pack']})",
                "build that jurisdiction's threshold rows first (SKILL.md, 'A jurisdiction without a pack'); never borrow another pack's values")
    consent = farm.get("consent") or {}
    if not synthetic and not (consent.get("recorded") is True and consent.get("date")):
        rep.add("error", "consent-missing", f"{w} → consent",
                "a real farm needs its written consent recorded (indicator X-07) before anything is computed",
                "set consent.recorded = true, consent.date and consent.scope after the farm has signed")
    seen = set()
    for i, ob in enumerate(farm.get("objects") or []):
        where = f"{w} → objects[{i}]"
        oid = (ob.get("id") or "").strip()
        if not oid:
            rep.add("error", "object-id-missing", where, "object without 'id'", "give every object a short code, e.g. WELL or F1")
            continue
        if oid in seen:
            rep.add("error", "object-duplicate", where, f"object id '{oid}' appears twice", "object ids must be unique")
        seen.add(oid)
        mx = ob.get("matrix")
        if mx not in smap["matrices"]:
            rep.add("error", "unknown-matrix", where, f"matrix '{mx}' is not in the screening map",
                    f"use one of: {', '.join(smap['matrices'])}", oid)
        role = ob.get("dose_role")
        if role not in (None, "drinking_water", "product"):
            rep.add("error", "dose-role", where, f"dose_role '{role}' is not known", "use drinking_water or product, or leave it out", oid)
        geom = ob.get("geometry")
        if geom is not None:
            ok = isinstance(geom, dict) and geom.get("type") in GEOMETRY_TYPES and "coordinates" in geom
            pts = list(walk_coords(geom.get("coordinates"))) if ok else []
            ok = ok and pts and all(-180 <= p[0] <= 180 and -90 <= p[1] <= 90 for p in pts)
            if not ok:
                rep.add("error", "geometry-invalid", f"{where} → geometry",
                        "geometry must be a GeoJSON geometry (Point, Polygon, …) with [longitude, latitude] pairs in WGS 84",
                        "leave geometry out if the boundary is not known; it is optional", oid)
        rep.objects[oid] = ob
    # dose scenarios: four are mandatory when the farm has a drinking-water source or a product
    dose_objects = [o for o in rep.objects.values() if o.get("dose_role")]
    roles = {s.get("role") for s in farm.get("dose_scenarios") or []}
    if dose_objects:
        missing = [r for r in smap["dose"]["mandatory_roles"] if r not in roles]
        if missing:
            rep.add("error", "dose-scenarios-missing", f"{w} → dose_scenarios",
                    f"mandatory dose scenarios missing: {', '.join(missing)}",
                    "SKILL.md: off-farm adult, resident adult, infant fed formula made with well water, young child resident")
    for i, s in enumerate(farm.get("dose_scenarios") or []):
        where = f"{w} → dose_scenarios[{i}]"
        bad = not (isinstance(s.get("bw_kg"), (int, float)) and s["bw_kg"] > 0) or not s.get("cases")
        for c in s.get("cases") or []:
            for k in ("milk_l_day", "water_l_day"):
                if k in c and not (isinstance(c[k], (int, float)) and c[k] >= 0):
                    bad = True
        if bad:
            rep.add("error", "dose-scenario-invalid", where, "a scenario needs bw_kg > 0 and cases with non-negative intakes",
                    "see the synthetic farm's farm.json")
        if not s.get("source"):
            rep.add("warning", "dose-source-missing", where, "the exposure factors carry no source",
                    "name the exposure-factor table (e.g. ATSDR 2023, Table 1)")
    prof = farm.get("profile")
    if prof is not None:
        bad = [k for k, v in prof.items() if not k.startswith("_") and v not in PROFILE_VALUES]
        if bad:
            rep.add("error", "profile-value", f"{w} → profile", f"flags must be true, false or \"unknown\": {', '.join(bad)}",
                    "an unknown fact is written \"unknown\", never left out")
    if catalogue_ids is not None:
        for key in ("coverage", "pixel_fit"):
            ids = [k for k in (farm.get(key) or {}) if not k.startswith("_")]
            unknown = [k for k in ids if k not in catalogue_ids]
            if unknown:
                rep.add("error", "unknown-indicator", f"{w} → {key}", f"not catalogue indicators: {', '.join(unknown)}",
                        "use IDs from core/indicators/farm-indicators.md")
    return synthetic


# ----------------------------------------------------------- measurements.csv
def check_rows(rep: Report, path: Path, smap: dict, packs: dict, today: date, synthetic: bool):
    w = path.name
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            rep.add("error", "empty-file", w, "the file is empty", "start from assets/input-template/measurements.csv")
            return
        header = [h.strip() for h in header]
        unknown = [h for h in header if h not in COLUMNS]
        for h in unknown:
            hint = difflib.get_close_matches(h.lower(), COLUMNS, n=1)
            rep.add("error", "unknown-column", w, f"column '{h}' is not part of the format",
                    f"did you mean '{hint[0]}'?" if hint else "the columns are listed in references/input-format.md §2", lines=[1])
        missing = [c for c in COLUMNS if c not in header]
        if missing:
            rep.add("error", "missing-column", w, f"missing columns: {', '.join(missing)}",
                    "keep every column of the template; leave a cell empty when it does not apply", lines=[1])
        if unknown or missing:
            return
        records = []
        for n, cells in enumerate(reader, start=2):
            if not any(c.strip() for c in cells):
                continue
            if len(cells) != len(header):
                rep.add("error", "row-length", w, f"{len(cells)} cells, expected {len(header)}",
                        "a comma inside a text cell needs quotes", lines=[n])
                continue
            records.append((n, dict(zip(header, (c.strip() for c in cells)))))

    for n, c in records:
        oid = c["object"]

        def add(level, code, text, fix="", col="", _n=n, _o=oid):
            rep.add(level, code, w, text, fix, _o, [_n], col)

        ob = rep.objects.get(oid)
        if ob is None:
            hint = difflib.get_close_matches(oid, list(rep.objects), n=1)
            add("error", "unknown-object", f"object '{oid}' is not declared in farm.json",
                f"did you mean '{hint[0]}'?" if hint else "add the object to farm.json → objects first", "object")
            continue
        mx = ob.get("matrix")
        mspec = smap["matrices"].get(mx)
        if mspec is None:
            continue
        if not c["parameter"]:
            add("error", "parameter-missing", "parameter is empty", "write the analyte, e.g. PFOS", "parameter")
            continue
        params = {k.lower(): k for k in mspec["parameters"]}
        pkey = params.get(c["parameter"].lower())
        evidence = c["evidence"].lower()
        if evidence not in EVIDENCE:
            add("error", "evidence-class", f"evidence must be one of {', '.join(EVIDENCE)}, got '{c['evidence']}'",
                "a value that was never measured is not a row: it is a gap, registered by the passport", "evidence")
            continue
        spec = mspec["parameters"].get(pkey) if pkey else None
        if spec is None:
            add("warning", "parameter-not-mapped", f"'{c['parameter']}' has no reference rows for matrix '{mx}': reported, not coloured",
                "to screen it, add the parameter and its reference rows to core/screening-map.json")
        # numbers
        nums, bad = {}, False
        for col in ("value", "reporting_limit", "detection_limit", "uncertainty", "low", "high"):
            v, prob = parse_number(c[col])
            nums[col] = v
            if prob:
                bad = True
                fixes = {"censored-as-text": "write '<' in the qualifier column, leave value empty and put the limit in reporting_limit",
                         "decimal-comma": f"use a decimal point: {c[col].replace(',', '.')}",
                         "not-a-number": "write a number, or leave the cell empty",
                         "negative": "a concentration cannot be negative — check the laboratory report"}
                add("error", prob, f"'{c[col]}' is not a usable {col.replace('_', ' ')}", fixes[prob], col)
        if bad:
            continue
        qual = c["qualifier"].strip()
        if qual not in ("",) + CENSORING_QUALIFIERS:
            add("error", "qualifier", f"qualifier '{qual}' is not known",
                "leave empty for a quantified result; '<' below the reporting limit; 'J' estimated below the reporting limit", "qualifier")
            continue
        censored = qual in CENSORING_QUALIFIERS
        # unit
        unit = c["unit"]
        factor, basis = 1.0, True
        if not unit:
            add("error", "unit-missing", "unit is empty", "copy the unit from the laboratory report", "unit")
            continue
        if spec is not None:
            uset = smap["unit_sets"][spec["unit_set"]]
            factor, basis, wet = unit_factor(unit, uset)
            if wet:
                add("error", "wet-weight", f"'{unit}' is wet weight; the references are dry weight",
                    "convert with the sample's moisture content and state 'dw', or ask the laboratory for dry weight", "unit")
                continue
            if factor is None:
                add("error", "unit-not-accepted", f"unit '{unit}' is not accepted for {c['parameter']} in {mx}",
                    f"use one of: {', '.join(uset['aliases'])}", "unit")
                continue
        canon = smap["unit_sets"][spec["unit_set"]]["canonical"] if spec else unit
        scale = lambda x: None if x is None else x * factor
        value, rl, dl = scale(nums["value"]), scale(nums["reporting_limit"]), scale(nums["detection_limit"])
        low, high, unc = scale(nums["low"]), scale(nums["high"]), scale(nums["uncertainty"])
        usable = evidence == "measured"
        # evidence-specific rules
        if evidence == "measured":
            if not basis:
                add("warning", "basis-not-stated", "dry or wet basis not stated; the references are dry weight",
                    "write 'µg/kg dw' when the laboratory reports dry weight")
            if censored and rl is None:
                add("error", "rl-missing", "a result below the reporting limit needs that limit",
                    "copy the reporting limit from the laboratory report; a censored value is never 0 and never missing", "reporting_limit")
                continue
            if not censored and value is None:
                add("error", "value-missing", "a measured result has no value",
                    "write the value, or '<' with the reporting limit; a parameter that was not analysed is a gap, not a row", "value")
                continue
            if qual == "J":
                add("warning", "estimated-value", "estimated value (J) is treated as censored: bounds [0, reporting limit]")
            if rl is not None and dl is not None and rl < dl:
                add("error", "rl-below-dl", "reporting limit is below the detection limit", "check the two limits on the report")
                continue
        elif evidence == "modelled":
            usable = False
            if low is None or high is None or low > high:
                add("error", "model-range", "a modelled row needs its range: low ≤ high",
                    "copy the model's range; a model never sets a colour, it is compared with the measurement", "low/high")
                continue
            if not c["source"]:
                add("error", "model-source-missing", "a modelled row must name its model",
                    "e.g. examples/reconstruct.py, or the model and its inputs", "source")
                continue
        else:
            usable = False
            add("warning", "remote-no-colour", "a remote value never sets a colour alone; it is printed as context")
        # date
        sampled = c["sampled"]
        key = None
        if sampled == "":
            if evidence != "modelled":
                add("error", "date-missing", "sampling date is empty",
                    "write YYYY-MM-DD, YYYY-MM or YYYY; a synthetic value whose source gives no date says 'not stated'", "sampled")
                continue
        else:
            key, prob = parse_date(sampled, today)
            if prob == "format":
                add("error", "date-format", f"'{sampled}' is not a date",
                    "write YYYY-MM-DD, YYYY-MM or YYYY; 'not stated' only for a synthetic value whose source gives no date", "sampled")
                continue
            if prob == "future":
                add("error", "date-in-future", f"sampling date {sampled} is after the run date {today}",
                    "check the year; a result cannot come from the future", "sampled")
                continue
            if key is None and evidence == "measured":
                if synthetic:
                    add("warning", "date-not-stated", "sampling date not stated in the source")
                else:
                    add("error", "date-missing", "a real result needs its sampling date",
                        "copy the sampling date from the chain-of-custody form", "sampled")
                    continue
        # provenance
        method = c["method"]
        mvalid = None
        if evidence == "measured":
            if not method:
                add("error", "method-missing", "method is empty",
                    "write the method from the report; for a synthetic value whose source names none, write 'not stated'", "method")
                continue
            if method.lower() == NOT_STATED:
                if synthetic:
                    add("warning", "method-not-stated", "method not stated in the source")
                else:
                    add("error", "method-missing", "a real result needs its analytical method",
                        "copy the method from the laboratory report", "method")
                    continue
            elif spec is not None and spec["methods"]:
                mvalid = method_ok(method, spec["methods"])
                if not mvalid:
                    usable = False
                    add("warning", "method-not-valid",
                        f"'{method}' is not validated for {c['parameter']} in {mx}: the result is printed grey",
                        f"re-analyse by {' or '.join(spec['methods'])} (references/methods.md)", "method")
            if not c["laboratory"]:
                add("error", "lab-missing", "laboratory is empty", "name the laboratory; a synthetic farm writes 'synthetic'", "laboratory")
                continue
        # reporting limit against the lowest reference (status-rules §4; methods.md)
        if censored and spec is not None and rl is not None:
            vals = [packs[r["row"]]["value"] for r in spec["references"] if isinstance(packs[r["row"]].get("value"), (int, float))]
            if vals and rl >= min(vals):
                add("warning", "rl-above-reference",
                    f"reporting limit {rl:g} {canon} is not below the lowest reference {min(vals):g} {canon}: the status depends on censoring",
                    "ask the laboratory for a lower reporting limit (it goes into the sampling plan)", "reporting_limit")
        rep.rows.append(Row(line=n, object=oid, matrix=mx, parameter=pkey or c["parameter"], sampled=sampled or NOT_STATED,
                            order_key=key or ("", n), value=value, censored=censored, qualifier=qual, rl=rl, dl=dl,
                            uncertainty=unc, unit_in=unit, unit=canon, method=method, method_valid=mvalid,
                            laboratory=c["laboratory"], evidence=evidence, low=low, high=high, source=c["source"],
                            mapped=spec is not None, usable=usable))

    # events: one value per object, parameter and date; order must be known for a series
    groups: dict = {}
    for r in rep.rows:
        if r.evidence == "measured":
            groups.setdefault((r.object, r.parameter), []).append(r)
    for (oid, par), rs in groups.items():
        lines = [r.line for r in rs]
        dated = [r.sampled for r in rs if r.sampled != NOT_STATED]
        dup = sorted({d for d in dated if dated.count(d) > 1})
        if dup:
            rep.add("error", "duplicate-event", w, f"{oid} {par}: more than one result on {', '.join(dup)}",
                    "the status rules count sampling events: report one value per event (the mean of laboratory duplicates)", oid, lines)
        if len(rs) > 1 and len(dated) < len(rs):
            rep.add("error", "order-unknown", w, f"{oid} {par}: {len(rs)} results but not all dated — their order cannot be set",
                    "date every result of a series; the red rule needs consecutive events", oid, lines)


def merged(messages: list) -> list:
    """For display: one warning per (code, text), its lines and objects joined, so ten soil rows give one message."""
    out, seen = [], {}
    for m in messages:
        if m.level != "warning" or not m.lines:
            out.append(m)
            continue
        k = (m.code, m.text, m.col)
        if k in seen:
            prev = seen[k]
            prev.lines = sorted(set(prev.lines + m.lines))
            if m.obj and m.obj not in prev.obj.split(", "):
                prev.obj = f"{prev.obj}, {m.obj}" if prev.obj else m.obj
            continue
        seen[k] = Message(m.level, m.code, m.where, m.text, m.fix, m.obj, list(m.lines), m.col)
        out.append(seen[k])
    return out


def validate(folder: str | Path, today: date | None = None, smap: dict | None = None) -> Report:
    folder = Path(folder)
    today = today or date.today()
    rep = Report(folder=str(folder), today=today.isoformat())
    smap = smap or load_map()
    packs = load_pack_rows(smap)
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import indicator_select as isel
        cat_ids = {r["id"] for r in isel.load_catalogue(ROOT / "core" / "indicators" / "farm-indicators.psv")}
    except Exception:  # catalogue unavailable: indicator ids are not checked
        cat_ids = None
    fpath, mpath = folder / "farm.json", folder / "measurements.csv"
    for p in (fpath, mpath):
        if not p.exists():
            rep.add("error", "file-missing", p.name, f"{p} not found", "an input folder holds farm.json and measurements.csv")
    if rep.errors:
        return rep
    try:
        farm = json.loads(fpath.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        rep.add("error", "json", f"farm.json line {e.lineno}", f"not valid JSON: {e.msg}", "check commas and quotes near that line")
        return rep
    rep.farm = farm
    synthetic = check_farm(rep, farm, smap, cat_ids)
    check_rows(rep, mpath, smap, packs, today, synthetic)
    return rep


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in argv
    today = None
    if "--date" in argv:
        today = date.fromisoformat(argv[argv.index("--date") + 1])
        del argv[argv.index("--date"):argv.index("--date") + 2]
    args = [a for a in argv if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 2
    try:
        rep = validate(args[0], today)
    except (OSError, UnicodeDecodeError) as e:
        print(f"error: cannot read the input: {e}", file=sys.stderr)
        return 2
    if as_json:
        print(json.dumps({"folder": rep.folder, "date": rep.today, "errors": len(rep.errors), "warnings": len(rep.warnings),
                          "messages": [dict(asdict(m), place=m.place) for m in merged(rep.messages)]}, ensure_ascii=False, indent=1))
    else:
        shown = merged(rep.messages)
        for m in shown:
            print(m.line())
        nw = sum(1 for m in shown if m.level == "warning")
        print(f"\n{len(rep.errors)} error(s), {nw} warning(s) — {rep.folder}")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
