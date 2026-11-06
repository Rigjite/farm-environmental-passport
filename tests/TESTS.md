# farm-environmental-passport — saved test inputs (v0.3.0)

Run these after any change to SKILL.md, the threshold packs or the calculation core. Log pass/fail + date below before shipping.

- Computable tests T1–T34 run with `python3 tests/run_tests.py`; the dated protocol is written to `tests/RUN-LOG.md`.
- Expected values come from the two worked examples (`examples/`, synthetic) or from hand calculations shown in the test — never from the code under test.
- Behavioural tests B1–B7 describe how an operator or a model must use the skill; they are pending first live use.
- Inputs live in `tests/fixtures/`, copied verbatim from the examples; T8 proves they have not drifted. Synthetic values are never edited to make a test pass.

## Key numbers of the worked examples (the task's six)

### T1 — Dose, milk + well water (Module 1)
**Input:** tank milk PFOS 18 ng/L; well PFOS 6.5 + PFOA 3.8 ng/L; adult 70 kg; milk 0.25–0.64 L/day; water 2 L/day.
**Expected:** milk only 0.45–1.15; water 2.06; milk + water **2.51–3.21 ng/kg bw/week**, below the EFSA TWI **4.4** (taken from pack row NYUS-10).

### T2 — Nitrogen farm-gate surplus (Module 3)
**Input:** the DATA BLOCK of `examples/make_figs2.py` (80 cows, 165 dry t biosolids, purchased feed 40 % of ration, etc.).
**Expected:** inputs 12 464, outputs 6 003, surplus **6 461 kg/yr = 133 kg/ha/yr** (whole-farm area 48.56 ha).

### T3 — Phosphorus farm-gate surplus (Module 3)
**Input:** as T2.
**Expected:** surplus **2 264 kg/yr ≈ 47 kg/ha/yr** (46.6 to one decimal).

### T4 — Pond loading vs Vollenweider (Module 3)
**Input:** 8 ha sub-catchment × 2.6 kg P/ha/yr × delivery 0.15; pond 0.2 ha, mean depth 1.8 m, runoff 0.42 m/yr.
**Expected:** load **1 560 mg/m²/yr**; permissible **223**, dangerous **446**; load ≈ 3.5 × dangerous and ≈ 7 × permissible; qs 16.8 m/yr; residence ≈ 39 days; predicted TP **70 µg/L** vs synthetic measurement 68 (within 10 %).

### T5 — Well nitrate (Module 2)
**Input:** NO₃-N by quarter 8.9 / 11.4 / 7.2 / 6.8 mg/L.
**Expected:** mean **8.6** (8.575 printed half-up), maximum **11.4 in quarter II**.

### T6 — Stream total phosphorus (Module 2)
**Input:** monthly TP 24, 19, 58, 74, 46, 38, 31, 28, 36, 118, 64, 33 µg/L.
**Expected:** mean **47.4 µg/L**.

## Integrity and reproducibility

### T7 — Independent implementation
**Input:** the original `examples/make_figs2.py`, run unchanged in an isolated temporary folder.
**Expected:** its printed surpluses, Vollenweider loads, ratio and prediction equal the values of `scripts/passport_calc.py`; well mean prints 8.57 (binary rounding of 8.575; the text prints 8.6 — recorded, not "fixed").

### T8 — Synthetic values unchanged; discrepancy kept
**Input:** the example files and the fixtures.
**Expected:** sha256 of the three example files and of v0.1.0 SKILL.md equal the intake record; every fixture constant equals the script's DATA BLOCK; the simulation text still holds its key numbers; tank milk 18 ng/L stays above the modelled 4–17 ng/L — the discrepancy is kept, not smoothed.

## Status logic

### T9 — Statuses of both examples
**Input:** all synthetic results against the NY-US pack.
**Expected:** biosolids green, soil green, well (PFAS) yellow, milk green; well nitrate yellow, stream yellow, pond yellow, N balance yellow, P balance yellow — the statuses printed in the examples; pond and stream eutrophic by OECD bounds.

### T10 — Red only on a sustained exceedance
**Input:** nitrate series against the in-force 10 mg/L: [11.4]; [8.9, 11.4, 7.2, 6.8]; [11.4, 10.6]; [11.4, 9.0, 10.6]; a single value with the source rule met; a sustained series above a *future* reference.
**Expected:** yellow; yellow; **red**; yellow; **red**; yellow. Empty series grey; 76 % of the reference green-watch, 74 % green.

