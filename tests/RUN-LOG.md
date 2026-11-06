# Test run — farm-environmental-passport v0.3.6

Date: 2026-11-06  ·  Python 3.13.18  ·  runner: tests/run_tests.py

**Result: 34 / 34 PASS**

| Test | Title | Result |
|---|---|---|
| T1 | Dose milk + well water vs EFSA TWI (Module 1) | PASS |
| T2 | Nitrogen farm-gate surplus (Module 3) | PASS |
| T3 | Phosphorus farm-gate surplus (Module 3) | PASS |
| T4 | Pond phosphorus loading vs Vollenweider criteria (Module 3) | PASS |
| T5 | Well nitrate: annual mean and quarterly maximum (Module 2) | PASS |
| T6 | Stream total phosphorus mean (Module 2) | PASS |
| T7 | Independent implementation: original make_figs2.py agrees with passport_calc | PASS |
| T8 | Synthetic values unchanged; model–measurement discrepancy kept | PASS |
| T9 | Statuses of both worked examples reproduced by the v0.2 decision table | PASS |
| T10 | Red only on a sustained exceedance | PASS |
| T11 | Censored values: bounds, sums, flag; never-measured is a gap | PASS |
| T12 | Completeness of the EFSA four-PFAS sum | PASS |
| T13 | Sensitive-group dose scenarios (new in v0.2) | PASS |
| T14 | EU pack applied to the synthetic farm (second jurisdiction) | PASS |
| T15 | Threshold packs: structure, rendered table in sync, freshness | PASS |
| T16 | Line-by-line verification covers every v0.1 threshold line | PASS |
| T17 | Analytical method by matrix | PASS |
| T18 | Nutrient balance against the Cornell NY feasible benchmark (new) | PASS |
| T19 | E. coli event sample against the verified references | PASS |
| T20 | Package structure; v0.1.0 untouched | PASS |
| T21 | Farm catalogue: schema, vocabulary, links to packs, NASA layer and twin | PASS |
| T22 | Completeness against the Eurostat agri-environmental indicators (external benchmark) | PASS |
| T23 | Completeness against the 12 Welfare Quality criteria | PASS |
| T24 | Her three blocks are complete: agronomy, livestock, farm ecosystem | PASS |
| T25 | Selection on the synthetic farm | PASS |
| T26 | Gap registry: complete vs partial, value-of-information order | PASS |
| T27 | Economy: laboratory work grouped into sampling panels | PASS |
| T28 | Crosswalk to the Ecosystem Digital Twin | PASS |
| T29 | New livestock and feed anchors: values and verification marks | PASS |
| T30 | NASA layer and the request for the data agent | PASS |
| T31 | Satellite drought signal drives triggers | PASS |
| T32 | DEC soil guidance: F1 PFOS above the unrestricted value (new 2026-11-05) | PASS |
| T33 | DEC groundwater guidance: well PFOS above the Class GA value (new 2026-11-05) | PASS |
| T34 | DEC soil guidance: F2 PFOS below the 75 % watch fraction (new 2026-11-05) | PASS |

## Detail

### T1 — Dose milk + well water vs EFSA TWI (Module 1): PASS

```
ok  milk only, ng/kg/wk: got [0.45, 1.15], expected [0.45, 1.15]
ok  water only, ng/kg/wk: got 2.06, expected 2.06
ok  milk + water, ng/kg/wk: got [2.51, 3.21], expected [2.51, 3.21]
ok  TWI from the pack: got 4.4, expected 4.4
ok  upper bound below TWI (adult scenario) — 3.212 < 4.4
```

### T2 — Nitrogen farm-gate surplus (Module 3): PASS

```
ok  N surplus, kg/yr: got 6461, expected 6461
ok  N surplus, kg/ha/yr: got 133, expected 133
ok  N input total (text: 12 464): got 12464, expected 12464
ok  N output with products (text: 6 003): got 6003, expected 6003
```

