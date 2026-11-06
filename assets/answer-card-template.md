# Farm answer card — template

Fill every field; a field that does not apply reads "n/a — reason", never blank. Every number carries its provenance tag: *measured · [lab, method, date]*, *modelled · [model]*, *remote · [NASA product, version, date, quality mask]*, *reference · [row ID, checked date]*.

```
FARM ENVIRONMENTAL PASSPORT — ANSWER CARD
Farm: [name or code]            Jurisdiction pack: [NY-US / EU / …] version [date]
Prepared: [date]  by [operator]  Skill version: 0.3.0  Core: 1.0.0-draft
Consent: [farm consent to use / publish — yes/no, date]   Public layer: [aggregated only]

STATUS BY OBJECT                     status        reference that set it        provenance
  Biosolids source                  [colour]      [row ID, value, legal status]  [tag]
  Soil, application fields          [colour]      …                              …
  Drinking well — PFAS              [colour]      …
  Drinking well — nitrate           [colour]      …
  Product — [milk / eggs / …]       [colour]      …
  Surface water — [stream / pond]   [colour]      …
  N balance / P balance             [colour]      [benchmark, denominator named]
  Livestock — bulk-tank milk (SCC, plate count)  [colour]  [PMO / EU 853/2004 row, rule]
  Livestock — welfare (12 Welfare Quality criteria)  [observed n of 12; no colour without a protocol]
  (grey = not assessed: never measured or model only)

DOSE (screening, not a health forecast)        n of 4 EFSA PFAS: [n] — [lower bound / complete]
  A  off-farm adult, product only     [x–y] ng/kg bw/wk   [% of TWI 4.4]
  B  resident adult, product + water  [x–y]               [%]
  C  infant formula with well water   [x] (mean) / [y] (95th)  [%]
  D  young child resident             [x] / break-even product intake [L/day]

INDICATORS (catalogue 113)  selected [n] · to confirm [n, waiting on k facts] · left out [n, reasons attached]
  Facts to confirm first: [list]
  Remote context (never a colour): drought flag [yes/no, SMAP months ≤ 20th pct], flooding, heat load (THI days)
  NASA request to the data agent: [products] · excluded by pixel fit: [objects]

WORK PLAN (value of information)  consent → confirm facts → records → NASA → field visits → lab panels
  1. …

GAP REGISTRY (what is not measured → the sample that closes it)
  1. …

SAMPLING PLAN (object · point · depth/volume · season · analytes · method · gap closed)
  1. …

RECOMMENDATIONS (each tied to a status or a gap)
  - …
  Re-check date: [date]   Threshold rows due for re-verification: [IDs or none]

LIMITS: screening and expert opinion, not a compliance determination; no medical conclusions;
synthetic or modelled values are labelled as such.
```

The words *complies*, *safe*, *unsafe*, *violation* do not appear on the card.
