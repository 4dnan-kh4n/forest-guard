# Offline model inference — 9 October 2026

The bounded prediction command is implemented and tested on the preserved
synthetic Kaggle model. This is a working engineering deliverable, not a forest
map or measured forest accuracy. Real imagery and reference labels are unchanged.

## What happens

Inputs are a trusted model ZIP, calibrated feature GeoTIFF with exact ordered
band descriptions, and its aligned binary usable mask. An external SHA-256 pins
the trusted archive before any model is loaded; internal checksums verify its
members. Checksums are not proof of source authenticity. Load only our known
project exports: [scikit-learn documents that joblib loading can execute code](https://scikit-learn.org/stable/model_persistence.html).
There is no arbitrary model-upload API.

The command checks feature order, classes, dependency versions, scope and grids.
It reads 16 rows per batch, uses one CPU worker, predicts usable finite pixels
and leaves invalid pixels as 255 (no data). Initial limits are 30 MiB per input,
250,000 crop pixels, width 2,048, at most 32 features and the existing 20 m
EPSG:32643 grid. It does not rescale already calibrated features. Synthetic models
require an explicitly synthetic input; real models require operational approval.
Other formats need a reviewed adapter. No canopy hectares are inferred here.

Outputs are `classes.tif` and `prediction_report.json`, including scope, model
and dataset versions, feature order, hashes, counts and actual runtime versions.
Existing output folders are rejected. A complete folder is published only after
all windows pass; validation failures leave no partial result folder.

## Reproduce

Optional CPU inference packages are pinned separately in
`requirements-inference.txt`; the basic inspection environment remains separately
defined. Five wheels from PyPI were downloaded (52,732,058 bytes) and installed
into the project virtual environment. No local fitting or GPU stack is used.
Before acquisition, available RAM was 1,157 MiB of 7,979 MiB and free disk was
44,861,607,936 bytes. Resources change; recheck before larger work.

```powershell
.\.venv\Scripts\python.exe -m pip install --no-index --find-links data/tooling/wheels/windows-cp311 --find-links data/phase3/inference_wheels -r requirements-inference.txt
.\.venv\Scripts\python.exe scripts/check_inference.py
.\.venv\Scripts\python.exe scripts/predict_crop.py --model data/phase3/inference_fixture_v1/model.zip --trusted-model-sha256 22ffa1df2945e55c4aab127ca7ac4d10d530d209d1b106b35433ba693107706a --features data/phase3/inference_fixture_v1/features.tif --mask data/phase3/inference_fixture_v1/mask.tif --output data/phase3/my_synthetic_prediction
```

Choose a fresh output folder. The verification command preserves a reproducible
synthetic fixture and first output in `data/phase3/inference_fixture_v1/`.
Its coordinates and feature values are fictional. No actual forest label is
created. Check result: `data/phase3/inference_verification.json`. A separate completed CLI
run is preserved at `data/phase3/offline_prediction_run1/`.

The check reconstructs the preserved cloud test predictions from its references
and complete error list, then compares all usable local predictions exactly.
It covers 256 synthetic pixels in multiple windows, three masked pixels, offline
execution with Python sockets disabled, wrong feature order, shifted mask grid,
synthetic/real mismatch, nonbinary mask, nonfinite usable features, ignored invalid
masked features, overwrite prevention, missing approval and trusted-hash failure.
The exported majority-class baseline also passes local inference. It never calls
model fitting. The model trained in Python 3.13 works for this
fixture in the local Python 3.11.5 environment; this is not a general compatibility
guarantee. NumPy 2.1.3, scikit-learn 1.6.1 and joblib 1.6.0 are checked exactly;
other runtime versions are recorded. Reverify each future model export locally.

## Licenses, storage and next step

The official downloaded wheels retain their bundled notices. scikit-learn,
joblib, SciPy, threadpoolctl and cloudpickle use BSD terms; SciPy also bundles
third-party notices, and cloudpickle embeds its copyright/license in its source
module. Preserve all notices when redistributing a runtime. Download sizes,
SHA-256 values and notice paths are recorded in
`data/phase3/inference_wheels/wheel_manifest.json`.

Data, wheels, models and predictions remain ignored by Git. Back them up
separately. Code, requirements and these instructions are trackable; no Git push
was made. This command is not yet connected to the dashboard. Next scientific
step remains credible reviewed forest/non-forest references and frozen independent
splits, followed by real cloud training and evaluation before operational approval.

The prediction raster now includes model/definition/class/approval metadata and
preserves study/date/season-review tags when present in the input. It does not
invent missing dates. [Change comparison requirements](PHASE4_CHANGE_DETECTION.md).
