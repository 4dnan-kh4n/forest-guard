# Local research map view — 10 October 2026

The officer dashboard now has a **Research map** navigation item. It displays the
saved December 2025 tree-cover proxy without marking the model as an approved
forest classifier or connecting it to real change/fire analysis.

Start with `start_ui.ps1`, open `http://127.0.0.1:8000/`, and use the existing local
Harda / Joga / `joga@123` account. Choose Research map. This remains a loopback
development account; shared-network deployment still needs individual accounts.
The updated local server was started successfully on port 8000.

## Working controls and outputs

The view displays the actual observation date, 94.37% usable coverage, 8,943
tree-cover proxy pixels, 3,419 other-cover proxy pixels and research-only model
status. These are prediction counts, not forest hectares or independent accuracy.
It identifies compartment 279 as a research polygon, not the full Joga beat.

The saved SVG uses the existing Leaflet map library, with zoom, drag/pan and Fit map.
Refresh saved result fetches and rechecks the saved metadata and map. The four
download links export the actual class GeoTIFF, uncalibrated decision-tree class
probability GeoTIFF, evidence JSON and self-contained HTML report. Metadata includes
the model/dataset versions, date, source image and observable pixel counts.
No online basemap, model service, new library or fitting step is needed.

## API and integrity

The existing officer-session middleware protects all new routes:

- `GET /api/research/proxy`: checked metadata or a clear unavailable state.
- `GET /api/research/proxy/image`: the checked saved SVG.
- `GET /api/research/proxy/download/{classes|votes|json|html}`: fixed file whitelist.

The current saved result is intentionally pinned to its externally retained
checksum-manifest SHA-256
`37406a53929df37c0cb09f57e982df8d28d359ae0a60d65622412fb38c93d2af`.
Each core artifact hash is checked before serving, alongside size and scope/approval
guards. Missing results yield a clear status; altered files/manifests yield 503 with
an actionable message. Unknown export formats yield 404. No caller-controlled path
is accepted. Replacing a saved research result requires reviewed source/metadata,
reverification and an explicit update to this pin; unapproved artifacts never become
operational forest models merely by appearing in the folder.

## Verification

```powershell
.venv\Scripts\python.exe scripts/check_research_dashboard.py
```

The isolated check uses temporary SQLite state and blocks outbound Python connects
and DNS. It passes unauthenticated denial, local login, metadata, SVG and all four
download bytes against hashes, attachment headers, missing files, corrupt files,
altered manifest, unsupported format and logout denial. Existing compartment data
remains available; real change readiness remains false. The frontend production
build passed using the existing pinned dependencies.

Live browser verification covered login, Research map navigation, correct displayed
metadata, loaded raster overlay, zoom and Fit map. User interaction interrupted the
remaining browser tests; panning and browser-triggered downloads are not yet
verified. The download API bytes were verified. The verification record and available
screenshots are retained under `data/phase5/research_dashboard_v1/`.
The retained screenshot shows the native viewer of the model-vote export after
user interaction; it is not a dashboard capture or byte-level download proof.

The interactive map container uses a named region so its zoom controls can remain
available to accessibility tools. Full keyboard/mobile accessibility checks remain
for delivery testing. No new scientific accuracy measurement was performed.

`.gitignore` continues to exclude generated data/builds, private artifacts, database
sessions and environments. Source, locks and these instructions remain trackable;
the backup recipe covers saved research data. Preserve the separate handoff backup.
The E: copy shares C:'s physical disk and does not protect against drive failure.
