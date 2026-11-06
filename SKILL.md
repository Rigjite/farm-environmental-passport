---
name: farm-environmental-passport
description: Build an independent environmental passport for a specific farm — input pathways, water and soil status, nutrient balances, contaminant screening (PFAS first module), a registry of what has never been measured, and a minimal sampling plan. Use when asked to assess a farm's environmental safety, biosolids history, well or irrigation water, nutrient export to water bodies, or the exposure a farm's product may carry. The skill collects and reconciles open data and existing analyses; it does not measure — certified laboratories measure.
author: Rigjita Baldanova
version: 0.3.7
license: CC BY 4.0 (method and documentation); CC BY-NC 4.0 (indicator catalogue, threshold packs, remote-sensing layer in core/); Apache-2.0 (code). See LICENSE-NOTICE.md, LICENSE, LICENSE-CORE, LICENSE-CODE
---

# Farm Environmental Passport

An independent passport for one specific farm: what enters it, what has been measured and by what method, what has never been measured, and what to sample first. The construction is the same for every module — collect open series, reconcile against thresholds with a stated legal status and date, register the gaps, and issue the answer as a status card. PFAS screening is the first module and sets the pattern; it is not the boundary of the product.

## Start here

1. Record the farm's consent (indicator X-07); nothing else starts without it.
2. Name the jurisdiction and load its threshold pack (`core/thresholds.md`; machine form `core/thresholds/*.json`). If any row you need is older than the pack's `max_age_days`, re-check it before use.
3. Fill the farm profile (true / false / unknown for each component and trigger) and select indicators from the farm catalogue with `scripts/indicator_select.py` (`core/indicators/farm-indicators.md`). Unknown facts are confirmed first — they decide which panels open.
4. Compose the NASA data request (`nasa_request`) for the data agent — whoever holds NASA Earthdata access — and collect inputs and open series (below); class every number as *measured*, *modelled*, *remote* or *never measured*.
5. Compute with `scripts/passport_calc.py` — doses, balances, loads, statuses. Do not compute by hand in the card.
6. Assign statuses with the decision table in `references/status-rules.md`.
7. Run the dose scenarios in `references/dose-scenarios.md`, including the sensitive group.
8. Generate the gap registry from the selection (`gap_registry`), collapse it into the work plan (`work_plan`: consent → one call to confirm the unknown facts → records interview → NASA request → field visits → laboratory panels) and write each panel's sampling plan (`references/methods.md` — method by matrix). Worked case: `examples/sim-farm-indicator-selection.md`.
9. Fill `assets/answer-card-template.md` and pass the quality gate at the end of this file.

## What the skill does not do

- It does not measure. Chemical and microbiological analyses are performed by a certified laboratory; the skill specifies points, depth, season and method.
- Its output is screening and an expert opinion, not an official determination of regulatory compliance.
- It makes no medical conclusions. A personal exposure fact (for example, a serum PFAS test) is a decision for the person, not for this skill; where a health agency gives explicit advice for a sensitive use (infant formula), the card repeats it with its source.
- A specific farm's data are never published without the farm's consent. The public layer is aggregated and de-identified results only.

## Inputs (from the farm or the client)

- Address and field boundaries; crops and livestock; herd size and production.
- Biosolids source (which treatment plant), class, rates, years and fields of application.
- Water: well (depth, use for drinking and for infant formula), surface source, irrigation.
- Existing analyses (soil, water, feed, product) — with laboratory, method and reporting limits.
- Purchases and sales for the farm-gate balance: feed, fertiliser, animals, crops, milk.

## What the skill collects itself (open series)

- Permits and reporting of the biosolids supplier (SPDES discharge monitoring; source and product test results under the applicable programme, e.g. NYS DEC DMM-7 for sources and DMM-7A for biosolids products).
- Soils and geology of the site; land-use history of the fields from the Landsat/HLS archive.
- Known contaminant sources nearby: airports (AFFF), industry, landfills.
- Watershed data where the farm sits in a managed watershed (context, not a source of status).

## Reconciliation and the gap registry

