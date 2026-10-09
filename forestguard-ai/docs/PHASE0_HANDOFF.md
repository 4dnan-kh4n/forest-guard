# Phase 0 handoff — compartment 279 — 9 October 2026

**Engineering handoff ready. The scientific Phase 0 exit requirement for credible
current forest-positive references is not met.** Proceed with the lightweight
Phase 1 foundation; do not interpret this as approval for validated forest
training, area/change reporting or fire forecasts. No further bulk reference
downloads are planned without a concrete evidence benefit.

## Objective and scope

Determine whether the selected compartment, real small imagery, available
references, INR 0 tools and existing hardware support a credible forest-cover
workflow. The user-confirmed compartment 279 polygon is the provisional study
area; it is not the whole Joga beat. Independent surveyed registration and
current administrative verification remain unmeasured.

## Working deliverables and verification

| Requirement | Result |
|---|---|
| Exact study polygon | Original KML and selected GeoJSON preserved; SHA-256/version checks pass; 82 ring vertices and 3,159 nonadjacent edge checks pass |
| Forest definition | Forest-associated tree stands above 0.5 ha, canopy above 10%, credible height/potential above 5 m; agricultural orchards/crops excluded; uncertain cases retained |
| Real Sentinel crops | April 3 / December 9, 2025; calibration, grids, masks/features and 27 hashes pass; common valid feature coverage 12,338/13,099 (94.19%) |
| Finer reference crops | April 7 / November 9 Resourcesat crops exported privately from Kaggle; seven hashes per bundle and grid/mask/count checks pass |
| November coverage | 209,362/209,468 nonzero study centres (99.9494%); 106 all-zero centres excluded. This is before full cloud/shadow assessment |
| Seven dated reference cases | Three satellite-interpreted open-water/non-forest cases; three wooded candidates and one mixed patch remain unknown. Screenshots, notes and provenance audit preserved |
| Historical height research | ETH 2020 height/uncertainty crop verified; case 3 has the strongest supporting height estimate. Stale model predictions do not become current independent truth |
| NASA measurement research | Bounded GEDI quality-screening/ICESat-2 subset attempts produced no accepted reference heights; actual failures/no-data outcomes preserved |
| Budget and licenses | Free/open tools and source attribution documented; heavy processing uses private hosted CPU; no paid model or API dependency introduced |
| Local foundation | Python 3.11.5, NumPy 2.1.3, Rasterio 1.4.3; pinned wheels retained. Offline real-data, corruption, missing-input and overwrite checks pass again |
| Git and reproducibility | Source notebooks/scripts/docs trackable; downloaded data, private review records, models and secrets ignored and preserved locally |

These are checks of data handling and interpretation feasibility, not forest
accuracy. April and December are different seasons; their visual difference must
not be reported as deforestation. Current cover area, loss/gain, fire events and
future risk have not been validated. Presentation-era synthetic results are not
evidence for this study.

## Remaining scientific requirement

See [the completed remaining-requirements review](PHASE0_REMAINING_REQUIREMENTS.md)
for the exact missing evidence and saved location-specific review packet.

Evidence must support the adopted stand/height/land-use definition for current
forest-positive examples. Existing independent test labels are absent. Further
model agreement, green imagery or administrative PF status cannot replace this.
Original field photography is prohibited and is not requested. Permitted dated
reference review or location-linked survey records can resolve the gap without
requiring photographs. Until then, retain unknowns and do not fabricate scores.

Phase 2 must establish reviewed labels and separate locations/dates before
extracting training samples. Freeze an independent test set before tuning. Report
precision, recall, F1, IoU and area error only after that evaluation exists.

## Phase 1 entry

The existing foundation can be retained and verified; it need not be rebuilt.
See `PHASE1_FOUNDATION.md`. Its stored-data command measures imagery coverage,
rejects unsafe/invalid inputs and exports CSV/JSON; it is not a forest classifier.
The old 278 crop in its regression check remains pipeline-only. Compartment 279
research and reference verifiers are available for the newly saved formats.

```powershell
.venv\Scripts\python.exe scripts/check_local.py
.venv\Scripts\python.exe scripts/check_notebook.py
.venv\Scripts\python.exe scripts/verify_research_bundle.py data/study/compartment_279_v1/research_v2_20261008/forestguard_279_research.zip
.venv\Scripts\python.exe scripts/verify_liss4_crop.py data/reference/bhoonidhi_20261009/november_crop_v1/liss4_279_reference.zip
```

Latest handoff checks: `data/phase0/compartment_279_handoff_20261009/verification.json`.
Evidence details: `HIGH_RESOLUTION_REFERENCE_CHECK.md`,
`HISTORICAL_HEIGHT_REFERENCE.md`, `GEDI_REFERENCE_CHECK.md` and
`ICESAT2_REFERENCE_CHECK.md`. Back up ignored data separately from Git; no commit
or push was performed.
