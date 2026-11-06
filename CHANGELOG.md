# farm-environmental-passport — Changelog

## v0.3.6 — 2026-11-06 — first public release (preview)

- Prepared for public release: README; licences by part — `LICENSE` (CC BY 4.0, method and documentation), `LICENSE-CORE` (CC BY-NC 4.0, everything under `core/`), `LICENSE-CODE` (Apache-2.0, code), with `LICENSE-NOTICE.md` mapping files to licences; `CITATION.cff` with the methods note (Zenodo, https://doi.org/10.5281/zenodo.24017216) as the preferred citation.
- The NASA data request is addressed to any data agent with NASA Earthdata access; without one, the operator downloads the same products from NASA Earthdata or AppEEARS. Internal team names removed from texts, scripts and tests.
- Illustration photographs are not part of the public package; their links are removed from the texts in force (the unchanged originals keep them as part of the intake record).
- `v0.1.0` moved to `archive/v0.1.0/`, unchanged; tests point to the new path.
- Primary sources added to the provenance register: soil-to-forage transfer factor, Simones et al. 2024 (doi:10.1021/acs.jafc.4c02078); PFOS secretion into milk, Kowalczyk et al. 2013 (doi:10.1021/jf304680j).
- Tests: 34/34.

## v0.3.5 — 2026-11-06

- Jurisdiction without a pack: rows are built first, nothing is borrowed silently, objects stay grey.
- DMM-7 tiers follow the primary text verbatim.
- Adult dose profile: the worked example keeps the ATSDR 2005 default (2 L/day, 70 kg) and prints the ATSDR 2023 sensitivity line (1.58–3.92 ng/kg bw/week); new cards use ATSDR 2023 for every age group.
- New section "First live use (pilot)": what the first real farm must record and when the skill counts as validated.
- Worked examples rewritten around the texts in force; semantic reconciliation with the Ecosystem Digital Twin farm map recorded.

## v0.3.4 — 2026-11-06

- Infant and young-child exposure factors checked against ATSDR (2023), Table 1 (EPA Exposure Factors Handbook 2019); PFAS example redaction 7; figures rebuilt.

## v0.3.3 — 2026-11-05

- Monte Carlo uncertainty block and first-order sensitivity indices for the PFAS example (`examples/uncertainty.py`, `reconstruct.py`); value of a quarterly well series.
- Figures with neutral series colours; status shown by outline and caption, not by series colour.

## v0.3.0 – v0.3.2 — 2026-11-01 to 2026-11-05

- Farm indicator catalogue (113 indicators: agronomy and soil 32, livestock 42, farm ecosystem 31, cross-cutting 8) with selection rules, gap registry, work plan and laboratory panels (`scripts/indicator_select.py`).
- NASA remote-sensing layer with resolutions checked against NASA sources and a pixel-fit rule (≥ 9 pure pixels).
- Shared core with the Ecosystem Digital Twin (`core/`, `core/crosswalk-twin.md`).
- Four mandatory dose scenarios, including an infant fed formula prepared with well water and a young child.

## v0.2.0 — 2026-11-01

- Threshold packs as data with legal status, date, determination rule and verification mark; line-by-line verification of the v0.1.0 pack (`references/threshold-verification-2026-11-01.md`).
- Status decision table and censored-value rules (`references/status-rules.md`); `scripts/passport_calc.py`.

## v0.1.0 — 2026-10-31

- First version: PFAS screening module and two synthetic worked examples (kept unchanged in `archive/v0.1.0/` and `examples/*-2026-10-31.md`).