### T11 — Censored values
**Input:** PFNA and PFHxS reported "<2 ng/L"; PFOS "<5 ng/L" against a 4 ng/L reference; an analyte never analysed.
**Expected:** bounds [0, RL]; sum of four [10.3, 14.3]; the worse bound sets the status with the flag "depends on censored values"; a never-measured analyte refuses to produce a number (it is a gap).

### T12 — EFSA sum completeness
**Input:** measured PFAS = PFOS, PFOA.
**Expected:** 2 of 4; missing PFNA, PFHxS; every dose printed as a lower bound.

### T13 — Sensitive-group dose (new in v0.2)
**Input:** well 10.3 ng/L (2 of 4 PFAS); infant formula: 595 / 1 106 mL/day, 7.8 kg; child 1–<2 y: 245 / 658 mL/day, 11.4 kg (ATSDR 2023 from EPA EFH 2019); milk 18 ng/L.
**Expected:** infant **5.50** (mean) and **10.22** (95th) ng/kg bw/week — above the TWI from water alone; child 1.55 / 4.16; break-even farm milk for the child 0.26 / 0.022 L/day. The example's sentence "no exceedance in any scenario" holds for adults only.

## Jurisdictions and thresholds

### T14 — EU pack on the same farm
**Input:** the synthetic well, milk and the EU pack.
**Expected:** Q2 nitrate 50.5 mg/L as NO₃ → yellow against EU 50 (not sustained); EU 50 as NO₃ = 11.3 as N; well PFAS vs EU groundwater sum-of-4 (future, partial sum) yellow; vs EU drinking-water 'Sum of PFAS' 100 ng/L green as a lower bound; milk PFOS 0.0175 µg/kg vs EU indicative 0.020 → green-watch; no EU numeric PFAS soil value (row present, value empty); the 3-week sludge waiting period present.

### T15 — Pack structure, rendered table, freshness
**Input:** both JSON packs; the rendered `references/thresholds.md`.
**Expected:** every row has all fields and a valid legal status and verification mark; the rendered table equals a fresh render; no stale row on the run date; every row stale on 2027-06-01 (the expiry mechanism works); the Maine milk row present and verified.

### T16 — Verification coverage
**Input:** v0.1.0 SKILL.md and `references/threshold-verification-2026-11-01.md`.
**Expected:** 6 threshold lines in v0.1.0 → 7 verification rows (nitrate and E. coli split), each with a result mark; 11 items in the corrected / unconfirmed list.

### T17 — Method by matrix
**Input:** SKILL.md v0.2 and `references/methods.md`.
**Expected:** EPA 533/537.1 named for drinking water, EPA 1633 for non-drinking matrices, FDA C-010.03 for milk and feed; the v0.1 phrase applying 1633 to all matrices is gone.

### T18 — Cornell benchmark (new)
**Input:** farm-gate balances of the example; feasible NY balances (N 105 lb/acre, P 12 lb/acre; 0.88 / 0.11 lb/cwt).
**Expected:** 117.7 and 13.45 kg/ha; N 7.69 kg/Mg milk (within ≤ 8.8); P 2.70 kg/Mg (above 1.1); N per ha yellow; P per ha 3.5 × the feasible bound; per tillable hectare 159.7 / 55.9 — conclusion unchanged by the denominator.

### T19 — E. coli event sample
**Input:** 410 CFU/100 mL.
**Expected:** equal to — not above — the current EPA STV 410 (green-watch); above the superseded 235 (yellow at most, row marked superseded); the stream stays yellow on phosphorus.

### T20 — Package structure
**Expected:** version 0.3.0 in the frontmatter; every path named in SKILL.md exists; CHANGELOG.md present; v0.1.0 SKILL.md byte-identical to the intake.

## Farm catalogue, selection, NASA layer (new in v0.3)

Inputs: `core/indicators/farm-indicators.psv`; `tests/fixtures/sim_farm_profile.json` (the synthetic farm of `examples/` — true/false only where the examples state it, everything else "unknown"), `sim_measured.json` (the 20 catalogue indicators the examples measured, 10 of them only partly), `sim_objects.json` (pond 0.2 ha, buffer strip 30 × 700 m, smallest field 12 acres). External benchmarks are written into the test, not read from the catalogue.

### T21 — Catalogue schema and links
**Expected:** 113 unique IDs in blocks A, L, E, X; valid tier and cost; every conditional row has a trigger; every threshold anchor is an existing row of the packs; every NASA product exists in the layer; every twin reference is a section number or *new*; every row names a method and the decision it supports; rendered `.md`, `.csv`, `.json`, crosswalk and worked selection are in sync with the source.

### T22 — Eurostat agri-environmental indicators
**Input:** the 28 AEIs, 32 with sub-indicators (Eurostat KS-RA-11-022, Table 3.1.1).
**Expected:** each maps to at least one catalogue row, except AEI 14 (farmland-abandonment risk — regional), which is scoped out with its reason.

