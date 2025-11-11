# CRISP-DM mapping (draft)

This document maps the CRISP-DM phases to repository folders and recommended practices.

1. Business Understanding
   - Artifacts: `docs/draft/` (objectives, success criteria, stakeholders)
   - Keep goals and evaluation metrics here.

2. Data Understanding
   - Artifacts: `notebooks/` for exploration; raw samples in `data/raw/`.
   - Use `src/data` to create reproducible ingestion pipelines.

3. Data Preparation
   - Artifacts: `src/features` (cleaning, transformations), `data/processed/` (exported datasets).
   - Ensure processing scripts are idempotent and parameterized.

4. Modeling
   - Artifacts: `src/models` (training code), `models/` (trained artifacts — gitignored).
   - Keep experiments reproducible (random seeds, config files).

5. Evaluation
   - Artifacts: `reports/` and `notebooks/` showing model validation results.

6. Deployment
   - Artifacts: `src/` packages, `models/` exports, `docs/` for runbooks.

Notes
- Keep `data/raw` immutable and track provenance for every file.
- Use `notebooks/` for narrative analysis; move stable code into `src/`.
- Use `requirements.txt` or `environment.yml` to pin dependencies.
