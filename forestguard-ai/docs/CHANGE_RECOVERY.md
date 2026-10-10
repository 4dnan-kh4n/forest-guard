# Saved change-result integrity and recovery

Objective: exclude incomplete or altered comparisons and recover completed results
after restarting the application. The local synthetic comparison records file sizes
and SHA-256 hashes for three copied inputs and three analysis outputs. A temporary
completion marker is renamed into place after analysis and checksum creation finish.
Readers verify these files before displaying or exporting saved results.

This detects accidental changes; it is not a signature against someone who can
rewrite both files and their manifest. Latest-result selection uses completion-marker
time so creating an old run's preview does not make it the newest analysis.

Incomplete, corrupted and older runs lacking the new integrity manifest are preserved
but excluded from the latest completed result. Direct access to an altered or legacy
completed run returns HTTP 409: preserve it and run a new comparison. Unpublished
runs return 404. No existing files are deleted or silently assigned new checksums.
The next synthetic comparison creates the new format.

Partial runs are not resumed. A new comparison uses a new directory; unfinished
files remain for inspection. Interruption after publication but before activity
logging retains the completed result, though the activity row can be absent.

## Verification

```powershell
.\.venv\Scripts\python.exe scripts/check_change_recovery.py
```

Measured PASS in isolated state with source fixtures unchanged:

- Interrupt during input copy, after result generation, before marker publication,
  and after publication before activity logging.
- Reject corrupt/missing results and malformed or legacy completion markers.
- Keep the previous intact result available when the latest run is corrupted.
- Preserve completion ordering despite preview-cache writes.
- Recover in a fresh Python process: 64 common observable synthetic pixels;
  synthetic scope retained.

Evidence: `data/phase5/change_recovery_verification.json`. Authenticated API
regression passed six change-layer PNGs and four export formats. Imagery/UI
regression passed 23 image responses and nine invalid-input cases. The local server
on port 8000 runs the updated code. Generated data, SQLite and markers remain ignored
by Git. Source code, instructions and the progress checklist remain trackable.

## Limits and next step

Interruptions were injected in Python; OS kill, power loss and disk-full behavior
remain unverified. Atomic rename prevents a partial completion marker from being
published; it does not promise power-loss durability. These synthetic checks
establish no real forest-change accuracy. Real training/evaluation remains pending.

Next: extend checksum-verified backups to reference imagery, label/review records,
training exports and completed runs, retaining each artifact's real/synthetic scope.
