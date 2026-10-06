# Phase 2: imagery and label preparation

Objective: preserve manageable calibrated observations, align dates, review real
forest/non-forest evidence, and freeze independent evaluation splits before
extracting training pixels. Started 6 October 2026; labels/splits are not complete.

## Working pipeline dataset

The two-date private Kaggle notebook uses the existing four-band crop pipeline
on the official-source Joga 278 candidate, which remains pipeline-only under the
user's instruction. It does not approve a study polygon or assign forest labels.

| Acquisition | Scene ID |
|---|---|
| 21 March 2024 | S2A_T43QFE_20240321T053116_L2A |
| 28 March 2025 | S2A_T43QFE_20250328T052953_L2A |

Both observations use B02/B03/B04/B08, native 10 m, EPSG:32643, a 339 x 307 grid.
Product-specific scale/offset are checked against headers and applied once.
SCL remains native 20 m quality information aligned by nearest-neighbor sampling.
Clouds, shadows, missing and uncertain classes are excluded by the documented
quality rule; SCL is not a forest label. Attribution now follows each acquisition
year rather than assuming every observation is from 2025.

Version 7, scriptVersionId 355697676, completed successfully in 65.3 seconds as
shown by Kaggle. Core processing recorded 18.585 seconds for 2024 and 16.348
seconds for 2025. The 6,161,209-byte pair ZIP includes date-specific source
metadata, reports, GeoTIFFs, verified sample ZIPs, candidate/common masks and preview.

| Candidate coverage | Pixels |
|---|---:|
| Candidate polygon | 58,971 |
| Usable on 21 March 2024 | 57,885 |
| Usable on 28 March 2025 | 58,439 |
| Common usable coverage | 57,605 (97.6836%) |

These are observable-coverage counts, not model accuracy, forest extent or loss.
Similar calendar season does not ensure identical water levels or phenology.
No forest-loss/gain estimates are produced by this notebook.

Reproduce the source notebook with `python scripts/build_pair_notebook.py`.
The public `notebooks/03_two_date_data.ipynb` has no boundary coordinates. Its
private execution copy stays in the ignored reference-data folder. Keep Kaggle
Private, Accelerator None and Internet On; export artifacts before session ends.

## Offline verification and versioned registry

After saving/extracting the pair under `data/phase2/pair_version7/`:

```powershell
.\.venv\Scripts\python.exe scripts/verify_pair.py data/phase2/pair_version7 --output data/phase2/dataset_registry.json
.\.venv\Scripts\python.exe scripts/check_phase2.py data/phase2/pair_version7
```

Use a fresh registry output path for repeat runs. The verifier checks all archive
and extracted hashes, uses Phase 1 to recheck each date, compares grids and
recomputes candidate/common masks. The registry preserves source IDs/dates,
calibration, band order, CRS, resolution, quality/resampling rules, license URLs,
attribution, cloud/local versions and sample hashes. Its dataset version is a
content-derived identifier for these exact artifacts, not a trained-model version.
Local verification passed for all 23 pair file hashes and reproduced both dates'
counts and the common mask. Registry version: `pipeline-5f9a7ea39daafa3f`.
The real pair also passed with Python networking disabled. Synthetic checker
fixtures proved rejection of weak test references, nearby split locations, stale
references and duplicate IDs; those fixtures were never saved as project labels.
Saved check summary: `data/phase2/verification.json`.

## Label review protocol

The user reports no independent reference evidence yet. The label template
remains empty, with zero reviewed forest examples. Do not fill it with predictions,
management-map colors, SCL classes or weak-map pixels and call them ground truth.

Copy `config/label_review_template.geojson` into `data/labels/` when real evidence
is available. Label features may initially be geographic points or small
single-ring polygons without holes. Record all required properties from the
template; use `unassigned` until evaluation grouping is deliberately frozen.

- `forest`: dated evidence supports established tree-dominated forest vegetation
  consistent with a documented study definition. Legal RF/PF status alone is
  insufficient. Final canopy/context criteria require reviewed examples.
- `non_forest`: dated evidence supports a non-forest cover/use, such as clear water,
  agricultural fields or settlement; mixed edge pixels need separate review.
- `unknown`: forest/scrub/plantation/orchard distinction or observation is uncertain.
  Keep it excluded from binary training and explain uncertainty.

Required provenance includes observation/reference dates, reference source and
access/license, reviewer/date, confidence, study-area version, reference kind,
review status and independence declaration. Allowed reference kinds are
`field_observation`, `dated_reference_imagery`, `weak_map`, and
`historical_management_document`. Review status is `unreviewed`, `reviewed`, or
`weak_only`; confidence is `high`, `medium`, or `low`.

The audit verifies metadata and declared separation, not whether a reviewer is
correct. Weak sources may be tracked for investigation; they cannot establish an
independent test set. In this initial strict audit, model splits require reviewed
independent dated field/reference imagery, exclude low confidence/unknown labels,
and require reference dates within 31 days of the stated observation. That time
tolerance is a preliminary screening choice, not a guarantee of truth.

```powershell
.\.venv\Scripts\python.exe scripts/audit_labels.py config/label_review_template.geojson --output data/phase2/label_audit_new.json
```

## Evaluation split policy and gate

Assign non-overlapping locations and observation dates before sampling. Initial
cross-split footprint separation is at least 100 m, to be revisited against
spatial correlation and patch sizes. The audit uses the local UTM zone 43N grid
and rejects input outside that zone. It rejects adjacent/overlapping
train/validation/test footprints and shared acquisition dates. Preserve an untouched
independently reviewed test set; keep weak-label creation out of test references.

No actual splits are frozen while labels and accepted geography are absent.
The registry and audit explicitly keep `training_eligible=false`. Completing
schema tests is not completing a reviewed label dataset or establishing accuracy.
Next required inputs are acceptable study geography and dated independent review
evidence; then populate/review labels and freeze actual split locations/dates.

## Preservation

`.gitignore` excludes downloaded catalogues, pair imagery, private execution copy,
populated labels and registries under /data/. Code, public source notebooks,
empty templates and safe measured summaries stay trackable. Keep ignored artifacts
in separate backups for offline operation. No new dependencies were installed.

## Verified handoff

The imagery-preparation deliverable is finalized at version
`pipeline-5f9a7ea39daafa3f`. A final offline check passed, and
`data/phase2/handoff.json` records hashes of the registry, label audit,
verification summary and exported pair ZIP for backup/transfer.

Full Phase 2 completion remains blocked by accepted study geography, reviewed
labels and actual independent evaluation splits. There are zero reviewed labels;
no split assignments, forest classes or model results were invented. Phase 3
training code can be developed separately, but this handoff is not eligible for
credible supervised forest-model training yet.
