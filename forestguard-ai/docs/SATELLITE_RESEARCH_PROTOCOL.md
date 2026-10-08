# Compartment 279 satellite research — 8 October 2026

## Current decision

The user confirms the supplied compartment 279 boundary is correct. Use exactly
`compartment-279-user-kml-v1`; do not replace it with the old 278 dataset or the
different working-plan 279 shape. User confirmation is recorded separately from
independent positional measurement and current administrative verification.

Original field photography is prohibited. No field-photo collection is planned.
Earlier officer forms remain historical preparation, not a current requirement.
We will research permitted dated remote references and keep their interpretation
uncertainty visible. A no-field-photo project is feasible as a research workflow;
independent current forest accuracy remains a separate question to establish.

## First experiment: seasonal data suitability

Version 2 preparation: rank up to 12 small native-20 m SCL windows per season by
usable pixel centres inside the actual polygon, then attempt at most three complete
band crops in that order. The original Version 1 policy below attempted just two
scenes ranked by whole-tile cloud percentage; its results remain preserved.
The new export includes the original four-band/SCL crop ZIP and a pre-texture
quality mask for each accepted scene, allowing offline reconstruction of all
features and the texture neighborhood. It also attempts one bounded WorldCover
2021 weak reference crop; reference failure is recorded separately from imagery
screening. Actual Version 2 results are recorded after export verification.

Inputs: the selected polygon and public Sentinel-2 Collection 1 Level-2A products.
Candidate acquisition windows are February–April, July–September and October–December
2025. These are search windows, not fabricated acquisition dates. Search at most
30 catalogue items and attempt two scenes per season. Cloud percentage ranks
candidates; measured valid coverage inside the polygon decides acceptance.

Processing: reuse the existing bounded calibrated four-band crop pipeline, then
add B05, B06, B07, B8A, B11 and B12 at their native 20 m grid. Average B02/B03/B04/B08
from 10 m to that grid. Calibration must agree between product metadata and
band headers. SCL 4/5/6 is only a quality screen, not a land-cover label. Require
valid contributing bands, common saved grids and a complete 3×3 quality neighborhood.
Initial screening target: at least 90% feature-valid pixel centres inside the
selected polygon per season. A failed season stays missing.

