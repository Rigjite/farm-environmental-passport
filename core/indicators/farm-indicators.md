# Farm indicator catalogue — rendered

Generated from `core/indicators/farm-indicators.psv` by `scripts/render_catalogue.py`; do not edit by hand.
Tier: core = always when the component is present; conditional = when a trigger is present; research = on request.
Anchor = threshold row in `core/thresholds.md` (— = no anchor: a named gap of the packs, never a borrowed number).
Twin § = section of the Ecosystem Digital Twin `references/indicators.md`; *new* = not covered there.
Indicators: 113.

## Agronomy — crops and soil (32)

| ID | Indicator | Unit | Tier | Present if / trigger | Cost | Panel | Method | Anchor | NASA | Twin § | AEI | Welfare Quality |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-01 | Field map, areas, crops and rotation | ha; crop per field-year | core | crops | desk | records | farm records, parcel registers; HLS crop-cover check | — | HLS | 9, 18 | 10.1 | — |
| A-02 | Soil pH | pH units | core | crops | lab | soil | 1:1 soil:water, composite 0–20 cm per field | — | — | 9 | 26 | — |
| A-03 | Soil organic matter / organic carbon | %; t C/ha | core | crops | lab | soil | loss on ignition or dry combustion; bulk density for stocks | — | — | 9 | 26 | — |
| A-04 | Soil-test phosphorus (Mehlich-3) | mg/kg | core | crops | lab | soil | Mehlich-3, ICP | — | — | 9, 5 | 16 | — |
| A-05 | Soil K, Mg, Ca and CEC | mg/kg; cmol/kg | core | crops | lab | soil | Mehlich-3 ICP; CEC by summation | — | — | 9 | 26 | — |
| A-06 | Soil nitrate (pre-sidedress or late fall) | mg N/kg | conditional | crops / row_crops, biosolids, manure | lab | soil-nitrate | KCl extraction, 0–30 cm | — | — | 9, 5 | 15 | — |
| A-07 | Texture and depth to a restrictive layer | % sand/silt/clay; cm | core | crops | desk | records | soil survey (SSURGO in the US); one lab texture per field to confirm | — | — | 9 | 26 | — |
| A-08 | Compaction: bulk density or penetration resistance | g/cm³; MPa | conditional | crops / heavy_machinery, grazing | field | soil | core sampling or penetrometer, 0–40 cm | — | — | 9, 23 | 26 | — |
| A-09 | Soil biology: respiration, active carbon, earthworms | mg CO2-C/kg; mg/kg; count/m² | research | crops | lab | soil | soil-health panel; hand sorting | — | — | 9, 13 | 26 | — |
| A-10 | Soil erosion (modelled) | t/ha/yr | core | crops | remote | nasa | RUSLE: rainfall erosivity (IMERG), erodibility (soil survey), slope, cover (HLS), practice | — | HLS, IMERG | 9 | 21 | — |
| A-11 | Soil cover / bare-soil days | days/yr bare | core | crops | remote | nasa | HLS NDVI / bare-soil index time series per field | — | HLS | 9, 10 | 11.1 | — |
| A-12 | Tillage practice | class | core | crops | desk | records | farm records; HLS residue check | — | HLS | 17 | 11.2 | — |
| A-13 | Cover crops and rotation diversity | % area; crops per rotation | core | crops | desk | records | farm records; HLS winter greenness | — | HLS | 17 | 10.1 | — |
| A-14 | Salinity (electrical conductivity; SAR where irrigated) | dS/m | conditional | crops / irrigation, arid, road_salt | lab | soil | saturated-paste EC; SAR | — | — | 9 | 26 | — |
| A-15 | Heavy metals in soil: Cd, Cu, Ni, Pb, Zn, Hg | mg/kg DM | conditional | crops / biosolids, manure | lab | soil | strong-acid digestion, AAS/ICP; 25 cores per ≤5 ha, 25 cm (86/278 Annex II C) | EU-09, EU-10, EU-11, EU-12, EU-13, EU-14 | — | 9, 6 | 26 | — |
| A-16 | PFAS in soil (EFSA four + method list) | µg/kg DM | conditional | crops / biosolids, near_afff | lab | soil | EPA 1633; application and control fields; depth stated | NYUS-16 | — | 9, 6 | 26 | — |
| A-17 | Crop and forage yield | t DM/ha | core | crops | desk | records | farm records; yield maps | — | HLS | 11, 17 | — | — |
| A-18 | Forage quality: crude protein, NDF, energy | % DM; MJ/kg | core | forage | lab | feed | NIRS forage analysis | — | — | 11 | — | — |
| A-19 | Nitrate in forage | % NO3 in DM | conditional | forage / drought_year, biosolids, manure | lab | feed | forage nitrate test | — | SMAP | 11 | — | — |
| A-20 | Plant disease and pest pressure | % plants affected; severity score | core | crops | field | scouting | scouting protocol; image-based detection as screening; HLS anomaly maps target the scouting | — | HLS | 11 | — | — |
| A-21 | Pesticide use: products, active substances, rates | kg a.i./ha | core | pesticides | desk | records | spray records | — | — | 17, 6 | 6 | — |
| A-22 | Pesticide risk indicator | index | conditional | crops / pesticides | desk | records | harmonised risk indicator from use records | — | — | 6 | 17 | — |
| A-23 | Pesticide residues in crops, feed or product | mg/kg vs MRL | conditional | crops / pesticides | lab | feed | multi-residue LC-MS/MS and GC-MS/MS | — | — | 6 | — | — |
| A-24 | Mineral fertiliser N, P, K | kg/ha/yr | core | crops | desk | records | purchase and spreading records | — | — | 17, 5 | 5 | — |
| A-25 | Organic inputs: biosolids, manure, compost — rate, N, P, metals | t DM/ha; kg N and P/ha | core | biosolids, manure | desk | records | delivery records and supplier analyses | NYUS-07, NYUS-08, EU-15, EU-08 | — | 17, 5, 23 | 15, 16 | — |
| A-26 | Irrigation volume and source | m³/ha/yr | core | irrigation | desk | records | meters; ECOSTRESS evapotranspiration as cross-check | — | ECOSTRESS | 3, 17 | 7, 20 | — |
| A-27 | Irrigation-water quality: EC, SAR, E. coli, PFAS where indicated | dS/m; CFU/100 mL; ng/L | conditional | irrigation / vegetables, biosolids, near_afff, stream | lab | irrigation-water | EC/SAR; E. coli (EPA 1603); PFAS (EPA 1633) | — | — | 4, 13, 6 | — | — |
| A-28 | NDVI / EVI and phenology | index; day of year | core | crops | remote | nasa | HLS 30 m time series per field, cloud-masked | — | HLS | 11, 18 | — | — |
| A-29 | Tile-drain flow and drain-water nitrate | mg N/L | conditional | crops / tile_drains | lab | drain | drain-outlet grab samples after events | — | IMERG | 5, 23 | 27.1 | — |
| A-30 | Energy use: fuel and electricity | kWh/yr; L diesel/yr | core | — | desk | records | bills and fuel records | — | — | 17 | 8 | — |
| A-31 | Renewable energy produced on the farm | kWh/yr | research | — | desk | records | meter data (solar, biogas) | — | — | 17 | 24 | — |
| A-32 | Crop varieties and genetic diversity | number of varieties; local varieties | research | crops | desk | records | seed records | — | — | 11 | 22 | — |

