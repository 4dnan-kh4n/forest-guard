# Project working rules

- Before starting a new phase, tell the user its objective, inputs, processing,
  outputs and verification. Keep PROJECT_PLAN.md current.
- Review and maintain .gitignore during every phase and before its handoff.
  Cover new secrets, downloaded data, model artifacts, local databases, private
  reference extracts, caches, dependencies and generated exports.
- Keep code, dependency lockfiles, safe configuration templates, source notebooks,
  reproducible instructions and non-sensitive evaluation summaries trackable.
  Do not blanket-ignore JSON, CSV, Markdown or notebooks.
- Preserve excluded datasets/models locally for offline operation and backups.
  Ignoring an artifact is not permission to delete it.
- Review notebook outputs and staged files for sensitive material before a push.
  The user will push after each phase; do not commit or push without a request.
- Keep the INR 0 budget, cloud-heavy processing and offline stored-data operation
  requirements. Do not fabricate boundaries, labels, accuracy or completed phases.
