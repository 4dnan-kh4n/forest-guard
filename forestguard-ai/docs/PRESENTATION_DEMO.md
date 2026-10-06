# Presentation walkthrough

Open http://127.0.0.1:8000 with the local server running. The landing page uses
the supplied PrivatePilot page as the layout/animation reference, with original
ForestGuard content, a trees-and-shield SVG logo and a forest workflow illustration.
All graphics and animations are local SVG/CSS; no downloaded imagery or new dependency.

1. Show the animated hero: satellite scan, quality masking and comparison stages.
   Pause/Play controls work; reduced-motion preferences are respected.
2. Click Officer login. District: Harda. Beat: Joga. Password: `joga@123`.
   The local demo credentials are preset for the presentation.
3. Click Run imagery analysis. The server reads the stored reflectance crop,
   applies valid-coverage masks and calculates NDVI from B08/B04.
4. Inspect Vegetation index, True colour and Common coverage. Enable Compare;
   pan/zoom both dates and select acquisition dates.
5. Run Check dataset, browse/search Datasets, and download CSV/HTML from Reports.
6. Logout returns to the landing page and invalidates the server-side session.

The account is a local presentation account, not production multi-user identity.
Session cookies are HttpOnly/SameSite Strict; tokens are hashed in local SQLite
and expire after eight hours. Dataset APIs and previews require login. Server
remains on 127.0.0.1. No private credentials or outside account login are required.

Analysis is a measured vegetation indicator, not a trained forest classifier.
NDVI is clipped to [-1,1] for the displayed index; NDVI > 0.35 is an illustrative
vegetation-signal threshold, not a forest definition. Synthetic layers are marked.
Real-pilot polygon/model evaluation requirements remain in PROJECT_PLAN.md.

Verification: scripts/check_ui.py covers unauthenticated access rejection, wrong
password rejection, login/session/logout, raster previews, vegetation calculations,
reports and imported inputs. Run it with the server active. Dependency/build and
startup instructions remain in docs/UI_STARTUP.md. Data/sessions/previews/builds
remain ignored by Git; source, lockfiles and these instructions are trackable.

## Five-year forest and fire example

After sign-in the officer dashboard opens directly to **Forest change & fire**.
It presents 60 deterministic monthly example records from Nov 2021 through
Oct 2026. The one-year/five-year switches and CSV export work offline. The
reproducible generator is `scripts/monthly_demo.py`; its JSON output is saved
under ignored `data/demo/forest_fire_history_demo_v1.json`.

The charts show fictional canopy hectares, monthly loss and fire-signal counts
and a seasonal example risk index. The example uses no satellite images, fire
reports, weather or real forest boundary. Values illustrate the report UI only.
It cannot substantiate deforestation or support field action. Current stored
satellite dates can instead be viewed from **Map workspace**; Sentinel-2 is
explained there in plain language as satellite imagery with infrared light.
