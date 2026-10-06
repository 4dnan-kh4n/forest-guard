# ForestGuard AI

Clean implementation started on 6 October 2026. No code, notebooks, downloaded
data, saved outputs or models from the earlier implementation are used here.

First product: local forest-cover mapping and suspected cover-change detection.
Pilot: Joga forest beat, Harda, Madhya Pradesh. The official beat boundary is
unverified. The research box below is only for checking our data pipeline.

Budget: INR 0 for software, datasets, APIs, model services and hosting. Heavy
processing/training runs in a free hosted CPU notebook when available. The
finished product must analyze stored data with saved models offline.

## Phase 0 — establish feasibility

Objective: inspect one real satellite crop and determine whether suitable
imagery, geography and credible labels can support the first product.

Inputs: freshly fetched Sentinel-2 Collection 1 L2A metadata, B02/B03/B04/B08 measurements,
scene classification (SCL), and research bbox [76.785,22.413,76.805,22.433].
Processing: cloud-only window reads, scale/offset once, quality masking, exact
pixel-center study mask and saved-output checks. Outputs: small GeoTIFFs, RGB
preview, coverage/provenance report and a checksummed ZIP.

Verification: reopen saved layers, check their grids and masks, recompute usable
coverage and inspect the real preview. A technical pass does not prove that the
area is forest, that labels are credible, or that the beat boundary is correct.

## Run the new notebook

The new notebook has already been created and imported at
[ForestGuard AI - Fresh Feasibility](https://www.kaggle.com/code/adnankh4n/forestguard-ai-fresh-feasibility/edit).
Private is selected, Accelerator None was selected, and the draft runtime is off.
Phone verification is complete. Internet On and Accelerator None were verified;
Version 1 completed successfully and its outputs are stored in `data/phase0/version1/`.
The current verified bundle and diagnostic evidence are saved in `data/phase0/version3/`.
The legacy calibration concern was avoided with Collection 1 and four-band
metadata/header checks in successful Version 3. Geographic suitability and
reviewed labels remain pending. See `docs/PHASE0_SAMPLE_REVIEW.md`.

1. Open that notebook. Account verification is complete; no billing is needed.
2. Enable Internet and keep Accelerator None. `notebooks/00_feasibility.ipynb`
   is the local source copy if reimporting is needed.
3. Save & Run All. Wait for `Verified sample bundle` in the output.
4. Use the saved Output tab's **Output actions > Download output** and preserve
   its archive. The sample ZIP is under `/kaggle/working/forestguard_phase0/<run timestamp>/`.
   Save the notebook version and download the bundle before stopping the session.
5. Keep the bundle locally. We will inspect the preview and measured coverage
   before deciding whether the crop is suitable for label work.

Colab alternative: upload the same notebook into a hosted Colab runtime, with
no GPU or local runtime. The script checks its required packages and does not
install missing ones automatically. Download the ZIP under `/content/forestguard_phase0/`.
Free runtime availability, storage and Internet access can change.

No local ML/geospatial installation is needed for this phase. The new notebook
can be regenerated from its new source with:

```powershell
python scripts/build_notebook.py
python scripts/check_notebook.py
python scripts/verify_bundle.py data/phase0/version3/forestguard_phase0.zip
```

## Scientific boundaries

SCL classes 4/5/6 are quality classes, not forest labels. Green crops, scrub and
orchards must not automatically be called forest. Remote-sensing cover does not
establish legal forest status. No forest area or change is calculated yet.

Later we will review forest/non-forest/unknown labels and freeze separate
locations/dates for training, validation and untouched testing **before** pixel
sampling. Cloud training will compare a baseline and Random Forest and export
the selected model with preprocessing, class mapping, versions and evaluation.

There is no Gemma or other hosted-model dependency in this fresh foundation.
An optional language feature can be considered after the offline analysis works.

See [progress and completion gates](PROJECT_PLAN.md) and [sources and licenses](docs/SOURCES.md).

## Git and phase handoffs

Use this `forestguard-ai` folder as the repository root for the clean project.
Its `.gitignore` keeps credentials, downloaded data, exported models, local
databases, private record extracts/reviews and generated files out of Git.
Code, source notebooks, dependency lockfiles, `.env.example` and public project
documentation remain trackable. The ignore rules are reviewed in every phase.

Keep ignored data/model artifacts locally and in backups for offline operation.
Before each push, review `git status --short` and `git diff --cached`. Ignore rules
do not remove files that were already tracked. No Git repository has been
initialized by this setup; the user controls commits and pushes.
