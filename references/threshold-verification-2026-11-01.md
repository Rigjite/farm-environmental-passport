# Line-by-line verification of the v0.1.0 threshold pack (checked 2026-11-01)

Scope: every threshold line of SKILL.md v0.1.0 (New York / US federal / EFSA) and every reference value used in the two worked examples. Method: web search and fetch of the issuing body's page or document; where only an authoritative secondary source was reachable, the line is marked *verified via secondary [provisional]*. Nothing unconfirmed was deleted — it is marked and listed in §3.

## 1. The six lines of the v0.1.0 pack

| # | v0.1.0 line | Result | What the source says | Source (body, document) | Row in v0.2 |
|---|---|---|---|---|---|
| 1 | NYS drinking water: PFOA and PFOS, MCL 10 ng/L each, in force since 2020 | **verified** | MCLs of 10 ppt each adopted 26 Aug 2020 for public water systems | NYS DOH; 10 NYCRR Subpart 5-1, DOH fact sheet | NYUS-01, -02 |
| 2 | US EPA: PFOA and PFOS, MCL 4.0 ng/L each; mandatory compliance from 2029 | **corrected (wording)** | MCLs 4.0 ppt unchanged; compliance 26 Apr 2029 under the 2024 rule; on 18 May 2026 EPA proposed a federal exemption pathway to 26 Apr 2031 — proposed, not final at the check date; compliance is by running annual average | US EPA proposed-rule page; Federal Register 20 May 2026 | NYUS-03, -04 |
| 3 | NYS DEC DMM-7: "PFOS attention level 20 ppb" | **corrected** | tiers apply to PFOS **or** PFOA: ≤20 µg/kg no action; >20 and <50 additional sampling; ≥50 DEC acts to prohibit recycling until <20. "Attention level" is not DEC's term. DMM-7 issued 7 Sep 2023, quarterly source sampling | NYS DEC, Program Policy DMM-7 (PDF) and DEC biosolids page | NYUS-07, -08 |
| 4 | DMM-7A (2026-06-10) requires testing of biosolids products | **verified** | issued 10 Jun 2026; products (compost, heat-dried, etc.) sampled within 90 days, then annually | NYS DEC DMM-7A (PDF); Cornell CALS biosolids FAQ quoting DEC | NYUS-09 |
| 5 | EFSA TWI 4.4 ng/kg bw per week, sum PFOS + PFOA + PFNA + PFHxS | **verified** | group TWI 4.4 ng/kg bw/week; critical effect immune response; BMDL in 1-year-old children | EFSA Journal 2020;18(9):6223 | NYUS-10 / EU-24 |
| 6a | Well nitrate: EPA MCL 10 mg/L as N | **verified** | 40 CFR 141.62(b)(7): 10 mg/L as N; nitrite 1; nitrate + nitrite 10 | eCFR (Cornell LII); EPA 2026 training deck | NYUS-06 |
| 6b | E. coli: geometric mean 126, single-sample maximum 235 CFU/100 mL | **corrected** | EPA 2012 RWQC: GM 126 with **STV 410** (or 100 / 320); 235 is the 1986 single-sample maximum, retained in 2012 only as an optional Beach Action Value | EPA E. coli factsheet 2021; MDE factsheet 2013 | NYUS-11, -12, -13 |

## 2. Reference values used in the worked examples