## Livestock — herd, feed, health, welfare, product safety (42)

| ID | Indicator | Unit | Tier | Present if / trigger | Cost | Panel | Method | Anchor | NASA | Twin § | AEI | Welfare Quality |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L-01 | Herd size and structure | head by class; LSU | core | livestock | desk | records | herd register | — | — | 23 | 10.2 | — |
| L-02 | Stocking density | LSU/ha | core | livestock | desk | records | herd register ÷ farmed area | — | — | 23 | 12 | — |
| L-03 | Milk yield and solids | kg/cow/yr; % fat, protein | core | dairy | desk | records | milk recording; processor statements | — | — | 23 | — | — |
| L-04 | Ration composition and purchased-feed share | % DM; kg DM/head/day | core | livestock | desk | records | ration sheets; purchase records | — | — | 23 | — | — |
| L-05 | Feed N and P content | % DM | core | livestock | lab | feed | NIRS or wet chemistry of main feeds; supplier analyses | — | — | 5, 23 | 15, 16 | — |
| L-06 | Aflatoxins in feed for dairy animals | µg/kg (ppb) | conditional | dairy / drought_year, purchased_grain, cottonseed | lab | feed | LC-MS/MS or validated ELISA screen | NYUS-24, EU-29 | IMERG, SMAP | new | — | — |
| L-07 | Other mycotoxins: DON, zearalenone, fumonisins | µg/kg | research | livestock | lab | feed | LC-MS/MS multi-mycotoxin | — | — | new | — | — |
| L-08 | PFAS in forage and feed (EFSA four + list) | µg/kg | conditional | livestock / biosolids, near_afff | lab | feed | FDA C-010.03 (silage and snaplage validated) or EPA 1633 for solids | EU-30 | — | 6, 23 | — | — |
| L-09 | Livestock drinking-water quality: nitrate, coliforms, TDS; PFAS where indicated | mg/L; CFU/100 mL | core | livestock | lab | well | same visit as the household well; PFAS by EPA 533/537.1 for a well | — | — | 8, 23 | — | — |
| L-10 | Water availability: water points, flow, cleanliness | troughs per animal; L/min; score | core | livestock | field | welfare-visit | on-farm check (Welfare Quality-type) | — | — | new | — | absence of prolonged thirst |
| L-11 | Body condition: share of animals too thin | % animals BCS ≤ 2 (5-point) | core | livestock | field | welfare-visit | 5-point body-condition scoring of a sample | — | — | new | — | absence of prolonged hunger |
| L-12 | Resting comfort: lying time, stall and bedding condition, cleanliness | h/day; score | conditional | livestock / housed | field | welfare-visit | observation or leg sensors; hygiene scoring | — | — | new | — | comfort around resting |
| L-13 | Heat load: temperature-humidity index above the heat-stress level | hours/yr above threshold | core | livestock | remote | nasa | THI from an on-farm sensor; NASA POWER daily T2M/RH2M (0.5°×0.625°) as fallback. The Welfare Quality dairy protocol has no measure for thermal comfort; THI is the skill's proxy | — | POWER | 1, 23 | — | thermal comfort |
| L-14 | Space allowance and freedom of movement (tethering, pen space) | m²/animal; % tethered | core | livestock | field | welfare-visit | on-farm measurement | — | — | new | — | ease of movement |
| L-15 | Lameness prevalence | % animals lame | core | livestock | field | welfare-visit | locomotion scoring (5-point) of the herd or a sample | — | — | new | — | absence of injuries |
| L-16 | Integument alterations (hock lesions, swellings) | % animals | conditional | livestock / housed | field | welfare-visit | on-farm scoring | — | — | new | — | absence of injuries |
| L-17 | Clinical mastitis incidence | cases/100 cows/yr | core | dairy | desk | records | treatment records | — | — | new | — | absence of disease |
| L-18 | Bulk-tank somatic cell count | cells/mL | core | dairy | lab | milk | electronic counter (processor testing) | NYUS-22, EU-26 | — | new | — | absence of disease |
| L-19 | Bulk-tank bacterial (plate) count | CFU/mL | core | dairy | lab | milk | plate count at 30 °C (processor testing) | NYUS-25, NYUS-26, EU-27 | — | new | — | — |
| L-20 | Mortality and culling rate by cause | % per year | core | livestock | desk | records | herd register | — | — | 23 | — | absence of disease |
| L-21 | Young-stock health: diarrhoea and respiratory disease | % calves affected | conditional | livestock / calves | desk | records | treatment records | — | — | new | — | absence of disease |
| L-22 | Access to pasture or an outdoor area | days/yr; h/day | core | livestock | desk | records | grazing records | — | — | 23 | — | expression of other behaviours |
| L-23 | Painful procedures without anaesthesia or analgesia (disbudding, castration, tail docking) | % animals | core | livestock | desk | records | farm protocols and records | — | — | new | — | absence of pain induced by management procedures |
| L-24 | Social behaviour: agonistic interactions | events/animal/hour | research | livestock | field | welfare-visit | direct observation (Welfare Quality protocol) | — | — | new | — | expression of social behaviours |
| L-25 | Human–animal relationship: avoidance distance | % animals that can be touched | research | livestock | field | welfare-visit | avoidance-distance test (Welfare Quality protocol) | — | — | new | — | good human-animal relationship |
| L-26 | Positive emotional state: qualitative behaviour assessment | QBA score | research | livestock | field | welfare-visit | Welfare Quality QBA | — | — | new | — | positive emotional state |
| L-27 | Antimicrobial use by substance and route | mg/PCU or treatment days per animal-year | core | livestock | desk | records | treatment records; veterinary prescriptions | — | — | new | — | — |
| L-28 | Share of highest-priority critically important antimicrobials | % of use | core | livestock | desk | records | from L-27 records by WHO category | — | — | new | — | — |
| L-29 | Biosecurity and vaccination plan | present/absent; score | core | livestock | desk | records | review of the farm plan | — | — | new | — | — |
| L-30 | Official status for notifiable and zoonotic diseases (e.g. tuberculosis, brucellosis; avian influenza for poultry) | status | core | livestock | desk | records | official herd or flock records | — | — | new | — | — |
| L-31 | Zoonotic pathogens in manure or the environment (Salmonella, STEC, Campylobacter) | presence; CFU/g | conditional | livestock / raw_milk_sales, public_access, vegetables | lab | manure | culture or PCR | — | — | 13 | — | — |
| L-32 | Manure production and N excretion | t/yr; kg N/yr | core | livestock | desk | records | herd × excretion coefficients; storage volumes | EU-08 | — | 23 | 10.2 | — |
| L-33 | Manure storage capacity, cover and freeboard | months of storage; covered yes/no | core | livestock | field | walkover | inspection and design records | — | — | 23 | 11.3 | — |
| L-34 | Manure application: rate, timing, method (incl. on frozen or saturated soil) | kg N/ha; dates; method | core | manure | desk | records | spreading log | EU-08 | IMERG, SMAP | 23, 17 | 15 | — |
| L-35 | Enteric methane | kg CH4/yr; g/kg milk | core | livestock | desk | records | IPCC 2019 Tier 2 from intake and yield | — | — | 2, 23 | 19 | — |
| L-36 | Ammonia from housing, storage and spreading | kg NH3/yr | core | livestock | desk | records | EMEP/EEA emission inventory guidebook, Tier 2 | — | — | 2, 23 | 18 | — |
| L-37 | Nitrous oxide from manure and soils | kg N2O/yr | core | livestock, crops | desk | records | IPCC 2019 Tier 1/2 | — | — | 2, 23 | 19 | — |
| L-38 | Veterinary drug residues in milk, meat or eggs | pass/fail vs tolerances or MRLs | core | sells_milk, sells_meat, sells_eggs | lab | milk | processor or official screening tests | — | — | new | — | — |
| L-39 | Aflatoxin M1 in milk | µg/kg | conditional | dairy / drought_year, purchased_grain, cottonseed | lab | milk | ISO 14501 (immunoaffinity + HPLC) or validated ELISA | NYUS-23, EU-28 | — | new | — | — |
| L-40 | PFAS in milk, meat or eggs (EFSA four + list) | ng/L; µg/kg | conditional | sells_milk, sells_meat, sells_eggs / biosolids, near_afff | lab | milk | FDA C-010.03 or an equivalent ISO/IEC 17025 food method | NYUS-14, NYUS-15, EU-18, EU-19, EU-20, EU-21, EU-22 | — | 6 | — | — |
| L-41 | Raw-milk pathogens (Listeria, Salmonella, STEC, Campylobacter) | presence per 25 mL | conditional | dairy / raw_milk_sales | lab | milk | culture or PCR in an accredited food laboratory | — | — | 13 | — | — |
| L-42 | Breeds and livestock genetic diversity | number of breeds; local breeds | research | livestock | desk | records | herd register | — | — | 15 | 22 | — |

