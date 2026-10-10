# Compartment 279: real-image research change — 10 October 2026

## Working deliverable

The officer workspace now has **Estimated change** under Saved observations.
It shows the real before/after images, estimated transitions and six exports.
No officer upload is required. This is a research tree-cover proxy result, not
an independently validated forest inventory or confirmed deforestation report.

| Measure | Computed result |
| --- | ---: |
| Before image | 16 December 2024 |
| After image | 9 December 2025 |
| Common clear pixels | 12,362 / 13,099 |
| Common clear coverage | 94.3736% |
| Observable mapped area | 494.48 ha |
| Stable tree-cover proxy | 345.36 ha |
| Stable other-cover proxy | 134.36 ha |
| Suspected tree-cover proxy loss | 2.40 ha (60 pixels) |
| Suspected tree-cover proxy gain | 12.36 ha (309 pixels) |

These are mapped pixel-class extents, not summed tree-crown area. Unobserved
pixels contribute to neither loss nor gain. No synthetic inputs were used in
this comparison. The 0.5 ha stand criterion and height/land-use criteria are
not established by this proxy; its numbers must not be called forest area.

## Objective, inputs, processing and outputs

Use the user-confirmed compartment 279 polygon, two calibrated December crops
and our exported cloud-trained Random Forest. Verify original bundle/model
hashes and runtime versions before loading the trusted model. Verify grids,
boundary, feature order, chronological dates and seven-day calendar-season gap.
Classify only common clear pixels in 16-row batches on the existing 20 m grid.
Compare 0/1 tree-proxy predictions; preserve nodata as 255. Multiply each valid
transition's pixel count by 0.04 ha. Check the count and net-change identities.

Outputs are in `data/phase4/research_proxy_change_v1/`: before/after classes,
change classes, before/after/change SVG images, CSV, offline HTML, JSON report,
source observation assessment, common mask and checksums. The report preserves
source IDs, dates, attribution, licenses, source/model/dataset hashes and limits.
Selected bounded files are also in versioned `deployment_data/`; the training
model and original private/downloaded data remain excluded by `.gitignore`.

```powershell
# Choose a NEW output directory to reproduce; existing artifacts are preserved.
.\.venv\Scripts\python.exe scripts/predict_research_change.py data/phase4/research_proxy_change_reproduction
.\.venv\Scripts\python.exe scripts/check_research_change.py
.\.venv\Scripts\python.exe scripts/check_deployment_data.py
.\.venv\Scripts\python.exe scripts/check_hosted_app.py
```

## How to obtain evidence without forest-officer photographs

The current [forest-cover definition](FOREST_COVER_DEFINITION.md) is FAO-informed:
stands larger than 0.5 ha, canopy above 10%, trees above 5 m or supported capacity
to reach that height, excluding predominantly agricultural/urban uses.
[FAO describes the underlying land-use and stand criteria](https://fra-data.fao.org/definitions/fra/2020/en/tad).
Satellite spectral features can separate some vegetation patterns but cannot
alone establish all those criteria at 20 m. A confirmed boundary identifies
where to study; it does not assign a forest label to everything inside it.

Use the already acquired dated Sentinel crops to assess cloud coverage, seasonal
signals and repeatability. Use permitted LISS-4 imagery to inspect stand context
and agricultural patterns. Use available GEDI shots as dated, quality-screened
height/structure evidence at their footprints; sparse shots cannot establish
height everywhere. Historical canopy-height maps provide supporting context,
with their old dates and model uncertainty retained. Conflicting or unsupported
height, land-use and cover cases remain unknown.

Our existing experiment already trained our own Random Forest in Kaggle against
WorldCover 2021 weak labels, with separated northern December-2024 training and
southern December-2025 validation samples and a 200 m exclusion strip. These
labels are old and use a different class definition. This is enough to demonstrate
the training pipeline, but not enough to measure current forest accuracy.

[Dynamic World](https://developers.google.com/earth-engine/datasets/catalog/GOOGLE_DYNAMICWORLD_V1)
is another possible public, dated prediction source (CC BY 4.0). It may support
temporal cross-checks, but agreement between two classifiers is not ground truth.
No additional service, account, large dataset or local training dependency was
introduced for this deliverable. Retain each adopted source's reuse terms and
attribution. Restricted online imagery must not be scraped or redistributed.

## How independent evaluation can work

1. Select spatially separated patches and dates BEFORE looking at predictions.
   Freeze three groups: training, validation for tuning, and untouched testing.
   Apply spatial buffers that account for pixel/texture footprints; neighboring
   pixels in one stand must not be treated as independent sites.
2. Interpret dated higher-resolution evidence and height/land-use context without
   showing the reviewer the model prediction or weak-map label. A forest officer
   is not mandatory, but evidence-supported interpretation is necessary. Record
   source/date, geometry, reference class, reviewer, confidence and uncertainty.
3. Exclude unknown cases from binary scores and report their fraction. Seek
   another interpretation for ambiguous examples rather than inventing labels.
4. Evaluate only frozen test locations/dates never used in model selection.
   Report precision, recall, F1, IoU, confusion matrix, estimated area error and
   representative failures; account for spatial dependence and sampling design.
   Use additional later dates to review persistence of apparent transitions.

The current before-date northern pixels were used in training and after-date
southern pixels in model selection. Neither this change map nor the existing
validation set is an untouched independent test. No independent accuracy score
or confirmed loss/gain has been produced. If only automated internet maps are
available, report reference-map agreement and keep the research scope.

## Verification and deployment

Offline reproduction passed: all four transitions, common masks, 255 nodata,
area/net-change conservation, byte-identical artifacts, original preservation,
overwrite rejection and corrupt-output rejection. Hosted-mode API checks passed
89 requests with external networking blocked, including authentication, saved
images, change exports, sessions and invalid formats. The frontend build passed.
The selected deployment bundle is 94 files / 37,702,102 bytes (below 40 MiB).

The actual production landing page and user-completed login were checked. Its
officer view currently reports saved observations and the research map unavailable.
The new comparison is not on that deployment yet. `vercel.json` now explicitly
includes `deployment_data/**`, `frontend/dist/**` and the native library directory.
Build-time manifest verification rejects missing/corrupt selected datasets.

Push the updated source, `vercel.json` and **all `deployment_data/` files**, then
redeploy. If the Vercel UI has a Build Command override, disable it so the updated
command in `vercel.json` takes effect. Keep the existing officer environment values.
Check `/api/health`: `saved_observations_available` and `research_change_available`
should both be true. Then verify authenticated Overview, both satellite dates,
Research map, Estimated change's three layers/six exports, Reports and mobile
navigation. These live checks remain pending the new deployment.
