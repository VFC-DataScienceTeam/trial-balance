# Reports

This folder contains generated reports and outputs from trial balance automation.

## Subfolders

### `validation_reports/`
Data quality and validation reports:
- Data quality scorecards
- Schema validation failures
- Balance check reports (out-of-balance items)
- Missing/invalid account codes
- Duplicate entries
- Timestamp: when validation was run

### `trial_balance_outputs/`
Final trial balance reports for stakeholders:
- Standard trial balance format (account, description, debit, credit, balance)
- Summary by account hierarchy
- Entity-level and consolidated views
- Export formats: Excel, PDF, CSV

### `variance_analysis/`
Period-over-period and budget variance reports:
- Variance from prior period
- Variance from budget/forecast
- Top N variances requiring explanation
- Variance commentary and sign-off tracking

## Naming Convention
`{report_type}_{period}_{entity}_{run_date}.{ext}`

Example: `validation_report_2025-10_EntityA_20251104.xlsx`

## Retention
- Keep reports for audit trail (minimum 7 years for financial data)
- Archive older reports to external storage quarterly
