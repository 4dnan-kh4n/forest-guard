# Deploy the complete current research workspace to Vercel

The old frontend-only deployment intentionally showed a local-login notice.
The new setup exports the same FastAPI application through root `app.py`, builds
React, includes selected saved datasets, and routes `/api/*` to the Python API.
Vercel no longer automatically enables landing-only mode in the Vite build.

## Required settings for the existing Vercel project

1. Commit and push the updated code **and `deployment_data/`**. Keep `data/`,
   `.venv/`, `.env*`, credentials, local databases and model files excluded.
   The selected deployment data is about 34.2 MiB; its 81 original file hashes are
   preserved in `deployment_data/manifest.json`.
2. Vercel → project **Settings → Build and Deployment**: set **Root Directory**
   to `forestguard-ai` if the repository contains that folder, or leave blank if
   `app.py` and `vercel.json` are directly at the repository root.
3. Choose **FastAPI** as the framework. Remove old Vite build/output/install
   overrides. Let `vercel.json` supply the build command; leave Output Directory
   unset. The build command explicitly runs pnpm 10.18.3 through npx, so the
   Python builder's default pnpm cannot reject our version 9 lockfile. It
   installs frontend packages with the existing frozen pnpm lockfile
   and builds `frontend/dist`. Python dependencies and Python 3.12 are configured
   in `pyproject.toml`; no local heavy stack or model training is added.
   The build also copies `libexpat.so.1` from the Linux build image into
   `runtime_libs/`. Root `app.py` loads it before Rasterio, because Vercel's
   function image lacks this native dependency. The generated binary stays out
   of Git; `runtime_libs/EXPAT_LICENSE.txt` preserves its MIT license notice.
4. Delete `VITE_FORESTGUARD_LANDING_ONLY` from Vercel environment settings, or
   set it to `false`. A remaining `true` explicitly requests the old public-only
   page. Do not set `FORESTGUARD_DATA_ROOT` on Vercel; the prepared directory is
   selected automatically. Vercel supplies `VERCEL=1`.
5. Prepare the private officer configuration on your computer:

   ```powershell
   .\.venv\Scripts\python.exe scripts/configure_hosted_officer.py
   ```

   Enter a new password of at least 12 characters and remember it. The tool writes
   `data/deployment/hosted-environment.private.json`, which is Git-ignored. It
   contains a salted password hash and a random session secret, not the plaintext
   password. Do not upload this file or paste its contents into chat.
6. Vercel → **Settings → Environment Variables**: copy the **values** for these
   three keys from that local file into Production (and Preview if used):

   - `FORESTGUARD_OFFICERS`: the full JSON array as one value.
   - `FORESTGUARD_SESSION_SECRET`: the generated secret.
   - `FORESTGUARD_ALLOWED_HOSTS`: `forest-guard-nu.vercel.app`; add any custom
     domain separated by commas. Vercel's deployment/production host variables
     are also accepted. Never use `*` to fix a host error.

7. Redeploy after both code and settings are updated. Sign in with **Harda →
   Joga → your newly chosen password**. The local `joga@123` account remains
   loopback-only; it is not a hosted password fallback.

## What is available

Landing page, officer login/logout, saved map/date comparison, coverage and NDVI,
input integrity checks, CSV/HTML reports, the stored research proxy and its four
exports, monthly simulated illustrations, synthetic change runs/layers/exports,
and bounded ZIP/GeoJSON imports. These are the currently implemented features,
not newly validated forest/fire forecasts. Protected data is served through
authenticated API routes, not a public static data mount.

## Storage and session behavior

Vercel functions use a read-only bundle and temporary writable storage. Bundled
project observations survive restarts/redeployment. New uploads, comparisons,
preview caches and activity records are temporary and may disappear **even
between requests** when a different instance serves the next request. The
dashboard displays this limit; export results immediately. Cloud uploads are
capped at 4 MiB and temporary session workspaces at 64 MiB. Local limits remain
unchanged. Durable shared uploads/history need a separate persistent storage
service; this change does not pretend SQLite in `/tmp` is persistent storage.

Hosted authentication uses individual configured officer IDs, PBKDF2 password
hashes and signed 30-minute HttpOnly/Secure/SameSite cookies. Workspaces are
separated per session. Credentials/session-secret rotation invalidates existing
tokens. Logout clears that browser's cookie; it does not centrally revoke a
copied signed token before its expiry. For operational shared use, add durable
session revocation and login rate limits. Vercel quotas are finite; no unlimited
free compute or permanent free tier is promised. Keep the local offline app and
its backups. No paid service, trial or credit-card-dependent addition is used.

## Verify after redeployment

`/api/health` must return JSON with `operation: "hosted saved data"`. Login must
show blank fields, issue a Secure HttpOnly cookie and open the dashboard. Check
Research map, Map workspace → Analyze/check data, CSV/HTML reports and Run saved
comparison. Log out and confirm `/api/datasets` returns 401. Confirm the hosting
storage notice appears. Private configuration values should never appear in
frontend source, HTML or browser console.

Local verification commands:

```powershell
.\.venv\Scripts\python.exe scripts/prepare_vercel_data.py
.\.venv\Scripts\python.exe scripts/check_hosted_app.py
.\.venv\Scripts\python.exe scripts/check_research_dashboard.py
```

Hosted-mode checks passed 75 requests with external networking blocked, including
bad credentials, forged/expired tokens, HTTPS cookie flags, disallowed hosts,
cross-origin mutations, three datasets and all map layers, analysis/validation,
reports, byte-identical research downloads, comparison exports, imports, session
isolation and a new-empty-instance simulation. Temporary results correctly cease
to exist in the new instance; login and bundled data remain available.
Verification used the existing Windows Python 3.11 runtime, not Vercel's actual
Linux/Python 3.12 function builder. A live deployment is not yet verified.

References: [FastAPI deployment](https://vercel.com/docs/frameworks/backend/fastapi),
[Python runtime and bundle limits](https://vercel.com/docs/functions/runtimes/python),
[temporary function filesystem](https://vercel.com/docs/functions/runtimes).
