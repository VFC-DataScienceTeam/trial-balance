# Copilot Instructions for Trial Balance Automation

## Project Overview

**Trial Balance Automation** is a CRISP-DM framework-based data science project that automates trial balance validation, reconciliation, and reporting. The MVP (Minimum Viable Product) is a Jupyter notebook that loads daily trial balance CSVs, consolidates them, creates pivot tables, and identifies mismatched GL accounts.

### Core Purpose
- Load trial balance data from `data/raw/Trial Balance/YYYY/Month/` structure
- Validate GL accounts against COA (Chart of Accounts) mapping
- Export updated account mappings when new accounts are discovered
- Create pivot tables (GL Account × Fund Name) for financial analysis

---

## Architecture & Data Flow

### Data Sources
```
data/raw/Trial Balance/2025/September/
├── Trial Balance/
│   └── *.csv (format: MM-DD-YYYY.csv, e.g., 09-15-2025.csv)
└── Chart of Accounts/
    └── *.csv (single file)
```

### Key Data Structures (in `01-rd-trial-balance-mvp.ipynb`)

1. **trial_balance_data** (dict): Maps date keys (YYYY-MM-DD) to DataFrames from daily CSVs
2. **trial_balance_consolidated** (DataFrame): Union of all daily TB data with Date column added
3. **trial_balance_pivot_table** (DataFrame): Aggregated view with GL Account rows, Fund Name columns, netamt values summed
4. **coa_mapping** (DataFrame): Reference data loaded from `data/references/COA Mapping/` (latest CSV/XLSX)
5. **updated_coa_mapping** (DataFrame): COA mapping with new accounts appended and `Is_New_Account` indicator column

### Reference Data
- **COA Mapping**: `data/references/COA Mapping/` (supports CSV/XLSX, auto-loads latest by modification time)
- **Portfolio Mapping**: `data/references/Portfolio Mapping/` (same loading logic)

---

## Critical Workflows & Commands

### Running the MVP Notebook
```bash
cd notebooks/
jupyter notebook 01-rd-trial-balance-mvp.ipynb
```
Cells execute sequentially (1–30+):
1. **Cells 1–4**: Initialize libraries, logging, imports
2. **Cells 5–8**: Define loading functions (`load_trial_balance_data`, `load_reference_data`)
3. **Cells 9–11**: Execute loaders; separate data into variables
4. **Cells 12–18**: Add date columns, consolidate, create pivot table
5. **Cells 19–27**: Match GL accounts with COA, identify new accounts, export updated mapping

### Logging
- Logs are automatically created in `logs/` with timestamp: `trial_balance_YYYYMMDD_HHMMSS.log`
- Both file and console output (dual handlers configured at cell 4)
- All major steps logged at INFO level; warnings for missing folders/files

### Exporting Updated COA Mapping
- Exported to `data/references/COA Mapping/Chart of Accounts Mapping as of MM.DD.YYYY.xlsx`
- Only exports if new accounts are found (missing_in_coa set is non-empty)
- Includes `Is_New_Account` boolean column for easy identification

---

## Project-Specific Conventions

### Naming & Conventions
- **Date Format in Code**: YYYY-MM-DD (parsed from MM-DD-YYYY filenames)
- **Variable Naming**: Descriptive (e.g., `trial_balance_consolidated` not `tb_cons`)
- **DataFrame Columns**: Original TB CSVs have columns like `accountname`, `level1accountname`, `netamt`
- **File Naming**: Daily TB files must follow `MM-DD-YYYY.csv` (validated; non-compliant files logged as warnings)

### Data Validation Patterns
1. **Folder existence checks**: All loaders validate folder presence before attempting to load
2. **File format support**: CSV and XLSX auto-detection via file suffix (`.csv` → `pd.read_csv`, `.xlsx/.xls` → `pd.read_excel`)
3. **GL Account matching**: Set operations (pivot_gl_accounts, coa_gl_accounts) to identify missing accounts
4. **Timestamp tracking**: Metadata dicts store `load_timestamp`, `year`, `month`, file names for audit trail

### Error Handling
- **Non-existent folders**: Logged as `⚠️ WARNING`, process continues
- **No files in folder**: Warning logged, continue with None or empty dict
- **File format errors**: ValueError caught for date parsing; non-compliant files listed in metadata
- **Multiple files in single-file folders**: First file loaded, warning logged (e.g., Chart of Accounts)