### T3 — Phosphorus farm-gate surplus (Module 3): PASS

```
ok  P surplus, kg/yr: got 2264, expected 2264
ok  P surplus, kg/ha/yr (≈47): got 47, expected 47
ok  P surplus, one decimal: got 46.6, expected 46.6
```

### T4 — Pond phosphorus loading vs Vollenweider criteria (Module 3): PASS

```
ok  areal load, mg/m2/yr: got 1560, expected 1560
ok  permissible, mg/m2/yr: got 223, expected 223
ok  dangerous, mg/m2/yr: got 446, expected 446
ok  load / dangerous: got 3.5, expected 3.5
ok  load / permissible (text: 7 times): got 7, expected 7
ok  predicted TP, µg/L: got 70, expected 70
ok  hydraulic load qs, m/yr (text 16.8): got 16.8, expected 16.8
ok  residence time, days (text ≈39): got 39, expected 39
ok  prediction within ±10 % of synthetic measurement 68
```

### T5 — Well nitrate: annual mean and quarterly maximum (Module 2): PASS

```
ok  mean NO3-N, mg/L: got 8.6, expected 8.6
ok  max NO3-N, mg/L: got 11.4, expected 11.4
ok  quarter of the max: got 'II', expected 'II'
```

### T6 — Stream total phosphorus mean (Module 2): PASS

```
ok  mean TP, µg/L: got 47.4, expected 47.4
```

### T7 — Independent implementation: original make_figs2.py agrees with passport_calc: PASS

```
ok  script finished (DONE printed)
ok  N surplus (script vs core): got (6461.0, 133.0), expected (6461.0, 133.0)
ok  P surplus (script vs core): got (2264.0, 46.6), expected (2264.0, 46.6)
ok  Vollenweider (script vs core): got (223.0, 446.0, 3.5, 70.0), expected (223.0, 446.0, 3.5, 70.0)
ok  well mean, 2 dp (script): got '8.57', expected '8.57'
ok  stream mean (script): got 47.4, expected 47.4
```

### T8 — Synthetic values unchanged; model–measurement discrepancy kept: PASS

```
ok  sha256 unchanged: examples/FARM-PFAS-SIMULATION-2026-10-31.md
ok  sha256 unchanged: examples/FARM-WATER-NUTRIENTS-SIMULATION-2026-10-31.md
ok  sha256 unchanged: examples/make_figs2.py
ok  sha256 unchanged: archive/v0.1.0/SKILL.md
ok  fixture = DATA BLOCK of make_figs2.py — all constants equal
ok  simulation text still contains 'PFOS 12 мкг/кг'
ok  simulation text still contains 'PFOS 6,5 нг/л, PFOA 3,8 нг/л'
ok  simulation text still contains 'PFOS 18 нг/л'
ok  simulation text still contains '4–17 нг/л'
ok  simulation text still contains '2,51–3,21'
ok  simulation text still contains '0,90 | 0,40'
ok  milk 18 ng/L stays above the model range 4–17 (discrepancy kept, not smoothed)
```

### T9 — Statuses of both worked examples reproduced by the v0.2 decision table: PASS

```
ok  Module 1 statuses: got {'biosolids': 'green', 'soil': 'green', 'well': 'yellow', 'milk': 'green'}, expected {'biosolids': 'green', 'soil': 'green', 'well': 'yellow', 'milk': 'green'}
ok  Modules 2–3 statuses: got {'well_nitrate': 'yellow', 'stream': 'yellow', 'pond': 'yellow', 'N_balance': 'yellow', 'P_balance': 'yellow'}, expected {'well_nitrate': 'yellow', 'stream': 'yellow', 'pond': 'yellow', 'N_balance': 'yellow', 'P_balance': 'yellow'}
ok  OECD class of the pond (TP 68, chl-a 21): got ('eutrophic', 'eutrophic'), expected ('eutrophic', 'eutrophic')
ok  OECD class of the stream mean (47.4): got 'eutrophic', expected 'eutrophic'
```