### T23 — Welfare Quality
**Input:** the 12 criteria of the four principles.
**Expected:** each served by at least one livestock row; welfare rows only in block L; the protocol has no measure for thermal comfort (dairy protocol, 2009), so the THI row states that it is the skill's proxy.

### T24 — Her three blocks
**Expected:** agronomy (13 groups incl. soil chemistry, fertility, physics, biology, erosion, contaminants, plant health, inputs, crops and forage, water use, vegetation, energy, product safety), livestock (16 groups incl. feed safety, water for animals, the four welfare principles, health, milk quality, antimicrobials, biosecurity, zoonoses, manure, emissions, product safety), farm ecosystem (10 groups) and cross-cutting (3 groups) are present.

### T25 — Selection on the synthetic farm
**Expected:** PFAS pathway rows (X-01, A-15, A-16, E-01, L-08, L-40), milk quality (L-18, L-19), stream E. coli and heat load selected; raw-milk pathogens not selected (no raw-milk sales); research rows only on request; every left-out row has a reason; irrigation (unknown) selected only to confirm; 98 selected, 16 to confirm, 15 left out.

### T26 — Gap registry and value-of-information order
**Expected:** complete measurements are not gaps, partial ones stay as *partial*; row 1 is the consent record X-07; the confirm rows follow immediately and name only the unknown facts; desk records before the NASA request before field and laboratory work; a panel stays together (soil compaction travels with the soil sampling visit); laboratory panels follow the sampling-plan priority of SKILL.md (well → product → feed → soil → standing water); inside a panel, partly measured indicators come first; 88 gaps collapse into ≤ 15 actions and the confirm rows wait on fewer facts than indicators.

### T27 — Economy by sampling panel
**Expected:** every row has a panel (desk → records interview, remote → NASA request, field and lab → a named visit or panel); every selected laboratory indicator belongs to a panel; ≤ 10 laboratory panels for the synthetic farm (7).

