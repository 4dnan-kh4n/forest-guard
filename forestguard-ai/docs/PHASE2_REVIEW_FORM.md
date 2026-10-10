# Offline reference-review proposals — 10 October 2026

The existing blind comparison now has a separate offline form. It reuses the
seven unchanged footprints and 24 embedded previews from the real April,
November and December 2025 observations. All initial classes remain unknown.
The previous comparison, registry and labels are preserved.

## Use the form

Open `data/labels/compartment_279_review_form_v1/review.html` in a browser. It is
self-contained and needs no Internet. A local preview is available at
`http://127.0.0.1:8002/review.html` while its temporary local server runs.

1. Inspect each numbered patch and its surrounding stand across the saved dates.
2. Enter the actual reviewer identifier and review date. Check a case only after
   reviewing it; unchecked cases export unchanged.
3. Record the proposed class, confidence, land-use origin and evidence/uncertainty.
   Use unknown where height, canopy or land use cannot be established.
4. Forest proposals need evidence-supported canopy above 10%, stand extent above
   0.5 ha, a cited height/height-potential assessment above 5 m, and forest-use
   evidence. Crops, agricultural orchards and scrub are excluded. Do not enter
   invented numeric estimates simply to pass the form.
5. Download proposed labels, then validate the downloaded file:

```powershell
.\.venv\Scripts\python.exe scripts/review_labels.py validate "C:\Users\mak22\Downloads\compartment_279_review_proposals.geojson"
```

The validator checks metadata and recorded criteria, not the truth of evidence
citations. It rejects changes to geometry, source/date, case IDs, study version,
independence or splits. The download is a proposal; it does not replace labels in
the registry, set independent truth, freeze splits or authorize training.
No prohibited field photos are requested. Permitted dated inventory records or
qualified interpretation of sufficiently informative reference imagery can
support a later review; these satellite images alone may not establish tree height.

## Reproduce and verify

```powershell
.\.venv\Scripts\python.exe scripts/check_review_form.py
.\.venv\Scripts\python.exe scripts/review_labels.py build data/labels/a_new_review_form_folder
```

The builder refuses existing folders. Checks passed for blank export, hypothetical
parser cases, unsupported forest proposals, provenance/geometry changes, independence
and split changes, offline generation and overwrite protection. Hypothetical test
records are kept in memory and temporary folders; they are not research labels.
The browser's actual blank download passed validation with seven unknown,
unassigned cases and zero independent reviewed examples.

Evidence: `data/phase2/review_form_verification.json`, with browser screenshot and
export verification under `data/phase2/review_form_browser/`. Generated forms and
review data remain ignored by Git. The Phase 9 v2 backup predates this addition;
preserve this new folder alongside it rather than modifying that archived checkpoint.

## Next scientific gate

A person must assess the permitted evidence and record their proposed interpretations.
Then assess source/reviewer independence separately and expand beyond these
convenience-selected patches to representative review locations. Freeze location
and date splits only when credible references exist. The current strict date-split
policy requires more than the two available Sentinel acquisition dates for three
fully separated groups. These seven cases do not constitute an independent test set.
Phase 2 label readiness and Phase 0's forest-positive reference gate remain open.
