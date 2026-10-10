# Progress checklist

Annual imagery and recent fire milestone — 10 October 2026:
- [x] Diagnose/download first cloud export, preserve its empty acquisition report.
- [x] Rerun privately on Kaggle CPU; acquire and verify real 2023–2026 imagery.
- [x] Keep original pixel masks and 90% default training screen; use measured partial
  coverage for annual viewing only.
- [x] Register real 2022–2026 images, proxy extent and four comparisons over common clear coverage.
- [x] Connect real NOAA-20/21 NASA fire feeds, refresh and saved offline fallback.
- [x] Verify local interface, exports, geometry/parser failures and bounded deployment data.
- [x] Verify 2022 product XML calibration, acquire an accepted crop and preserve the prior dataset.
- [x] Submit a bounded NASA NOAA-20 archive request for 2022–2026 (request 820485).
- [ ] Acquire 2022–2026 archived fire history.
- [ ] Push/redeploy and verify these additions on actual Vercel production.
- [ ] Independently evaluate forest labels/model and operational change claims.
See `docs/ANNUAL_AND_FIRE.md`.

Connected Phase 0–5 prototype — 10 October 2026:
- [x] Add explicit real-observation / synthetic-scenario selection, isolated
  navigation, scoped datasets/reports and automatic stored-image analysis.
- [x] Expose functional synthetic change comparison and monthly history without
  requiring officer uploads; keep real observations as the default.
- [x] Shorten repeated UI status messages while preserving data provenance,
  scientific scope, input errors and synthetic labels.
- [x] Verify synthetic data, real registry, offline model inference, change
  arithmetic/guards, browser comparison run and actual 60-row CSV download.
- [ ] Independent real forest labels/splits/evaluation and operational acceptance.
See `docs/PHASE0_TO_5_PROTOTYPE.md` for deliverables and reproducible checks.

Officer workflow correction — 10 October 2026:
- [x] Replace wrapped mobile navigation with accessible collapsible navigation.
- [x] Open real compartment 279 observations and automatically measured vegetation
  indicators after login; omit synthetic fixtures from officer navigation.
- [x] Remove officer uploads and use team-managed missing-data recovery wording.
- [x] Verify local login, saved image, automatic indicators, phone-width navigation,
  no file inputs, no horizontal overflow and no observed console errors.
- [ ] Verify the updated deployed mobile view after the user's push.
See `docs/OFFICER_WORKFLOW.md`; acquisition updates remain the team's pipeline.

Resume checkpoint — 10 October 2026:
- [x] Inspect current engineering deliverables and scientific acceptance gaps.
- [x] Re-audit the seven saved compartment 279 labels: zero independent reviewed
  examples, all seven splits unassigned; no labels changed or generated.
- [x] Record the current scope and next evidence gate in `docs/CURRENT_STATUS.md`.
- [x] User confirms deployed officer login works after credential correction.
- [ ] Obtain evidence-supported independent reference review and freeze splits.
- [ ] Verify all deployed dashboard features; login success alone is insufficient.

Vercel full research application:
- [x] Remove automatic landing-only mode; add FastAPI entrypoint/configuration,
  bounded deployable data, server-side officer authentication and temporary state.
- [x] Verify 75 isolated hosted API checks and existing local research checks.
- [x] Verify hosted-mode browser login and saved research map using isolated
  test credentials on localhost; Vercel-mode frontend build passes. This is
  a local simulation, not verification of the deployed Vercel URL.
- [ ] Configure private Vercel environment values and redeploy using the project
  root, then verify the actual Linux/Python 3.12 deployment.
- [ ] Add durable shared uploads/history, centrally revocable sessions and rate
  limits before operational shared use; current new hosted results are temporary.
See [Vercel full-app setup and actual limits](docs/VERCEL_FULL_APP.md).

- [x] Adopt the supplied shield/tree/leaf logo design as a scalable vector across
  landing, login, dashboard and favicon; verify production build and live header.
  Visual evidence: `data/phase5/branding_v1/landing-logo.png` (local, Git-ignored).