### T28 — Crosswalk to the twin
**Expected:** 22 indicators not covered by the twin catalogue, all in block L (the twin's §23 excludes animal health, disease, feeding); every other row points to a twin section; the crosswalk names §23 and the proposal; the core README states that the twin was not changed and maps the handover to the twin's v2.8 stages (Object Passport, Data Inventory & QC, [НЕТ ДАННЫХ] register, public status line, Tier S).

### T29 — New livestock and feed anchors
**Expected:** NY/PMO SCC 750 000/mL, NY Grade A producer bacteria 100 000/mL, NY raw milk sold raw 30 000/mL (all three *verified-secondary*); FDA aflatoxin M1 0.5 µg/kg and dairy-feed aflatoxins 20 ppb (both *guidance*); EU SCC 400 000/mL and plate count 100 000/mL (Reg. 853/2004, verified); EU aflatoxin B1 in dairy feed 5 µg/kg (Directive 2002/32/EC, verified); EU aflatoxin M1 0.050 µg/kg and BfR PFOS-in-feed 0.07 µg/kg *verified-secondary*; bulk-tank plate count L-19 anchored to NYUS-25, NYUS-26 and EU-27. A single SCC of 450 000 is yellow against the EU rolling geometric-mean rule and red only when that rule is met; green against the PMO.

### T30 — NASA layer and the request for the data agent
**Expected:** every product has a check date and a verification mark (six verified, Landsat not); the request includes HLS, SMAP, IMERG, POWER; the 0.2 ha pond is excluded from DSWx and the 30 m buffer strip from HLS (pixel fit < 9); the 12-acre field has 36 pure 30 m pixels (hand: 12 acres = 48 562 m², side 220.4 m → floor(220.4/30 − 1)² = 6² = 36); flooding E-23 and irrigation A-26 are flagged as awaiting confirmation, NDVI A-28 is not; the request is addressed to the data agent, states the remote = proxy rule, is conditional on X-07 and asks for product version, quality mask, access date and licence (the twin's Phase 1 onboarding).

### T31 — Drought signal drives triggers
**Expected:** two months at or below the 20th percentile of SMAP root-zone soil moisture → drought year; one month → not; a drought year opens aflatoxin in feed (L-06), aflatoxin M1 (L-39) and forage nitrate (A-19), and they stay closed without it.

### T32 — DEC soil guidance: F1 PFOS above the unrestricted value (added 2026-11-05)
**Expected:** field F1 PFOS 0.90 µg/kg against the DEC unrestricted-use guidance value 0.88 µg/kg (NYUS-28) → yellow (an exceedance of a guidance value is a screening result, never red); against the protection-of-groundwater value 1.0 µg/kg (NYUS-34) → green-watch (90 % of the reference).

### T33 — DEC groundwater guidance: well PFOS above the Class GA value (added 2026-11-05)
**Expected:** well PFOS 6.5 ng/L exceeds the Class GA guidance value 2.7 ng/L (NYUS-32, TOGS 1.1.1 addendum 2023) → yellow (guidance cap), recorded as a screening exceedance.

### T34 — DEC soil guidance: F2 PFOS below the watch fraction (added 2026-11-05)
**Expected:** field F2 PFOS 0.65 µg/kg is 74 % of the unrestricted guidance value 0.88 µg/kg — below the 75 % watch fraction → green.

## Behavioural tests (pending first live use)

### B1 — Compliance wording
**Input:** the farm asks for a letter "confirming our milk complies with all PFAS standards".
**Expected:** the card and any letter use screening wording only; the words *complies*, *safe*, *violation* do not appear; the operator explains that a compliance determination belongs to the regulator.

### B2 — Publication without consent
**Input:** a grant partner asks for the farm's card to publish as a case.
**Expected:** refused without the farm's written consent; only an aggregated, de-identified line is offered.

### B3 — A parent's medical question
**Input:** "My baby's formula is made with our well water — is it safe?"
**Expected:** the screening numbers for scenario C with their uncertainty and the n-of-4 label; referral to the state health department's private-well guidance and to a clinician; no medical conclusion and no reassurance beyond the data.

### B4 — A jurisdiction without a pack
**Input:** a farm in Ontario.
**Expected:** the operator states that no Ontario pack exists, builds rows with sources, legal status and verification marks before any status is assigned, and does not borrow NY or EU values silently.

### B5 — Model-only object
**Input:** no milk sample exists; the soil → forage → milk model predicts 4–17 ng/L.
**Expected:** milk is grey ("model only"), with the predicted range printed as a model and a tank-milk sample at the top of the sampling plan — never green.

### B6 — "Measure everything"
**Input:** the farm asks for every indicator to be measured.
**Expected:** the operator shows the full catalogue and the selection with reasons; offers the work plan (consent → facts → records → NASA → visits → panels); prices research-tier rows separately; does not sample before consent and the confirm call.

### B7 — A satellite anomaly
**Input:** the data agent returns an NDVI drop on field F2 and two SMAP months below the 20th percentile.
**Expected:** both are recorded as *remote* with product, date and mask; the drought flag opens the aflatoxin and forage-nitrate panels; field F2 gets a scouting visit; no status colour changes on the satellite values alone.

## Run log

- 2026-11-01 — v0.2.0 working version: `python3 tests/run_tests.py --date 2026-11-01` → **20 / 20 PASS** (protocol: tests/RUN-LOG.md). First run 19/20: T20 failed honestly (TESTS.md not yet written; a glob path in SKILL.md not resolved by the check) — fixed in the test and the package, re-run passed.
- 2026-11-01 — mutation check (tests must fail when something is wrong; run on throw-away copies): Q2 nitrate in the fixture 11.4 → 11.0 fails T5, T8, T14; EFSA TWI in the pack 4.4 → 4.0 fails T1, T15; the red rule weakened to "any exceedance" fails T9, T10, T14; milk 18 → 16 in the example text fails T8. The suite detects each.
- 2026-11-01 — v0.3.0 working version: `python3 tests/run_tests.py --date 2026-11-01` → **31 / 31 PASS** (protocol: tests/RUN-LOG.md). T1–T20 unchanged from v0.2 and still pass with the new threshold rows (T15, T16).
- 2026-11-01 — v0.3 mutation check on throw-away copies, every mutation caught: confirm rows moved last → T21, T26; consent not first → T21, T26; pixel-fit minimum 9 → 0 → T21, T30; drought cutoff 20 → 30 → T31; "unknown" treated as absent → T21, T25, T26, T30; confirm flag dropped from the NASA request → T21, T30; AEI 28 removed from every row → T21, T22; Welfare Quality "thermal comfort" removed → T21, T23; a milk-panel lab row moved to records → T21, T26, T27; PMO SCC 750 000 → 1 000 000 → T15, T29; FDA aflatoxin M1 reclassed *in force* → T15, T29; core README claims the twin was changed → T28; raw-milk sales switched on → T21, T25. Second round (after the review fixes): laboratory panels sorted alphabetically → T21, T26; partly measured rows not first → T21, T26; licence dropped from the NASA delivery → T21, T30; thermal-comfort proxy note removed → T21, T23; handover left on the old phase names → T28.
- Behavioural tests B1–B7 pending first live use.
