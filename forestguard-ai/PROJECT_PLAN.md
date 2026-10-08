# Progress checklist

Started fresh: 6 October 2026. Current work: return to Phase 0 scientific
feasibility following the hackathon, at the user's request on 7 October 2026.
Phase 1 foundation passes its offline checks; Phase 0 geography/reference gates,
Phase 2 reviewed labels/splits and Phase 5 model integration remain open.
See [restart audit and ordered remaining work](docs/RESTART_AUDIT.md).

Update on 7 October 2026: the user selects **compartment 279** as the study target.
The saved official Handia KML tags it PF / RAMPURA beat / JOGA circle. Selection
is confirmed; exact geometry comparison with the user's Google Earth export and
spatial registration remain pending. Do not substitute the old 278 dataset or
describe 279 as the entire Joga beat. Its 95-vertex source candidate passes the
bounded topology check (4,277 edge pairs), with source bytes preserved.
See [279 evidence and next inputs](docs/COMPARTMENT_279_STUDY.md), safe scope config
`config/study_area.json`, and [adopted cover definition v1](docs/FOREST_COVER_DEFINITION.md).
The cover definition is selected; credible reference labels and evaluation design
remain unfinished. No new study-area imagery, labels or model results are claimed.

Update on 8 October 2026: the supplied `comp_PF.kml` provides one 279 polygon.
Its 82-vertex ring passes 3,159 edge comparisons. Selected coordinates are preserved
as `compartment-279-user-kml-v1`, a user-selected provisional research geometry;
independent registration and current official status remain unverified. The old
working-plan candidate has 95 vertices and differs in projected area by about
3.770891 ha. Both versions and original source bytes are retained; no geometry
is adjusted to force an attribute match. Exact-coordinate selection is now resolved.
[Officer data request and collection procedure](docs/FIELD_OFFICER_DATA_REQUEST.md)
and [blank field form](docs/FIELD_OBSERVATION_FORM.md) are ready. No field labels
have been collected or trained model performance claimed.

Research update, 8 October 2026: the user confirms the supplied 279 boundary is
correct. This resolves user confirmation; an independent registration measurement
has not been obtained. Original field photography is prohibited. The active route
is now [satellite research](docs/SATELLITE_RESEARCH_PROTOCOL.md), with uncertain
land-use/origin cases excluded rather than assigned assumed labels. A hosted-only
three-season 2025 notebook prepares ten bands and five numerical features on a
native 20 m grid. Public/private separation, numerical feature checks and local
execution refusal pass. Cloud outputs and reference feasibility are tracked
separately from syntax checks; no four-class accuracy is assumed.

The separate private 279 research notebook Version 1 completed on 8 October 2026
(script version 356345375). Saved locally: verified 1.54 MB research ZIP with
12 hashed files. The December 13 crop supplies 94.21% feature-valid coverage
inside the selected polygon at 20 m. Dry/wet candidates failed the initial 90%
screen; status is partial seasonal data screening. Offline grids, polygon masks,
counts, index formulas and tampered-hash rejection pass. No labels or classifier
were created. Expand the bounded scene screen and establish remote-reference
feasibility next; do not treat notebook execution success as completed science.

Research Version 2 completed on 8 October 2026 (script version 356354114).
- [x] Screen 36 bounded SCL crops using actual polygon coverage, then process
  the best local candidates without relaxing the 90% feature threshold.
- [x] Preserve April 3 and December 9, 2025 observations on a shared 20 m grid:
  94.52% / 94.37% feature coverage; common coverage 94.19% (12,338 / 13,099 centres).
- [x] Acquire a 262×396 WorldCover 2021 v200 crop under CC BY 4.0, retain original
  classes/provenance/attribution, and verify nearest-neighbor alignment. The
  102,720,459-byte source tile was not downloaded in full.
- [x] Verify and preserve the 4,937,030-byte ZIP: 27 hashes/CRC pass, original
  quality crops included, all feature/texture values reconstructed offline.
- [x] Prepare seven unlabeled review footprints and a self-contained offline
  review page; source/case checks and browser layout verification pass.
- [ ] Establish reviewed forest-positive reference evidence and evaluation splits.
  Convenience cases and the old weak map do not meet this gate.

NASA reference check, 8 October 2026:
- [x] Verify Earthdata sign-in and free/open collection metadata; preserve the
  small public CMR inventory and actual spatial/variable subset settings.
- [x] Download the 104,730-byte March 6 L2A V003 subset and inspect 81 real shots:
  38 centres inside compartment 279; none pass the initial degrade=0 screen.
- [x] Check the May 28 and June 23 subsets: Harmony returns two `nodata` warnings;
  retain underlying workflow evidence instead of treating service success as data.
