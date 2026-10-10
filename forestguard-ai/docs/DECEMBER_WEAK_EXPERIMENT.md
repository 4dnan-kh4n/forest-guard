# December weak-reference experiment — prepared 10 October 2026

Status: user-supplied cloud export verified against the December dataset; both
models' validation predictions and reported metrics reproduced offline. The
exploratory run is complete; operational forest use remains unapproved.
This compares agreement with the historical WorldCover tree-cover map, not current
forest accuracy. The prior April/December experiment and its failed transfer result
remain preserved. No production model, reviewed label or scientific gate changed.

The December observations passed the [calendar-matched data assessment](SAME_SEASON_OBSERVATIONS.md).
The same preparation helper now accepts an optional earlier verified December
bundle; its original April/December behavior remains available and regression-tested.
The historical 2021 weak map from the saved 2025 bundle is reused only after the
study geometry/version, grid and feature order agree. It was not observed in 2024
or 2025 and remains a model-generated reference with agricultural-tree limitations.

| Group | Observation | Region | Other-cover proxy | Tree-cover proxy | Total |
| --- | --- | --- | --- | --- | --- |
| Training | 16 December 2024 | North | 2,109 | 2,830 | 4,939 |
| Validation | 9 December 2025 | South | 1,206 | 4,861 | 6,067 |

Regions are chosen before extracting samples, excluding a ten-row/200 m strip.
Each group uses its own verified usable mask; train features are checked directly
against the actual 2024 crop and both target arrays against the historical map.
The reference is three/four nominal calendar years older than the observations.
Class balance differs between the two regions; report confusion matrices alongside
F1/IoU and do not mistake a constant majority prediction for a useful classifier.
Neither group is an independent forest test set.

Dataset: `data/phase2/weak_december_experiment_v1/weak_experiment.zip`, 518,195 bytes.
SHA-256: `b4d93e7db778b51addcea7e9c574e1f593b56c48786778a1629cf3921cf7f8ec`.
The manifest retains the source hashes, dates, feature/band order, reference license,
attribution, age and false approval/independence flags. The 15 calibrated features
are reused without additional scaling. No extra dependencies or downloads are needed.

## Minimal cloud handoff

Browser automation for the existing Kaggle session was unavailable this turn.
Only the desktop application was exposed by the current computer-use inventory;
no cloud execution, runtime or model scores are claimed.

1. In Kaggle, create a private notebook named `ForestGuard December weak proxy`.
   Choose File → Import Notebook and upload
   `data/phase3/weak_december_run_v1/private_run.ipynb` from this workspace.
2. Keep visibility **Private**, Accelerator **None**, Internet **Off**. The verified
   small dataset is already embedded; no separate dataset attachment or installation
   is required. Use Save Version → Save & Run All.
3. After success, download `forestguard_weak_proxy_run1.zip` from Output and retain
   the cloud version/runtime. Stop the draft session afterward. Keep this run separate
   from the earlier exploratory model; do not overwrite its files.

The existing hosted-only trainer fits the majority baseline and 100-tree Random
Forest, exports both, checks their reload predictions and saves the measured
historical-reference agreement metrics. After download, verify checksums/scope with
`scripts/verify_weak_export.py`, then compare saved predictions offline. Do not
publish scores or integrate an artifact into forest alerts before those checks.
Free hosted sessions have quotas; download completed artifacts before termination.

The model verifier can bind an export to the expected dataset. This matters because
both cloud experiments export the same filename. Before any joblib load, use the
downloaded export's separately retained SHA-256 and the December dataset checksum:

```powershell
.venv\Scripts\python.exe scripts/verify_weak_export.py PATH_TO_NEW_EXPORT.zip --sha256 CLOUD_EXPORT_SHA256 --dataset data/phase2/weak_december_experiment_v1/weak_experiment.zip --dataset-sha256 b4d93e7db778b51addcea7e9c574e1f593b56c48786778a1629cf3921cf7f8ec
.venv\Scripts\python.exe scripts/check_weak_export_identity.py
```

The identity check passes with the actual preserved earlier export and its original
dataset, rejects that same export for the December dataset, and rejects a wrong
dataset checksum or incomplete binding. It performs no network access, unpickling
or training. A local checksum alone does not establish where an unknown file came
from: only load the artifact downloaded from our own reviewed private cloud run.
At the initial continuation check, no December export was present and no accessible
Kaggle browser was exposed. The user subsequently supplied the completed export;
the results and preservation record below supersede that pending status.

## Measured result from the supplied cloud export

