# Status rules, censored values and units

The status of every object in the passport is computed by one decision table, the same for every module. The code is `scripts/passport_calc.py` (`screening_status`, `censored_status`, `worst`); this page is its specification. Tests T9–T11 run the table on edge cases.

## 1. Classes of evidence

| Class | Meaning | May carry a colour? |
|---|---|---|
| measured | laboratory result, method and laboratory named | yes |
| modelled | model named, inputs named | no — the object stays **grey** with a risk note and a priority sample |
| remote | satellite product named with version, date, quality mask (`core/remote-sensing/nasa-layer.json`) | no — targets sampling, sets triggers, gives context; the object stays **grey** until measured |
| never measured | nothing exists | no — **grey**, and a full row in the gap registry |

A model never upgrades or downgrades a measured status. When model and measurement disagree, both are printed and the disagreement is a gap (example: milk 18 ng/L measured vs 4–17 ng/L modelled in the worked example — kept as is).

## 2. Kinds of reference

Each threshold row carries a `legal_status`: **in force**, **future** (adopted, applies from a date), **guidance** (official non-binding value, benchmark, recommendation, TWI), **orientation** (classification or literature criterion), **superseded**, **requirement** (procedure, no number). Applicability is separate: a public-water MCL compared with a private well is a reference *by analogy* — the colour logic is the same, the wording changes ("above the health-based reference", never "violation").

## 3. Decision table (one object, one reference)

Apply in order; the first matching line decides.

| # | Condition | Status |
|---|---|---|
| 1 | No measured value | **grey** — not assessed |
| 2 | All values below the reference | **green**; **green-watch** if the highest value is ≥ 75 % of the reference (a skill convention, not a norm) |
| 3 | A value is above a reference that is *future*, *guidance*, *orientation* or *superseded* | **yellow** at most — screening only |
| 4 | The reference is *in force* and its **own determination rule** is met (running annual average, confirmation sample, percentile over a season, a regulator's tier triggered by one result) | **red** |
| 5 | The reference is *in force*, it has no determination rule of its own, and **two consecutive sampling events** are above it | **red** |
| 6 | Any other exceedance (one sample; one quarter above while the mean is below) | **yellow** |

An object compared with several references takes the **worst** status among them, and the card names the reference that set it. Grey never hides a colour: an object with one measured and one never-measured analyte gets the colour of the measured one plus a gap row for the other.

Red means a sustained exceedance under the source's own rule — never a single sample, unless the source itself acts on a single result (DMM-7 tiers are such a case).

## 4. Censored values (below the reporting limit)

- A result reported as `<RL` is stored as censored with its reporting limit — never as 0, never as missing.
- Sums are reported as **[lower bound, upper bound]**: censored results count as 0 in the lower bound and as RL in the upper bound (the convention EFSA uses for exposure).
- The status is computed on both bounds. If they differ, the card prints the worse one and the flag **"depends on censored values"** — the remedy is a laboratory with a lower reporting limit, which goes into the sampling plan.
- An analyte that was never analysed is not censored; it is a gap. A sum that misses analytes is a **partial sum**, printed with "n of N analytes — lower bound".

## 5. Units

| Conversion | Rule | Where it bites |
|---|---|---|
| Nitrate as N → as NO₃ | × 4.427 (62.00 / 14.01) | US MCL 10 mg/L as N vs EU 50 mg/L as NO₃ (= 11.3 as N) |
| Milk per litre → per kg | ÷ 1.03 kg/L (stated convention) | EU indicative levels for milk are in µg/kg |
| lb/acre → kg/ha | × 1.12085 | Cornell feasible balances |
| lb/cwt milk → kg/Mg milk | × 10 | Cornell balances per unit of milk |
| ppb in solids | = µg/kg dry weight | DMM-7 tiers; state the basis (dry / wet) |
| ng/L ↔ µg/L | ÷ / × 1000 | EU drinking-water values are printed in µg/L |

Every converted number in the card shows the original unit in brackets.

## 6. Wording in the card

- green — "below the [reference] ([value], [status], checked [date])"
- yellow — "above the [future / guidance] reference; screening, not a compliance finding"
- red — "sustained exceedance of the in-force [reference] under its own rule ([rule])"
- grey — "not assessed: [never measured / model only]; closing sample: [...]"

The words *complies*, *safe*, *unsafe*, *violation* do not appear in a passport.
