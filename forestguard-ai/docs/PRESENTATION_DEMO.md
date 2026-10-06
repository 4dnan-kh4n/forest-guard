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
