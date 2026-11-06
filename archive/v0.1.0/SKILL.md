---
name: farm-environmental-passport
description: Build an independent environmental passport for a specific farm — input pathways, water and soil status, nutrient balances, contaminant screening (PFAS first module), a registry of what has never been measured, and a minimal sampling plan. Use when asked to assess a farm's environmental safety, biosolids history, well or irrigation water, nutrient export to water bodies, or the exposure a farm's product may carry. The skill collects and reconciles open data and existing analyses; it does not measure — certified laboratories measure.
author: Rigjita Baldanova
version: 0.1.0
license: CC BY 4.0 (text and method); Apache-2.0 (code)
---

# Farm Environmental Passport

An independent passport for one specific farm: what enters it, what has been measured and by what method, what has never been measured, and what to sample first. The construction is the same for every module — collect open series, reconcile against thresholds with a stated legal status and date, register the gaps, and issue the answer as a status card. PFAS screening is the first module and sets the pattern; it is not the boundary of the product.

## What the skill does not do

- It does not measure. Chemical and microbiological analyses are performed by a certified laboratory; the skill specifies points, depth, season and method.
- Its output is screening and an expert opinion, not an official determination of regulatory compliance.
- It makes no medical conclusions. A personal exposure fact (for example, a serum PFAS test) is a decision for the person, not for this skill.
- A specific farm's data are never published without the farm's consent. The public layer is aggregated and de-identified results only.

## Inputs (from the farm or the client)

- Address and field boundaries; crops and livestock.
- Biosolids source (which treatment plant), years and fields of application.
- Water: well, surface source, irrigation.
- Existing analyses (soil, water, product, milk) — if any exist.

## What the skill collects itself (open series)

- Permits and reporting of the biosolids supplier (SPDES discharge monitoring; biosolids and biosolids-product test results under the applicable state programme, e.g. NYS DEC DMM-7 / DMM-7A).
- Soils and geology of the site; land-use history of the fields from the Landsat/HLS archive.
- Known contaminant sources nearby: airports (AFFF), industry, landfills.
- Watershed data where the farm sits in a managed watershed (context, not a source of status).

## Reconciliation and the gap registry

Every statement in the passport carries a source and a date. Data are divided into three classes: **measured** (laboratory, method named), **modelled** (model named, inputs named), **never measured**. A gap is a full row of the passport, not an omission. Censored values (below the detection limit, ND) are flagged and never silently treated as zero or as missing; where a sum depends on them, the result is reported as a range.

## Thresholds (status and date are mandatory for every threshold)

Threshold packs are jurisdiction-specific and versioned. Each entry states: value, unit, legal status (in force / adopted, future compliance date / draft guidance), and the date it was checked against the primary source. A screening result is never worded as compliance. Example pack (New York / US federal, checked 2026-10-31):

- Drinking water, New York State: PFOA and PFOS, MCL 10 ng/L each (in force since 2020).
- Drinking water, US EPA: PFOA and PFOS, MCL 4.0 ng/L each; mandatory compliance from 2029 — before that date, comparisons are screening only.
- Biosolids, NYS DEC DMM-7 interim strategy: PFOS attention level 20 ppb in biosolids; DMM-7A (2026-06-10) requires testing of biosolids products.
- Consumer dose reference, EFSA: tolerable weekly intake 4.4 ng/kg body weight per week for the sum PFOS + PFOA + PFNA + PFHxS.
- Well nitrate: EPA MCL 10 mg/L as nitrogen.
- Surface-water bacteria: EPA recreational criteria for E. coli (geometric mean 126, single-sample maximum 235 CFU/100 mL) — used as orientation values, labelled as such.

## Sampling plan (when key measurements are absent)

Minimal set: soil of the application fields; well water; the product (milk / eggs / vegetables, by the farm's profile). Method — EPA 1633 or the current analogue for PFAS; a laboratory certified by the state health department. The skill sets the points, depth and season; the laboratory measures.

## Modules of the passport

Each module repeats the construction of Module 1: the farm's question → open series and analyses → reconciliation against thresholds (status and date) → status per pathway or object → gap registry → minimal sampling plan → one line in the farm's overall answer card.

1. **PFAS and biosolids pathways.** Inputs: biosolids, irrigation and drinking water, soil accumulation, feed, nearby AFFF/industrial sources. Product pathway: soil → forage → animal → milk/product; the consumer dose scenario below.
2. **Water.** Drinking and irrigation water quality and the state of the farm's water bodies: well nitrate by season; microbiology of streams and ponds; water availability in dry periods. Inputs: seasonal laboratory series, IMERG precipitation, site hydrology, satellite turbidity and colour proxies.
3. **Plant nutrition and export to water bodies.** Farm-gate nitrogen and phosphorus balances (inputs: fertiliser, biosolids, purchased feed, fixation, deposition; outputs: milk, livestock, sold crops) and field export to streams and ponds. Orientation: the Vollenweider loading model for standing waters; OECD boundaries for total phosphorus and chlorophyll-a. Output: surplus in kg/ha and the load on the receiving water, not a general fertiliser recommendation. Note: applying biosolids at a nitrogen-based rate structurally produces a phosphorus surplus; the balance makes this visible instead of hiding it.
4. **Soil.** Fertility (NPK, pH, organic matter) from point analyses; erosion and bare ground from the Landsat/HLS archive; salinisation and compaction screened from open data with ground verification. Status per field, as in Module 1.
5. **Other contaminants and biological safety.** Heavy metals, pesticides, microplastics; pathogens and antibiotic resistance in biosolids, manure and water — the microbiological block. Thresholds from current state norms and federal references, each with a check date.
6. **Climate risks.** Drought (SMAP soil moisture, precipitation), field flooding (OPERA DSWx), frost and livestock heat stress from NASA series and forecasts. Output: an exposure map of fields and pastures, not a weather forecast.
7. **Ponds and aquaculture.** Oxygen regime, blooms, feed base: ground samples plus satellite proxies (chlorophyll, turbidity); status as for any water body in the passport.
8. **Farm biodiversity.** Buffer strips, pollinators, birds and amphibians. The acoustic layer is a probabilistic detector with a published error rate; it is never the sole basis for a status.

## The product → dose scenario

Weekly dose = concentration in the product × usual weekly consumption of the product ÷ body weight. The result is compared with the EFSA TWI and presented as an estimate with uncertainty, not as a health forecast. Total exposure includes water and other foods; the contribution of this one farm is a separate line.

## Output — the farm's answer card

- Status per pathway or object: green / yellow / red. Red only on a sustained exceedance, never on a single sample.
- Gap registry: what is not measured, and which sample closes it.
- Recommendations: continue or suspend biosolids application; buffer strips; re-check date.
- A provenance line for every number: *data · skill* or *data · search*, with the primary source named.

## Maintenance

Re-run on new data: annual biosolids testing, new laboratory results, a new season. The pipeline and sources are assembled once; a repeat pass takes days, not months.

## Worked examples (synthetic, published as method demonstrations)

Two full simulations on one synthetic dairy farm (Delaware County, NY, Catskill/Delaware watershed; all values synthetic and labelled as such): Module 1 — PFAS screening including the milk-and-well-water dose scenario; Modules 2–3 — water quality, nitrate seasonality, N and P farm-gate balances and a Vollenweider pond assessment.