Every statement in the passport carries a source and a date. Data are divided into four classes: **measured** (laboratory or on-farm observation, method named), **modelled** (model named, inputs named), **remote** (satellite product, version, date and quality mask named), **never measured**. Only measured data carry a colour; model-only, remote-only and never-measured objects are **grey** with a gap row. A gap is a full row of the passport, not an omission. Censored values (below the reporting limit) are stored with their limit, never silently treated as zero or as missing; sums are reported as [lower bound, upper bound], and a status that depends on censoring is flagged (`references/status-rules.md` §4). When a model and a measurement disagree, both are printed and the disagreement becomes a gap — it is never smoothed.

## Thresholds (status and date are mandatory for every threshold)

Threshold packs are jurisdiction-specific and versioned, kept as JSON in the shared core (`core/thresholds/ny-us.json`, `core/thresholds/eu.json`) and rendered to `core/thresholds.md`. Each row states: value, unit, legal status (in force / adopted with a future date / guidance / orientation / superseded / requirement), date of application, applicability, the source's own determination rule, the issuing body and document, the date it was checked, and a verification mark (verified / verified via secondary — provisional / corrected / not verified). Unconfirmed rows are kept and marked, never deleted. A screening result is never worded as compliance.

**A jurisdiction without a pack** (behavioural test B4): build its rows first — value, legal status, date, source, verification mark — and only then assign statuses; never borrow New York or EU values silently. Until the pack exists, every object stays grey except the dose line, which is compared with the EFSA TWI as an orientation reference (yellow at most).

Packs in this version: **New York / US federal** (with EFSA and the Maine milk line) and **European Union** (drinking water, groundwater, nitrates, sewage sludge and soil, food maximum and indicative levels, EFSA, bathing water). The line-by-line check of the v0.1 pack is in `references/threshold-verification-2026-11-01.md`.

Key anchors (full rows and sources in the packs):

- PFAS in drinking water: NYS MCL 10 ng/L each for PFOA and PFOS (in force); EPA MCL 4.0 ng/L each (compliance 2029; a 2031 exemption pathway proposed in May 2026) — screening only until compliance; EU 'Sum of PFAS' 0.10 µg/L and 'PFAS Total' 0.50 µg/L (since 12 Jan 2026).
- Groundwater (EU): sum of four PFAS 4.4 ng/L, applies from 22 Dec 2027 (provisional).
- Biosolids (NYS DMM-7, issued 2023-09-07): PFOS or PFOA 20 µg/kg dw or less — no action; above 20 and below 50 — additional sampling, and if the level is not below 20 after one year DEC restricts recycling; 50 or greater — DEC acts to prohibit recycling until below 20. EU: no PFAS value for sludge; heavy-metal limits in soil (86/278/EEC Annex I A) and a minimum 3-week wait before grazing or forage harvest.
- Dose: EFSA TWI 4.4 ng/kg bw per week for the sum of four PFAS.
- Product: Maine PFOS action level 210 ng/L in cow's milk; EU indicative levels for milk (PFOS 0.020 µg/kg) and maximum levels for eggs, meat and offal.
- Nitrate: EPA MCL 10 mg/L as N; EU 50 mg/L as NO₃ (= 11.3 as N) — convert before comparing.
- E. coli (orientation for farm streams): EPA 2012 GM 126 / STV 410 CFU/100 mL; EU inland bathing water percentiles.
- Nutrient balance (NY dairies): Cornell feasible balances N 0–117.7 kg/ha, P 0–13.45 kg/ha — name the denominator.

## Status rules