- [x] Keep the landing cursor across the application and inside the native login
  modal. Login starts with Select district / Select beat and an empty password;
  selected values are submitted, and all fields reset on reopening. Verified
  local login, dashboard cursor, blank fields and production build; proof:
  `data/phase5/branding_v1/login-custom-cursor.png`.

Local research dashboard — 10 October 2026:
- [x] Add an officer-only research view with real saved proxy map, scope, date,
  coverage, pixel counts, model/dataset version and four actual export links.
- [x] Pin/check saved-result integrity; reject corrupt files and unsupported formats;
  preserve production forest/change approval gates and existing dataset access.
- [x] Pass frontend build and isolated offline API/auth/download checks.
- [x] Verify live login, research navigation, displayed data, map zoom and Fit map.
- [x] Complete drag/keyboard panning, all four browser downloads with byte-level
  checks, refresh/missing/corrupt/recovery, narrow layout and core keyboard checks.
- [x] Fix rejected-session recovery and verify actual browser return to login.
- [x] Complete the updated full-backup restoration/offline acceptance handoff:
  546 files restored; restored API and cold startup passed with external Python
  networking blocked. Final receipts are retained with the acceptance supplement.
See [startup, measured verification and limits](docs/RESEARCH_DASHBOARD.md).

Offline research inference — 10 October 2026:
- [x] Generate a saved December 2025 tree-cover proxy map from our own cloud model,
  plus uncalibrated decision-tree probability values and georeferenced outputs.
- [x] Verify 12,362 usable pixels, class/vote nodata, grid/source/dependency identity,
  offline operation, unchanged originals and the exact saved validation matrix.
- [x] Preserve explicit research scope and false operational approval; production
  forest loader rejects the model. No forest area/change/fire result is produced.
- [x] Display the saved output in a separated local application research view.
See [working map and reproducible inference](docs/RESEARCH_PROXY_MAP.md).

Current handoff — 10 October 2026:
- [x] Close the December exploratory model and disagreement-inspection milestone.
- [x] Retain reproducible source, cloud notebooks, real inputs, model exports,
  evaluation, offline checks, error contexts and measured limitations.
- [ ] Scientific Phase 2: independent reviewed labels and frozen evaluation splits.
- [ ] Scientific Phase 3: independently evaluated forest classifier approved for use.
No additional training or error-case generation is required to close this exploratory
scope. See [handoff and acceptance decision](docs/EXPLORATORY_PHASE_HANDOFF.md).

December proxy error inspection — 10 October 2026:
- [x] Generate nine actual shrub/crop/tree reference disagreements with dated
  image contexts and preserved central-pixel coordinates/provenance.
- [x] Verify 27 embedded views, selection/spacing, source preservation, offline
  generation and zero reviewed labels; inspect three representative figure rows.
- [x] Document unresolved texture, study-edge and mixed-pixel interpretation limits.
- [ ] Independent current land-use/forest reference evidence and evaluated test set.
See [inspection deliverables and limits](docs/PROXY_ERROR_INSPECTION.md).

Exploratory December comparison — 10 October 2026:
- [x] Prepare 4,939 December 2024 training and 6,067 December 2025 validation
  pixels using separated regions and explicitly historical map targets.
- [x] Verify actual date-specific features, targets, calibration/grid provenance,
  offline operation, original records, private embedding and hosted-only guards.
- [x] Prepare a private cloud notebook with the verified small dataset embedded.
- [x] Bind model-export verification to the expected dataset; actual earlier
  artifacts are accepted for their original dataset and rejected for December.
- [x] Receive and preserve the user's completed cloud comparison export; verify
  it belongs to the December experiment before loading either model.
- [x] Reproduce both models' confusion matrices and metrics offline; Random Forest
  F1 0.977588 is historical map agreement, not independent forest accuracy.
- [x] Report class errors: 69/78 shrub and 69/244 crop proxy targets disagreed.
Cloud UI version/runtime remain unverified. Production forest use is unapproved.
See [minimal handoff and reproduction](docs/DECEMBER_WEAK_EXPERIMENT.md).

