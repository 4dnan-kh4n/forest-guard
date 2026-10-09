# Phase 3 training engineering — 9 October 2026

Training code and cloud notebooks are prepared. A synthetic engineering run
succeeded in Kaggle; no real forest model has been fitted and no independent
forest accuracy is measured.
Phase 2 reference evidence and frozen evaluation splits remain prerequisites.

## Objective and workflow

Inputs: verified compartment 279 research ZIP, exact selected boundary and a
separate evidence-supported frozen label GeoJSON. The current seven convenience
review records are rejected. Keep original uncertain records unchanged; do not
change independence flags or invent evidence to unlock training.

The workflow reuses the existing imagery verifier, geometry match and provenance
audit. It requires both classes in each split, reviewed independent references,
the existing 100 m cross-split separation and distinct acquisition dates. Under
this strict date policy, at least three accepted observation dates are needed;
our two current dates cannot supply train/validation/test. Seasonal differences
still require deliberate evaluation design. Declared metadata is not external
verification of reviewer correctness or scientific independence.

Forest reference records additionally need supported canopy above 10%, stand
area above 0.5 ha, nonempty height/height-potential evidence and forest-use evidence.
Unknowns cannot enter model splits. Every sampled footprint must lie within the
crop, have usable finite features on its observation date, and avoid duplicated
reference pixels. Extraction is bounded to 50,000 pixels, with the verified 20 m
feature order retained. The original extraction checks used no local training stack. The later optional
CPU inference environment is documented in [offline inference](OFFLINE_MODEL_INFERENCE.md);
no local model fitting is performed.

Train a majority-class baseline and a Random Forest with 100 trees, maximum depth
12, minimum leaf size 2, balanced class weights, two CPU workers and seed 42.
Choose the higher validation forest F1; baseline wins ties. Evaluate both fixed
candidates on test only after selection. Do not tune after looking at test results.
Report precision, recall, F1, IoU, confusion counts, sampled area error and up to
20 misclassified reference pixels identified by site/date/row/column. Sampled
area error is not a compartment-wide forest estimate. Pixel metrics are spatially
correlated; representative independent sites remain important.

## Reproduce engineering checks locally

```powershell
.\.venv\Scripts\python.exe scripts/build_training_notebook.py
.\.venv\Scripts\python.exe scripts/check_training.py
```

The check passes for known metric arithmetic, invalid vectors, rejection of the
actual unresolved labels before imagery loading, reference-criterion validation,
local training prevention, synthetic bounded sample extraction/overlap rejection,
notebook syntax and exact embedded-source parity. Synthetic fixtures test code;
they are not saved project reference labels or forest accuracy results. Cloud
fitting/serialization/export now pass the separate synthetic check below.
Record: `data/phase3/engineering_verification.json`.

## Verified synthetic cloud run

Private [Kaggle engineering check](https://www.kaggle.com/code/adnankh4n/forestguard-synthetic-training-engineering-check),
version 1 (356728295), completed successfully in 25.5 seconds with Accelerator
None and Internet off. This is an observed fixture runtime, not an estimate for
real training. It fitted the baseline and Random Forest, checked validation
selection, exported/reloaded models, reported deliberately introduced fixture
errors and rejected an incorrect feature count. Synthetic extraction was mocked;
this run does not validate real sampling or reference evidence.

Observed runtime: Python 3.13.15, NumPy 2.1.3, Rasterio 1.5.1 / GDAL 3.12.4,
scikit-learn 1.6.1 and joblib 1.6.0. No local training dependencies were installed.
The 11,303-byte archive is preserved at
`data/phase3/synthetic_check_v1/synthetic_training_check.zip` with the exact
uploaded source notebook, check report, screenshot and offline verification.
SHA-256: `88bf62fc504474cb67c95a5a5e7de0de7e2e88b2f0a30feb6324ed3d639a8176`.
Local verification checked all seven inner artifact hashes and rejected a
modified model file without unpickling models. Synthetic model/dataset IDs are
prefixed `synthetic-` and operational approval is false.

```powershell
.\.venv\Scripts\python.exe scripts/verify_training_smoke.py data/phase3/synthetic_check_v1/synthetic_training_check.zip
```

Reproduce fitting by importing `notebooks/09_synthetic_training_check.ipynb`
into a private Kaggle CPU notebook. It needs no uploaded imagery or Internet.
Download its output before session termination and back it up separately from
Git. Version 1's exact source is retained: afterward the notebook builder was
corrected to preserve the definition document's original line-ending bytes for
consistent dataset hashes. Current embedded-source parity passes locally; that
bootstrap byte-preservation change has not been rerun in cloud. Fitting logic is
unchanged.

## Run only after Phase 2 evidence is ready

Import `notebooks/08_forest_training.ipynb` into a private Kaggle CPU notebook
(Accelerator None), or a hosted Colab runtime. Attach only preserved, verified
inputs. Set BUNDLE, BOUNDARY and LABELS to their real uploaded paths. The source
notebook embeds no private geometry or populated labels. It contains no automatic
package installation; use available NumPy/Rasterio/scikit-learn/joblib and retain
actual versions. No network imagery or online model endpoint is called by training.

Download `forestguard_model_run1.zip` before session termination. A successful
future run will export both fitted candidates, evaluation JSON, selected model
manifest, unchanged labels, feature code, cover definition and file checksums.
Manifest includes feature/band order, calibration/processing, class mapping,
model parameters, dataset/model identifiers and dependency versions. Saved-model
prediction equivalence is asserted after joblib roundtrip. Operational approval
remains false until performance, errors and local inference are reviewed.

Free hosted compute has changing quotas. Keep exported inputs/models separately
from Git; `.gitignore` already covers data, model ZIPs and joblib files. Load only
trusted project joblib artifacts, with compatible runtime versions. Local saved-model inference now passes the synthetic fixture check; application
integration and real-model validation remain later work. See
[offline inference](OFFLINE_MODEL_INFERENCE.md).

## Licenses and next step

Checked the official [scikit-learn license](https://raw.githubusercontent.com/scikit-learn/scikit-learn/main/COPYING)
and [joblib license](https://raw.githubusercontent.com/joblib/joblib/main/LICENSE.txt):
both use BSD 3-Clause terms requiring retained notices/disclaimers when
redistributing their software. Training uses hosted installed packages; retain
the licenses from the exact installed versions if distributing a runtime.
Estimator parameters follow the [official Random Forest documentation](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html).
This introduces no paid service or local package installation.

Next required step is credible reviewed references and frozen representative
splits, followed by an actual cloud run and inspection of its exported results.
Preparing code is not completing Phase 3 model training.