One decision table for every module (`references/status-rules.md`): grey without a measurement; green below every reference (green-watch at ≥ 75 % of it — a skill convention); yellow at most for exceedances of future, guidance or orientation references and for any non-sustained exceedance; **red only when an in-force reference is exceeded under its own determination rule** (running annual average, confirmation sample, seasonal percentile, a regulator's tier) or, without one, in two consecutive sampling events. An object takes the worst status across its references, and the card names the reference that set it.

## Sampling plan (when key measurements are absent)

Minimal set, ordered by value of information: re-analysis for the missing EFSA analytes; the drinking well; the product; feed; soil of application and control fields; standing water. Methods by matrix (`references/methods.md`): **EPA 533 or 537.1** for drinking water (including a private well when the question is drinking-water standards); **EPA 1633** for groundwater investigations, surface water, soil, sediment, biosolids and tissue; an FDA-type food method (**FDA C-010.03**) or an equivalent ISO/IEC 17025 method for milk, food and feed. Reporting limits must sit below the reference being used. A laboratory certified for the method and matrix measures; the skill sets points, depth, season and analytes.

## The product → dose scenario

Weekly dose = concentration in the product × usual daily consumption × 7 ÷ body weight, compared with the EFSA TWI and presented as an estimate with uncertainty, not as a health forecast (`references/dose-scenarios.md`). Four scenarios are mandatory: off-farm adult (product), resident adult (product + water), **infant fed formula made with well water**, and **young child resident**; parameters come from cited exposure-factor tables (water: ATSDR 2023, Table 1, for every age group), and where a consumption figure cannot be sourced the card prints a break-even intake instead. With fewer than four EFSA PFAS measured, every dose is a labelled lower bound. Total exposure includes water and other foods; the contribution of this one farm is a separate line.

## Modules of the passport

Each module repeats the construction of Module 1: the farm's question → open series and analyses → reconciliation against thresholds (status and date) → status per pathway or object → gap registry → minimal sampling plan → one line in the farm's answer card.

| # | Module | Maturity in v0.3 | Threshold anchors in the packs |
|---|---|---|---|
| 1 | PFAS and biosolids pathways — inputs (biosolids, irrigation and drinking water, soil, feed, AFFF/industry), product pathway soil → forage → animal → milk/product, dose scenarios | **demonstrated** — worked example + tests | NY-US, EU, EFSA, Maine |
| 2 | Water — drinking and irrigation water, well nitrate by season, stream and pond microbiology, water availability | **demonstrated** (nitrate, TP, E. coli event) | EPA, EU DWD/GWD, bathing water |
| 3 | Plant nutrition and export to water bodies — farm-gate N and P balances, field export, Vollenweider loading, OECD trophic bounds | **demonstrated** — worked example + tests | Cornell (NY), Nitrates Directive (EU), OECD, Vollenweider |
| 4 | Agronomy and soil — catalogue block A (32 indicators): soil chemistry, fertility, physics and biology, erosion and cover (HLS, IMERG), tillage and rotation, inputs incl. pesticides, crop and forage yield and quality, plant health, irrigation | catalogue + selection demonstrated on the synthetic farm; no measured worked example | EU sludge-soil metal limits; NYS PFAS background (provisional) |
| 5 | Other contaminants and biological safety — heavy metals, pesticides, microplastics; pathogens and AMR in biosolids, manure, water | specified, not demonstrated | heavy metals (EU 86/278); others not yet in packs |
| 6 | Climate risks — drought (SMAP, precipitation), flooding (OPERA DSWx), frost and heat stress; exposure map, not a forecast | specified, not demonstrated | — |
| 7 | Ponds and aquaculture — oxygen regime, blooms, feed base; ground samples + satellite proxies | partly demonstrated (trophic state, loading); oxygen regime not | OECD, Vollenweider |
| 8 | Farm biodiversity — buffer strips, pollinators, birds, amphibians; acoustic layer with a published error rate, never the sole basis | specified, not demonstrated | — |
| 9 | **Livestock — herd, feed, health, welfare, product safety** — catalogue block L (42 indicators): herd and stocking, ration and feed safety (aflatoxins, PFAS in feed), drinking water for animals, the twelve Welfare Quality criteria, mastitis and bulk-tank milk quality, antimicrobial use, biosecurity, manure and emissions (NH₃, CH₄, N₂O), product safety (residues, aflatoxin M1, PFAS) | catalogue + selection demonstrated on the synthetic farm; no measured worked example | NY 1 NYCRR §2.8 and PMO, EU 853/2004 milk criteria; FDA and EU aflatoxin levels; EU NVZ manure-N; BfR feed model (orientation) |

Note for Module 3: applying biosolids at a nitrogen-based rate structurally produces a phosphorus surplus; the balance makes this visible instead of hiding it. The per-hectare balance depends on the denominator (whole farm or tillable land) — the card names it and, where they differ, reports both.

## Farm indicator catalogue — every indicator in, only the useful ones measured

`core/indicators/farm-indicators.psv` (rendered to `.md`, `.csv` for spreadsheets and `.json`) lists 113 indicators in four blocks: **A** agronomy and soil (32), **L** livestock (42), **E** farm ecosystem — water, nutrients, habitat, climate (31), **X** cross-cutting — contaminant sources, antimicrobial resistance, governance (8). Each row carries unit, tier, the component that makes it relevant, the trigger, cost class, sampling panel, method, threshold anchor (or "—", a named gap), NASA product, the twin catalogue section, the Eurostat agri-environmental indicator it serves and the Welfare Quality criterion it serves.

- **Completeness is tested, not claimed:** every one of the 28 Eurostat agri-environmental indicators (32 with sub-indicators) maps to a catalogue row or to a stated scope exclusion (only AEI 14, farmland-abandonment risk, is regional and excluded); every one of the 12 Welfare Quality criteria maps to a livestock row (the protocol has no measure for thermal comfort; the catalogue's temperature-humidity index is labelled as the skill's proxy).
- **Selection is disciplined:** core indicators enter whenever their component is present; conditional ones only with a trigger; research ones on request. Unknown facts are confirmed before anything is sampled. Every indicator left out carries its reason, so "the passport covers all indicators" stays true while the measured set stays small.
- **Gap registry and sampling plan come from the selection** (`gap_registry`), ordered by value of information: consent, then the questions that open or close panels, then desk and satellite work, then field checks, then laboratory panels — one sample serving several indicators. `work_plan` collapses the registry into actions and `lab_panels` into sampling visits: on the synthetic farm 98 selected indicators and 88 gaps become 14 actions, the 16 indicators waiting on a fact wait on 11 facts, and the laboratory work is 7 panels.

## NASA remote-sensing layer

`core/remote-sensing/nasa-layer.json` names the products the passport uses — HLS (30 m), OPERA DSWx-HLS (30 m), ECOSTRESS (70 m), SMAP L4 (9 km), GPM IMERG (0.1°), NASA POWER (0.5° × 0.625°), with each resolution checked against NASA sources — and the rules for using them. The skill writes the request (`nasa_request`); a data agent with NASA Earthdata access executes it. Without such an agent the operator downloads the same products from NASA Earthdata or AppEEARS; the rules below do not change. Satellite values are evidence class *remote*: they target field checks, set triggers (a drought year opens the aflatoxin and forage-nitrate panels), give context, and never set a status colour alone. A field-scale product is applied to an object only with at least nine pure pixels — the synthetic farm's 0.2 ha pond and its 30 m buffer strip are excluded at 30 m, and the request says so.

## Shared core with the Ecosystem Digital Twin

The passport and the twin stay two products — a snapshot and a model answer different questions — but share one library: threshold packs, the farm indicator catalogue, the NASA layer, methods and units (`core/README.md`). A passport is the twin's entry level for one farm; `core/crosswalk-twin.md` maps every farm indicator to the twin's catalogue sections and lists the 22 livestock indicators the twin does not cover yet. A semantic reconciliation of the twin's 212-item farm map with this catalogue (2026-11-05) finds 118 map items with a full or partial counterpart, 88 outside the passport by design, 6 candidate gaps of the core, and 36 core rows without a counterpart, 27 of them livestock. No change is made to the twin without the author's approval.

## Output — the farm's answer card

Template: `assets/answer-card-template.md`.

- Status per pathway or object: green / green-watch / yellow / red / grey, with the reference row that set it. Red only on a sustained exceedance as defined above.
- Dose block with the four scenarios and the completeness of the EFSA sum.
- Gap registry: what is not measured, and which sample closes it.
- Recommendations: continue or suspend biosolids application; buffer strips; re-check date; threshold rows due for re-verification.
- A provenance line for every number: *measured*, *modelled*, *remote* or *reference*, with the primary source named.
- Indicator selection and work plan: what was selected and why, what was left out and why, the facts to confirm, the NASA request sent to the data agent (products, what was excluded by the pixel-fit check).

## Quality gate (before a card leaves the operator)

- [ ] Every number came from `passport_calc.py` or a laboratory report; none typed by hand.
- [ ] Every threshold used has a row ID, legal status and a check date within the pack's limit.
- [ ] No status is coloured from a model alone; every grey has a gap row and a closing sample.
- [ ] Censored values are bounded; partial sums are labelled lower bounds.
- [ ] The four dose scenarios are present, including the sensitive group.
- [ ] Method named per matrix; reporting limits below the references.
- [ ] Unit conversions shown (nitrate as N vs NO₃; milk per L vs per kg).
- [ ] No wording of compliance or safety; consent for any non-aggregated use recorded.
- [ ] Indicator selection saved with reasons for every indicator left out; unknown facts confirmed or listed first.
- [ ] Satellite values labelled *remote*, with product, date and quality mask; no colour set by a satellite value alone.
- [ ] `python3 tests/run_tests.py` passes after any change to the skill or the packs.

## Maintenance

Re-run on new data: biosolids testing, new laboratory results, a new season. Re-check threshold rows when they pass the pack's age limit or when a tracked rule changes (the EPA PFOA/PFOS extension rule; EU groundwater and surface-water PFAS standards from December 2027; the EU soil PFAS watch list). The pipeline and sources are assembled once; a repeat pass takes days, not months.

## Tests

`tests/TESTS.md` lists the saved test inputs and expected behaviour; `python3 tests/run_tests.py` runs the computable ones and writes a dated pass/fail protocol to `tests/RUN-LOG.md`. Behavioural tests (how an operator or model uses the skill) are listed and pending first live use.

## First live use (pilot)

The method is demonstrated on a synthetic farm; the first real farm is its validation. With written consent (X-07), the pilot records: hours per step of the work plan; which facts the confirm call settled and which panels they opened or closed; every model prediction set against the laboratory result that later replaced it (for example, the milk model range against the tank-milk sample); every status that changed and why; the outcome of behavioural tests B1–B7 in live use; what the farmer understood from the card and what had to be explained. The skill counts as validated when one real card has passed the quality gate and B1–B7 have been run; until then its maturity column says *demonstrated*, not *validated*.

## Worked examples (synthetic, published as method demonstrations)

`examples/` holds two simulations on one synthetic dairy farm (Delaware County, NY, Catskill/Delaware watershed; every laboratory value synthetic and labelled).

- **Texts in force.** Each text exists in English (`*.en.md`) and in its Russian source; numbers, statuses and conclusions are identical. Module 1 — `examples/FARM-PFAS-SIMULATION-2026-10-31-r7.en.md` (source `examples/FARM-PFAS-SIMULATION-2026-10-31-r7.md`): PFAS screening; DEC soil and groundwater guidance; DMM-7 tiers checked against the 2023-09-07 primary; adult, infant and young-child dose scenarios with the infant and child profiles from the ATSDR 2023 primary; the uncertainty and sensitivity block reproduced by `examples/uncertainty.py`; the milk-model chain reproduced by `examples/reconstruct.py`; the sampling order by value of information; an amendment register. Modules 2–3 — `examples/FARM-WATER-NUTRIENTS-SIMULATION-2026-10-31-r2.en.md` (source `examples/FARM-WATER-NUTRIENTS-SIMULATION-2026-10-31-r2.md`): well nitrate by season, a stream E. coli event equal to (not above) the EPA STV, N and P farm-gate balances against the Cornell benchmark (phosphorus 3.5 times the feasible upper bound), a Vollenweider pond assessment. `examples/ACTIVE-TEXTS.md` maps each module to its text in force.
- **Figures.** English figures for all modules in `examples/figures/en/`, built by `examples/make_figs_en.py` (Modules 2–3 computed from the unchanged data block of `make_figs2.py`). Russian figures in `examples/figures/`, built by `make_figs1.py` (Module 1), `make_figs2_v2.py` (balances) and the original `make_figs2.py`, which reproduces every number of Modules 2–3. Data series are neutral; red, yellow and green are reserved for status.
- **Intake record.** The original texts of 31 October 2026 (`examples/FARM-PFAS-SIMULATION-2026-10-31.md`, `examples/FARM-WATER-NUTRIENTS-SIMULATION-2026-10-31.md`) stay byte-identical (sha256 checked by T8); later rules are recorded in the texts in force and in `references/dose-scenarios.md` §4 and `references/threshold-verification-2026-11-01.md` §2. The synthetic values are the same in every redaction.
- `examples/sim-farm-indicator-selection.md` (generated by `scripts/render_catalogue.py`) applies the catalogue to the same farm: indicator selection with reasons, the work plan, the gap registry and the NASA request.