Phase 2 — calendar-matched observations, 10 October 2026:
- [x] Acquire the bounded December 2024 crop privately in Kaggle CPU; preserve
  scene metadata, product calibration, source attribution and downloaded archive.
- [x] Verify 12 new source files and the unchanged 27-file 2025 source; align the
  December pair on the same 20 m grid with 12,362 common clear pixels (94.37%).
- [x] Check calendar gap, source integrity, offline operation, date/overwrite guards
  and both embedded images in the saved HTML comparison.
- [ ] Review weather/vegetation-cycle comparability and independent forest evidence.
- [x] Run the exploratory calendar-matched weak-reference comparison; verify export.
See [observations, reproducible checks and limits](docs/SAME_SEASON_OBSERVATIONS.md).
This passes the data assessment; it does not complete scientific Phase 2/3 gates.

Exploratory weak-reference experiment, 10 October 2026:
- [x] Prepare verified real-image feature samples with explicitly historical
  WorldCover proxy targets; preserve reference licenses/source hashes and age limits.
- [x] Separate north/April training and south/December validation before extraction,
  with a 200 m excluded strip; no independent test set or current forest truth claimed.
- [x] Fit baseline and Random Forest privately in Kaggle CPU with Internet off;
  successful 19.2-second version 356844511, no local fitting.
- [x] Download and checksum-verify both fitted artifacts; reproduce cloud predictions
  offline and confirm the production forest loader rejects the proxy export.
- [x] Document failed Random Forest transfer and constant-baseline selection; retain
  unapproved status, actual feature diagnostics and original review/training gates.
- [ ] Qualified current reference review and scientifically evaluated forest model.
See [measured exploratory result](docs/WEAK_PROXY_EXPERIMENT.md). This is not a
completed Phase 2/3 forest-classification release.

Phase 2 — mask-based spatial candidates, 10 October 2026:
- [x] Select 14 unlabeled 100 m patches from 16 spatial blocks using only verified
  study/common-clear masks; retain excluded blocks and selection provenance.
- [x] Verify 25 clear pixels per patch, nonoverlap, at least 100 m separation,
  embedded dated views, proposal form and compatibility with the earlier pack.
- [x] Preserve original seven cases/registry and pass offline, mask, geometry,
  spacing, form, source-preservation and overwrite checks.
- [ ] Independent reviewed forest/non-forest references and frozen representative splits.
User confirmed no independent reviewer currently available. More candidate generation
will not close this scientific gate; training remains unapproved.
See [spatial candidates, measured checks and limits](docs/PHASE2_SPATIAL_REVIEW.md).

Phase 2 — offline review form, 10 October 2026:
- [x] Reuse the blind comparison to make a self-contained proposal form for seven
  unchanged cases with 24 saved-image views; originals remain untouched.
- [x] Export reviewer/date/class/confidence/uncertainty and forest-evidence fields;
  retain source provenance, geometry, unassigned splits and false independence.
- [x] Pass offline generation, hypothetical parser cases, unsupported forest,
  provenance/geometry/split/independence changes and overwrite checks.
- [x] Verify actual browser export and Python validation: seven unknown/unassigned
  cases, no independent reviewed labels and no training approval.
- [ ] Obtain evidence-supported human review and assess source independence.
- [ ] Expand representative reference locations/acquisition dates and freeze evaluation splits.
See [review form instructions and scientific limits](docs/PHASE2_REVIEW_FORM.md).

Phase 9 — current research-application engineering checkpoint, 9 October 2026:
- [x] Fresh UI/inference runtime installed from retained local wheels; dependency checks pass.
- [x] Browser login, real maps, comparison, integrity and vegetation controls work with
  external Python connections/DNS denied and same-origin browser resource policy.
- [x] Preserve a bounded release backup covering code/build, current research inputs,
  two LISS-4 reference crops, historical height predictions, unresolved review records,
  synthetic model exports, saved results and runtime wheels; verify isolated restoration.
- [x] Verify corrupted/invalid inputs, trusted-model/scope gates, overwritten-output
  prevention, injected disk-full failures and actual owned-process termination/recovery.
