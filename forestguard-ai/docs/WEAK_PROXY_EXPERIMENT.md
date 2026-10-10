# Exploratory weak-map training — 10 October 2026

This is a separate research experiment, not completion of reviewed-label Phase 2
or the operational forest model in Phase 3. With no independent reviewer available,
the target is agreement with ESA WorldCover 2021 v200's predicted tree-cover class.
Tree cover includes agricultural trees and plantations, and the reference is four
nominal calendar years older than the 2025 observations. No forest area, change,
fire inference or independent accuracy result is produced.

## Actual cloud run and saved deliverables

Private [Kaggle notebook](https://www.kaggle.com/code/adnankh4n/forestguard-exploratory-tree-cover-proxy),
version 1 / script version **356844511**, completed successfully in **19.2 seconds**.
Accelerator None, Internet off, draft runtime off. No fitting ran on the laptop.

- Input: `data/phase2/weak_proxy_experiment_v1/weak_experiment.zip`, 515,208 bytes.
  SHA-256: `15d7c83557657a116f10080953405f521f100e64b389ef8b0dcaea3632945279`.
- Model export: `data/phase3/weak_proxy_run_v1/forestguard_weak_proxy_run1.zip`,
  1,102,779 bytes. SHA-256:
  `eca2839185a91e729bbf9ab4c52813f2137a6e056b13c432b97bbe9a8ae7061c`.
- Source notebook with no data: `notebooks/10_weak_tree_cover_proxy.ipynb`.
- Exact private executed notebook: `data/phase3/weak_proxy_run_v1/private_run.ipynb`.
- Export verification and offline reproduction: `verified_export.json` and
  `offline_verification.json` in that same run folder.

The export contains the fitted majority baseline and Random Forest, the dataset/
model manifest, evaluation report and artifact checksums. Model manifest preserves
class meaning, calibrated feature order, preprocessing, source hashes, reference
license/citation, observation identities, runtime versions and unapproved scope.
Estimator parameters and seed are retained in the archived executed source.
Both cloud serialization roundtrips passed; local predictions reproduced both
cloud confusion matrices on all 6,067 validation samples without network access.

## Design and measured outcome

The north/south spatial regions and excluded 200 m strip were set before pixel
extraction. Training used 4,915 April 3 samples in the north; validation used
6,067 December 9 samples in the south. Observation dates and sampled locations
are separate, but the teacher map is the same historical product. There is no
independent test set. This design combines geography and season changes, so it
cannot isolate their individual effects. Neither group has independently reviewed labels.

| Model | Weak-reference agreement F1 | Tree-proxy recall | Interpretation |
|---|---:|---:|---|
| Majority baseline | 0.88964 | 1.00000 | Predicts tree cover for every validation sample; misses all 1,206 teacher non-tree samples. |
| Random Forest | 0.01340 | 0.00679 | Predicts only 33 of 4,861 teacher tree-cover samples correctly; fails this transfer experiment. |

The documented selection rule picked the baseline. Its high F1 reflects the
teacher-class imbalance and constant behavior; it is not a useful forest classifier.
Neither model is approved for application use. The production forest loader rejects
this separate proxy export; the dashboard's real-model connection remains unchanged.

Feature diagnostics show substantial differences between groups:

| Teacher class | April/north median NDVI | December/south median NDVI |
|---|---:|---:|
| Tree cover | 0.2356 | 0.6535 |
| Other known cover | 0.2516 | -0.3523 |

These are measurements of the sample groups, not class truths or proof of a single
cause. Geographic class composition, season, reference age/errors and actual
land-cover changes can all contribute. Do not tune on this validation set to make
the score appear successful or reinterpret failed predictions as deforestation.

## Reproduction

```powershell
.\.venv\Scripts\python.exe scripts/prepare_weak_experiment.py data/phase2/a_new_weak_experiment
.\.venv\Scripts\python.exe scripts/build_weak_notebook.py
.\.venv\Scripts\python.exe scripts/check_weak_experiment.py
.\.venv\Scripts\python.exe scripts/check_weak_export.py
```

Fit only on hosted CPU. Import the public notebook into a private Kaggle/Colab
session; attach the prepared ZIP and set BUNDLE and TRUSTED_SHA256 in its input
cell. Save and run, then download the exported model ZIP before session termination.
The preserved private run instead embeds the same checksum-verified small dataset
so no Internet or dataset attachment is needed for its hosted execution.
Free hosted quotas can change. The notebook installs no packages or paid services.

Dataset preparation and notebook checks passed offline, including overwrite,
wrong checksum, date/spatial separation and the local-fitting guard. Model export
checks verified four artifact hashes and rejected corruption. Original research
review records and production training eligibility were unchanged. Runtime wheels
already existed; no new dependencies were installed.

WorldCover metadata retains CC BY 4.0, the provider attribution and Zanaga et al.
(2022), ESA WorldCover 10 m 2021 v200, DOI 10.5281/zenodo.7254221. Sentinel metadata
retains its original calibration and attribution. Public source notebooks contain
no coordinates, labels or fitted artifacts. Actual data/executed notebooks/models
remain ignored by Git and must be preserved separately. The broader backup recipe
now includes this experiment; existing Phase 9 archives remain immutable.

An eight-file source/data/model preservation package was verified at
`data/backups/weak_proxy_run_v1_preservation.zip` (2,151,941 bytes), with SHA-256
`bd05d048abc4adc0b00c8e849d2b18c0804e104b2a4d616bccd492a027d95d30`.
A matching copy and receipt are retained at
`E:\ForestGuard_Backups\2026-10-10\`. As previously checked, E: shares C:'s physical
disk, so this does not provide physical disk-failure protection. The saved cloud
screenshot and log excerpt are retained in the run folder separately.

## Next step

Keep this as a failed exploratory transfer result. Establish suitable same-season
observations and credible current references before claiming forest-model performance.
The lack of a reviewer and independent ground truth remains a scientific blocker;
this experiment does not remove it. No classifier or alert has been silently promoted.
