# Change dashboard integration — 9 October 2026

The officer workspace now opens Change detection. It runs the tested offline
comparison on the saved synthetic classification fixture, displays the result,
and preserves each run. No real model inference or forest/fire finding is claimed.
The older generated monthly forest/fire chart is under Monthly illustration.

## Open and operate

Start `start_ui.ps1` from the project directory, then open
http://127.0.0.1:8000/ and use the existing local presentation account
(Harda / Joga, password `joga@123`). This remains a loopback-only presentation
account; per-officer authorization is required before shared-network use.

Run saved comparison performs the real comparison code on explicitly fictional
class maps; the numbers are computed, not hardcoded UI cards. Before/after maps
and change/loss/gain/common-coverage layers pan and zoom without online tiles.
Fit maps restores the extent. Refresh saved result recovers the latest completed
run, including after reload. Dates, scope, observable versus study-mask area,
model/study/definition versions and the run identifier are displayed.

CSV, HTML, evidence JSON and the geographic change TIFF download from the result
used by the screen. Each completed run retains copies of its three inputs and
the comparison's output. All are under `data/app/change_runs/change-<id>/`.
Incomplete/failed runs are not exposed as completed results. Failure information
is recorded in the existing SQLite activity log. Database connections now close
explicitly after their transactions, fixing Windows file-handle retention.

The screen explicitly states that real analysis needs reviewed labels, an
independently evaluated model and suitable observations. Synthetic model/class
maps are not applied to real Joga imagery. There is no arbitrary model or path
upload in this workflow. Missing inputs return a useful error rather than invented
results. Restore the fixture from backup or run `scripts/check_change.py`.

## Reproduce checks

With the server running:

```powershell
.\.venv\Scripts\python.exe scripts/check_change_api.py
.\.venv\Scripts\python.exe scripts/check_ui.py
```

These checks sign in/out of the local presentation account and record actual
test activity. They end its sessions; sign in again afterward for browser use.
The new check tests authentication, run execution, persistence, all six map
layers (including exact transparent/visible pixel counts), four export formats,
invalid identifiers/layers/formats, missing and corrupt inputs, and failed-run
non-publication. Direct failure checks use a separate temporary state and leave
the preserved input fixture unchanged.

New API checks pass; result is
`data/phase4/dashboard_api_verification.json`. Existing API regression checks
also pass: 17 image responses, nine invalid-input cases, sample import,
login/logout and vegetation analysis. These are engineering checks, not accuracy.

Production build passed using the existing installed Vite CLI with no downloads:

```powershell
cd frontend
node node_modules/vite/bin/vite.js build
```

This avoids Corepack attempting to discover a package-manager version online.
No package or dependency change was needed for this integration. Backend SQLite
cleanup and both API suites were checked after the fix. A fresh login with only
the sessions table now returns an empty activity list instead of an error. `pip check` and
`git diff --check` pass.

Browser verification covered login into the new default screen, running a new
comparison, all four selectable change layers, fitting maps and refreshing the
saved result, reload recovery and an actual four-row CSV download. All three map images loaded. Desktop (1280 × 900) and mobile
(390 × 844) had no horizontal overflow; mobile buttons remained visible. No
browser error logs were observed. Temporary viewport overrides were reset.
Screenshots and a browser-check record are preserved in
`data/phase5/change_dashboard_v1/`.

## Remaining work

Saved runs now have atomic integrity markers and tested fresh-process recovery;
see [interruption checks and legacy-run behavior](CHANGE_RECOVERY.md).

Real training and independent change evaluation remain blocked by reference
evidence/split readiness. This milestone integrates Phase 4 engineering with the
application; it does not complete the scientific phases or the full Phase 5
release. Real inference, reviewed input registration, broader job/recovery tests,
and full offline/fresh-install/backup restoration still need completion.
Fire and future-loss models remain untrained. Git ignores run inputs/results,
SQLite, screenshots and build output; back these up separately. No commit or push
was made.