- [x] Publish generated PNG previews atomically; failed/interrupted previews stay unpublished.
- [x] Measure small real-crop inspection plus synthetic inference: 133.82 MiB peak
  working set, 2.222 seconds on the observed laptop; not a full-product benchmark.
- [x] Document startup, fresh installation, backup/restoration and cloud retraining.
- [x] Preserve a checksum-matching backup outside the workspace on E:; E: and C:
  are on the same physical disk, so physical-drive failure is not covered.
- [ ] Re-run release checks with the future independently evaluated real models.
- [ ] Optional disaster-recovery validation: physical power loss, OS-wide Internet
  disconnection and a backup on an existing separate physical device.
This completes the engineering acceptance scope for the current research application,
not scientific model validation or final-product Phase 9 certification.
See [delivery scope, instructions and limitations](docs/PHASE9_DELIVERY.md).

Reliability — interrupted change analysis, 9 October 2026:
- [x] Publish completion markers atomically with six input/output size and SHA-256 records.
- [x] Verify integrity before display/export; preserve incomplete, corrupt and legacy
  artifacts while excluding them from latest completed results.
- [x] Order saved results by completion time rather than preview-cache folder changes.
- [x] Pass four injected interruptions, missing/corrupt/malformed-marker rejection
  and fresh-process recovery; original fixture inputs remain unchanged.
- [x] Pass authenticated change API and existing imagery/UI regressions after the fix.
- [x] Validate owned-process termination and injected disk-full handling.
- [ ] Physical power-loss durability remains unclaimed.
See [recovery behavior and compatibility](docs/CHANGE_RECOVERY.md).

Reliability — fresh offline installation, 9 October 2026:
- [x] Create a clean Python 3.11 environment; install all 22 locked UI packages
  from local wheels with no package index; verify nine historical wheel hashes,
  retain the current 22-wheel inventory and check dependency consistency.
- [x] Restore real compartment 279 inputs into an isolated application with copied
  code/build and fresh database/cache; verify original and registered artifacts.
- [x] Pass ASGI login/logout/access controls, six real maps, analysis, integrity
  checks, two frontend assets and CSV/HTML exports with outbound connections/DNS blocked.
- [x] Start the fresh Uvicorn application on loopback and verify HTTP health/index;
  stop the temporary server without replacing the existing dashboard.
- [x] Check browser operation with application external connections blocked; broader
  release recovery checked. OS Internet was not disabled globally.
See [fresh installation evidence and reproduction](docs/OFFLINE_INSTALL_CHECK.md).

Reliability — compartment 279 imagery recovery, 9 October 2026:
- [x] Preserve a bounded 17-file imagery backup with a separately recorded SHA-256.
- [x] Restore into an isolated folder; verify original archive, geometry and registration.
- [x] Generate all six restored map-layer PNGs with Python network sockets blocked.
- [x] Reject wrong hashes, missing/corrupt/unsafe files, overwrites and interrupted copies;
  preserve live sources. Retain recovery evidence and reproduction instructions.
- [x] Resolve all 22 locked UI dependencies using retained wheels with no package index.
- [x] Complete fresh installation from retained local wheels and application checks.
- [x] Verify browser stored-data operation with external application networking blocked.
- [x] Preserve current labels/references/synthetic models/results and verify release recovery.
- [x] Copy backup outside workspace to E: and verify its hash; physical-disk protection
  still requires existing separate physical storage.
See [imagery recovery instructions](docs/RESEARCH_BACKUP.md). Phase 9 remains in progress.

Phase 5 real compartment 279 observations, 9 October 2026:
- [x] Register 14 bounded dashboard files from the verified 27-file source archive;
  preserve selected geometry, dates, calibration provenance and exact source copies.
- [x] Integrate the real dataset into the library, default map selection, date
  comparison, common coverage, named-band vegetation indicators and boundary display.
- [x] Display the true 20 m analysis grid and explicit seasonal/model limitations.
- [x] Export scene IDs, license links, source hash, dataset/study versions and
  coverage; keep HTML observation table readable.
