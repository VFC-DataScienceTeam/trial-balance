# Report Catalog - Trial Balance Automation

This document provides a comprehensive catalog of all available reports in the Trial Balance Automation system.

---

## Active Reports

### 1. Trial Balance MVP

**ID:** `trial_balance_mvp`  
**Notebook:** `01-rd-trial-balance-mvp.ipynb`  
**Category:** Trial Balance  
**Status:** ✅ Active  

**Description:**  
Loads daily trial balance CSVs from a selected month, consolidates data, creates pivot tables (GL Account × Fund), validates GL accounts against the Chart of Accounts mapping, identifies new accounts, and exports comprehensive Excel reports with financial statements and segmented summaries.

**Schedule:** Daily  

**Parameters:**
- `year` (default: auto) - Year to process
- `month` (default: auto) - Month to process
- `input_location` (default: shared_drive) - Data source location
- `output_location` (default: shared_drive) - Output destination

**Dependencies:** None

**Inputs Required:**
- Trial Balance CSVs in format `MM-DD-YYYY.csv`
- Chart of Accounts CSV

**Outputs:**
1. **Trial_Balance.xlsx** - Complete financial report with:
   - 5 main consolidation sheets
   - 16 fund-specific sheets
   - Pivot tables (GL Account × Fund)
   
2. **Trial Balance Monthly.xlsx** - Segmented summary report with:
   - 16 fund-specific sheets
   - Monthly aggregations

3. **Chart of Accounts Mapping as of {date}.xlsx** - Updated COA mapping with:
   - New accounts flagged with `Is_New_Account` column
   - All existing accounts preserved

**Execution Time:** 1-3 minutes

**Location:** `data/processed/Trail Balance/{year}/`

**Example Usage:**
```python
from src.orchestration.notebook_executor import NotebookExecutor

executor = NotebookExecutor()
output = executor.execute_report(
    'trial_balance_mvp',
    parameters={
        'year': '2025',
        'month': 'September',
        'input_location': 'shared_drive',
        'output_location': 'shared_drive'
    }
)
```

---

### 2. Monthly Month-End Data Consolidation

**ID:** `monthly_consolidation`  
**Notebook:** `monthly_month_end_data_conso.ipynb`  
**Category:** Consolidation  
**Status:** ✅ Active  

**Description:**  
Loads all daily trial balance files for a specified month, consolidates data into a single DataFrame, extracts unique account combinations, adds monthly tracking columns, and exports comprehensive Excel reports with summary statistics.

**Schedule:** Monthly  

**Parameters:**
- `year` (default: auto) - Year to process
- `month` (default: auto) - Month to process

**Dependencies:**
- `trial_balance_mvp` - Requires trial balance data to be processed first

**Inputs Required:**
- Trial Balance CSVs for entire month (all days)

**Outputs:**
1. **Monthly_Consolidation_{month}_{year}.xlsx** - Contains 3 sheets:
   - **Summary** - Processing metadata and statistics
   - **Unique Accounts** - Unique account combinations with:
     - Account details (accountname, level1accountname, etc.)
     - Month and Year columns
     - Record count for each combination
   - **Consolidated Data** - All daily data combined with:
     - Date column (YYYY-MM-DD format)
     - Month and Year columns
     - All original trial balance columns

**Execution Time:** 1-2 minutes

**Location:** `data/processed/Consolidation/{year}/`

**Example Usage:**
```python
executor = NotebookExecutor()
output = executor.execute_report(
    'monthly_consolidation',
    parameters={
        'year': '2025',
        'month': 'October'
    }
)
```

**Key Features:**
- Automatically loads all daily files using DataLoader
- Parses dates from filenames (MM-DD-YYYY format)
- Adds monthly metadata columns
- Includes summary statistics:
  - Number of daily files processed
  - Date range (start/end)
  - Total records
  - Unique account combinations

---

## Planned Reports

### 3. Variance Analysis Report

**ID:** `variance_analysis`  
**Notebook:** `02-variance-analysis.ipynb`  
**Category:** Analysis  
**Status:** 📋 Planned  

**Description:**  
Analyzes variances between periods, identifies significant changes in account balances, highlights trends, and generates detailed variance reports with explanations and drill-down capabilities.

