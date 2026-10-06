# Progress checklist

Started fresh: 6 October 2026. Current phase: 2, in progress. Phase 1 foundation completed; Phase 0 validation gates remain open.

User-authorized demonstration scope: Phase 0 demo setup is complete using clearly
labeled synthetic/assumed data. Phase 1 is complete. This demo status is separate
from real-pilot gates below. See [synthetic demo data](docs/DEMO_DATA.md).

Only results from this new project count toward its completion gates.

Deadline priority: deliver the smallest working forest-cover/change workflow.
Avoid optional infrastructure and advanced risk features before the first release.
Keep essential geography, label, leakage and integrity checks; report unmet gates
honestly instead of marking them complete to meet a deadline.

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
- [ ] Validate sourced compartment polygon topology and spatial registration;
  establish current beat membership rather than equating compartment and beat.
- [ ] Establish official beat boundary or an explicitly confirmed provisional study polygon.
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
| 5 — application | Local maps, dashboard, API and CSV/HTML exports | End-to-end stored-data operation including offline maps | Pending |
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