- [x] Pass offline registration/corruption/false-metadata/overwrite checks,
  final 23-image API regression and browser maps/layers/date/fit/HTML download.
- [ ] Verify this updated real-data view on a mobile viewport; browser override did not apply.
- [ ] Complete independent forest references, actual model training/evaluation
  and same-season change validation; no actual forest accuracy claimed.
See [real-data dashboard handoff](docs/COMPARTMENT_279_DASHBOARD.md).

Phase 5 change-dashboard integration, 9 October 2026:
- [x] Add authenticated saved-comparison execution, immutable run input copies,
  completed-result recovery, six preview layers and four download formats.
- [x] Open the change workspace by default, label synthetic scope, display dates,
  observable coverage and versions; retain monthly illustrations separately.
- [x] Connect comparison, refresh, layer, fit and report controls to actual outputs.
- [x] Fix shared SQLite connection cleanup and the empty activity table on fresh login.
- [x] Pass new API checks and existing regression checks after the fix; build UI.
- [x] Verify browser login/run/layers/fit/refresh and desktop/mobile layouts.
- [ ] Integrate and evaluate real forest model and independently reviewed changes.
- [x] Complete current research-app interruption/recovery, offline installation and
  backup restoration checks; repeat with evaluated real models before final release.
See [dashboard handoff](docs/CHANGE_DASHBOARD.md). Synthetic integration is not
real forest/change validation or a completed operational release.

Phase 4 change-detection engineering, 9 October 2026:
- [x] Implement bounded offline comparison of dated aligned classifications
  and an explicit study mask, with common-valid coverage and hectare exports.
- [x] Enforce model/definition/study/class/scope consistency, chronological dates,
  seasonal review and operational approval for real maps.
- [x] Verify all transitions, no-data exclusion, area arithmetic, stable maps,
  offline processing, invalid inputs, overwrite and partial-output prevention.
- [x] Preserve synthetic fixture, GeoTIFF/JSON/CSV results and reproduction steps.
- [x] Preserve available dated/study metadata in inference exports; repeat inference checks.
- [ ] Evaluate actual forest classifications and same-season changes independently.
- [ ] Connect evaluated changes to the local dashboard.
See [change detection](docs/PHASE4_CHANGE_DETECTION.md). Synthetic checks do not
complete real change validation or establish findings about Joga.

Phase 3 offline inference, 9 October 2026:
- [x] Install separately pinned CPU inference packages from preserved official wheels;
  retain notices/hashes and pass dependency checks. No local fitting performed.
- [x] Implement trusted-model checksum/version/approval checks and bounded crop
  prediction with exact feature order, matching grids, quality mask and no-data.
- [x] Match saved cloud predictions offline on the synthetic fixture; verify
  invalid inputs, scope guards, overwrite and partial-output prevention.
- [x] Recheck real imagery inspector after installation; inputs unchanged.
- [ ] Connect evaluated real model inference to the application after scientific review.
See [offline inference](docs/OFFLINE_MODEL_INFERENCE.md). Real model training and
accuracy remain pending reviewed labels and independent splits.

Phase 3 engineering verification, 9 October 2026:
- [x] Implement cloud-only baseline/Random Forest training with existing
  provenance, grid, coverage and label audits.
- [x] Require qualifying forest evidence and independent date/spatial splits;
  reject current unresolved records before extracting samples.
- [x] Prepare validation-based selection, later test evaluation, error examples,
  model roundtrip checks and checksum/version/preprocessing artifact exports.
- [x] Check metric arithmetic, synthetic extraction/overlap, real-label rejection,
  local training guard and notebook source parity without local model fitting.
- [x] Run private Kaggle synthetic fitting/export check (25.5 s, CPU, Internet off);
  verify seven artifact hashes locally and reject a corrupted model archive.
- [ ] Establish credible labels and freeze independent representative splits.
- [ ] Run real-data cloud fitting, verify exported models and evaluate real errors.
See [training instructions and limits](docs/PHASE3_TRAINING.md). Phase 3 is not
scientifically completed and no model accuracy is claimed.

