# Farm Environmental Passport

![version 0.3.6](https://img.shields.io/badge/version-0.3.6_preview-blue)
[![Method: CC BY 4.0](https://img.shields.io/badge/method-CC_BY_4.0-lightgrey)](LICENSE)
[![Core: CC BY-NC 4.0](https://img.shields.io/badge/core-CC_BY--NC_4.0-lightgrey)](LICENSE-CORE)
[![Code: Apache 2.0](https://img.shields.io/badge/code-Apache_2.0-blue)](LICENSE-CODE)
[![Methods note DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24017216.svg)](https://doi.org/10.5281/zenodo.24017216)

An agent skill that builds an independent environmental passport for **one specific farm**: what enters the farm, what has been measured and by what method, what has never been measured, and which sample to take first. PFAS screening is the first module; the same construction covers water, nutrients, soil, livestock, other contaminants, climate risk, ponds and biodiversity.

> **Status — preview (v0.3.6).** The method is demonstrated on a **synthetic** dairy farm in Delaware County, New York. Every laboratory value in `examples/` is invented and labelled as such; the thresholds, the structure and the calculations are real. The skill has **not yet been validated on a real farm** — a field pilot is the next step. The passport is screening and expert opinion, not a compliance determination, a laboratory report or medical advice.

**Method:** Baldanova R. (2026). *Farm Environmental Passport: a status-and-gap method for screening the environmental pathways of a single farm, with PFAS as the first module.* Methods note. Zenodo. https://doi.org/10.5281/zenodo.24017216

## What it does

- **Thresholds are data.** Every reference value is stored with its unit, legal status (in force, future, guidance, orientation, superseded, requirement), date, the issuing body's own determination rule, the date of the last check and a verification mark. Packs: New York / US federal and European Union (`core/thresholds/`).
- **Only measurements carry a colour.** Anything known only from a model, a satellite product or not at all stays **grey** and enters the gap registry with the sample that would close it. Red is reserved for a sustained exceedance of a rule in force (`references/status-rules.md`).
- **Four mandatory dose scenarios** — off-farm adult, resident adult, infant fed formula prepared with well water, young child — with exposure factors from ATSDR (2023) and the EFSA tolerable weekly intake (`references/dose-scenarios.md`).
- **Uncertainty and value of information.** Monte Carlo propagation and first-order sensitivity indices rank the next samples (`examples/uncertainty.py`).
- **Indicator catalogue** of 113 indicators — agronomy and soil, livestock, the farm ecosystem, cross-cutting items — with selection rules so that "considered" does not mean "sampled" (`core/indicators/`).
- **NASA remote-sensing layer** — products, resolutions and rules; satellite values target field checks and set triggers but never set a status alone (`core/remote-sensing/nasa-layer.json`).

## What it does not do

It does not measure: certified laboratories measure, and the passport specifies points, depth, season, analytes and methods. It does not issue compliance determinations or health conclusions, and it never publishes a farm's data without the farm's written consent.

## Use

The skill is a folder with `SKILL.md` at its root, in the Agent Skills format: an AI agent that supports skills reads `SKILL.md` and follows it, calling the scripts in `scripts/`.

Run the tests (Python 3.10+; `numpy` and `matplotlib` only for the examples and figures):

```bash
python3 tests/run_tests.py
```

The run writes `tests/RUN-LOG.md`. Expected result for this version: 34/34 PASS.

## Layout

| Path | Contents |
|---|---|
| `SKILL.md` | the skill: procedure, rules, quality gate |
| `core/` | shared library: indicator catalogue, threshold packs, NASA layer, crosswalk to the Ecosystem Digital Twin catalogue |
| `references/` | status rules, dose scenarios, methods by matrix, threshold verification record |
| `scripts/` | `passport_calc.py` (doses, balances, statuses), `indicator_select.py` (selection, gap registry, sampling plan, NASA request), `render_catalogue.py` |
| `examples/` | synthetic farm: PFAS module (redaction 7), water and nutrients module (redaction 2), originals, figures and scripts |
| `tests/` | `run_tests.py`, test descriptions, last run log |
| `archive/v0.1.0/` | the first version, unchanged |

## Related

- Ecosystem Digital Twin — the companion skill for living models of ecosystems; the passport is the twin's entry level for one farm: https://github.com/Rigjite/Ecosystem-Digital-Twin

## Author

Rigjita Baldanova, PhD — New York, NY, USA · ORCID [0009-0009-7891-7007](https://orcid.org/0009-0009-7891-7007)

Large language models assisted with drafting, code and reference checks; the author verified every source and number.

## Licence

Method and documentation — CC BY 4.0; indicator catalogue, threshold packs and remote-sensing layer (`core/`) — CC BY-NC 4.0; code — Apache-2.0. Full texts: `LICENSE`, `LICENSE-CORE`, `LICENSE-CODE`; which part is under which licence: `LICENSE-NOTICE.md`.