---

## Key Files & Modules

| File | Purpose |
|------|---------|
| `notebooks/01-rd-trial-balance-mvp.ipynb` | **Main MVP script** – all current logic lives here (10 sections) |
| `data/raw/Trial Balance/` | Raw trial balance CSV inputs (year/month/date structure) |
| `data/references/` | COA Mapping & Portfolio Mapping reference tables |
| `docs/workflow-diagram.md` | Mermaid flowcharts documenting the entire process |
| `src/` | Future production code modules (data/, validation/, reconciliation/, reporting/) |
| `logs/` | Auto-generated timestamped log files |

---

## Development Guidelines

### When Adding New Features
1. **Start in the notebook** (`01-rd-trial-balance-mvp.ipynb`), not in `src/`
2. **Use the logger** for all non-trivial operations: `logger.info()`, `logger.warning()`, `logger.error()`
3. **Follow the 10-section structure**: Initialize → Define → Load → Transform → Analyze → Export
4. **Add docstrings** to new functions (see `load_reference_data`, `load_trial_balance_data` for examples)
5. **Validate paths & files** before processing; log results

### When Refactoring to Production
1. Extract functions from notebook and move to `src/data/` (for loading), `src/validation/` (for matching), etc.
2. Create unit tests in `tests/` (not yet established; follow pytest conventions)
3. Update `src/__init__.py` to expose public interfaces
4. Update notebook to import from `src/` instead of inline code

### CRISP-DM Alignment
- **Business Understanding**: See `docs/draft/overview.md`
- **Data Understanding**: Notebook section 4–7 (data profiling, consolidation)
- **Data Preparation**: Sections 5–6 (date column, consolidation)
- **Modeling**: Future (reconciliation, variance analysis)
- **Evaluation**: Future (validation reports in `reports/validation_reports/`)
- **Deployment**: Future (automated reporting in `src/reporting/`)

---

## Common Patterns

### Dynamic Path Resolution
```python
from pathlib import Path
base_path = Path('../data/raw/Trial Balance')
year_folders = sorted((f for f in base_path.iterdir() if f.is_dir()), reverse=True)
latest_year = year_folders[0]  # Finds latest by sort order
```

### Multi-Format File Loading
```python
def load_file(file_path):
    if file_path.suffix.lower() == '.csv':
        return pd.read_csv(file_path)
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
```

### Metadata Tracking
```python
metadata = {
    'load_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'year': '2025',
    'month': 'September',
    'tb_files': [{'filename': '09-15-2025.csv', 'date': '2025-09-15', 'records': 1000}]
}
```

### Logging with Context
```python
logger.info(f"Pivot table created: {shape[0]} GL Accounts × {shape[1]} Funds")
if len(missing_in_coa) > 0:
    logger.warning(f"⚠️ {len(missing_in_coa)} new accounts found")
```

---

## Debugging Tips

1. **Check logs first**: `logs/trial_balance_*.log` contains all execution history with timestamps
2. **Inspect data shapes**: Use `.shape`, `.columns.tolist()`, `.head()` on DataFrames
3. **Validate folder structure**: Use `Path.exists()` and list with `list(path.glob('*.csv'))` 
4. **Print metadata**: All loaders return metadata dict for debugging load decisions
5. **Test date parsing**: Use `datetime.strptime(filename, '%m-%d-%Y')` to validate file names

---

## Known Limitations & Future Work

- **Notebook-based**: All logic currently in single notebook; production refactoring to `src/` is planned
- **Manual COA updates**: New accounts require manual classification (TB Account Name, Account Type, FS Classification)
- **No UI/CLI**: Notebook-only interface; future CLI tool planned
- **Limited validation**: Currently only GL account matching; balance checks (debits=credits) not yet implemented
- **No error recovery**: Script halts on critical errors; idempotency not designed in

---

## References

- **CRISP-DM Mapping**: `docs/draft/crisp-dm.md`
- **Workflow Diagrams**: `docs/workflow-diagram.md` (Mermaid)
- **Data Dictionaries**: `references/README.md`
- **Project Overview**: `docs/draft/overview.md`
