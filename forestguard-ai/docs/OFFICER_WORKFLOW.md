# Officer workflow

ForestGuard's development/data pipeline acquires imagery, checks provenance,
prepares the confirmed study crop and ships saved observations. Officers select
their authorized district and beat at sign-in; they do not supply satellite ZIPs
or boundary files. New imagery acquisition is not yet an automatic scheduled
service: the retained cloud preprocessing workflow prepares updates.

The officer dashboard opens Forest overview for compartment 279. It uses only
the prepared compartment dataset, automatically requests measured vegetation
indicators from its saved reflectance and masks, and displays those measurements
with dated imagery, usable coverage and downloadable evidence. The Research map
shows the stored experimental prediction with its validation limits. Reports
contain the actual observation dates and provenance. Synthetic development
examples are omitted from officer navigation and dataset selection; original
fixtures and backend engineering checks remain preserved.

Mobile navigation is collapsed behind a named Menu button, exposes its expanded
state and closes after selecting a section. The four sections are Forest overview,
Satellite images, Research map and Reports. Missing prepared data reports a
team-managed restoration issue instead of asking an officer to upload inputs.

## Verification

Local browser login and refresh opened the real compartment observations and
automatically measured 12,338 common usable pixels for both dates. Saved imagery
loaded. At a 390 by 844 viewport, navigation opened and closed correctly, the
document did not exceed viewport width, no file input was present, and no browser
console error was observed. Production frontend build passed. These checks do not
verify the updated deployed website, a physical mobile device, or independent
forest classification accuracy.

Evidence screenshots are in `data/deployment/officer-mobile-overview.png` and
`data/deployment/officer-mobile-navigation.png` (Git-ignored). Existing data is
April/December 2025 imagery; no current imagery, observed deforestation, fire
records or fire forecasts were invented. Deploy the updated frontend code to
apply this workflow to Vercel.