| Value in the example | Result | Finding | Row |
|---|---|---|---|
| Maine action level for PFOS in milk 210 ng/L (example 1, §3.4) | **verified** | Maine CDC action level, 2017, used by DACF to decide whether milk may be sold; Maine also has 3.4 ng/g for beef | NYUS-14, -15 |
| "DEC draft for agricultural soils, maximum PFOS 3.0 µg/kg, not adopted" (example 1, §3.2) | **not confirmed as worded** | 3.0 µg/kg PFOS (1.5 PFOA) is DEC's rural **background** concentration from its 2023 background study (secondary source); a draft agricultural maximum was not found | NYUS-16 |
| DMM-7A as the control for land-applied class B biosolids (example 1, §3.1) | **interpretation corrected** | DMM-7A covers biosolids *products*; class B biosolids from a source are covered by DMM-7 quarterly source sampling | NYUS-07, -09 |
| EPA 1633 for well water (example 1, §6) | **corrected** | drinking-water comparisons use EPA 533 / 537.1; 1633 is for non-drinking-water matrices | methods.md |
| E. coli 410 "above the single-sample value 235" (example 2, §3.2) | **corrected** | 410 equals, and does not exceed, the current STV 410; the exceedance exists only against the superseded 235. The stream stays yellow on phosphorus, not on E. coli | NYUS-12, -13 |
| OECD TP bounds 10 / 35 / 100 µg/L (example 2) | **verified via secondary [provisional]** | same bounds in the OECD table reproduced by Onondaga County (Janus & Vollenweider 1981) | NYUS-19 |
| OECD chlorophyll-a bounds (pond 21 µg/L "eutrophic") | **verified via secondary [provisional]** | 2.5 / 8 / 25 µg/L — 21 is eutrophic | NYUS-20 |
| Vollenweider permissible 10 / dangerous 20 µg/L and the loading formula | **not verified** | citation located (Mem. Ist. Ital. Idrobiol. 33, 1976); primary text not opened; arithmetic reproduced exactly (T4) | NYUS-21 |
| "N surplus 133 kg/ha — upper part of the range typical for dairy farms" (example 2, §4.1) | **replaced by a sourced benchmark** | Cornell feasible balances for NY dairies: N 0–105 lb/acre (0–117.7 kg/ha), P 0–12 lb/acre (0–13.45 kg/ha); the example's N is above, P is 3.5 times the upper bound | NYUS-17, -18 |
| Transfer factors TF 0.026–0.37 and 14 % of PFOS dose to milk | **verified (primary)**, 2026-11-06 | TF: mean PFOS soil-to-forage values 0.026–0.27 (plots) and 0.039–0.37 (farms) in mixed grasses and legumes on biosolid-amended fields; milk: cumulative PFOS secretion 14 ± 3.6 % in a dairy-cow feeding study | Simones et al. 2024, J. Agric. Food Chem. 72(42):23108–23117, doi:10.1021/acs.jafc.4c02078; Kowalczyk et al. 2013, J. Agric. Food Chem. 61(12):2903–2912, doi:10.1021/jf304680j |
| Export coefficients, delivery ratio 0.15 | **not verified** (outside the threshold pack) | literature ranges, kept as labelled model assumptions | — |

## 3. Unconfirmed or corrected — the list for the report

1. EPA PFOA/PFOS compliance date — wording incomplete: 2029 stands in the 2024 rule, but a 2031 exemption pathway is proposed (not final). Corrected.
2. DMM-7 "PFOS attention level" — wrong term and incomplete (PFOS or PFOA; second tier 50). Corrected.
3. E. coli 235 as the single-sample maximum — superseded by STV 410 (2012). Corrected; 235 kept as a superseded row.
4. EPA 1633 for well/drinking water — wrong method for that purpose. Corrected in methods.md.
5. "DEC draft maximum PFOS 3.0 µg/kg in agricultural soil" — not confirmed; 3.0 is a background value (secondary source). Kept, marked.
6. DMM-7A cited as the control for land-applied class B biosolids — misattributed; DMM-7 applies. Corrected.
7. Vollenweider criteria — primary not opened. Kept, marked *not verified*.
8. OECD trophic bounds — secondary source only. Kept, marked *provisional*.
9. EU groundwater sum-of-4 PFAS 4.4 ng/L and Regulation 2023/915 / Recommendation 2022/1431 numbers — secondary sources; the EU legal acts were located but their annex tables were not read. Marked *provisional*.
10. EU surface-water EQS for the sum of 25 PFAS — value not retrieved. Row kept as a named gap.
11. EPA MCLs for PFHxS, PFNA, HFPO-DA and the Hazard Index — added; proposed for rescission (May 2026). Orientation only until EPA decides.

Re-check due: 2027-05-03 (183 days), or immediately when the EPA extension rule is finalised.

## 4. Rows added in v0.3.0 (livestock, milk quality, feed safety) — checked 2026-11-01

