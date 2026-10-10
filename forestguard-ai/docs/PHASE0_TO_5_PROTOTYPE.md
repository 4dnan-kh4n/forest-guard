# Phase 0–5 prototype handoff

This release supports two explicit data views. Saved observations are real
compartment 279 images. Synthetic scenario uses generated geometry, dates,
classes and monthly values. It exercises application behavior without claiming
observed forest loss, fire records or independent forest accuracy.

## Working deliverables

| Phase | Prototype deliverable | Scientific limit |
| --- | --- | --- |
| 0 — feasibility | User-confirmed compartment 279 research polygon, real small crops, coverage and reference feasibility checks | No beat-wide totals; independent forest-positive evidence remains absent |
| 1 — foundation | Locked local tools, bounded processing, offline verification and stored artifacts | No new cloud dependency for opening saved results |
| 2 — data | Calibrated real observations and provenance registry; explicit synthetic classes and disjoint fixture splits | Synthetic labels do not replace reviewed real labels or independent test locations |
| 3 — model | Our cloud-trained baseline/Random Forest exports and locally verified research proxy inference | Historical-map agreement, not independent forest accuracy; no new local training |
| 4 — changes | Executable synthetic before/after comparison, loss/gain/common-coverage maps, hectare arithmetic and exports | No observed Joga loss/gain established |
| 5 — application | Login, real overview with automatic vegetation calculation, imagery comparison, proxy map, reports, synthetic scenario and mobile menu | Deployed version still needs acceptance after pushing; Vercel new run/history state is temporary |

## Present or use it

1. Start `start_ui.ps1` and open `http://127.0.0.1:8000/`. Local development
   sign-in remains Harda / Joga / `joga@123`; hosted sign-in uses the configured
   private password.
2. Leave **Data view → Saved observations** selected for real images, dated
   vegetation measurements and source reports. No officer uploads are needed.
3. Open **Research map** for our saved model's experimental tree-cover prediction.
4. Select **Data view → Synthetic scenario** to exercise generated class maps,
   **Change detection → Run saved comparison**, loss/gain layers and exports.
5. Open **Monthly scenario** for the generated 60-month series and its 12/60-month
   controls. Its CSV explicitly names simulated measurements.
6. Return to **Saved observations** to restore real-only navigation and reports.

Synthetic change and monthly history are separate fixtures, not a matched pair
of Joga datasets. Never compare their totals or treat the monthly series as 60
acquired satellite images. The source fixtures are preserved, not invented as
current observations to fill missing scientific evidence.

## Verification in this handoff

- Production frontend build and actual client session-helper checks passed.
- Synthetic dataset: 20 hashes, same-seed reproducibility, separated locations
  and simulated dates, overwrite rejection passed.
- Real registry: offline reproducibility, unchanged labels, source preservation,
  date/version/footprint and premature-split rejection passed.
- Model: network-blocked inference reproduced 12,362 usable pixels and the
  original cloud validation confusion matrix; grids/checksums/vote limits and
  production-loader rejection passed. No model was fitted locally.
- Changes: all four transitions, coverage/hectares, nodata, empty overlap,
  grid/date/season guards, overwrite and unapproved-real-map rejection passed.
- Browser: switched modes, ran a new synthetic comparison, viewed its results,
  used the monthly date range and downloaded the actual monthly CSV. It contains
  60 rows with explicitly simulated fields.

Reproduce with the existing check scripts:

```powershell
.\.venv\Scripts\python.exe scripts/check_demo_data.py data/demo/fixture_v1
.\.venv\Scripts\python.exe scripts/check_study_dataset.py
.\.venv\Scripts\python.exe scripts/check_research_proxy_map.py
.\.venv\Scripts\python.exe scripts/check_change.py
node scripts/check_client_session.cjs
```

## Deployment and acceptance boundary

Push the updated frontend source and documentation, retaining `deployment_data/`.
Keep data, private credentials, model binaries, generated screenshots and local
environments Git-ignored. Vercel rebuilds the UI using the existing configuration.

This closes the connected prototype workflow, not scientific Phase 0–5
acceptance. Credible real labels, frozen independent splits and model/change
evaluation remain necessary for operational findings. Fresh imagery acquisition
remains the team's cloud preprocessing workflow; no scheduled acquisition or
validated fire forecast was added in this handoff.