### T10 — Red only on a sustained exceedance: PASS

```
ok  single sample 11.4 above in-force MCL: got 'yellow', expected 'yellow'
ok  one quarter above, mean below [8.9, 11.4, 7.2, 6.8]: got 'yellow', expected 'yellow'
ok  two consecutive events above [11.4, 10.6]: got 'red', expected 'red'
ok  non-consecutive [11.4, 9.0, 10.6]: got 'yellow', expected 'yellow'
ok  source rule met (e.g. RAA) on a single reported value: got 'red', expected 'red'
ok  sustained above a FUTURE reference stays yellow: got 'yellow', expected 'yellow'
ok  no measurement -> grey: got 'grey', expected 'grey'
ok  7.6 = 76 % of 10 -> green-watch: got 'green-watch', expected 'green-watch'
ok  7.4 = 74 % of 10 -> green: got 'green', expected 'green'
```

### T11 — Censored values: bounds, sums, flag; never-measured is a gap: PASS

```
ok  ND bounds: got (0.0, 2.0), expected (0.0, 2.0)
ok  sum of 4 with two ND, [LB, UB]: got (10.3, 14.3), expected (10.3, 14.3)
ok  ND with RL 5 vs reference 4 -> worse bound reported: got 'yellow', expected 'yellow'
ok  flag 'depends on censored values' raised
ok  never-measured raises (must be a gap, not a number)
```

### T12 — Completeness of the EFSA four-PFAS sum: PASS

```
ok  measured of 4: got 2, expected 2
ok  missing analytes: got ['PFNA', 'PFHxS'], expected ['PFNA', 'PFHxS']
ok  dose must be printed as a lower bound
```

### T13 — Sensitive-group dose scenarios (new in v0.2): PASS

```
ok  infant formula with well water, mean (hand: 10.3*0.595*7/7.8): got 5.5, expected 5.5
ok  infant, 95th percentile (hand: 10.3*1.106*7/7.8): got 10.22, expected 10.22
ok  infant mean already above the TWI with 2 of 4 PFAS — 5.50 > 4.4
ok  child 1–<2 y water only, mean / 95th: got (1.55, 4.16), expected (1.55, 4.16)
ok  break-even farm milk for the child, L/day (mean / 95th water): got (0.26, 0.022), expected (0.26, 0.022)
ok  adult-only conclusion 'no exceedance in any scenario' is not general
```

### T14 — EU pack applied to the synthetic farm (second jurisdiction): PASS

```
ok  Q2 nitrate as NO3, mg/L (11.4 × 4.427): got 50.5, expected 50.5
ok  well nitrate vs EU 50 mg/L NO3: got 'yellow', expected 'yellow'
ok  EU 50 as NO3 = 11.3 as N: got 11.3, expected 11.3
ok  well vs EU groundwater sum-of-4 (future, partial sum = lower bound): got 'yellow', expected 'yellow'
ok  well vs EU drinking water 'Sum of PFAS' 100 ng/L (2 of 20 = lower bound): got 'green', expected 'green'
ok  milk PFOS, µg/kg (18 / 1000 / 1.03): got 0.0175, expected 0.0175
ok  milk PFOS vs EU indicative 0.020 µg/kg -> watch (87 %): got 'green-watch', expected 'green-watch'
ok  EU has no numeric PFAS value for agricultural soil (row EU-17 value null)
ok  EU sludge waiting period before grazing ≥ 3 weeks present (EU-16)
ok  same object, two packs, different binding reference — both printed
```

### T15 — Threshold packs: structure, rendered table in sync, freshness: PASS

