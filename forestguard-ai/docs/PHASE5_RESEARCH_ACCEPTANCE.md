# Phase 5 research-application acceptance — 10 October 2026

The remaining research-dashboard engineering checks are complete. This is the
current local research application acceptance scope, not approval of operational
forest-cover, change or fire findings. Scientific Phase 2/3 gates remain open.

## Verified behavior

- Actual map loading, zoom, Fit map, drag panning and arrow-key panning.
- Refresh, visible unavailable/corrupt-result messages and recovery after restoring
  the isolated test data. Original source files were not altered.
- Four browser-triggered downloads, with every saved GeoTIFF/JSON/HTML byte matching
  its separately verified source hash. Results are in the user's Downloads folder.
- Core keyboard navigation: visible Fit map focus, Enter activation, map arrow keys,
  and page navigation. Named map regions preserve zoom-control accessibility.
- Narrow desktop-window layout: approximately 520 pixels of visible browser content;
  navigation, cards, maps, provenance and all export controls remained reachable.
- Rejected sessions return to login. This regression used expired sessions only
  in the disposable test copy; the actual client helper passed response checks.
- An isolated restored imagery checkout with the updated UI served successfully
  on port 8004 while external Python connections/DNS were denied. Same-origin CSP
  restricted browser resources. Existing maps, analysis, auth and report checks passed.

The restored-copy check used the existing pinned local Python runtime; it did not
perform a new dependency installation. Earlier fresh offline-runtime installation
evidence remains separate. No dependency, hosted endpoint, trial or payment was added.

## Working deliverable and reproducibility

Start `start_ui.ps1`, open `http://127.0.0.1:8000/`, use the existing Harda / Joga /
`joga@123` local account, and choose Research map. The application reads stored
observations/results, provides their dates/coverage/model metadata, and offers the
actual exports. Forest/change readiness remains gated. The default account is for
loopback development; shared-network operation still requires individual accounts.

API and client checks:

```powershell
.venv\Scripts\python.exe scripts/check_research_dashboard.py
```

Run `scripts/check_client_session.cjs` with the existing Node runtime to verify the
actual client API helper without browser/network access. Full UI test results,
download checksums and screenshot evidence are preserved in
`data/phase5/research_dashboard_v1/`. The isolated test project is in
`data/phase5/research_acceptance_v1/project/`; it is not the production workspace.

The full release backup/restoration receipt records exact hashes, files and the
updated source/build. Restore only into a new data-directory checkout, using
`scripts/backup_delivery.py restore` with its separately retained SHA-256.
Preserve the E: copy; that partition shares the laptop's physical disk.

The verified full archive is `data/backups/phase5_research_delivery_v1.zip`
(213,657,441 bytes, 546 files), SHA-256
`02da139334688ac4b472f48b4385bcb06478700b36b27aa7dcabe7c8615e459c`.
It restored into `data/recovery/phase5_research_delivery_v1/`. The restored API
checks passed; cold startup on loopback port 8005 served byte-identical built
assets and the authenticated saved map while external Python networking was
blocked. Exact evidence is `data/phase5/research_dashboard_v1/acceptance_restore.json`.
The immutable archive predates this final receipt/checklist update; retain
`data/backups/phase5_acceptance_supplement_v1.zip` alongside it for final evidence.

## Full Phase 5 gate

The local engineering milestone can close, but the complete operational Phase 5
release cannot: no independently evaluated forest classifier or real forest-change
result exists. The displayed Random Forest output is an explicitly unapproved
historical tree-cover proxy; its F1 is map agreement, not forest accuracy. Existing
change and monthly-history illustrations remain synthetic. Independent references,
frozen evaluation splits and real model/change acceptance must precede promotion.

Physical-device touch testing, exhaustive screen-reader/WCAG testing, OS-wide
Internet disconnection and physical-drive disaster recovery were not performed.
These limits do not become completed results through this checklist.