The user supplied `forestguard_weak_proxy_run1 (1).zip` from the reported
[Kaggle run](https://www.kaggle.com/code/adnankh4n/notebook0200720366/output).
Its 631,542-byte export has SHA-256
`8bf0858faaee969b35e003c466de19ab1767a96c5c8ed9098cb8010f13d3a6b8`.
Four artifact hashes, model identity, dataset identity, false approval flags and
selection rule passed verification before loading these user-provided project
artifacts. Cloud version ID and elapsed runtime were not accessible and remain null;
the user-reported run and downloaded artifacts do not establish those measurements.
The export reports Python 3.13.15, NumPy 2.1.3, scikit-learn 1.6.1 and joblib 1.6.0.

| Model | Precision | Recall | F1 | IoU |
| --- | --- | --- | --- | --- |
| Constant majority baseline | 0.801220 | 1.000000 | 0.889641 | 0.801220 |
| Random Forest | 0.968315 | 0.987040 | 0.977588 | 0.956158 |

These are historical tree-cover-reference agreement metrics, not independent
forest accuracy. Random Forest was selected by the existing F1 rule. Its matrix
is `[[1049,157],[63,4798]]`, rows reference other/tree and columns predicted
other/tree: 220 disagreements among 6,067 held-out validation pixels. The baseline
predicts tree for every pixel and misses all 1,206 other-cover targets.

The previous April/December Random Forest F1 was 0.013404. This large improvement
supports continuing with calendar-matched imagery, but does not isolate a causal
season effect: dates, feature distributions and 24 training samples also changed.
Train and validation remain spatially separated within a single small compartment.
Both use the same historical teacher, with no independently reviewed test set.

Reference-class breakdown exposes errors hidden by the aggregate score:

| WorldCover reference class | Validation pixels | Disagreements |
| --- | --- | --- |
| Tree cover (10) | 4,861 | 63 |
| Shrubland (20) | 78 | 69 |
| Grassland (30) | 142 | 19 |
| Cropland (40) | 244 | 69 |
| Bare/sparse vegetation (60) | 2 | 0 |
| Permanent water (80) | 740 | 0 |

The 88.46% shrub and 28.28% crop disagreement rates matter for our forest definition.
Historical map errors and actual changes may also cause disagreements. Even the
tree-cover class can include plantations and agricultural trees. No pixel here has
been independently established as current natural forest.

Saved artifacts, evaluation, manifest, receipt, class breakdown and offline check
are under `data/phase3/weak_december_run_v1/`. The offline checker reproduced both
confusion matrices and all four metrics with networking blocked, verified constant
baseline behavior, rejected a corrupted export and confirmed the production forest
loader rejects the weak-proxy format. It fitted no local model. Its original-run
regression also passed. Preserve the ZIP; the application still has no approved
real forest classifier.

To repeat the actual offline check:

```powershell
.venv\Scripts\python.exe scripts/check_weak_export.py --bundle data/phase3/weak_december_run_v1/forestguard_weak_proxy_run1.zip --sha256 8bf0858faaee969b35e003c466de19ab1767a96c5c8ed9098cb8010f13d3a6b8 --dataset data/phase2/weak_december_experiment_v1/weak_experiment.zip --dataset-sha256 b4d93e7db778b51addcea7e9c574e1f593b56c48786778a1629cf3921cf7f8ec --output data/phase3/weak_december_run_v1/offline_verification_new.json
```

Explicit verification output paths refuse overwrites. The selected model remains
research-only. Next, inspect representative shrub/crop disagreements on saved
dated imagery and document evidence/uncertainty before adding complexity or
promoting forest classification. Independent reference review is still absent.

## Reproducible preparation

```powershell
.venv\Scripts\python.exe scripts/prepare_weak_experiment.py data/phase2/weak_december_experiment_new --before data/study/compartment_279_v1/december_2024_v1/forestguard_279_research.zip
.venv\Scripts\python.exe scripts/build_weak_notebook.py --output data/phase3/weak_december_run_new/private_run.ipynb --dataset data/phase2/weak_december_experiment_new/weak_experiment.zip
.venv\Scripts\python.exe scripts/check_december_experiment.py
```

The private builder refuses existing embedded notebooks and limits embedding to
1 MiB in the Git-ignored data folder. The trackable public notebook
`notebooks/12_december_weak_proxy.ipynb` has empty inputs and no executed outputs.
The new check passes offline source preservation, sample provenance/counts,
spatial/date separation, input checksum, overwrite/invalid-pair rejection, embedded
dataset identity, notebook compilation and refusal of local fitting. The old
experiment's regression check also passes. `.gitignore` continues to cover private
data, artifacts and generated exports. The delivery backup recipe now includes
this new experiment; a separate checksum receipt preserves this milestone.

Calendar matching does not verify weather or vegetation-cycle equivalence.
Independent reviewed forest references and frozen evaluation splits remain missing.
No forest area, loss/gain, fire forecast or independent accuracy was produced.
