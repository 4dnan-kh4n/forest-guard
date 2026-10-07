# Scientific development restart — 7 October 2026

The hackathon is complete. Continue from the first unmet scientific gate while
preserving verified tooling, real imagery and useful interface work. Existing
synthetic fixtures are test inputs, not evidence of forest loss or fire in Joga.

## Actual phase status

| Phase | Existing deliverable | Remaining work |
|---|---|---|
| 0 — feasibility | Real calibrated crops, quality masks, official-source candidate geometry and pipeline checks | Accepted study geography; boundary registration/current membership; credible label feasibility; forest-cover definition and evaluation design |
| 1 — foundation | Bounded offline inspector, pinned runtime, retained install wheels and corruption/overwrite safeguards | Core gate passes. Recheck resources before substantial processing; update setup when later dependencies are adopted |
| 2 — data/labels | Real aligned March 2024/2025 pair, common-valid mask, registry and provenance/split audits | Curated inputs for the accepted area; reviewed labels with dated independent evidence; actual spatial/temporal splits frozen before sampling |
| 3 — classifier | No selected trained forest classifier or exported model bundle | Baseline and Random Forest training in free cloud compute, independent evaluation and reusable exported artifact |
| 4 — cover changes | Aligned pair supports technical comparison | Validated classifier outputs, suspected loss/gain maps on common coverage, area estimates and seasonal/alignment error review |
| 5 — application | Local React/Leaflet/FastAPI/SQLite observation interface and exports; public landing page | Real model/change jobs, uncertainty/coverage display, job failure handling and replacement of simulated history as the operational default |
| 6–8 — additional capabilities | No evaluated fire/loss forecasts or operational alert system | Establish credible event/weather/change evidence first; evaluate risk models only when feasible; implement traceable recommendation/alert rules |
| 9–10 — delivery/maintenance | Some input validation and offline checks exist | Full release checks, fresh setup, interruption/resource/corrupt-input/offline/recovery tests; backups, monitoring, retraining and rollback |

## Phase 0 tasks to close first

1. **Study area and geography.** Obtain current Joga beat mapping with provenance,
   or obtain explicit acceptance of a clearly named provisional study polygon.
   The prior user decisions restrict both Salyakhedi and compartment 278 to
   pipeline checks; they are still unapproved for pilot training/reporting.
   Check registration, current compartment/beat membership and the unresolved
   historical/source area discrepancy. Review reuse conditions before distributing
   official map/KML contents or derived geometry.
2. **Forest-cover definition.** Define the cover target and treatment of scrub,
   plantations, orchards, crops, mixed pixels and uncertainty. Administrative
   forest status and greenness alone do not establish the target class.
3. **Credible reference feasibility.** Collect dated, geolocated independent
   field/reference evidence and reviewed forest/non-forest/unknown patches.
   The review template and saved label audit contain zero labels. Weak land-cover
   maps may help investigate or bootstrap training, but cannot serve as reused
   independent test truth.
4. **Evaluation design and acceptance criteria.** Identify candidate independent
   locations/dates before extracting training samples. Review label quality and
   sampling/separation requirements. Keep performance aspirations distinct from
   achieved results; finalize model acceptance thresholds after baseline review.
   Actual finalized labels and frozen splits belong to Phase 2.

## Verification performed in this audit

Using the retained local Python 3.11.5 environment:

```powershell
.\.venv\Scripts\python.exe scripts/check_local.py
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe scripts/check_phase2.py data/phase2/pair_version7
python scripts/check_boundary.py data/reference/handia_working_plan_2022_2032/joga_278.candidate.geojson
python scripts/check_notebook.py
```

All five checks passed. The real stored candidate reproduces 58,439 usable pixels
of 58,971; the pair checker verifies real saved outputs with Python networking
disabled. Corrupt/missing inputs and report overwrite are rejected. Label checks
reject weak test references, nearby split locations, stale references and duplicate
IDs. Notebook checks cover four source notebooks, empty outputs, private-settings
separation and the local-processing guard. The boundary checker passes 1,484 edge
comparisons for the 57-vertex ring and explicitly records unverified registration,
unverified current beat boundary and no study-area approval.

The saved pair handoff records `phase2_complete=false`, `reviewed_label_count=0`,
`evaluation_splits_frozen=false` and `training_eligible=false`. These scientific
gates cannot be satisfied by passing engineering checks.

Current C: drive free space observed: approximately 40.09 GiB. The Windows CIM
RAM query was unavailable in this execution environment; current free RAM has not
been established and must be rechecked before substantial local processing.
No new downloads or dependencies were required for this audit.

The application/API and remote Vercel deployment were not revalidated in this
audit; previous UI build checks are historical evidence. The public deployment
is configured as a landing page, while officer sign-in and stored-data processing
require the local backend. The 60-month forest/fire series is generated, and the
real imagery comparison currently measures vegetation indicators, not a trained
forest classifier or verified forest-loss/fire findings.

## Completion standard and next step

Require passing agreed release checks, reproducible measured model evaluation,
and no unresolved blocking defects. Handle expected input/network/data failures
clearly. Software testing does not prove permanent absence of bugs, and model
performance is measured on independent data rather than promised to be perfect.

Next work starts with Phase 0 geography and independent label-reference feasibility.
Do not replace existing pipeline-only decisions with implied approval. Preserve
ignored imagery, reference material, labels, models and databases outside Git;
maintain `.gitignore` and keep reproducible source/documentation trackable.