```
ok  NY-US: all 36 rows complete, vocabulary valid
ok  NY-US: stale rows on 2026-11-06: got [], expected []
ok  NY-US: every row stale on 2027-06-01 (mechanism works)
ok  EU: all 30 rows complete, vocabulary valid
ok  EU: stale rows on 2026-11-06: got [], expected []
ok  EU: every row stale on 2027-06-01 (mechanism works)
ok  core/thresholds.md equals a fresh render of the JSON packs
ok  EU pack covers drinking water, EFSA, soil
ok  Maine milk line present and verified
```

### T16 — Line-by-line verification covers every v0.1 threshold line: PASS

```
ok  threshold lines in v0.1.0: got 6, expected 6
ok  rows in the verification table (6 lines, nitrate/E. coli split): got 7, expected 7
ok  each row carries a result mark
ok  items in the unconfirmed / corrected list: got 11, expected 11
ok  pack marks counted — corrected: 5, not-verified: 2, verified: 35, verified-secondary: 24
```

### T17 — Analytical method by matrix: PASS

```
ok  SKILL names EPA 533 or 537.1 for drinking water
ok  SKILL names EPA 1633 for non-drinking matrices
ok  SKILL names a food method for milk (FDA C-010.03)
ok  v0.1 phrase 'EPA 1633 or the current analogue' removed
ok  methods.md has the matrix table
```

### T18 — Nutrient balance against the Cornell NY feasible benchmark (new): PASS

```
ok  105 lb/acre in kg/ha: got 117.7, expected 117.7
ok  12 lb/acre in kg/ha: got 13.45, expected 13.45
ok  N per Mg milk (feasible ≤ 8.8): got 7.69, expected 7.69
ok  P per Mg milk (feasible ≤ 1.1): got 2.7, expected 2.7
ok  N per ha whole farm -> status: got 'yellow', expected 'yellow'
ok  P per ha / feasible upper bound: got 3.5, expected 3.5
ok  per tillable ha N / P: got (159.7, 55.9), expected (159.7, 55.9)
ok  conclusion robust to denominator (both above feasible)
```

### T19 — E. coli event sample against the verified references: PASS

```
ok  410 vs EPA 2012 STV 410 (equal, not above): got 'green-watch', expected 'green-watch'
ok  410 vs superseded 235 -> yellow at most, row marked superseded: got 'yellow', expected 'yellow'
ok  legal status of the 235 row: got 'superseded', expected 'superseded'
ok  stream stays yellow on phosphorus (orientation): got 'yellow', expected 'yellow'
```

### T20 — Package structure; v0.1.0 untouched: PASS

```
ok  frontmatter version 0.3.6
ok  all 27 paths named in SKILL.md exist
ok  CHANGELOG.md present
ok  v0.1.0 SKILL.md unchanged
```

### T21 — Farm catalogue: schema, vocabulary, links to packs, NASA layer and twin: PASS

```
ok  indicators in the catalogue: got 113, expected 113
ok  IDs unique
ok  blocks: got ['A', 'E', 'L', 'X'], expected ['A', 'E', 'L', 'X']
ok  tiers valid
ok  cost classes valid
ok  every conditional row has a trigger
ok  every anchor is an existing threshold row — 21 anchored rows
ok  every NASA product exists in the layer
ok  every twin reference is a section number or 'new'
ok  every row has a method and a decision it supports
ok  rendered catalogue, CSV, JSON, crosswalk and worked selection are in sync
```

### T22 — Completeness against the Eurostat agri-environmental indicators (external benchmark): PASS

```
ok  AEIs (incl. sub-indicators): got 32, expected 32
ok  every AEI mapped or explicitly scoped out
ok  scoped out (with reason): got ['14'], expected ['14']
ok  no unknown AEI codes in the catalogue
```

### T23 — Completeness against the 12 Welfare Quality criteria: PASS

```
ok  all 12 criteria served by at least one livestock indicator — 12/12
ok  welfare rows sit in the livestock block
ok  thermal comfort: the protocol has no measure — the THI row says it is the skill's proxy
```

### T24 — Her three blocks are complete: agronomy, livestock, farm ecosystem: PASS

