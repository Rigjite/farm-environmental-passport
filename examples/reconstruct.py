"""Reconstruct the deterministic chain of FARM-PFAS-SIMULATION (Delaware, synthetic).
2026-11-05. All inputs are taken from the simulation texts (module 1 and module 2)
or from the v0.2 report. Expected output: adult 2.06 / 0.45-1.15 / 2.51-3.21; milk model 4.2-17.4 ng/L.
"""
# --- inputs from the simulations (synthetic or assumptions, as labelled there) ---
well_pfos, well_pfoa = 6.5, 3.8          # ng/L, one October sample (synthetic)
milk_pfos = 18.0                          # ng/L, bulk tank, one date (synthetic)
soil = {"F1": 0.90, "F2": 0.65, "F3": 0.50, "F4": 0.35, "F5": 0.15}  # ug/kg PFOS (synthetic)
TF_lo, TF_hi = 0.026, 0.37                # soil->feed transfer, literature range
dm_intake, own_share = 22.0, 0.60         # kg DM/day per cow; share of own feed
cow_water = 100.0                         # L/day per cow (from well)
transfer_milk = 0.14                      # fraction of PFOS dose excreted to milk
milk_yield = 10500 / 365                  # kg/day per cow (module 2 assumption)
TWI = 4.4                                 # ng/kg bw/week, EFSA 2020, sum of 4 PFAS

w = well_pfos + well_pfoa

# --- adult (simulation section 4) ---
bw, water_L = 70.0, 2.0
milk_lo, milk_hi = 0.25, 0.64
d_water = w * water_L * 7 / bw
d_milk_lo, d_milk_hi = milk_pfos * milk_lo * 7 / bw, milk_pfos * milk_hi * 7 / bw
print(f"adult water {d_water:.2f}; milk {d_milk_lo:.2f}-{d_milk_hi:.2f}; "
      f"total {d_water+d_milk_lo:.2f}-{d_water+d_milk_hi:.2f}  (sim: 2.06; 0.45-1.15; 2.51-3.21)")

# --- infant: back-calculate intake per kg from v0.2 doses 5.50 / 10.22 ---
inf_mean = 5.50 / (7 * w); inf_p95 = 10.22 / (7 * w)
print(f"infant intake implied: mean {inf_mean*1000:.1f} mL/kg/d, P95 {inf_p95*1000:.1f} mL/kg/d; "
      f"%TWI {5.50/TWI:.0%} / {10.22/TWI:.0%}")

# --- child 1-2 y: v0.2 break-even milk 0.26 L/d (mean water), 0.02 (P95 water). BW 11.4 kg assumed ---
bw_c = 11.4
budget = TWI * bw_c / 7                      # ng/day
w_mean = (budget - 18.0 * 0.26) / w
w_p95 = (budget - 18.0 * 0.02) / w
print(f"child BW {bw_c}: implied water mean {w_mean:.3f} L/d, P95 {w_p95:.3f} L/d")

# --- milk model: soil -> feed -> cow (+ cow drinking water) -> milk ---
soil_feed_fields = sum(soil[f] for f in ["F1", "F2", "F3", "F4"]) / 4   # ug/kg
own_feed = dm_intake * own_share
for TF in (TF_lo, TF_hi):
    feed_ng = soil_feed_fields * 1000 * TF * own_feed       # ng/day from own feed
    water_ng = cow_water * well_pfos                         # ng/day from well water
    milk = (feed_ng + water_ng) * transfer_milk / milk_yield
    print(f"TF {TF}: feed {feed_ng:.0f} ng/d, cow water {water_ng:.0f} ng/d "
          f"(water share {water_ng/(feed_ng+water_ng):.0%}) -> milk {milk:.1f} ng/L")
print(f"mean soil F1-F4 = {soil_feed_fields:.2f} ug/kg (sim model: 4-17 ng/L)")