**Schedule:** Monthly  

**Parameters:**
- `year` (default: auto) - Current year
- `month` (default: auto) - Current month
- `comparison_months` (default: 2) - Number of months to compare
- `input_location` (default: shared_drive)
- `output_location` (default: shared_drive)

**Dependencies:**
- `monthly_consolidation` - Requires consolidated monthly data

**Inputs Required:**
- Trial Balance data for current and comparison periods
- Historical monthly consolidations

**Outputs:**
1. **Variance_Analysis_{month}_vs_{comparison}.xlsx**
   - Period-over-period variance calculations
   - Percentage changes
   - Significant variance highlights
   - Trend analysis

**Execution Time:** 2-4 minutes (estimated)

**Location:** `reports/variance_analysis/{year}/`

**Planned Features:**
- Month-over-month comparison
- Year-over-year comparison
- Variance thresholds and alerting
- Drill-down to account level
- Visualization-ready data export

---

### 4. Balance Validation Report

**ID:** `balance_validation`  
**Notebook:** `03-balance-validation.ipynb`  
**Category:** Validation  
**Status:** 📋 Planned  

**Description:**  
Validates that debits equal credits for each fund, checks account balance consistency across periods, identifies out-of-balance conditions, and generates validation reports with reconciliation details and exceptions.

**Schedule:** Daily  

**Parameters:**
- `year` (default: auto)
- `month` (default: auto)
- `tolerance` (default: 0.01) - Allowable rounding difference
- `input_location` (default: shared_drive)
- `output_location` (default: shared_drive)

**Dependencies:**
- `trial_balance_mvp`

**Inputs Required:**
- Trial Balance CSVs for selected period

**Outputs:**
1. **Balance_Validation_{date}.xlsx**
   - Debit/credit balance checks by fund
   - Out-of-balance exceptions
   - Reconciliation details
   - Suggested corrections

**Execution Time:** 1-2 minutes (estimated)

**Location:** `reports/validation_reports/{year}/`

**Planned Features:**
- Automated balance equation validation
- Fund-level balance checks
- Inter-fund validation
- Historical balance consistency checks
- Exception reporting with severity levels

---

### 5. Reconciliation Report

**ID:** `reconciliation`  
**Notebook:** `04-reconciliation.ipynb`  
**Category:** Reconciliation  
**Status:** 📋 Planned  

**Description:**  
Performs inter-company reconciliation, eliminates duplicate entries, matches transactions across funds, identifies reconciliation differences, and generates comprehensive reconciliation reports.

**Schedule:** Monthly  

**Parameters:**
- `year` (default: auto)
- `month` (default: auto)
- `input_location` (default: shared_drive)
- `output_location` (default: shared_drive)

**Dependencies:**
- `trial_balance_mvp`
- `balance_validation`

**Inputs Required:**
- Trial Balance data
- Inter-company transaction mapping

**Outputs:**
1. **Reconciliation_{date}.xlsx**
   - Inter-company eliminations
   - Matched transactions
   - Unmatched/unreconciled items
   - Reconciliation summary by fund

**Execution Time:** 3-5 minutes (estimated)

**Location:** `reports/reconciliation/{year}/`

**Planned Features:**
- Automated inter-company matching
- Duplicate elimination
- Cross-fund transaction validation
- Reconciliation exceptions and alerts
- Audit trail

---

## Report Dependencies

```
┌─────────────────────────┐
│  trial_balance_mvp      │  (No dependencies)
│  - Daily TB processing  │
└───────────┬─────────────┘
            │
            ├─────────────────────────────────┐
            │                                 │
            ↓                                 ↓
┌────────────────────────┐      ┌──────────────────────┐
│ monthly_consolidation  │      │ balance_validation   │
│ - Monthly aggregation  │      │ - Daily validation   │
└───────────┬────────────┘      └──────────┬───────────┘
            │                               │
            ↓                               │
┌────────────────────────┐                 │
│  variance_analysis     │                 │
│  - Period comparison   │                 │
└────────────────────────┘                 │
                                           │
                                           ↓
                              ┌────────────────────────┐
                              │   reconciliation       │
                              │   - Inter-company      │
                              └────────────────────────┘
```