Phase 2 evidence-review preparation, 9 October 2026:
- [x] Reuse the real three-date comparison to make an offline blind-review pack.
- [x] Hide prior interpretation notes and individual weak-map class hints;
  preserve all original records and export a separate unanswered review template.
- [x] Test metadata/geometry preservation, blank unknown records, embedded views,
  offline operation, original comparison compatibility and overwrite safeguards.
- [ ] Obtain an evidence-supported fresh review; the new template is unanswered,
  not independent truth. Convenience selection and label readiness limits remain.

Phase 2 compartment 279 update, 9 October 2026:
- [x] Register the verified real imagery, exact boundary and unchanged reference
  records at dataset version `compartment-279-4a65d6141daf0a02`.
- [x] Preserve calibration, grids, source licenses, feature order, runtime and
  content hashes; snapshot label records and forest definition for reproducibility.
- [x] Verify seven review footprints against common usable pixel centres.
- [x] Check offline reproducibility, label version/date, outside-grid rejection,
  uncertain/non-independent splits, overwrite prevention and unchanged inputs.
- [ ] Establish credible forest-positive labels and representative independently
  reviewed evaluation evidence; current records contain zero confirmed forest.
- [ ] Freeze actual spatial/date train/validation/test groups before sampling.
- [ ] Acquire suitable same-season observations and reviewed change references.
The imagery/registry portion is complete; Phase 2 supervised-data readiness is not.

Phase 1 compartment 279 update, 9 October 2026:
- [x] Retain pinned lightweight local dependencies; `pip check` passes.
- [x] Add a bounded offline command for the saved 20 m study bundle, reusing
  existing verification/export code and requiring matching selected geometry.
- [x] Export actual per-date/common coverage JSON and CSV; common mask is
  12,338/13,099 pixels (94.1904%). Forest area is not inferred.
- [x] Verify real counts, JSON/CSV outputs, wrong boundary, corrupt raster,
  missing input, overwrite prevention and unchanged source files.
- [x] Recheck the older inspector; maintain instructions and `.gitignore`.
Phase 1 engineering is complete. Next is Phase 2 reviewed labels and frozen
evaluation splits; scientific reference gaps remain documented.

Remaining-requirements review, 9 October 2026:
[exact evidence and registration requirements](docs/PHASE0_REMAINING_REQUIREMENTS.md).
All seven cases audited again, historical height statistics verified, selected
boundary topology rechecked, and original inputs unchanged. A private packet
lists actual review locations and permitted evidence needed. Forest-positive
reference evidence and independent registration remain absent; no labels upgraded.

Latest handoff: [Phase 0 consolidated result](docs/PHASE0_HANDOFF.md), 9 October
2026. Bounded acquisition/inspection and engineering handoff are finished;
scientific forest-reference exit remains unmet. Stop further bulk searching until
it has a specific evidence benefit. Phase 1's existing offline foundation was
rechecked successfully; retain it instead of restarting working code.

Started fresh: 6 October 2026. Current work: return to Phase 0 scientific
feasibility following the hackathon, at the user's request on 7 October 2026.
Phase 1 foundation passes its offline checks; Phase 0 geography/reference gates,
Phase 2 reviewed labels/splits and Phase 5 model integration remain open.
See [restart audit and ordered remaining work](docs/RESTART_AUDIT.md).

Latest decision, 9 October 2026: [Phase 0 current assessment](docs/PHASE0_FEASIBILITY_RESULT.md)
supersedes the older 278-only result. Engineering feasibility passes for the
user-confirmed compartment 279 research polygon. Scientific Phase 0 exit remains
blocked by credible forest-positive reference feasibility; no training readiness
or independent boundary registration is claimed. The targeted NASA download
backlog is resolved. Further label work must seek dated, permitted evidence rather
than fabricate labels or repeatedly download rejected measurements.

Second reference route, 9 October 2026:
- [x] Recheck all 42 original office-file hashes; inspect 279-specific cells in
  three workbooks without changing them. Historical planting/project context
  found; dated patch-level 2025 forest truth not established.