```
ok  block A: 13 required groups present — 32 indicators
ok  block L: 16 required groups present — 42 indicators
ok  block E: 10 required groups present — 31 indicators
ok  block X: 3 required groups present — 8 indicators
```

### T25 — Selection on the synthetic farm: PASS

```
ok  L-18 selected (Bulk-tank somatic cell count)
ok  L-19 selected (Bulk-tank bacterial (plate) count)
ok  X-01 selected (Biosolids source — PFOS, PFOA and method list)
ok  A-15 selected (Heavy metals in soil: Cd, Cu, Ni, Pb, Zn, Hg)
ok  A-16 selected (PFAS in soil (EFSA four + method list))
ok  E-01 selected (Drinking well — PFAS (EFSA four + method list))
ok  L-08 selected (PFAS in forage and feed (EFSA four + list))
ok  L-40 selected (PFAS in milk, meat or eggs (EFSA four + list))
ok  E-06 selected (Stream — E. coli or enterococci)
ok  L-13 selected (Heat load: temperature-humidity index above the heat-stress level)
ok  L-41 raw-milk pathogens not selected: no raw-milk sales
ok  research rows not selected unless requested
ok  every unselected indicator carries a reason
ok  A-26 irrigation selected only to confirm (profile: unknown)
ok  selected / confirm / not selected: got (98, 16, 15), expected (98, 16, 15)
ok  a requested research indicator is selected
```

### T26 — Gap registry: complete vs partial, value-of-information order: PASS

```
ok  complete measurements are not gaps
ok  partial measurements stay as 'partial' gaps
ok  first row: farm consent (nothing starts without it): got 'X-07', expected 'X-07'
ok  confirmation of unknown facts comes right after consent — rows 2–17
ok  each confirm row names the facts to confirm (only the unknown ones)
ok  desk records before NASA request before field and laboratory work
ok  a laboratory panel stays together (compaction travels with the soil sampling visit)
ok  laboratory panels follow the sampling-plan priority in SKILL.md: well → product → feed → soil → standing water — well → milk → feed → soil → soil-nitrate → pond → stream
ok  inside a panel, partly measured indicators come first (complete what was started)
ok  88 gaps collapse into ≤ 15 actions; 16 confirm rows wait on 11 facts — 14 actions
```

### T27 — Economy: laboratory work grouped into sampling panels: PASS

```
ok  catalogue has a sampling-panel column
ok  desk rows → records interview, remote rows → NASA request, field and lab rows → a named visit or panel
ok  every selected laboratory indicator belongs to a panel
ok  lab panels for the synthetic farm ≤ 10 (one visit can serve many indicators) — 7: well, milk, feed, soil, soil-nitrate, pond, stream
```

### T28 — Crosswalk to the Ecosystem Digital Twin: PASS

```
ok  indicators the twin does not cover: got 22, expected 22
ok  all of them in the livestock block (the twin's §23 excludes animal health, disease, feeding)
ok  every other indicator points to at least one twin section
ok  crosswalk names §23 and the proposal
ok  core README states that the twin was not changed
ok  handover mapped to the twin's v2.8 stages (Object Passport, Data Inventory & QC, [НЕТ ДАННЫХ] register, public status line)
```

### T29 — New livestock and feed anchors: values and verification marks: PASS