**Execution Order for Full Suite:**
1. `trial_balance_mvp` → Daily foundation
2. `balance_validation` → Validate daily data
3. `monthly_consolidation` → Aggregate month data
4. `variance_analysis` → Analyze trends
5. `reconciliation` → Final reconciliation

---

## Report Categories

### Trial Balance
Processing and transformation of raw trial balance data.

**Reports:**
- Trial Balance MVP

**Purpose:**
- Daily data ingestion
- Data validation
- Pivot table generation
- COA mapping validation

---

### Consolidation
Aggregation and consolidation of data across time periods.

**Reports:**
- Monthly Month-End Data Consolidation

**Purpose:**
- Monthly aggregation
- Unique record extraction
- Period tracking
- Summary statistics

---

### Analysis
Analytical reports for trend analysis and variance detection.

**Reports:**
- Variance Analysis Report (planned)

**Purpose:**
- Period-over-period comparison
- Trend identification
- Variance explanation
- Historical analysis

---

### Validation
Data quality checks and balance validation.

**Reports:**
- Balance Validation Report (planned)

**Purpose:**
- Debit/credit validation
- Balance equation checks
- Data quality assurance
- Exception reporting

---

### Reconciliation
Inter-company and cross-fund reconciliation.

**Reports:**
- Reconciliation Report (planned)

**Purpose:**
- Inter-company elimination
- Transaction matching
- Duplicate detection
- Reconciliation tracking

---

## Usage Examples

### Execute Single Report

```python
from src.orchestration.notebook_executor import NotebookExecutor

executor = NotebookExecutor()

# Execute Trial Balance MVP
output = executor.execute_report(
    'trial_balance_mvp',
    parameters={
        'year': '2025',
        'month': 'September',
        'input_location': 'shared_drive',
        'output_location': 'shared_drive'
    }
)

print(f"Report completed: {output}")
```

### Execute Batch Reports

```python
# Execute full month-end suite
results = executor.execute_batch([
    'trial_balance_mvp',
    'monthly_consolidation',
    'variance_analysis'
], parameters={
    'year': '2025',
    'month': 'September'
})

# Check results
for report_id, output_path in results.items():
    print(f"✅ {report_id}: {output_path}")
```

### Execute by Category

```python
# Execute all consolidation reports
consolidation_reports = executor.list_reports(category='consolidation', status='active')
report_ids = [r['id'] for r in consolidation_reports]

results = executor.execute_batch(
    report_ids,
    parameters={'year': '2025', 'month': 'September'}
)
```

---

## Report Status Meanings

| Status | Icon | Description |
|--------|------|-------------|
| Active | ✅ | Report is production-ready and can be executed |
| Planned | 📋 | Report is planned but not yet implemented |
| Development | 🔄 | Report is under active development |
| Deprecated | ⚠️ | Report is deprecated and should not be used |
| Archived | 📦 | Report is archived for historical reference |

---

## Adding New Reports

See [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) for detailed instructions on:
- Creating new report notebooks
- Registering reports in the registry
- Testing and deployment
- Best practices

---

## Support and Maintenance

### Report Owners

| Report | Owner | Contact |
|--------|-------|---------|
| Trial Balance MVP | Data Science Team | [team-email] |
| Monthly Consolidation | Data Science Team | [team-email] |
| Variance Analysis | TBD | TBD |
| Balance Validation | TBD | TBD |
| Reconciliation | TBD | TBD |

### Maintenance Schedule

- **Monthly Review:** Check execution logs and success rates
- **Quarterly Updates:** Review and update report logic
- **Annual Audit:** Comprehensive review of all reports

---

## Execution History

View execution history via:

```python
executor = NotebookExecutor()

# View all executions
history = executor.get_execution_history()

# View specific report history
tb_history = executor.get_execution_history('trial_balance_mvp')

# Get statistics
stats = executor.get_execution_stats()
print(f"Success rate: {stats['success_rate']:.1%}")
```

---

## Related Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) - How to create new reports
- [README.md](../README.md) - User guide and getting started
- [workflow-diagram.md](workflow-diagram.md) - Process flowcharts
