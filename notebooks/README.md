# Notebooks

Jupyter notebooks for trial balance analysis and automation development.

## Folder Organization

### `01_data_exploration/`
Initial data exploration and profiling:
- Load and inspect raw trial balance files
- Data profiling (nulls, duplicates, distributions)
- Identify data quality issues
- Map source fields to target schema

### `02_validation/`
Validation rule development and testing:
- Balance checks (debits = credits)
- Schema validation
- Referential integrity checks
- Business rule validation

### `03_reconciliation/`
Reconciliation logic and variance analysis:
- Period-over-period reconciliation
- Inter-company elimination logic
- Adjustment entry tracking
- Variance investigation workflows

### `templates/`
Reusable notebook templates

## Notebook Naming Convention
Prefix notebooks with numbers to indicate sequence:
- `00_setup_and_config.ipynb`
- `01_load_and_profile_data.ipynb`
- `02_validate_trial_balance.ipynb`
- `03_reconcile_and_report.ipynb`

## Best Practices
- Include markdown cells explaining objectives and assumptions
- Add metadata cell at top: author, date, purpose
- Move stable/production code from notebooks to `src/`
- Keep notebooks focused on analysis and narrative
- Clear all outputs before committing to git
