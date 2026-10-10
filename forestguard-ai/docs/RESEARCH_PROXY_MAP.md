# Offline research proxy map — 10 October 2026

Our stored Random Forest now produces a bounded, offline map for the verified
9 December 2025 observation of compartment 279. This is a research-only tree-cover
proxy trained against WorldCover 2021, not an approved forest classifier. The
production forest loader and application approval gates remain unchanged.

## Deliverables

Open `data/phase3/research_proxy_map_v1/map.html` directly offline. It embeds the saved
image and predicted overlay; it needs no external tiles, service, login or Internet.
Green means tree-cover proxy and orange means other-cover proxy. Outside-study and
unobserved pixels get no class. These colours do not establish legal/current forest.

The same folder contains georeferenced `proxy_classes.tif` (0/1, nodata 255) and
`tree_vote_share.tif` (float32, nodata -1), a source/date/model report, SVG preview,
file checksums and the verification report. Mean decision-tree class probability
is uncalibrated; it is not canopy percentage, accuracy or a reliable confidence level.
`map_figure.png` was rendered from the exact saved SVG with the already bundled
sharp renderer and visually inspected. Its retained recipe is optional for inference;
it introduced no project dependency. This is a scientific figure, not browser QA.

Measured output: 12,362 observable pixels / 13,099 study-mask pixels (94.37%),
8,943 predicted tree-proxy pixels and 3,419 other-proxy pixels. No forest hectares,
loss/gain, fire inference or new accuracy claim is produced. The raster is on the
source 123 by 172, 20 m EPSG:32643 grid. It is not an independent model evaluation:
the south validation region was already used to select the research model.

## Reproduce and verify

```powershell
.venv\Scripts\python.exe scripts/predict_research_proxy.py data/phase3/research_proxy_map_new
.venv\Scripts\python.exe scripts/check_research_proxy_map.py
```

This deliberately narrow research adapter accepts our exact checksum-bound model,
dataset and saved observation only. It verifies artifact identity, source integrity,
dependency versions, feature order, valid features and estimator/classes before
predicting in bounded 16-row batches. Calibration is not reapplied. No fitting or
training dependency installation is performed. Existing output folders are refused;
completed outputs publish from a temporary folder with checksums.

The assert-based check passes with networking blocked: matching output grids,
12,362 observed pixels, class/vote nodata and range, checksum integrity, unchanged
source and review files, exact validation matrix `[[1049,157],[63,4798]]`, rejected
overwrites and continued production-loader rejection. NumPy 2.1.3, scikit-learn
1.6.1 and joblib 1.6.0 match the cloud export; the existing Rasterio runtime is used.

The saved satellite metadata retains its Copernicus attribution and license.
Existing dependency/license decisions apply; no new dependency or paid service was
adopted. The generated map stays Git-ignored, and the delivery backup recipe includes
it. Source scripts and these instructions remain trackable. A separate preservation
receipt records the matching backup; E: shares the laptop's physical disk.

## Limits and next step

Independent forest references, height/canopy/land-use evidence and a frozen reviewed
test set remain missing. The earlier shrub/crop errors remain relevant, even where
vote values are high. This map cannot authorize an alert, inspection accusation or
forest-change conclusion. HTML browser rendering was not verified in this milestone.

Next, the local application can display this output in a clearly separated research
view with the same scope/approval labels. Real forest/change analysis remains gated
until the scientific acceptance criteria in the phase handoff are met.