| Row | Value | Legal status | Source read | Mark |
|---|---|---|---|---|
| NYUS-22 | somatic cells ≤ 750 000 per mL, prepasteurized Grade A producer milk (cows) | in force | 1 NYCRR §2.8 *Quality standards* (text via Justia reproduction); the same value in the Grade "A" PMO (AVMA policy page) | verified via secondary — two independent sources agree; official NYCRR publisher not opened |
| NYUS-23 | aflatoxin M1 0.5 µg/kg in milk | guidance (action level) | FDA CPG Sec. 527.400 | verified |
| NYUS-24 | total aflatoxins 20 ppb in feed for dairy animals (100 / 200 / 300 ppb for other classes) | guidance (action level) | FDA CPG Sec. 683.100 (March 2019 PDF) | verified |
| NYUS-25 | bacteria ≤ 100 000 per mL, Grade A producer milk before commingling (commingled 300 000) | in force | 1 NYCRR §2.8 (via Justia) | verified via secondary |
| NYUS-26 | bacteria ≤ 30 000 per mL, raw milk sold raw to consumers | in force | 1 NYCRR §2.8 (via Justia) | verified via secondary |
| EU-26 | somatic cells 400 000 per mL, rolling geometric average over three months, ≥ 1 sample per month | in force | Regulation (EC) 853/2004, Annex III, Section IX, Chapter I (legislation.gov.uk, EU text at 31.12.2020) | verified |
| EU-27 | plate count at 30 °C 100 000 per mL, rolling geometric average over two months, ≥ 2 samples per month | in force | same | verified |
| EU-28 | aflatoxin M1 0.050 µg/kg in raw and heat-treated milk | in force | Regulation (EU) 2023/915, Annex I row 1.1.16, as reproduced by Food Safety Magazine (8 May 2023) | verified via secondary — EUR-Lex annex not retrieved |
| EU-29 | aflatoxin B1 0.005 mg/kg in compound feed for dairy cattle and calves (feed at 12 % moisture) | in force | Directive 2002/32/EC, Annex I, Section II, consolidated text CELEX 02002L0032-20191128 (legislation.gov.uk) | verified — amendments after 2020 not checked on EUR-Lex |
| EU-30 | PFOS 0.07 µg/kg in feed (modelled to keep food below EU maximum levels) | orientation | BfR, via Food Safety Magazine | verified via secondary |

Correction made during this check: EU-29 was entered with the act "not confirmed"; the consolidated Directive 2002/32/EC confirms the value and the category, so the mark was raised to *verified*. Not anchored (named gaps of the packs): raw-milk pathogen criteria for New York raw-milk permits (L-41), veterinary-drug residue tolerances (L-38 — the PMO transmittals and EU MRL tables are not loaded), mycotoxins other than aflatoxins (L-07), welfare outcomes (no legal threshold exists; Welfare Quality scoring is a protocol, not a limit).

## Дополнение 2026-11-05 — строки DEC (почва и подземные воды)

Добавлены строки NYUS-27–NYUS-32 в пакет NY-US (core/thresholds/ny-us.json, версия пакета 2026-11-05); таблица core/thresholds.md перерендерена скриптом render_thresholds.py.

- NYUS-27 / NYUS-28 — почва, неограниченное использование: PFOA 0,66 мкг/кг, PFOS 0,88 мкг/кг. Статус: guidance. Первоисточник: руководство NYSDEC по PFAS в программах Part 375 (апрель 2023), значения применены в Decision Document DEC по объекту C203167 (19.09.2025). Отметка: verified.
- NYUS-29 / NYUS-30 — почва, жилое использование: PFOA 6,6 мкг/кг, PFOS 8,8 мкг/кг. Таблица землепользования руководства DEC (январь 2021) в изложении отчёта DEC по объекту P828219 (18.09.2025). Отметка: verified-secondary.
- NYUS-31 / NYUS-32 — подземные воды класса GA: PFOA 6,7 нг/л, PFOS 2,7 нг/л. Статус: guidance. Первоисточник: TOGS 1.1.1, дополнение 2023 года (финал 15.03.2023); таблица итоговых guidance values на странице DEC «Water Quality Standards and Classifications». Отметка: verified.

Проверка выполнена 05.11.2026 по публикациям NYSDEC (dec.ny.gov / extapps.dec.ny.gov).


### Supplement 2026-11-05 (second group) — NYUS-33…NYUS-36

Checked 2026-11-05 against reproductions of the issuing body's documents (the DEC primary PDFs were not opened; rows are therefore marked verified-secondary in the pack):

| Row | Value | Source as checked | Mark |
|---|---|---|---|
| NYUS-33 soil (protection of groundwater) PFOA | 0.8 µg/kg | NYSDEC April 2023 PFAS guidance, soil guidance values table — protection-of-groundwater column (reproduced in NEWMOA webinar materials, Dec 2024; summarised in the Lippes Mathias client alert on the NYSDEC PFAS programme, 2026) | verified-secondary |
| NYUS-34 soil (protection of groundwater) PFOS | 1.0 µg/kg | same table | verified-secondary |
| NYUS-35 soil (rural background, proposed) PFOA | 1.5 µg/kg (surface; subsurface 1.2) | NYSDEC Rural Soil Background Study, proposed background concentrations (Lippes Mathias summary, January 2026) | verified-secondary |
| NYUS-36 soil (rural background, proposed) PFOS | 3.0 µg/kg (surface; subsurface 0.801) | same study | verified-secondary |
