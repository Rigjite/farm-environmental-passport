# Screening matrix — parameter → reference → unit → method

Generated from `core/screening-map.json` and `core/thresholds/ny-us.json` by `scripts/render_matrix.py`. Do not edit by hand.
Map version 2026-11-10; pack NY-US version 2026-11-05 (a row older than 183 days must be re-checked before use).

Which reference rows a measured result is compared with, in which unit it must arrive and which analytical methods are validated for it. Values, legal status and dates come from the pack; the map holds row IDs only. A result by a method not listed for its matrix is printed grey (`references/methods.md`). Status rules: `references/status-rules.md`.

Fit of a reference: **object** — the row applies to the object directly (default); **farmland** — a reference written for farmland or rural soil; sets the summary status of a group of fields; **other land use** — a reference written for another land use (e.g. remedial-site soil guidance); sets the status of the individual field, is printed beside the group summary, and does not set the group summary (references/status-rules.md §3a).

## `biosolids` — biosolids applied to the fields (sampled at the source)

| Parameter | Unit (canonical) | Validated methods | Reference row | Value | Legal status | Fit | Verification | Checked |
|---|---|---|---|---|---|---|---|---|
| PFOS | µg/kg | EPA 1633 | NYUS-07 — biosolids recycled in NYS (dry weight), PFOS or PFOA (each) | 20 µg/kg dw (ppb) | in force | object | corrected vs v0.1 | 2026-11-01 |
| PFOS | µg/kg | EPA 1633 | NYUS-08 — biosolids recycled in NYS (dry weight), PFOS or PFOA (each) | 50 µg/kg dw (ppb) | in force | object · acts on a single result | verified | 2026-11-01 |
| PFOA | µg/kg | EPA 1633 | NYUS-07 — biosolids recycled in NYS (dry weight), PFOS or PFOA (each) | 20 µg/kg dw (ppb) | in force | object | corrected vs v0.1 | 2026-11-01 |
| PFOA | µg/kg | EPA 1633 | NYUS-08 — biosolids recycled in NYS (dry weight), PFOS or PFOA (each) | 50 µg/kg dw (ppb) | in force | object · acts on a single result | verified | 2026-11-01 |
| PFNA | µg/kg | EPA 1633 | — no reference in this pack: reported, not coloured | — | — | — | — | — |
| PFHxS | µg/kg | EPA 1633 | — no reference in this pack: reported, not coloured | — | — | — | — | — |

## `soil` — field soil (state the depth in the object label)

Objects of this matrix form the group **soil**: the card prints one summary line and names any field whose own status is worse (status-rules §3a).

| Parameter | Unit (canonical) | Validated methods | Reference row | Value | Legal status | Fit | Verification | Checked |
|---|---|---|---|---|---|---|---|---|
| PFOS | µg/kg | EPA 1633 | NYUS-16 — agricultural / rural soil, PFOS (PFOA 1.5) | 3.0 µg/kg | orientation | farmland | verified via secondary [provisional] | 2026-11-01 |
| PFOS | µg/kg | EPA 1633 | NYUS-28 — soil (unrestricted use), PFOS | 0.88 µg/kg | guidance | other land use | verified | 2026-11-05 |
| PFOS | µg/kg | EPA 1633 | NYUS-34 — soil (protection of groundwater), PFOS | 1.0 µg/kg | guidance | other land use | verified via secondary [provisional] | 2026-11-05 |
| PFOA | µg/kg | EPA 1633 | NYUS-35 — soil (rural background — proposed), PFOA | 1.5 µg/kg | proposed | farmland | verified via secondary [provisional] | 2026-11-05 |
| PFOA | µg/kg | EPA 1633 | NYUS-27 — soil (unrestricted use), PFOA | 0.66 µg/kg | guidance | other land use | verified | 2026-11-05 |
| PFOA | µg/kg | EPA 1633 | NYUS-33 — soil (protection of groundwater), PFOA | 0.8 µg/kg | guidance | other land use | verified via secondary [provisional] | 2026-11-05 |
| PFNA | µg/kg | EPA 1633 | — no reference in this pack: reported, not coloured | — | — | — | — | — |
| PFHxS | µg/kg | EPA 1633 | — no reference in this pack: reported, not coloured | — | — | — | — | — |

## `well-drinking` — private well used for drinking (people and herd)

Varies by season: one sampling event is flagged; closing sample — a quarterly series for one year, the full EFSA four by EPA 533 or 537.1 (references/methods.md §3, item 2).

