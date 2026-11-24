# Bad input — what the check says (since v0.3.8)

Three input folders with deliberate errors, for `python3 scripts/validate_input.py FOLDER`. They are illustrations of input errors, not farms. Test T37 checks that each gives exactly these messages.

| Folder | What is wrong | Messages |
|---|---|---|
| `1-censored-written-as-text/` | results written `<2` and `ND` in the value column; a `<` result without its reporting limit; a decimal comma | errors `censored-as-text` (2), `rl-missing`, `decimal-comma` |
| `2-units-and-objects/` | soil PFOS in mg/kg; soil PFOA on a wet-weight basis; an object that was never declared; nitrate without its basis; a drinking-water PFAS result by EPA 1633 | errors `unit-not-accepted` (2), `wet-weight`, `unknown-object`; warning `method-not-valid` — that result is printed grey |
| `3-missing-provenance/` | a real farm (`synthetic: false`) without its consent and without dose scenarios; a date in the future; an empty method; an empty date; two results for one event; a model row without its range | errors `consent-missing`, `dose-scenarios-missing`, `date-in-future`, `method-missing`, `date-missing`, `duplicate-event`, `model-range` |

Every message names the file, the line and the column, and says how to fix it.
