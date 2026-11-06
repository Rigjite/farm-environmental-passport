# Shared core — one library, two products

**Status:** working proposal inside farm-environmental-passport v0.3.0. Nothing has been changed in the Ecosystem Digital Twin repository; extracting this folder into a shared library and wiring the twin to it needs the author's approval.

## Why a shared core

The Farm Environmental Passport (a snapshot of one farm: status card, gap registry, sampling plan) and the Ecosystem Digital Twin (a model of a living system: calibration, forecasts, scenarios) answer different questions for different clients, so they stay two skills. What they must not do is keep two copies of the same facts: a threshold re-checked in one copy and forgotten in the other is how a screening product goes wrong. Everything that is a *fact about the world* lives here once; everything that is *a way of working* stays in each skill.

| In the core (shared, versioned) | In each skill (its own) |
|---|---|
| Threshold packs with legal status, check date, verification mark (`core/thresholds/`) | The passport's status table; the twin's watch levels and alert rules |
| Indicator catalogue for farms (`core/indicators/`), keyed to the twin's sections | The twin's full ecosystem catalogue (§1–§32) — referenced, not copied |
| NASA remote-sensing layer: products, resolutions, rules (`core/remote-sensing/`) | Models, calibration, scenarios (twin); dose scenarios, answer card (passport) |
| Analytical methods by matrix; unit conversions | Workflows, templates, tests of behaviour |

## Versioning and governance

- The core carries its own version (this draft: core 1.0.0-draft). Each skill pins the core version it was tested with.
- A threshold or method changes in one place; both skills re-run their tests against the new core before they move their pin.
- IDs are stable: a row or indicator is never renumbered; retired rows are marked *superseded*, never deleted.
- Rows expire: thresholds after 183 days, the NASA layer after 365 days, then they must be re-checked.

## How the passport hands over to the twin

A passport is the twin's entry level for one farm, and the natural next step after it is the twin's **Tier S — Diagnostic & Feasibility Twin**. Mapping checked against the twin's SKILL.md v2.8 (7-stage cycle, Phases 0–6; read 2026-11-01, file sha 0770dfc4):

| Passport output | Twin input (v2.8) |
|---|---|
| Farm identity, field boundaries, the farm's question, consent record (X-07) | Stage 1 — Object Passport (Phase 0): boundaries, management question, maturity level, build tier |
| Threshold rows used (row IDs, legal status, check date) | Stage 1 thresholds — the twin's hierarchy (jurisdiction law first; guidance and drafts stay yellow; the stricter binding standard governs red) is the same rule as the passport's yellow ceiling and red rule; the passport's green-watch (≥ 75 %) plays the role of the twin's operational early-warning level |
| Indicator selection with reasons; gap registry | Stage 1 indicator choice and the [НЕТ ДАННЫХ] register — every passport gap row becomes a register entry |
| Measured values with provenance; NASA time series from the data agent | Stage 2 — Data Inventory & QC (Phase 1): files enter `landing/`, move to `trusted/` after `qc_series.py`; the NASA request already asks for what the Phase 1 onboarding checklist needs (source, access date, licence, resolution, quality mask) |
| Work plan and sampling panels (value-of-information order — a heuristic: consent, facts, cost) | Stage 6 sampling priority and the Tier S VoI/EVSI step: the twin re-ranks the passport's plan quantitatively once a model exists |
| Answer card (status per object, gaps) | Stage 6 public status line (green / yellow / red, maturity label, [НЕТ ДАННЫХ] gaps) |

## Proposed changes to the twin (need her "yes")

1. Its PFAS thresholds and the farm-relevant rows of `references/thresholds.md` point to core row IDs instead of holding their own numbers.
2. A new section (or an extension of §23 "Livestock farm as an ecosystem") references the core's livestock block: feed safety, welfare (Welfare Quality principles), health, milk quality, antimicrobial use, biosecurity, product safety. §23 currently states that it does not cover animal health, disease, breeding or feeding rations — `core/crosswalk-twin.md` lists the 22 indicators that would fill that gap.
3. The twin's agriculture quick set (§18) points to the farm catalogue for field-level detail.

## NASA data

The core's remote-sensing layer names the products, their resolution and their limits; the passport composes a request (`indicator_select.nasa_request`) and **a data agent with NASA Earthdata access executes it**. Satellite values enter as evidence class *remote*: they target sampling, set triggers (for example a drought year from SMAP opens the aflatoxin and forage-nitrate panels) and describe context. They never set a status colour alone, and a field-scale product is used for an object only when it covers at least nine pure pixels.
