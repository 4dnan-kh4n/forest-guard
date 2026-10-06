# ForestGuard AI: meeting brief

Prepared 6 October 2026. Describe completed work separately from intended features.

## 45-second pitch

ForestGuard AI is a forest-monitoring project for Joga beat in Harda, Madhya
Pradesh. Its first release will classify forest cover from Sentinel-2 imagery
and compare suitable observations to flag suspected loss and gain. We use free
data and open-source tools, train our model in Kaggle, and export the model and
data for local operation. So far, the satellite preprocessing pipeline works
on real imagery, outputs pass integrity checks, and we have located official
compartment mapping. The next work is geographic validation, reviewed labels,
model training and evaluation, then a dashboard. Fire and future-loss risk are
later extensions, subject to sufficient data.

## Stack and status

| Layer | Technology | Status |
|---|---|---|
| Processing | Python, NumPy, Rasterio | Working cloud sample pipeline |
| Imagery | Sentinel-2 L2A, EarthSearch metadata/COGs | Real sample crops processed |
| Previews | Pillow, Matplotlib | Used in cloud inspection |
| Model | scikit-learn Random Forest, simple comparison baseline | Planned; no trained forest model |
| Model export | joblib and preprocessing/version metadata | Planned |
| Training runtime | Kaggle CPU; Colab fallback | Kaggle sample runs verified |
| API | Python FastAPI | Planned |
| Interface | React with JavaScript | Planned |
| Metadata | SQLite | Planned |
| Files | GeoTIFF, GeoJSON, KML reference, JSON reports | Existing sample/reference artifacts |
| Version control | Git, maintained .gitignore | Ignore rules present; user controls pushes |

Fresh implementation has no Gemma dependency. A language-model feature is
optional for explaining already computed evidence; it does not establish forest
classification accuracy. No mandatory hosted model service is planned.

## Likely questions

- **How does it work?** Crop satellite bands, apply reflectance calibration,
  mask invalid pixels, align the grid, classify pixels with the trained model,
  then compare classifications over common valid coverage.
- **Why Random Forest?** A practical first model for tabular spectral features;
  compare it with a simple baseline before adding deep learning.
- **Can green crops become forest?** Yes, that is a failure risk. Reviewed labels
  must distinguish crops, orchards, scrub and forest; NDVI alone is insufficient.
- **What is your accuracy?** No measured forest-model accuracy yet. Independent
  spatial/date test data will measure precision, recall, F1, IoU and area error.
- **What is 99.87%?** Usable imagery coverage in a pipeline-check crop, not accuracy.
- **Is the boundary verified?** Official Handia KML contains a feature tagged
  Joga/278/RF. Its candidate geometry still needs spatial/current-boundary review.
- **What about clouds?** Exclude uncertain observations; report observable area
  and calculate changes only where both dates are valid.
- **Can you detect illegal logging?** We flag suspected cover change for review;
  imagery alone does not establish cause, illegality or responsibility.
- **Will it work offline?** The intended application uses exported models and
  saved inputs locally. New imagery requires internet; offline application is not built yet.
- **What does it cost?** INR 0 new-service budget. Free notebook quotas can change;
  export artifacts after runs. Existing hardware/internet/storage are used.
- **What is completed?** Real-data preprocessing, exported checked crops,
  geographic-source discovery and candidate extraction. Labels/model/dashboard pending.
- **What is the submission scope?** Forest-cover mapping and suspected change
  detection first. Fire/loss forecasts are later capabilities, not completed results.

Do not claim 100% accuracy, live monitoring, a finished dashboard, or trained
prediction models. The project is currently a working feasibility/data prototype.