| Parameter | Unit (canonical) | Validated methods | Reference row | Value | Legal status | Fit | Verification | Checked |
|---|---|---|---|---|---|---|---|---|
| PFOS | ng/L | EPA 533, EPA 537.1 | NYUS-02 — drinking water (public systems), PFOS | 10 ng/L | in force | object | verified | 2026-11-01 |
| PFOS | ng/L | EPA 533, EPA 537.1 | NYUS-04 — drinking water (public systems), PFOS | 4.0 ng/L | future (adopted, applies from a date) | object | corrected vs v0.1 | 2026-11-01 |
| PFOS | ng/L | EPA 533, EPA 537.1 | NYUS-32 — groundwater (Class GA), PFOS | 2.7 ng/L | guidance | object | verified | 2026-11-05 |
| PFOA | ng/L | EPA 533, EPA 537.1 | NYUS-01 — drinking water (public systems), PFOA | 10 ng/L | in force | object | verified | 2026-11-01 |
| PFOA | ng/L | EPA 533, EPA 537.1 | NYUS-03 — drinking water (public systems), PFOA | 4.0 ng/L | future (adopted, applies from a date) | object | corrected vs v0.1 | 2026-11-01 |
| PFOA | ng/L | EPA 533, EPA 537.1 | NYUS-31 — groundwater (Class GA), PFOA | 6.7 ng/L | guidance | object | verified | 2026-11-05 |
| PFNA | ng/L | EPA 533, EPA 537.1 | NYUS-05 — drinking water (public systems), PFHxS; PFNA; HFPO-DA (each); Hazard Index mixture | 10 ng/L (HI unitless) | future (adopted, applies from a date) | object | verified via secondary [provisional] | 2026-11-01 |
| PFHxS | ng/L | EPA 533, EPA 537.1 | NYUS-05 — drinking water (public systems), PFHxS; PFNA; HFPO-DA (each); Hazard Index mixture | 10 ng/L (HI unitless) | future (adopted, applies from a date) | object | verified via secondary [provisional] | 2026-11-01 |
| nitrate (as N) | mg/L as N | any (none listed in references/methods.md) | NYUS-06 — drinking water, nitrate (as N) | 10 mg/L as N | in force | object | verified | 2026-11-01 |

## `milk` — cow's milk, bulk tank

Varies by season: one sampling event is flagged; closing sample — a repeat bulk-tank sample by an FDA-type food method, repeated where model and measurement disagree (references/methods.md §3, item 3).

| Parameter | Unit (canonical) | Validated methods | Reference row | Value | Legal status | Fit | Verification | Checked |
|---|---|---|---|---|---|---|---|---|
| PFOS | ng/L | FDA C-010.03, ISO/IEC 17025 | NYUS-14 — cow's milk, PFOS | 210 ng/L (ppt) | in force | object | verified | 2026-11-01 |
| PFOA | ng/L | FDA C-010.03, ISO/IEC 17025 | — no reference in this pack: reported, not coloured | — | — | — | — | — |
| PFNA | ng/L | FDA C-010.03, ISO/IEC 17025 | — no reference in this pack: reported, not coloured | — | — | — | — | — |
| PFHxS | ng/L | FDA C-010.03, ISO/IEC 17025 | — no reference in this pack: reported, not coloured | — | — | — | — | — |

## Accepted units

A result in another unit is refused with the list below; a wet-weight result for a solid is refused until it is converted to dry weight.

| Unit set | Canonical | Accepted as written (factor to canonical) |
|---|---|---|
| solid_ug_kg | µg/kg | µg/kg (×1), ug/kg (×1), ng/g (×1), ppb (×1), µg/kg dw (×1), ug/kg dw (×1), ng/g dw (×1), ppb dw (×1); basis dry weight — a unit without 'dw' is accepted with a warning |
| water_ng_l | ng/L | ng/L (×1), ng/l (×1), ppt (×1), µg/L (×1000), ug/L (×1000), µg/l (×1000), ug/l (×1000) |
| nitrate_mg_l_n | mg/L as N | mg/L as N (×1), mg/l as N (×1), mg/L NO3-N (×1), mg/L as NO3 (×0.225897), mg/l as NO3 (×0.225897) |

## Dose

Reference row NYUS-10 — sum PFOS + PFOA + PFNA + PFHxS, 4.4 ng/kg bw per week. EFSA four: PFOS, PFOA, PFNA, PFHxS. Mandatory scenarios: off_farm_adult, resident_adult, infant_formula_well_water, young_child_resident.
