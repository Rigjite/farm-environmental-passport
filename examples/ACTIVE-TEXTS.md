# Действующие тексты примеров (с v0.3.6)

| Модуль | Действующий текст | Где лежит | Исходная редакция (не меняется) |
|---|---|---|---|
| 1 — PFAS | редакция 7 от 06.11.2026 (профили младенца и ребёнка — по ATSDR 2023) | `examples/FARM-PFAS-SIMULATION-2026-10-31-r7.md` | `examples/FARM-PFAS-SIMULATION-2026-10-31.md` (sha256 — T8) |
| 2–3 — вода и биогены | редакция 2 от 05.11.2026 (правки Р2: E. coli = STV 410; эталон Cornell) | `examples/FARM-WATER-NUTRIENTS-SIMULATION-2026-10-31-r2.md` | `examples/FARM-WATER-NUTRIENTS-SIMULATION-2026-10-31.md` (sha256 — T8) |

Фигуры модуля 1 (`figures/fig_biosolids.png`, `fig_dose.png`, `fig_well.png`, `fig_soil.png`) соответствуют редакции 7 и строятся `make_figs1.py`. Схема зон, пути поступления и хронология (`figures/fig_zone_map.png`, `fig_pathway.png`, `fig_timeline.png`) вложены в пакет; фотографии-иллюстрации `photo_*.jpg` в публичный пакет не входят; в действующих редакциях ссылки на них убраны, в исходных (sha256 — T8) остаются как часть исходного текста. Фигуры модулей 2–3: действующие — `figures/fig2_n_balance_v2.png` и `figures/fig2_p_balance_v2.png` (нейтральные цвета серий, десятичная запятая; скрипт `make_figs2_v2.py`); исходные `fig2_n_balance.png` и `fig2_p_balance.png` сохранены рядом (скрипт `make_figs2.py`, sha256 — T8). Остальные fig2_* в пакет не вложены.

Синтетические значения во всех редакциях одни и те же.