- [x] Save and verify bounded ATL08 V007 catalogue metadata: three 2025 candidates,
  including April 3 and December 10 near the saved imagery dates.
- [x] Submit Earthdata order 2688356423 with spatial trimming enabled and HDF
  selected; preserve actual processing status and screenshot.
- [x] Inspect actual ICESat-2 outcome: three `nodata` warnings, zero subset
  files; preserve workflow text/screenshot and request bounds. No segments exist
  to quality-screen. The forest-reference gate stays unresolved.
Details: [ICESat-2 reference research](docs/ICESAT2_REFERENCE_CHECK.md).

Finer-image reference follow-up, 9 October 2026:
- [x] Check current official source/access conditions; inspect Esri's actual
  permitted-use PDF and exclude the paid Planet program from the INR 0 workflow.
- [x] Prepare a bounded Bhoonidhi search for the selected 279 geometry and 2025
  dates; confirm the official free standard-data policy at 5 m and coarser.
- [x] User completes Bhoonidhi account registration/terms and signs in; verified
  portal account controls.
- [x] Registration and subsequent email activation/sign-in complete. Public MX70
  L2 search displays 13 free
  candidates, including 7 April 2025; catalogue/April metadata preserved.
- [x] Verify local coverage, dates, product size and reuse conditions; acquire
  free April/November products and assess reference feasibility. The assessment
  found that credible forest-positive evidence is still insufficient.
- [x] Download and preserve one April 7 free ZIP: 626,385,051 bytes, matching
  original/project SHA-256; inspect small product metadata (5.8 m native / 5 m
  resampled grid). No full-scene raster processing on the laptop.
- [x] Prepare cloud-only LISS-IV crop notebook; source/guard checks pass.
- [x] Import crop notebook privately in Kaggle and verify Accelerator None;
  final Version 5 (356634805) completes successfully; earlier diagnostic failures
  retained as history. Rounded supplier CRS validated and normalization recorded.
- [x] Retry the interrupted input upload with the preserved .zip.bin; one private
  dataset file is ready and attached, original source checksum retained.
- [x] Preserve the 875,456-byte crop bundle and verify its seven hashes, CRC,
  geometry, grid, bands and counts offline. Candidate nonzero coverage is 58.0576%;
  87,856 all-zero pixels excluded as suspected fill. No cloud/forest labels inferred.
- [x] Review screened patches and inspect the November observation for the
  missing portion; forest-positive reference feasibility remains unmet.
- [x] Compare seven 120 m patches on April/December Sentinel and April LISS-IV;
  preserve three AI-assisted open-water/non-forest interpretations and four unknowns.
  Original review candidates remain unchanged; no independent test truth claimed.
- [x] Preserve November 9 LISS-IV metadata and check actual image corners against
  the saved study grid: predicted coverage 209,356/209,468 (99.9465%). Pixels and
  cloud quality not acquired/validated; compressed download size remains unknown.
- [x] After session refresh, download the exact free November archive: 551,494,580
  bytes; original/project checksums match. Inspect ZIP entries and small metadata;
  full bands stay unprocessed locally. Preserve source_spec.json and archive inventory.
- [x] Prepare November cloud notebook with actual source checksum/date/size;
  shared source guards, notebook compilation and April crop regression checks pass.
- [x] Finish private November dataset upload (one 551.49 MB file); import the
  prepared notebook, attach the exact input, verify Accelerator None and submit
  Version 1 with Save & Run All. Runtime success/output not yet verified.
- [x] November Version 1 (356648963) succeeds in 44.8 seconds. Preserve the
  1,640,588-byte crop; seven hashes/CRC, grid, masks and counts pass offline.
  Exclude 106 all-zero centres; nonzero candidates cover 209,362/209,468 (99.9494%).
  All seven review patches have full nonzero reference coverage; clouds/labels
  are not established by this count.
- [x] Visually inspect all seven November reference patches with dated Sentinel
  context; preserve screenshots, dated notes, three open-water interpretations and
  four unknowns. Three unknowns are wooded-cover candidates; no height evidence is
  invented. Provenance audit passes; original candidate file remains unchanged.
