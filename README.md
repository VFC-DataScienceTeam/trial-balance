# Trial Balance Automation

Automated trial balance validation, reconciliation, and reporting system following the CRISP-DM framework.

## 📊 Visual Workflow

For a comprehensive visual representation of the automation workflow, see:
- **[Workflow Diagrams](docs/workflow-diagram.md)** - Complete Mermaid flowcharts showing data flow, processing steps, and error handling

## Project Structure (actual)

```
trial-balance/
├── .gitignore
├── .venv/                           # Virtual environment (local)
├── .vscode/                         # VS Code workspace settings
├── config/                          # Configuration files
├── data/
│   ├── raw/
│   │   └── Trial Balance/
│   │       └── 2025/
│   │           └── September/       # Daily TB CSVs and Chart of Accounts
│   ├── processed/                   # Processed outputs (currently empty)
│   └── external/                     # Third-party data sources
├── docs/
│   ├── workflow-diagram.md          # Mermaid diagrams and flowcharts
│   ├── Trail Balance Automation Flowchart.html
│   └── draft/                        # Draft documentation
├── logs/                            # Application logs (created at runtime)
├── models/                          # Model artifacts (if used)
├── notebooks/
│   ├── 01-rd-trial-balance-mvp.ipynb
│   ├── trial_balance_mvp.ipynb
│   └── README.md
├── references/
│   └── README.md                     # Reference data notes
├── reports/
│   ├── trial_balance_outputs/
│   ├── validation_reports/
│   └── variance_analysis/
├── requirements.txt
├── README.md
├── references/                       # Data dictionaries, links
├── reports/                          # Output folders and reports
├── src/
│   ├── data/                         # Data ingestion and loading code
│   ├── features/                     # Feature engineering
│   ├── models/                       # Reconciliation / ML models
│   ├── reconciliation/               # Reconciliation logic
│   ├── reporting/                    # Report generation
│   ├── utils/                        # Helper utilities
│   └── validation/                   # Validation rules and checks
├── tests/                            # Unit and integration tests
```

## Workflow (CRISP-DM Phases)

1. **Business Understanding** → `docs/draft/overview.md`
   - Define objectives, success criteria, stakeholders

2. **Data Understanding** → `notebooks/01_data_exploration/`
   - Profile raw trial balance data
   - Identify data quality issues

3. **Data Preparation** → `src/data/`, `src/validation/`
   - Clean and validate data
   - Apply business rules
   - Check balances (debits = credits)

4. **Modeling** → `src/reconciliation/`, `src/models/`
   - Reconciliation logic
   - Variance analysis
   - Anomaly detection (optional ML)

5. **Evaluation** → `reports/validation_reports/`
   - Validation results
   - Reconciliation sign-off

6. **Deployment** → `src/reporting/`
   - Generate final reports
   - Distribute to stakeholders

See `docs/draft/crisp-dm.md` for detailed phase mapping.

## Quick Start

1. **Place raw data**:
   - Trial balance files → `data/raw/trial_balance_inputs/`
   - Chart of accounts → `data/raw/gl_accounts/`
   - Mapping tables → `data/raw/mapping_tables/`

2. **Configure settings**:
   - Copy `config/config.example.yml` to `config/config.yml`
   - Update paths and validation rules

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run validation**:
   - Start with notebooks in `notebooks/01_data_exploration/`
   - Move production code to `src/`

5. **Generate reports**:
   - Outputs saved to `reports/trial_balance_outputs/`
   - Validation reports in `reports/validation_reports/`

## Key Features

- **Automated validation**: Balance checks, schema validation, business rules
- **Reconciliation**: Period-over-period, inter-company eliminations
- **Variance analysis**: Identify and explain significant variances
- **Audit trail**: Complete lineage from source to report
- **Configurable**: YAML-based configuration for rules and settings