- [x] Export exact-ID CSV/GeoJSON, hashes and inspection report; actual-data checks
  pass, with existing-output and resource limits enforced.
- [x] Fix pending-label audit and verify it still rejects premature reviewed/training
  transitions. Recompute review medians with masks respected; all cases stay unknown.
- [ ] Obtain credible positive forest references; GEDI 2025 check did not resolve this.

Reproduction and measured limits: [GEDI reference check](docs/GEDI_REFERENCE_CHECK.md).

Among the 12 screened monsoon scenes, maximum SCL coverage was 55.95%; the three
processed candidates gave 48.94%, 30.91% and 13.25% feature coverage and were
rejected. Scientific status remains partial seasonal data screening. No forest
labels, model accuracy or change estimates have been manufactured. Latest files:
`data/study/compartment_279_v1/research_v2_20261008/` and
`data/labels/compartment_279_v2_review_pack/`. Reproduction and limitations are in
`docs/SATELLITE_RESEARCH_PROTOCOL.md`.

User-authorized demonstration scope: Phase 0 demo setup is complete using clearly
labeled synthetic/assumed data. Phase 1 is complete. This demo status is separate
from real-pilot gates below. See [synthetic demo data](docs/DEMO_DATA.md).

Only results from this new project count toward its completion gates.

Development priority: deliver an evaluated working forest-cover/change workflow.
Avoid optional infrastructure and advanced risk features before the first release.
The hackathon deadline no longer controls scientific or engineering decisions.
Keep essential geography, label, leakage and integrity checks; fix known defects
and require agreed release checks to pass before claiming a completed product.

Before starting each new phase, explain its objective, inputs, processing,
deliverable and verification in chat. Continue only with honest measured results.

For every phase, review new files and maintain .gitignore before handoff. Keep
secrets, data/models, private reference records and generated files local; keep
source code, notebooks, safe templates and reproducible documentation trackable.
The user will push the code after each phase.

## Phase 0 — scope and feasibility

- [x] Record INR 0 budget and offline stored-data requirement.
- [x] Fresh local resource check: 7.79 GiB total RAM, 1.09 GiB available,
  C: 44,140,777,472 bytes free; observations can change.
- [x] Create new cloud-only sample source and notebook.
- [x] Check generated notebook syntax and refusal to run processing locally.
- [x] Import into a newly created Kaggle notebook; Private selected, Accelerator None,
  draft saved and runtime off.
- [x] Execute the new private cloud notebook and export its outputs; Version 1 successful.
- [x] Inspect real imagery preview and measured usable coverage (98.1143% in research box).
- [x] Avoid demonstrated legacy calibration ambiguity with Collection 1 and
  metadata/header agreement checks; Version 3 successful.
- [x] Inspect user-supplied historical Joga records: repeated 278 RF/Handia/Joga
  references and neighboring 320 PF GPS candidates found; current boundary unverified.
- [x] Prepare a reusable location-review notebook and a Git-ignored private
  execution copy; syntax and original cloud-only guard checks pass.
- [x] Inspect satellite crop/point overlay around historical neighboring-site GPS candidates:
  Version 4 rejected for 0.3624% usable coverage; Version 5 supplies 99.8651%.
- [x] Preserve both location-review runs locally; all seven exported sample hashes
  pass. Public/private notebook separation and current .gitignore checked.
- [x] Find and preserve official Handia management map from Harda's listed
  2022-23 to 2031-32 working plan; visually confirm compartment 278/Joga context.
- [x] Extract official Handia KML's one Joga/278/RF candidate polygon; retain
  source bytes, metadata and explicit unapproved status. Structural checks pass.
- [x] Check candidate simple-ring topology offline: 57 vertices, 1,484 edge
  comparisons, no crossings/touches or degenerate/backtracking edges detected.
- [x] Prepare empty provenance-aware label template and measurable technical
  acceptance/evaluation policy; no populated labels or frozen splits claimed.
- [x] Run candidate/imagery pipeline check in private Kaggle Version 6; native-10 m
  polygon mask and export integrity pass. Candidate coverage 99.0979%, not accuracy.
- [x] Inspect actual overlay and save feasibility result. No independent positional
  error measurement or credible forest-positive labels established.
- [ ] Validate sourced compartment polygon spatial registration and establish
  current beat membership rather than equating compartment and beat. Topology
  already passes its documented single-ring check.
- [x] Establish an explicitly confirmed provisional compartment 279 study polygon
  from the user-supplied KML on 8 October 2026. Official/current-boundary status
  and independent registration checks remain open; this is not the full Joga beat.
- [ ] Demonstrate credible reviewed forest/non-forest/unknown labels.
- [ ] Establish independent evaluation locations/dates and attainable acceptance targets.

