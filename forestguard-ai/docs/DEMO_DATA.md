# Synthetic demonstration setup

User authorized dummy/assumed data on 6 October 2026. **Phase 0 demo setup and
Phase 1 local tooling are complete.** Real-pilot validation remains separate.

`data/demo/fixture_v1/` contains three 128 x 128 four-band GeoTIFFs, simulated
forest/non-forest labels, unknown/invalid pixels, masks, previews, metadata,
checksums and `synthetic_demo.zip`. The fictional 1.28 km square metric grid
is not Joga's boundary. Dates are simulated; no downloaded imagery was used.

| Split | Simulated non-forest | Simulated forest | Unknown/excluded inside split |
|---|---:|---:|---:|
| Train | 2,046 | 2,767 | 307 |
| Validation | 1,061 | 1,806 | 205 |
| Test | 1,854 | 2,012 | 230 |

Regions were assigned before sampling, with 160 m gaps and distinct simulated
dates. Class 255 is excluded. These are procedural labels, not field-reviewed
ground truth. Any resulting model score measures synthetic-test performance.

From the project root, choose a fresh output directory:

```powershell
.\.venv\Scripts\python.exe scripts/make_demo_data.py --output data/demo/my_fixture --seed 42
.\.venv\Scripts\python.exe scripts/check_demo_data.py data/demo/my_fixture
```

Twenty hashes, ZIP CRCs, saved pixels/grids, class presence, split separation,
deterministic regeneration on the tested runtime and overwrite protection passed.
Saved result: `data/demo/fixture_v1/verification.json`. No additional dependencies
or model training were needed. Heavy training remains remote.

Metadata marks `data_kind=synthetic`, `demo_training_eligible=true`,
`real_forest_training_eligible=false`, `real_pilot_validation=false`.
Real sources, reviewed-label counts and real validation gates were not changed.
Generated artifacts stay ignored under /data/ and need separate backups.

For a later Phase 3 demo, use only class 0/1 inside assigned splits and preserve
the synthetic role, seed, preprocessing, band order and class mapping with exports.
