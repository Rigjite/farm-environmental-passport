# Texts in force (from v0.3.7)

| Module | Text in force (English) | Russian source | Original redaction (never changed) |
|---|---|---|---|
| 1 — PFAS | `FARM-PFAS-SIMULATION-2026-10-31-r7.en.md` — redaction 7 of 2026-11-06 (infant and child profiles from ATSDR 2023) | `FARM-PFAS-SIMULATION-2026-10-31-r7.md` | `FARM-PFAS-SIMULATION-2026-10-31.md` (sha256 — T8) |
| 2–3 — water and nutrients | `FARM-WATER-NUTRIENTS-SIMULATION-2026-10-31-r2.en.md` — redaction 2 of 2026-11-05 (E. coli = STV 410; Cornell benchmark) | `FARM-WATER-NUTRIENTS-SIMULATION-2026-10-31-r2.md` | `FARM-WATER-NUTRIENTS-SIMULATION-2026-10-31.md` (sha256 — T8) |

**Figures.** English: `figures/en/` — all 13 figures of Modules 1–3, built by `make_figs_en.py`; Modules 2–3 are computed from the unchanged data block of `make_figs2.py`. Russian: `figures/` — Module 1 by `make_figs1.py`; balances `fig2_*_v2.png` by `make_figs2_v2.py`; water sketch, well nitrate, creek phosphorus and the Vollenweider diagram from the original `make_figs2.py`; the original balance figures `fig2_n_balance.png` and `fig2_p_balance.png` are kept beside the `_v2` versions (script sha256 — T8). Series colours in the figures in force are neutral; red, yellow and green mean status only.

Illustration photographs are not part of the public package. The unchanged originals of 31 October keep their original image paths (`farm-sim-figures/…`, `photo_*.jpg`), which are not in the package; read the texts in force for working figures.

The synthetic values are the same in every redaction and in both languages.