Phone verification is complete; Internet On and Accelerator None were verified
in Kaggle. The first real crop and its checksummed outputs are preserved locally.
Collection 1 calibration/header checks pass; reviewed labels, a trained model,
performance scores, an official boundary and beat-wide measurements do not exist.
See [measured results and scientific limits](docs/PHASE0_SAMPLE_REVIEW.md).

New notebook: [ForestGuard AI - Fresh Feasibility](https://www.kaggle.com/code/adnankh4n/forestguard-ai-fresh-feasibility/edit).
Saved first successful run: scriptVersionId 355664060, private Version 1.
Original river-crop run: scriptVersionId 355668914, private Version 3.
Its outputs are preserved in data/phase0/version3/; all seven file hashes pass
the offline verifier. This crop demonstrates the data pipeline, not forest-model
feasibility. Next: authoritative geographic evidence and representative reviewed
forest/non-forest/unknown examples. The user has no beat boundary or compartment
details at that time. Newly supplied historical records now provide compartment
references and neighboring-site GPS candidates, summarized in the local-only
record review (docs/JOGA_RECORDS_REVIEW.md, excluded from Git). No beat polygon has been
substituted or fabricated.

Latest successful location-review run: scriptVersionId 355679695, private Version 5.
28 March 2025, 292 x 283 native-10 m pixels, 80,032 inside research box,
79,924 usable (99.8651%); 77,784 usable land-quality pixels, not forest area.
Saved under data/phase0/location_review_version5/. Image inspection shows field
patterns and extensive brown textured cover whose forest/scrub status is unresolved.
Historical points are overlaid without connecting them. Datum remains assumed.
This is neighboring-site evidence, not a verified Joga pilot boundary.
User decision: keep the Salyakhedi crop for pipeline checks only. It is not an
approved study polygon and must not supply pilot training/evaluation labels or
forest-area/change totals. Preserve its outputs as technical verification evidence.
The official Handia management map has now been found and reviewed. See
[Joga map evidence and verification gaps](docs/JOGA_MAP_EVIDENCE.md).
The official KML identifies compartment 278 as N_BEAT=JOGA, but its area attribute
differs from the historical record. User decision: retain this polygon for pipeline
checks only as well; no approved study polygon exists. Simple-ring topology now
passes. Next: validate spatial registration,
reconcile area records and establish current beat membership or a separately
confirmed research area. Reviewed dated
labels remain required. Phase 0 stays open.
See [Phase 0 exit check and exact remaining gates](docs/PHASE0_EXIT_CHECK.md).
See [final measured feasibility assessment](docs/PHASE0_FEASIBILITY_RESULT.md).
The candidate overlay/mask works and is qualitatively consistent with river/village
context, but neither that check nor deadline pressure changes pipeline-only scope.
Phase 1 tooling may proceed independently; Phase 0 is not marked complete.

## Remaining phases

| Phase | Deliverable | Completion evidence | Status |
|---|---|---|---|
| 1 — foundation | Reproducible lightweight local processing command | Offline real-data check, corruption/overwrite safeguards, dependency lock and retained wheels | Complete |
| 2 — imagery and labels | Curated crops, reviewed labels, frozen splits | Two-date cloud pipeline run succeeds; independent labels and actual frozen splits pending | In progress |
| 3 — model | Cloud-trained baseline/Random Forest and exported model bundle | Independent precision, recall, F1, IoU, area error and failure review | Pending |
| 4 — changes | Suspected loss/gain layers and hectare estimates | Common valid coverage, alignment and seasonal errors reviewed | Pending |
| 5 — application | Local maps, dashboard, API and CSV/HTML exports | Observation UI verified on real/synthetic saved data; model inference/change jobs pending | UI delivered; model integration pending |
| 6 — fire risk | Evaluated model if credible events/weather permit | Time-aware validation, false alarms, PR-AUC and calibration | Pending |
| 7 — loss risk | Forecast if justified, otherwise historical indicators | Sufficient multi-year labels and later-period/separate-area evaluation | Pending |
| 8 — recommendations | Transparent evidence-based rules and alert history | Traceable evidence/time/version; authorization before network sharing | Pending |
| 9 — reliability | Local release and recovery instructions | Corrupt inputs, interruption, offline use, resources and restoration tested | Pending |
| 10 — maintenance | Freshness, evaluation, retraining and rollback process | Replacement models pass fixed acceptance checks | Pending |

First release stops at Phase 5. F1 >= 0.85 and IoU >= 0.70 remain aspirations;
we will set attainable targets after the baseline and label-quality review.
No fire or future-loss prediction is assumed feasible.

## Phase 1 verification

- [x] Inspect existing code and recheck resources before dependency acquisition.
- [x] Isolate a minimal local runtime; install checked binary wheels without a
  local training stack; retain all nine wheels (38,807,174 bytes) for offline setup.
- [x] Record tested Windows/Python 3.11 package pins and bundled-license metadata.
- [x] Implement bounded offline inspection with JSON/CSV measured-coverage exports.
- [x] Reproduce real cloud crop/candidate counts, with Python networking disabled.
- [x] Reject corrupt/missing inputs and report overwrite; preserve source hashes.
- [x] Maintain .gitignore for wheels, environment, private data and generated reports.

Working report: data/phase1/coverage_run1/. Reproduction and limits:
[Phase 1 foundation](docs/PHASE1_FOUNDATION.md).

## Phase 2 progress

- [x] Inspect existing exports/template and record no independent reference evidence available.
- [x] Preserve March 2024 public metadata catalogue and select a comparable acquisition.
- [x] Run private cloud two-date preprocessing on the pipeline-only candidate;
  grids align and common valid coverage is 57,605 / 58,971 pixels (97.6836%).
- [x] Prepare local pair-integrity/coverage registry and label-provenance/leakage audits.
- [x] Download and locally verify all pair outputs (23 file hashes), masks/counts
  and grids; preserve registry pipeline-5f9a7ea39daafa3f.
- [x] Pass offline real-pair checks and synthetic checker tests for weak test labels,
  adjacent split locations, stale references and duplicate IDs; no fixture labels saved.
- [ ] Demonstrate credible reviewed labels using dated independent reference evidence.
- [ ] Confirm acceptable study area and freeze actual independent split locations/dates.

Phase 2 reproduction and review rules: [data and labels](docs/PHASE2_DATA_AND_LABELS.md).
Imagery handoff finalized and verified at pipeline-5f9a7ea39daafa3f; manifest
preserved in data/phase2/handoff.json. Full Phase 2 remains blocked on the unchecked
label/geography/split gates above. Phase 3 has not started.

## Synthetic demonstration completion

- [x] User authorizes dummy/assumed data for remaining Phase 0/1 demo requirements.
- [x] Generate fictional geometry, band-like inputs, synthetic classes and disjoint splits.
- [x] Verify 20 hashes, saved pixels/grids, 160 m gaps, distinct simulated dates,
  deterministic regeneration and overwrite protection.
- [x] Preserve demo ZIP/manifest/check result; keep generated data ignored.

Demo dataset: data/demo/fixture_v1/. No real reviewed labels or accuracy claimed.

## Phase 5 UI milestone

- [x] Announce phase objective and advance UI at the user's request.
- [x] Build React dashboard and local Leaflet raster maps without online tiles/fonts.
- [x] Connect actual saved Sentinel-2 metadata, dates, masks and synthetic class layers.
- [x] Implement dataset library/search, ZIP import and display-only GeoJSON outlines.
- [x] Implement CSV/HTML exports and SQLite history of real checks/imports/exports.
- [x] Build production assets; final API check verifies 15 image responses and
  nine invalid input cases after importing the saved sample.
- [x] Verify browser comparison, layer/date selection, checks, search, CSV download,
  ZIP/GeoJSON imports and navigation; no browser console errors observed.
- [x] Verify narrow/mobile and desktop layouts without horizontal overflow.
- [x] Maintain Git exclusions for databases, data, caches, dependencies and builds.
- [ ] Connect selected exported model and suspected cover-change layers after training.

Startup and reproducible checks: [local UI](docs/UI_STARTUP.md).

## Presentation UI update

- [x] Reference-inspired forest landing page, trees-and-shield logo, cycling
  headline, animated satellite/forest workflow, section reveals and FAQ controls.
- [x] Harda/Joga login with requested local demo password, server-side sessions,
  protected dataset APIs, logout and preset presentation inputs.
- [x] Run imagery analysis computes real NDVI vegetation indicators from stored
  reflectance/masks, with an index layer, date summaries and report fields.
- [x] Production build and API checks pass including wrong-password rejection,
  access control, logout and stored-data analysis; no trained classifier claimed.

Presentation steps: [demo walkthrough](docs/PRESENTATION_DEMO.md).

User requested the officer screen focus on deforestation/fire reporting with
plain-language labels and a universal landing page. Login now opens the monthly
forest/fire report first. `scripts/monthly_demo.py` reproducibly provides 60
simulated month records (Nov 2021–Oct 2026) with canopy area, example cover change,
fire signals and a seasonal illustration index. Time filters and CSV export are
wired. This monthly dataset is synthetic only: no 60 monthly satellite images,
reference forest boundaries, fire detections or training data were supplied.
No simulated value is presented as a finding about Joga or any real area. The
saved real March 2024/2025 imagery remains available under Satellite map.
