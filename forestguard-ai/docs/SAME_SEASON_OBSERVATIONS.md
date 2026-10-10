# December observation pair — 10 October 2026

The calendar-matched data check passed for the user-confirmed compartment 279
research polygon. This is neither the full Joga beat nor an evaluated forest model.
The earlier April/December weak-reference experiment failed to discriminate classes;
this pair reduces its seasonal mismatch without resolving the reference-label gap.

| Observation | Selected scene | Usable study pixels |
| --- | --- | --- |
| 16 December 2024 | S2A_T43QFE_20241216T053216_L2A | 12,405 / 13,099 (94.70%) |
| 9 December 2025 | S2B_T43QFE_20251209T053610_L2A | 12,362 / 13,099 (94.37%) |

Both observations use the same 123 by 172 pixel, 20 m EPSG:32643 grid.
Common clear coverage is 12,362 pixels (94.37%). Their calendar dates differ by
seven days. Common-pixel median NDVI is 0.5984 and 0.6062 respectively: these are
vegetation signals, not measured forest area or loss/gain. Similar calendar dates
do not establish comparable weather, vegetation cycles or survey-level alignment.

## Acquisition and verification

The private [December screening notebook](https://www.kaggle.com/code/adnankh4n/forestguard-december-2024-observation-screening)
completed Kaggle version 356849804 in 61.9 seconds, CPU / Accelerator None,
Internet enabled for public satellite crop reads. The draft runtime was switched
off afterward. Four small scene-classification windows were screened; the selected
16 December scene had 100% preliminary SCL coverage. The final all-band and
neighborhood mask retained 94.70%. No full scenes, labels or models were downloaded
or fitted. Hosted free compute remains quota-dependent.

The retained new crop ZIP is 2,452,861 bytes, SHA-256
`c072df3555fa446f8e8e7af5557b1993abb22f8088b6f4bc9298157adb9adc5b`.
All 12 source file hashes, calibration, masks, feature counts and grid checks passed.
The 2025 source retains SHA-256
`bdc1f3b07c91446bfd6bcf504f4fbed516ec104509e4993b5e0504073558fbfb`
and 27 verified files. Reflectance scale 0.0001 and offset -0.1 were applied once
using the original product metadata; quality masks are not class labels.

The existing dataset registry and review records remain unchanged. April 2025,
December 2024 and December 2025 observations are available in separate preserved
bundles; this does not make the forest dataset training-ready. Independent reviewed
references and representative frozen evaluation splits are still absent.

## Reproduce with stored data

From the project directory, using the existing lightweight environment:

```powershell
.venv\Scripts\python.exe scripts/check_observation_windows.py
.venv\Scripts\python.exe scripts/check_observation_pair.py
.venv\Scripts\python.exe scripts/assess_observation_pair.py data/study/compartment_279_v1/december_2024_v1/forestguard_279_research.zip data/study/compartment_279_v1/research_v2_20261008/forestguard_279_research.zip data/phase2/december_pair_assessment_new
```

The assessment refuses existing output directories. It verifies source hashes,
boundary/version, CRS, transform, shape, band/feature order, chronological dates,
calendar gap and common finite pixels before publishing JSON, a common-valid
GeoTIFF and an offline HTML comparison. Checks also reject reversed/same dates,
overwrite and invalid acquisition windows; original sources remain unchanged.

Current deliverables are in `data/phase2/december_pair_assessment_v3/`.
Versions v1/v2 are preserved intermediates. Open `comparison.html` directly offline;
both saved images are embedded. Browser verification confirmed both images loaded
and displayed the correct dates and 94.37% coverage; its screenshot is retained.
Previews use each observation's original mask; statistics use their intersection.

`scripts/build_same_season_notebook.py` regenerates the public notebook
`notebooks/11_same_season_observation.ipynb` and the private study-specific notebook.
Acquisition runs in the hosted notebook, not on the laptop. Sentinel source IDs,
license URL and modified-Copernicus attribution remain in the source metadata and
assessment. Existing reviewed license records apply; no new provider/dependency
was adopted. Data, private notebooks and screenshots remain Git-ignored; source,
public notebook and these instructions are trackable. Preserve data separately.

## Next step and limits

Run a clearly exploratory weak-reference experiment using the December pair,
with spatial separation before sample extraction. Compare both class errors and
the simple baseline. Even a better result would measure agreement with an old
land-cover map, not independent current forest accuracy. Do not promote its model
to forest alerts. A qualified reference reviewer remains unavailable.

Weather/phenology equivalence, surveyed boundary accuracy and independent forest
labels were not verified. No forest-cover change or fire conclusion was produced.
The backup recipe includes the new observation and v3 assessment; previous release
backups remain immutable. A separate preservation receipt records this milestone's
file hashes and matching E: copy; E: shares C:'s physical disk.
