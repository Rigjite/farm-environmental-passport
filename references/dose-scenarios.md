# Product → dose scenarios

Weekly dose (ng/kg bw per week) = concentration × daily intake × 7 ÷ body weight (`passport_calc.weekly_dose`). The result is compared with the EFSA tolerable weekly intake, **4.4 ng/kg bw per week for the sum of PFOS + PFOA + PFNA + PFHxS** (EFSA Journal 2020;18(9):6223). It is a screening estimate with stated uncertainty, not a health forecast.

## 1. Mandatory scenarios

A passport prints at least these rows; a scenario whose parameters cannot be sourced is printed as a **break-even intake** instead of a dose.

| Scenario | Who | Pathways | Parameters and their source |
|---|---|---|---|
| A | consumer off the farm, adult | the product only (milk, eggs, meat, vegetables) | body weight 70 kg; product intake range stated with its source |
| B | resident adult | product + well water | water: new cards use ATSDR 2023, Table 1 — adult (21–78 y) 1,313 mL/day mean, 3,229 mL/day 95th percentile, body weight 80 kg. The worked example keeps the earlier ATSDR default (2 L/day, 70 kg; Public Health Assessment Guidance Manual 2005, which the 2023 guidance updates) and prints the ATSDR 2023 range as a sensitivity line: 1.58–3.92 ng/kg bw/week, conclusions unchanged |
| C | **sensitive group: infant fed formula made with well water** | well water | birth to < 1 year: 595 mL/day mean, 1,106 mL/day 95th percentile, body weight 7.8 kg (ATSDR 2023, Table 1, from the EPA Exposure Factors Handbook 2019 update, Chapter 3) |
| D | **sensitive group: young child resident** | well water (+ product) | 1 to < 2 years: 245 mL/day mean, 658 mL/day 95th percentile, body weight 11.4 kg (same source); product intake only with a cited consumption value — otherwise break-even |

Why C and D are mandatory: the critical effect behind the TWI (reduced vaccine response) was identified in 1-year-old children, and per-kilogram water intake of infants and toddlers is several times that of adults. An adult-only scenario can report "no exceedance" while the people the TWI was built to protect are above it.

## 2. Completeness of the sum

The TWI applies to a four-PFAS sum. With fewer than four measured, every dose is a **lower bound** and is printed as "n of 4 PFAS — lower bound"; the missing analytes go to the gap registry with the sample that closes them (usually: the same samples, re-analysed for the full list, no new field trip). Censored analytes enter as [0, RL] (status-rules.md §4).

## 3. Break-even intake

When a product's consumption by a group is not sourced, print the intake at which the group reaches the TWI given the other pathways: `passport_calc.break_even_intake(4.4 − dose_from_other_pathways, concentration, body_weight)`. This keeps the card honest without inventing a consumption figure.

## 4. Worked check on the synthetic farm (examples/, values synthetic)

Inputs: well PFOS 6.5 + PFOA 3.8 = 10.3 ng/L; tank milk PFOS 18 ng/L; 2 of 4 PFAS measured.

| Scenario | Dose, ng/kg bw/week | Share of TWI | Note |
|---|---|---|---|
| A, adult, milk 0.25–0.64 L/day | 0.45–1.15 | 10–26 % | as in the simulation |
| B, adult resident, milk + 2 L water | 2.51–3.21 | 57–73 % | as in the simulation |
| C, infant formula, mean water intake | 5.50 | 125 % | **above the TWI from water alone, with 2 of 4 PFAS** |
| C, infant formula, 95th percentile | 10.22 | 232 % | |
| D, child 1–<2 y, water only, mean | 1.55 | 35 % | break-even farm milk ≈ 0.26 L/day |
| D, child 1–<2 y, water only, 95th pct | 4.16 | 95 % | break-even farm milk ≈ 0.02 L/day |

Consequence for the worked example: the simulation's sentence "no exceedance in any scenario" holds for adults only. The synthetic farm's card must carry the sensitive-group line, and the well — already the first object of re-sampling — becomes the first object for the household's water choices for infant formula, a decision that belongs to the household and its health department, not to the passport.

## 5. Limits

The skill does not give medical advice and does not estimate serum levels. Background exposure from the general diet is outside the farm's line and is stated as such. Nitrate is a separate, acute pathway for infants: where a health agency states that water above 10 mg/L nitrate-N should not be used for infant formula (for example Connecticut DPH private-well guidance), the card repeats that advice with its source.