- [ ] Establish credible forest-positive feasibility and independent review;
  cloud/shadow screening beyond visible patch inspection remains unresolved.
- [x] Check ETH 2020 height-map license, exact tile and byte-range access; run a
  private CPU crop (Version 1, 356717456, 31.7 s). Preserve the 39,819-byte export;
  two hashes/CRC, masks/grids and all seven case statistics pass offline checks.
  Altered-report median is rejected. Historical predictions prioritize case 3;
  no labels assigned or 2025 truth inferred. See docs/HISTORICAL_HEIGHT_REFERENCE.md.
Details: [finer-image source check](docs/HIGH_RESOLUTION_REFERENCE_CHECK.md).

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

Historical reference follow-up, 8 October 2026:
- [x] Expand the bounded catalogue to 2019–8 October 2026: 25 L2A/25 L2B
  candidates saved, hashes/counts/intervals and invalid-date guards verified.
- [x] Inspect actual March 2023/May 2024 workflow: two `nodata` warnings,
  zero subset files; preserve screenshots and source status.
- [x] Save bounded Sentinel-2 metadata around two 2020 dates; retain next-page
  limits and keep raster-download and coverage claims false.
- [x] Download and inspect the July 24, 2020 subset: 253,699 bytes, 200 shots,
  129 centres inside the polygon, zero passing the reference-quality screen.
  Both release-2 and release-3 quality flags are zero for all 129 interior shots.
- [x] Download and inspect the January 14, 2020 subset: 277,800 bytes, 188 shots,
  121 centres inside the polygon, all degradation flag 70 and none passing.
  Actual-file, exact-ID, quality-screen and overwrite checks pass. Historical
  measurements were not promoted to 2025 labels.

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
preserved in data/phase2/handoff.json. This historical pipeline remains subject to its unchecked
label/geography/split gates. Current 279 progress and Phase 3 engineering are
recorded at the top of this checklist.

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

### Hosted runtime repair (2026-10-10)

- [x] Diagnose live HTTP 500 from the supplied traceback: Rasterio cannot load
  `libexpat.so.1` in Vercel's function image.
- [x] Add build-time native library packaging, explicit bundle inclusion,
  startup preload and Expat license notice; preserve Windows behavior.
- [x] Verify byte-preserving packaging and missing-library rejection locally.
- [ ] Verify Linux native loading and live login after deploying this repair.

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
# Real-image research change — 10 October 2026

- [x] Compute December 2024/2025 tree-proxy transitions on common clear coverage.
- [x] Preserve actual dates/source/model hashes, nodata and explicit research scope.
- [x] Add officer Estimated change view with both source images and six exports.
- [x] Verify offline reproduction, conservation and corrupt-output rejection.
- [x] Pass frontend build and 89 isolated hosted-mode API checks.
- [x] Prepare bounded deployment data and explicit Vercel bundle inclusion.
- [x] Check actual hosted login; identify missing saved-data deployment failure.
- [x] Push/redeploy and verify production saved observations, real change results and exports.
- [x] Deploy the tested no-store app HTML response patch; Vercel entry-page caching remains provider-controlled.
- [x] Deploy and verify the bundled synthetic comparison patch after a temporary-job image failure.
- [ ] Independently assess forest definition and accuracy; review apparent changes.

See [the deliverable and public-reference evaluation protocol](docs/REAL_IMAGE_CHANGE.md).


Officer dashboard simplification — 10 October 2026:
- [x] Default to yearly forest-change summary; remove synthetic selection from officer navigation.
- [x] Use same-area tree-class percentages and net hectare direction, with explicit increase/decrease colours.
- [x] Use Joga in normal navigation; retain exact mapped-area provenance in expandable details.
- [x] Remove unexplained greenness numbers and repeated banners; retain factual source/coverage details.
- [x] Disable wheel zoom on every Leaflet map; preserve zoom buttons and page scrolling.
- [x] Pass arithmetic checks, frontend build, 112 hosted API checks and local browser verification.
- [ ] Push/redeploy and verify this interface on Vercel.