## Farm ecosystem — water, nutrients, habitat, climate (31)

| ID | Indicator | Unit | Tier | Present if / trigger | Cost | Panel | Method | Anchor | NASA | Twin § | AEI | Welfare Quality |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E-01 | Drinking well — PFAS (EFSA four + method list) | ng/L | conditional | drinking_well / biosolids, near_afff, industry_near | lab | well | EPA 533 or 537.1, reporting limit ≤ 2 ng/L | NYUS-01, NYUS-02, NYUS-03, NYUS-04, NYUS-05, EU-01, EU-02, EU-04 | — | 8, 6 | — | — |
| E-02 | Drinking well — nitrate and nitrite | mg/L as N | core | drinking_well | lab | well | ion chromatography or approved colorimetric method | NYUS-06, EU-03, EU-07 | — | 8 | 27.1 | — |
| E-03 | Drinking well — total coliform and E. coli | presence/100 mL | core | drinking_well | lab | well | approved presence/absence method | — | — | 8, 13 | — | — |
| E-04 | Drinking well — geogenic elements (arsenic, manganese, uranium) | µg/L | conditional | drinking_well / geogenic_risk | lab | well | ICP-MS | — | — | 8 | — | — |
| E-05 | Stream — total phosphorus, nitrate, suspended solids | µg/L; mg/L | core | stream | lab | stream | monthly grab and event samples | NYUS-19 | IMERG | 4, 5 | 27.1 | — |
| E-06 | Stream — E. coli or enterococci | CFU/100 mL | conditional | stream / grazing, manure, biosolids | lab | stream | EPA 1603 / 1600; seasonal series for geometric mean and percentile | NYUS-11, NYUS-12, EU-25 | IMERG | 4, 13 | — | — |
| E-07 | Stream flow (stage and discharge) | m³/s | conditional | stream / biosolids, manure | field | stream | staff gauge and rating curve | — | IMERG | 3 | — | — |
| E-08 | Pond — total phosphorus, chlorophyll-a, Secchi depth | µg/L; m | core | pond | lab | pond | monthly May–September | NYUS-19, NYUS-20, NYUS-21 | DSWx | 4, 5, 12 | — | — |
| E-09 | Pond — dissolved-oxygen and temperature profile | mg/L by depth | core | pond | field | pond | multiparameter probe, 0.5 m steps | — | — | 4 | — | — |
| E-10 | Cyanobacteria and cyanotoxins (microcystins) | cells/mL; µg/L | conditional | pond / eutrophic_pond, animal_access_pond | lab | pond | cell counts; ELISA for microcystins | — | — | 12 | — | — |
| E-11 | Farm-gate nitrogen balance | kg N/ha/yr; kg N/Mg milk | core | — | desk | records | passport_calc.farm_gate_balance from records; denominator named | NYUS-17, EU-08 | — | 5, 17 | 15 | — |
| E-12 | Farm-gate phosphorus balance | kg P/ha/yr; kg P/Mg milk | core | — | desk | records | as E-11 | NYUS-18 | — | 5, 17 | 16 | — |
| E-13 | Field nutrient export and delivery to water (modelled) | kg/yr | core | stream, pond | desk | records | export coefficients × area × delivery ratio, checked against E-05 and E-08 | — | — | 5 | 16 | — |
| E-14 | Riparian buffer width and condition | m; % vegetated | core | stream, pond | field | walkover | field survey; HLS NDVI along banks only if the pixel-fit check passes | — | HLS | 10 | 28 | — |
| E-15 | Livestock access to watercourses | % of bank fenced | conditional | stream, pond / grazing | field | walkover | survey | — | — | 10, 23 | — | — |
| E-16 | Semi-natural habitat share: hedgerows, margins, woodland | % farm area | core | — | remote | nasa | HLS or aerial classification with field check | — | HLS | 10 | 28 | — |
| E-17 | Protected or high-nature-value areas on or next to the farm | ha; distance | conditional | — / protected_area_near | desk | records | public protected-area registers | — | — | 10, 17 | 2, 23 | — |
| E-18 | Pollinators (abundance, diversity) | count per transect | conditional | crops / insect_pollinated | field | biodiversity | transect walks or pan traps in season | — | — | 14, 16 | — | — |
| E-19 | Farmland birds | species; pairs | research | — | field | biodiversity | point counts; acoustic detector with a published error rate, never the sole basis | — | — | 15 | 25 | — |
| E-20 | Amphibians at farm ponds | presence by species | research | pond | field | biodiversity | visual or egg-mass surveys; eDNA | — | — | 15 | — | — |
| E-21 | Land-use and land-cover change | ha changed per class | core | — | remote | nasa | HLS (from 2013) and the Landsat archive | — | HLS, LANDSAT | 10 | 9 | — |
| E-22 | Drought exposure: soil-moisture and precipitation anomalies | percentile vs climatology | core | — | remote | nasa | SMAP L4 root zone (9 km) and IMERG (0.1°) — farm-level context, not field status | — | SMAP, IMERG | 1 | — | — |
| E-23 | Field flooding | days flooded per field | conditional | — / floodplain | remote | nasa | OPERA DSWx-HLS 30 m, pixel-fit check per field | — | DSWx | 3, 1 | — | — |
| E-24 | Frost and heat days; growing degree days | days; °C·days | core | — | remote | nasa | on-farm station; NASA POWER daily T2M as fallback | — | POWER | 1 | — | — |
| E-25 | Water abstraction, all uses | m³/yr | core | — | desk | records | meters or estimates per use | — | — | 3, 17 | 20 | — |
| E-26 | Whole-farm greenhouse-gas balance | t CO2e/yr; kg CO2e/kg product | core | — | desk | records | IPCC 2019 from L-35, L-37, A-30 and fertiliser | — | — | 2, 17 | 19 | — |
| E-27 | Organic status and agri-environment commitments | status; ha under a scheme | core | — | desk | records | certificates; scheme contracts | — | — | 17 | 1, 4 | — |
| E-28 | Farmer training and use of advisory services | yes/no; hours | research | — | desk | records | interview | — | — | 17 | 3 | — |
| E-29 | Input intensity (fertiliser, feed, LSU per hectare) | kg/ha; LSU/ha | core | — | desk | records | derived from A-24, L-04, L-02 | — | — | 17 | 12 | — |
| E-30 | Farm type and specialisation | type class | core | — | desk | records | farm records (standard-output classes) | — | — | 17 | 13 | — |
| E-31 | Pesticides in the well or stream | µg/L | conditional | drinking_well, stream / pesticides | lab | well | multi-residue LC-MS/MS | — | — | 6, 8 | 27.2 | — |