Features: ten calibrated bands, NDVI, EVI, NDRE using B8A/B05, NDMI using B8A/B11,
and 3×3 NDVI standard deviation. The texture footprint is 60 m. It cannot resolve
individual trees or prove plantation rows. Seasonal differences can reflect leaf
loss, crops, moisture, clouds or disturbance; they are not automatically forest loss.
The [official band documentation](https://docs.sentinel-hub.com/api/latest/data/sentinel-2-l1c/)
lists native band resolutions; resampling does not create additional detail.

Outputs: seasonal reflectance and feature GeoTIFFs, study and usable masks,
transparent previews, source metadata/calibration, acquisition dates, grid settings,
coverage counts, failures, runtime versions, checksums and a verified ZIP. These
are model inputs, not predictions or reviewed labels. Seasons are aligned for
feature exploration; change detection still needs suitable same-season date pairs.

## Reproduce without local training

Run locally only to generate/check source:

```powershell
.venv\Scripts\python.exe scripts/build_research_notebook.py
.venv\Scripts\python.exe scripts/check_notebook.py
.venv\Scripts\python.exe scripts/check_research_features.py
```

The public notebook `notebooks/04_multiseason_research.ipynb` contains no boundary
or outputs. The private execution copy is under ignored
`data/study/compartment_279_v1/04_multiseason_research.private.ipynb`.
Import the private copy into a separate private Kaggle notebook. Keep Internet
On and Accelerator None. Save & Run All exports durable version outputs. Download
the resulting ZIP, verify its CRC/SHA-256 manifest, and preserve it under ignored
`data/study/compartment_279_v1/`. Do not stop at a successful notebook status:
inspect `research_report.json` for accepted scenes and failed coverage checks.

No package installation is required in the notebook. It checks for at least
250 MiB hosted free storage and bounds each additional raster window to 256×256.
The code refuses acquisition on Windows. Kaggle quotas and runtime availability
are finite; exported files are necessary to survive session termination.

Offline export verification:

```powershell
.venv\Scripts\python.exe scripts/verify_research_bundle.py data/study/compartment_279_v1/research_v1_20261008/forestguard_279_research.zip
```

The compact ZIP preserves accepted 20 m inputs/features, masks, provenance and
candidate catalogues. The original four-band/scene-quality crops for all attempts
also exist in the saved private Kaggle version's `forestguard_phase0` output tree;
they are not included in this compact ZIP. Export those original quality rasters
before freezing a training dataset or changing preprocessing rules. A source path
inside the hosted report is not a local filesystem path.

## Reference research and class policy

Start with the binary operational cover definition in `FOREST_COVER_DEFINITION.md`.
Natural forest and forestry plantations may be tagged separately only when dated
evidence supports origin/use. Orchard/crop and scrub are useful challenge cases;
regular spacing and high NDVI alone do not determine them. At 20 m, unresolved
subclasses remain unknown. Expanding to four classes requires reviewable examples
and independent evaluation of each class, not just adding input bands.

Candidate reference sources, not yet acquired or adopted for 279:

| Source | Appropriate role | Limit |
|---|---|---|
| [ESA WorldCover 2020/2021](https://esa-worldcover.org/en/data-access) | Weak starting map; attribution under CC BY 4.0 | Old labels; tree cover is not legal forest or verified current forest use. |
| [Dynamic World](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1) | Weak predictions/probabilities and temporal comparison | Model predictions, not independent truth; trees include plantations; verify access/reuse conditions before adoption. |
| [Published global 10 m reference dataset](https://zenodo.org/records/14871660) | Investigate original interpreted reference sites; CC BY 4.0 verified on record page | Reference year 2015; single CSV is 2.0 GB. Not downloaded. Local coverage unverified; its trees class does not establish forest use/origin. Nearby subpixels of one site are not independent sites. |
| Permitted dated higher-resolution imagery and documentary records | Human interpretation with traceable evidence | Need adequate date/location detail and checked reuse permission; do not scrape or redistribute restricted imagery. |

Sentinel processing uses the [Copernicus Sentinel data license](https://cds.climate.copernicus.eu/licences/ec-sentinel)
and preserves acquisition-year attribution. Do not silently adopt a new dataset
until its actual license, size and local coverage are checked.

Each reviewed patch must use `config/label_review_template.geojson`, recording
reference source/date, geometry, reviewer, confidence and unresolved ambiguity.
Separate independent sites and later evaluation dates before sample extraction.
Never randomly split neighboring pixels or call agreement with a weak map field
accuracy. A satellite-interpreted test is reported as such. If all references derive
from the same satellite/model inputs, evaluation measures agreement/consistency,
not independently established forest truth.

## Verification status

Numerical index/texture checks use explicitly synthetic tiny arrays. They check
formulas and invalid-neighborhood behavior, not class accuracy. Notebook syntax,
embedded-source consistency, empty public outputs and cloud-only guard checks pass.
Cloud Version 1 ran successfully in the private notebook
[ForestGuard 279 Satellite Research](https://www.kaggle.com/code/adnankh4n/forestguard-279-satellite-research),
script version 356345375. Runtime reported by Kaggle: 3m 10s. Its scientific status
is `PARTIAL_DATA_SCREENING`, not complete seasonal coverage.

| Window | Observed feature coverage inside polygon | Result |
|---|---:|---|
| Dry: 17 February / 12 February 2025 | 86.85% / 83.74% | Both below the 90% initial screening target |
| Wet: 6 August / 10 September 2025 | 48.94% / 0.00% | Both below target |
| Post-monsoon: 13 December 2025 | 94.21% | Accepted |

The accepted grid is 123×172 at 20 m, EPSG:32643. The selected polygon contains
13,099 pixel centres, of which 12,340 have valid research features. This is
observable feature coverage, not forest accuracy or surveyed forest area.
The preview was inspected: vegetation, water and field-like patterns are present;
their natural-forest/plantation/orchard identities are not established.

Local artifacts: `data/study/compartment_279_v1/research_v1_20261008/`.
ZIP: 1,541,037 bytes, SHA-256
`406699cb9059c0625ccbeda80f9e41dd10cd5b36a8d9d0bad58ad4b4e73b6f95`.
All 12 member hashes, CRC, saved grids, boundary mask, valid counts and index
formulas pass offline verification. A deliberately changed boundary hash was
rejected despite valid ZIP CRC. No new local dependencies were installed.
Observed local resources during preservation: about 0.70 GiB RAM available and
44,396,847,104 bytes free on C:; measurements change over time.

Next: inspect additional bounded candidates using local polygon coverage before
selecting seasonal observations; investigate permitted reference coverage and
review small traceable patches. Two failures per season do not prove that all
imagery in that season is unusable. Do not lower the threshold simply to fill
missing seasons or label the accepted crop as verified forest.
Permitted independent reference coverage and trained classifier evaluation remain
open; reviewed labels = 0, trained models = 0, independent model accuracy unmeasured.

## Version 2: local coverage selection and weak reference

The updated notebook ran on hosted CPU with Internet enabled and Accelerator None.
Kaggle initially stalled at committing; reloading the preserved draft and retrying
created Version 2. Execution completed successfully, reported runtime 4m 39s,
script version 356354114. Its scientific screening status is still partial.

Screened 12 native-20 m SCL crops in each of three windows (36 total), ranked by
usable centres inside the selected polygon. Only bounded windows were read, not
whole scenes. Processed at most three complete candidates per season. Acceptance
uses feature-valid coverage, which additionally excludes unusable reflectance/index
neighborhoods; SCL coverage alone cannot guarantee usable features.

| Accepted observation | Scene | Feature-valid centres | Coverage |
|---|---|---:|---:|
| 3 April 2025 | S2B_T43QFE_20250403T053649_L2A | 12,381 / 13,099 | 94.52% |
| 9 December 2025 | S2B_T43QFE_20251209T053610_L2A | 12,362 / 13,099 | 94.37% |
| Common coverage | Both masks intersected | 12,338 / 13,099 | 94.19% |

Maximum local SCL coverage among the twelve screened monsoon candidates: 55.95%.
The three processed candidates had feature coverage of 48.94%, 30.91% and 13.25%.
They were rejected and remain missing, without invented values or interpolation.
This bounded screen does not establish that every monsoon acquisition is unusable.
The accepted dates are different seasons; their colour/index differences must not
be counted as deforestation. Same-season observations from separate years are
still needed for the change-detection milestone.

The free public WorldCover 2021 v200 reference crop is available: tile N21E075,
262×396 native geographic-grid cells, EPSG:4326, resolution 1/12000 degree.
Only the small window was read from its COG; the source tile is 102,720,459 bytes
and was not downloaded in full. Cropped files are checksummed; the source ETag is
stored as metadata, not treated as a whole-file SHA-256 checksum. Original class
codes and annual 2021 reference date are preserved, with required CC BY 4.0
attribution and citation. Nearest-neighbor alignment to accepted 20 m grids was
independently reproduced offline. No predicted tree class is converted to a
verified current forest label. See the
[ESA access/license documentation](https://esa-worldcover.org/en/data-access) and
[class definitions](https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/docs/WorldCover_PUM_V2.0.pdf).

Native historical hints inside the polygon include tree cover, shrubland, grassland,
cropland, sparse/bare vegetation and water. These are model predictions describing
2021, not current surveyed forest area. Tree cover includes some plantations and
agricultural trees, so its label semantics differ from our operational forest target.

Stored export: `data/study/compartment_279_v1/research_v2_20261008/`.
ZIP size: 4,937,030 bytes; SHA-256:
`bdc1f3b07c91446bfd6bcf504f4fbed516ec104509e4993b5e0504073558fbfb`.
All 27 hashes, archive CRC, source-crop provenance, shared grids, polygon masks,
quality masks, counts, indices, texture reconstruction and historical-map alignment
pass local verification. Original four-band/SCL crop ZIPs are now included for
each accepted scene; the old Version 1 compact-export limitation is resolved here.
Resource observation: 1,336,520,704 bytes RAM available and 44,050,849,792 bytes
free on C: during preparation. No local training or new package installation.

## Review pack and next evidence gate

The new review preparation selects only 120 m footprints with common usable
coverage and homogeneous historical map hints. Convenience selection seeks up to
three cases per mapped class, with at least 240 m between centres; this is not a
representative test design or a claim of statistical independence. Seven cases
were found: three tree-cover hints, one cropland hint and three water hints.
No supported homogeneous scrub cases were manufactured to balance the pack.

Artifacts under ignored `data/labels/compartment_279_v2_review_pack/`:
- `review_cases.geojson` reuses the existing label template. All classes are
  `unknown`, review status `unreviewed`, reviewer/confidence unset, split `unassigned`.
- `review.html` embeds both real previews and numbered footprints. Open it directly
  in a browser; it requires no internet, API, basemap or installed plotting library.
- `review_preparation.json` preserves the source bundle and selection limits.

Reproduce into a new directory; existing outputs are protected:

```powershell
.venv\Scripts\python.exe scripts/verify_research_bundle.py data/study/compartment_279_v1/research_v2_20261008/forestguard_279_research.zip
.venv\Scripts\python.exe scripts/check_research_review.py data/study/compartment_279_v1/research_v2_20261008/forestguard_279_research.zip
.venv\Scripts\python.exe scripts/prepare_research_review.py data/study/compartment_279_v1/research_v2_20261008/forestguard_279_research.zip data/labels/compartment_279_new_review
```

Source/case checks pass, including preservation of unknown labels and rejection of
existing-output overwrite. The self-contained page was rendered and visually
inspected through a temporary loopback server: dates, masks and markers display
correctly. April looks much browner than December, demonstrating why seasonal
appearance alone cannot establish cover loss. This observation does not determine
natural forest versus plantation, orchard or scrub.

Next, review the case evidence and identify permitted dated references that can
support forest use/origin and height/canopy criteria. If only weak satellite hints
are available, retain those limits and evaluate an explicitly exploratory proxy
separately from independently supported forest accuracy. Freeze spatial and date
evaluation groups before extracting training pixels. Reviewed labels remain zero,
evaluation splits remain unfrozen and the forest classifier remains untrained.

On 8 October 2026, the [NASA GEDI check](GEDI_REFERENCE_CHECK.md) screened the
three available intersecting 2025 granules through actual small spatial subsets.
March produced 38 centres inside the polygon, all with nonzero degradation;
May/June returned `nodata`. No accepted height references or forest labels were
created. The pending-case audit now accepts intentionally unset review fields
while rejecting premature training transitions. Actual masked feature summaries
are reproduced by `scripts/inspect_review_features.py`; the corrected report is
`data/labels/compartment_279_v2_review_pack/patch_feature_inspection_v2.json`.
The initial one-off summary is retained for traceability. Review medians are
interpretation aids and do not determine forest use, origin or height.
