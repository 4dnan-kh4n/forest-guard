# Progress checklist

Started fresh: 6 October 2026. Current phase: 0, in progress.

Only results from this new project count toward its completion gates.

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
Current successful run: scriptVersionId 355668914, private Version 3.
Its outputs are preserved in data/phase0/version3/; all seven file hashes pass
the offline verifier. This crop demonstrates the data pipeline, not forest-model
feasibility. Next: authoritative geographic evidence and representative reviewed
forest/non-forest/unknown examples. The user has no beat boundary or compartment
details at that time. Newly supplied historical records now provide compartment
references and neighboring-site GPS candidates, summarized in the local-only
record review (docs/JOGA_RECORDS_REVIEW.md, excluded from Git). No beat polygon has been
substituted or fabricated.

## Remaining phases

| Phase | Deliverable | Completion evidence | Status |
|---|---|---|---|
| 1 — foundation | Reproducible lightweight local processing command | Runs on stored inputs offline; compatible dependency versions recorded | Pending |
| 2 — imagery and labels | Curated crops, reviewed labels, frozen splits | Coverage/alignment/provenance checked; no spatial or temporal leakage | Pending |
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