## Cross-cutting — contaminant sources, AMR, governance (8)

| ID | Indicator | Unit | Tier | Present if / trigger | Cost | Panel | Method | Anchor | NASA | Twin § | AEI | Welfare Quality |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| X-01 | Biosolids source — PFOS, PFOA and method list | µg/kg DM | conditional | — / biosolids | desk | records | supplier DMM-7 results; EPA 1633 | NYUS-07, NYUS-08, NYUS-09 | — | 6, 17 | — | — |
| X-02 | Biosolids — heavy metals | mg/kg DM | conditional | — / biosolids | desk | records | supplier analyses | EU-15 | — | 6 | — | — |
| X-03 | Biosolids — pathogen class and treatment | class; indicator organisms | conditional | — / biosolids | desk | records | supplier certificates | EU-16 | — | 13 | — | — |
| X-04 | Nearby sources: AFFF sites, landfills, industry, spill records | list; distance | core | — | desk | records | public registers and maps | — | — | 6, 17 | — | — |
| X-05 | Antimicrobial-resistant bacteria or genes in manure, biosolids or water | presence; gene copies | research | livestock, biosolids | lab | manure | culture with breakpoints; qPCR of resistance genes | — | — | 13 | — | — |
| X-06 | Microplastics in soil (biosolids, plastic mulch, silage film) | particles/kg | research | crops | lab | soil | density separation and spectroscopy | — | — | 6 | — | — |
| X-07 | Farm consent and data-use record | recorded yes/no; scope | core | — | desk | records | signed consent | — | — | 17 | — | — |
| X-08 | Completeness of farm records (feed, fertiliser, manure, antimicrobial use, spreading) | % of required logs present | core | — | desk | records | records audit | — | — | 17 | — | — |
