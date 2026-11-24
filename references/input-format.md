# Input format — one farm, one folder (since v0.3.8)

A farm's input is one folder with two files: `farm.json` (the farm, its objects, consent and dose scenarios) and `measurements.csv` (one result per row, long format). Start from `assets/input-template/`; the synthetic farm in this format is `examples/synthetic-farm/`.

```bash
python3 scripts/validate_input.py FOLDER          # check only: every message names the place and the fix
python3 scripts/demo.py --farm FOLDER             # check, then write passport.json and answer-card.md into FOLDER
```

Errors stop the run and nothing is written. Warnings are printed and carried into the run record of the passport. Which parameters, units and methods are accepted for which matrix comes from `core/screening-map.json` (rendered: `core/screening-matrix.md`).

## 1. `farm.json`

| Field | Required | Meaning |
|---|---|---|
| `passport_input` | yes | format version: `farm-environmental-passport/input@1` |
| `farm_id` | yes | a short code; the farm's name stays private unless the farm agrees |
| `name` | no | free text |
| `synthetic` | yes | `true` only for an invented farm (every output is then labelled SYNTHETIC); a real farm is `false` |
| `jurisdiction` | yes | the threshold pack: `NY-US` in this version. A jurisdiction without a pack is refused — its rows are built first (SKILL.md) |
| `consent` | yes for a real farm | `recorded` (true/false), `date`, `scope`. A real farm without recorded consent (indicator X-07) is refused |
| `objects` | yes | one entry per sampled object: `id` (unique), `label` (say the depth for soil), `matrix` (a key of the screening map: `biosolids`, `soil`, `well-drinking`, `milk`), optional `dose_role` (`drinking_water` or `product`), optional `geometry` |
| `geometry` | no | a GeoJSON geometry (Point, Polygon, …) with [longitude, latitude] in WGS 84. A real farm's geometry is private: it enters the public layer only aggregated and with consent |
| `dose_scenarios` | yes when an object has a `dose_role` | the four mandatory scenarios (`off_farm_adult`, `resident_adult`, `infant_formula_well_water`, `young_child_resident`); each with `bw_kg`, `cases` (`water_l_day`, `milk_l_day`), `source` of the exposure factors, optional `break_even: true`. A case without a sourced intake is left without it — the card prints the break-even intake instead (`references/dose-scenarios.md`) |
| `profile` | no | farm components and triggers for indicator selection: `true`, `false` or `"unknown"` (never left out) — `scripts/indicator_select.py` |
| `coverage` | no | what the farm already has, by catalogue ID: `source`, `partial`, `missing` — feeds the gap registry |
| `pixel_fit` | no | small objects for the NASA pixel-fit check, by catalogue ID: `area_m2`, or `width_m` and `length_m` |

## 2. `measurements.csv`

UTF-8, comma-separated, one header row with exactly these columns (a cell that does not apply stays empty):

| Column | Meaning |
|---|---|
| `object` | the object's `id` from farm.json |
| `parameter` | the analyte as named in the screening map (PFOS, PFOA, PFNA, PFHxS, `nitrate (as N)`); another analyte is accepted, reported and not coloured |
| `sampled` | sampling date: `YYYY-MM-DD`, `YYYY-MM` or `YYYY`. A synthetic value whose source gives no date writes `not stated`; a real result must be dated. Empty only for a modelled row |
| `value` | the reported number, in `unit`, with a decimal point. Empty for a result below the reporting limit |
| `qualifier` | empty for a quantified result; `<` below the reporting limit; `J` estimated below the reporting limit (treated as censored) |
| `reporting_limit` | the laboratory's reporting limit; required for `<` and `J` |
| `detection_limit` | the method detection limit, if reported |
| `unit` | as reported; must be one of the accepted units for the parameter (`core/screening-matrix.md`, "Accepted units") |
| `uncertainty` | expanded uncertainty (±, same unit), if the laboratory reports it |
| `method` | the analytical method as on the report (e.g. `EPA 533`); a synthetic value whose source names none writes `not stated` |
| `laboratory` | the laboratory; a synthetic farm writes `synthetic` |
| `evidence` | `measured`, `modelled` or `remote` (`references/status-rules.md` §1). A value that was never measured is not a row — it is a gap |
| `low`, `high` | the range of a modelled value (required for `modelled`) |
| `source` | the laboratory report or file; for a modelled row, the model and its inputs (required) |

## 3. What the check enforces

**Errors** (nothing is computed): a missing or unknown column; an object not declared in farm.json; a result written as text (`<2`, `ND`) instead of the qualifier; a decimal comma; a negative or non-numeric value; a censored result without its reporting limit; a reporting limit below the detection limit; a unit that is not accepted, a nitrate result without its basis (as N or as NO₃), a wet-weight result for a solid; a date that is not a date or lies after the run date; two results for one object, parameter and date (the status rules count sampling events — report the mean of laboratory duplicates); a series whose dates are not all known; a modelled row without its range or its model; an empty method or laboratory; for a real farm — missing consent, a missing date, a method `not stated`; missing mandatory dose scenarios; an unknown matrix, indicator ID or profile value; a geometry that is not GeoJSON.

**Warnings** (computed, printed in the run record): a sampling date or a method `not stated` on a synthetic farm; a solid without its dry or wet basis (the references are dry weight); an estimated (`J`) value treated as censored; a reporting limit not below the lowest reference (the status then depends on censoring — the remedy is a lower limit, which goes into the sampling plan); a method not validated for the matrix (the result is printed grey, `references/methods.md`); a parameter with no reference row (reported, not coloured); a remote value (never a colour alone).

Three folders in `examples/bad-input/` show the messages: censored results written as text; units and objects; missing provenance on a real farm.

## 4. What comes out

`passport.json` (`farm-environmental-passport/passport@1`):

- `objects` — per object: status, the reference rows that set it (strongest legal weight first for yellow and red; the closest reference for green), every reference evaluated, the measurements, flags (partial panel, one sampling event in a medium that varies by season, model against measurement, method not valid, depends on censored values, never measured) with the closing sample;
- `groups` — the summary of a group of fields (`references/status-rules.md` §3a) and the fields flagged beside it;
- `dose` — the four scenarios (point values, share of the TWI), the completeness of the EFSA four, break-even intakes; a medium that enters a case but was never measured is named, never counted as zero;
- `indicators` — selection, facts to confirm, work plan, laboratory panels, gap registry, NASA request (when `profile` is given);
- `references_used` and `run_record` — skill version, run date and command, threshold pack and version, every row used with its check date and verification mark, rows stale on the run date, sha256 of the input files and of the core files, the input-check warnings.

`answer-card.md` is rendered from `passport.json` and changes no number. `python3 scripts/demo.py --check` confirms that the committed outputs of the synthetic farm equal a fresh run.
