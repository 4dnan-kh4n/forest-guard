# Current development checkpoint - 10 October 2026

## Working release

The officer dashboard has Forest change, Fire detections, Inspection plan and
Reports. Officers do not upload satellite files. The study area is the user-confirmed
compartment 279 polygon in Joga, not the whole beat.

- Real 2022-2026 imagery, dated previews and four comparisons over common clear pixels.
- Estimated yearly tree-cover direction and hectares; sources and coverage remain inspectable.
- Recent NASA NOAA-20/21 observations with online refresh and stored-data fallback.
- Newly acquired NASA NOAA-20 fire history for 2022-2026, yearly map markers and PDF report.
- Checklist selection, CSV export and links to the relevant annual image.
- Readable PDF annual/fire/observation reports; NASA link opens at the mapped location.
- Synthetic fixtures remain preserved for engineering tests and are absent from officer navigation.

## Measured historical fire records

NASA request 820485 exported a 2,110-byte ZIP with 66 records in the requested box.
Polygon/2 km filtering retains 44 detection centres. Counts are pixels, not incidents.

| Year | Inside mapped polygon | Nearby within 2 km |
| --- | --- | --- |
| 2022 | 0 | 14 |
| 2023 | 0 | 8 |
| 2024 | 0 | 0 |
| 2025 | 0 | 8 |
| 2026 (partial archive) | 3 | 11 |

The 2026 archive may lag recent observations. Zero is not proof that no fire occurred.
Source CSV, download SHA-256, boundary, request dates and report hashes are retained.

## Verification

121 isolated hosted API checks passed with networking blocked, including archived
counts, authenticated PDF attachments, secure cookies, source integrity and fallback.
Annual transition arithmetic, fire parsing/archive rejection, checklist CSV and
frontend build passed. Interrupted-job and disk-full checks passed. Bounded crop/
synthetic-inference resource check: 1.965 seconds, peak process working set 135.37 MiB;
this does not measure browser use or full-scene workloads.

The current Vercel annual and recent-fire PDFs were downloaded and parsed successfully
(four pages and one page). The new fire-history/landing changes are local and need
push/redeployment. The deployable data package has 107 files / 37,921,461 bytes.
An updated backup preserves annual/fire data, deployment data, models, code and
Windows offline wheels; retain its receipt checksum separately.

## Remaining evidence and external steps

1. Push the new changes including deployment_data and verify the archived fire view on Vercel.
2. Credible independent forest/non-forest review and representative frozen evaluation
   splits are still unavailable. Seven existing records are unassigned, with zero
   independently reviewed forest labels. No forest-accuracy claim is justified.
3. Canopy density is not measured by the tree-class percentage. Forest-cover change
   remains a model estimate, not independently confirmed deforestation.
4. Fire-risk and future forest-loss forecasts require suitable outcomes, weather,
   multi-year labels and later-period evaluation. Current data does not establish this.
5. Durable shared audit/acknowledgement storage and centrally revocable/rate-limited
   officer sessions remain prerequisites for operational shared use. Hosted new
   activity is temporary; the local installation and exported artifacts survive offline.
6. Ongoing label review, data refresh and model monitoring are maintenance work,
   not a one-time completed phase.

No new model was fitted, no reviewed labels were fabricated, and no phase was
marked scientifically complete by substituting generated data.