```
ok  NYUS-22 somatic cell count = 750000 cells/mL [verified-secondary]
ok  NYUS-23 aflatoxin M1 = 0.5 µg/kg (ppb) [verified]
ok  NYUS-24 total aflatoxins (B1+B2+G1+G2) = 20 µg/kg (ppb) [verified]
ok  NYUS-25 bacterial count = 100000 per mL [verified-secondary]
ok  NYUS-26 bacterial count = 30000 per mL [verified-secondary]
ok  EU-26 somatic cell count = 400000 cells/mL [verified]
ok  EU-27 plate count at 30 °C = 100000 CFU/mL [verified]
ok  EU-28 aflatoxin M1 = 0.05 µg/kg [verified-secondary]
ok  EU-29 aflatoxin B1 = 5 µg/kg (0.005 mg/kg, feed at 12 % moisture) [verified]
ok  EU-30 PFOS = 0.07 µg/kg feed [verified-secondary]
ok  secondary-only rows are marked provisional (EU-28, EU-30; NY milk rows read via a reproduction of 1 NYCRR §2.8)
ok  EU-29 confirmed in Directive 2002/32/EC Annex I (consolidated text): got 'verified', expected 'verified'
ok  bulk-tank plate count anchored for NY (Grade A producer, raw-milk sales) and the EU
ok  FDA action levels classed as guidance (colour capped at yellow)
ok  SCC 450 000 vs EU 400 000, single month: got 'yellow', expected 'yellow'
ok  SCC 450 000 vs EU rule met (rolling 3-month geometric mean above): got 'red', expected 'red'
ok  SCC 450 000 vs US PMO 750 000: got 'green', expected 'green'
```

### T30 — NASA layer and the request for the data agent: PASS

```
ok  every product row carries a check date and verification mark
ok  products verified against NASA sources: got ['DSWx', 'ECOSTRESS', 'HLS', 'IMERG', 'POWER', 'SMAP'], expected ['DSWx', 'ECOSTRESS', 'HLS', 'IMERG', 'POWER', 'SMAP']
ok  request includes HLS, SMAP, IMERG, POWER — ['DSWx', 'ECOSTRESS', 'HLS', 'IMERG', 'LANDSAT', 'POWER', 'SMAP']
ok  0.2 ha pond excluded from DSWx (pixel fit)
ok  30 m buffer strip excluded from HLS (pixel fit)
ok  smallest field F3 (12 acres) pure 30 m pixels: got 36, expected 36
ok  request addressed to the data agent and states the remote = proxy rule
ok  indicators that depend on an unconfirmed fact are flagged (flooding E-23 waits on 'floodplain', irrigation A-26 on 'irrigation')
ok  confirmed indicators are not flagged (NDVI A-28 on HLS)
ok  every requested product carries its verification mark; unverified ones are named
ok  request is conditional on the farm consent record
ok  delivery asks for what the twin's Phase 1 onboarding needs (version, date, quality mask, access date, licence)
```

### T31 — Satellite drought signal drives triggers: PASS

```
ok  two months at ≤ 20th percentile → drought year
ok  one month only → not a drought year
ok  drought year opens aflatoxin in feed (L-06), aflatoxin M1 (L-39), forage nitrate (A-19)
ok  without drought (and no other trigger) they stay closed
```

### T32 — DEC soil guidance: F1 PFOS above the unrestricted value (new 2026-11-05): PASS

```
ok  F1 PFOS value from fixture: got 0.9, expected 0.9
ok  F1 0.90 vs 0.88 (guidance) -> yellow: got 'yellow', expected 'yellow'
ok  F1 0.90 vs 1.0 (groundwater protection) -> green-watch (90 %): got 'green-watch', expected 'green-watch'
```

### T33 — DEC groundwater guidance: well PFOS above the Class GA value (new 2026-11-05): PASS

```
ok  well PFOS value from fixture: got 6.5, expected 6.5
ok  well 6.5 exceeds the GA guidance value 2.7
ok  exceedance of a guidance value -> yellow (screening cap): got 'yellow', expected 'yellow'
```

### T34 — DEC soil guidance: F2 PFOS below the 75 % watch fraction (new 2026-11-05): PASS

```
ok  F2 PFOS value from fixture: got 0.65, expected 0.65
ok  F2 share of the guidance value < 75 %
ok  F2 0.65 vs 0.88 -> green: got 'green', expected 'green'
```

Behavioural tests B1–B5 (tests/TESTS.md) are not executable here: pending first live use.
