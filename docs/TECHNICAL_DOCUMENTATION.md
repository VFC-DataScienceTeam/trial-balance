# Trial Balance Automation - Technical Documentation

**Version:** 1.0  
**Last Updated:** November 21, 2025  
**Project:** Trial Balance Data Processing & Reporting  
**Framework:** CRISP-DM

---

## Table of Contents

1. [Project Structure](#project-structure)
2. [Data Inventory](#data-inventory)
3. [Data Flow & Processing Pipeline](#data-flow--processing-pipeline)
4. [DataFrame Transformations](#dataframe-transformations)
5. [Functions Reference](#functions-reference)
6. [Execution Workflow](#execution-workflow)
7. [Reproducibility Guide](#reproducibility-guide)

---

## Project Structure

### Directory Layout

```
trial-balance/
├── .venv/                          # Virtual environment (Python 3.12.2)
├── config/
│   └── run_config.json             # GUI-generated configuration (Year, Month, data_path, output_base_path)
├── data/
│   ├── raw/
│   │   └── Trial Balance/
│   │       └── {YEAR}/             # e.g., 2025
│   │           └── {MONTH}/        # e.g., September
│   │               ├── Trial Balance/
│   │               │   └── *.csv   # Daily TB files: MM-DD-YYYY.csv
│   │               └── Chart of Accounts/
│   │                   └── *.csv   # COA reference file
│   ├── processed/
│   │   └── Trail Balance/
│   │       └── {YEAR}/             # e.g., 2025
│   │           ├── Trial Balance Monthly.xlsx  # Segmented report
│   │           └── Trial_Balance.xlsx          # Full financial report
│   ├── references/
│   │   ├── COA Mapping/
│   │   │   └── Chart of Accounts Mapping as of MM.DD.YYYY.xlsx
│   │   └── Portfolio Mapping/
│   │       └── Portfolio Mapping.xlsx
│   └── external/                   # Third-party data (not used in MVP)
├── logs/
│   └── trial_balance_YYYYMMDD_HHMMSS.log
├── notebooks/
│   ├── 01-rd-trial-balance-mvp.ipynb  # Main processing notebook (101 cells)
│   └── executed_trial_balance_reports/
│       └── trial_balance_report_YYYYMMDD_HHMMSS.ipynb
├── src/
│   └── gui/
│       ├── __init__.py
│       └── trial_balance_app.py    # Tkinter GUI with input/output location selectors & connection monitoring
├── scripts/
│   └── launchers/
│       ├── setup_env_trial_balance.bat  # Environment setup
│       └── README.md
├── launch_gui.bat                  # Main application launcher
├── requirements.txt                # Python dependencies
└── *.md                           # Documentation files
```

---

## Data Inventory

### Input Data Sources

#### 1. Trial Balance CSVs (Daily)

**Location:** `data/raw/Trial Balance/{YEAR}/{MONTH}/Trial Balance/`

**File Naming:** `MM-DD-YYYY.csv` (e.g., `09-01-2025.csv`)

**Expected Columns:**
- `accountname` (str): GL account name
- `accountnumber` (str): GL account code
- `level1accountname` (str): Fund/Portfolio identifier
- `netamt` (float): Net amount (debits - credits)
- Additional columns vary by source system

**Example Records:** ~1,300 rows per file (varies by day)

**Load Pattern:** All CSV files in month folder are loaded as separate DataFrames

#### 2. Chart of Accounts (COA)

**Location:** `data/raw/Trial Balance/{YEAR}/{MONTH}/Chart of Accounts/`

**File Naming:** `RD - Chart of Accounts.csv` (or any `.csv` file)

**Expected Columns:**
- `accountname` (str): GL account name
- `accountnumber` (str): GL account code
- Additional metadata columns

**Load Pattern:** First CSV file found in folder is loaded

#### 3. COA Mapping (Reference)

**Location:** `data/references/COA Mapping/`

**File Naming:** `Chart of Accounts Mapping as of MM.DD.YYYY.xlsx` (dated files)

**Expected Columns:**
- `TB Account Name` (str): Account name from trial balance
- `Account Type` (str): Classification (Asset, Liability, Equity, etc.)
- `FS Classification` (str): Financial statement category
- `Is_New_Account` (bool): Flag for newly discovered accounts

**Load Pattern:** Latest file by modification time is loaded

#### 4. Portfolio Mapping (Reference)

**Location:** `data/references/Portfolio Mapping/`

**File Naming:** `Portfolio Mapping.xlsx` (or similar)

**Expected Columns:**
- `Fund_Code` (str): Portfolio/Fund identifier (e.g., 'PEMI', 'BSP')
- `level1accountname` (str): Fund full name
- Additional fund metadata

**Load Pattern:** Latest file by modification time is loaded

---

## Data Flow & Processing Pipeline

### High-Level Pipeline

```
[User Selects Year/Month in GUI]
        ↓
[GUI writes config/run_config.json]
        ↓
[Papermill executes notebook]
        ↓
[Cell 13: Load Trial Balance Data] → trial_balance_data (dict)
        ↓
[Cell 19: Load Reference Data] → coa_mapping, portfolio_mapping
        ↓
[Cell 29: Consolidate TB Data] → trial_balance_consolidated (DataFrame)
        ↓
[Cell 32: Create Pivot Table] → trial_balance_pivot_table (DataFrame)
        ↓
[Cell 37: Merge with COA Mapping] → tb_fs_df (DataFrame)
        ↓
[Cell 45: Update COA Mapping] → Export updated mapping if new accounts found
        ↓
[Cell 60: Create Segmented DataFrames] → segmented_results (dict)
        ↓
[Cell 91: Define export_financial_report()] 
[Cell 93: Call export] → Trial_Balance.xlsx (21 sheets)
        ↓
[Cell 96: Define export_segmented_summary()]
[Cell 97: Call export] → Trial Balance Monthly.xlsx (16 sheets)
        ↓
[Reports saved to user-selected location:]
  • Shared Drive: X:\Trail Balance\data\processed\Trail Balance\{YEAR}\
  • Local Storage: {project_root}\data\processed\Trail Balance\{YEAR}\
        ↓
[Reports displayed in GUI]
```

### Detailed Cell Execution Flow

#### **Phase 1: Initialization (Cells 1-12)**

| Cell | Type | Purpose | Output Variables |
|------|------|---------|------------------|
| 4 | Code | Import libraries | pandas, numpy, os, datetime, logging, etc. |
| 6 | Code | Setup logging | logger, log_path |
| 8 | Code | Deprecated parameters | N/A |
| 12 | Code | Define `load_reference_data()` | Function definition |

#### **Phase 2: Data Loading (Cells 13-19)**

| Cell | Type | Purpose | Key Variables Created |
|------|------|---------|----------------------|
| 13 | Code | Load trial balance & COA from selected folder | `data` (dict), `trial_balance_data` (dict), `chart_of_accounts` (DataFrame) |
| 16-18 | Code | DEPRECATED (old UI) | N/A |
| 19 | Code | Load reference data | `reference_data` (dict), `coa_mapping` (DataFrame), `portfolio_mapping` (DataFrame) |

**Critical Variable Extraction (Cell 13):**
```python
# Extract to expected variable names
trial_balance_data = data['trial_balance']
chart_of_accounts = data['chart_of_accounts']
```

**Critical Variable Extraction (Cell 19):**
```python
# Extract to expected variable names
coa_mapping = reference_data['coa_mapping']
portfolio_mapping = reference_data['portfolio_mapping']
```

#### **Phase 3: Data Consolidation (Cells 24-34)**

| Cell | Purpose | Input | Output |
|------|---------|-------|--------|
| 24 | Extract dates from trial_balance_data | `trial_balance_data` (dict) | `dates` (list) |
| 26 | Add Date column to each DataFrame | `trial_balance_data` | Modified DataFrames with 'Date' column |
| 29 | Consolidate all daily TBs into single DF | `trial_balance_data` | `trial_balance_consolidated` (40,162 rows) |
| 32 | Create pivot table (GL Account × Fund Name) | `trial_balance_consolidated` | `trial_balance_pivot_table` (261 rows) |
| 34 | Display summary statistics | `trial_balance_pivot_table` | Console output |

#### **Phase 4: COA Mapping & Validation (Cells 37-50)**

| Cell | Purpose | Input | Output |
|------|---------|-------|--------|
| 37 | Merge TB pivot with COA mapping | `trial_balance_pivot_table`, `coa_mapping` | `tb_fs_df` (63 rows) |
| 40 | Identify new GL accounts | `trial_balance_pivot_table`, `coa_mapping` | `missing_in_coa` (set) |
| 42 | Display missing accounts | `missing_in_coa` | Console output |
| 45 | Define `update_coa_mapping_and_save()` | N/A | Function definition |
| 46 | Call update function | `coa_mapping`, `missing_in_coa` | Updated COA file (if new accounts found) |

#### **Phase 5: Segmentation by Fund (Cells 52-72)**

| Cell | Purpose | Input | Output |
|------|---------|-------|--------|
| 52 | Define segmentation function | N/A | `create_segmented_dfs()` function |
| 54 | Prepare portfolio mapping dict | `portfolio_mapping` | `portfolio_mapping_dict` |
| 56 | Define reporting dates function | N/A | `get_latest_reporting_dates()` function |
| 60 | Create segmented DataFrames | `tb_fs_df`, `portfolio_mapping_dict` | `segmented_results` (dict, 16 funds) |
| 62 | Get latest reporting dates | `trial_balance_consolidated` | `latest_reporting_dates_structured`, `latest_reporting_dates_flat` |
| 72 | Validate segmented data | `segmented_results` | Console output |

#### **Phase 6: Export Reports (Cells 91-97)**

| Cell | Purpose | Input | Output |
|------|---------|-------|--------|
| 91 | Define `export_financial_report()` | N/A | Function definition |
| 93 | Export full financial report | `main_dfs`, `segmented_results`, `portfolio_mapping` | `Trial_Balance.xlsx` (4.5 MB, 21 sheets) |
| 96 | Define `export_segmented_summary()` | N/A | Function definition |
| 97 | Export segmented summary | `segmented_results`, `portfolio_mapping` | `Trial Balance Monthly.xlsx` (33 KB, 16 sheets) |

---

## DataFrame Transformations

### 1. trial_balance_data (dict → dict of DataFrames)

**Source:** Cell 13  
**Structure:** `{'YYYY-MM-DD': DataFrame, ...}`

**Example:**
```python
trial_balance_data = {
    '2025-09-01': DataFrame(1300 rows × 15 cols),
    '2025-09-02': DataFrame(1312 rows × 15 cols),
    ...
    '2025-09-30': DataFrame(1340 rows × 15 cols)
}
```

**Key Columns:**
- `accountname`, `accountnumber`, `level1accountname`, `netamt`, `Date`

### 2. trial_balance_consolidated (DataFrame)

**Source:** Cell 29  
**Transformation:** Union (pd.concat) of all daily DataFrames

**Dimensions:** 40,162 rows × 15 columns

**Key Operation:**
```python
trial_balance_consolidated = pd.concat(
    trial_balance_data.values(), 
    ignore_index=True
)
```

**Purpose:** Single DataFrame containing all daily trial balance records for the month

### 3. trial_balance_pivot_table (DataFrame)

**Source:** Cell 32  
**Transformation:** Pivot aggregation

**Dimensions:** 261 rows × 16+ columns (varies by number of funds)

**Key Operation:**
```python
trial_balance_pivot_table = trial_balance_consolidated.pivot_table(
    values='netamt',
    index='accountname',
    columns='level1accountname',
    aggfunc='sum',
    fill_value=0
)
```

**Structure:**
- **Index:** GL Account Names (unique)
- **Columns:** Fund Names (e.g., 'PEMI', 'BSP', 'DLSU')
- **Values:** Summed netamt for each Account × Fund combination

### 4. tb_fs_df (DataFrame)

**Source:** Cell 37  
**Transformation:** Left merge pivot table with COA mapping

**Dimensions:** 63 rows × 19+ columns

**Key Operation:**
```python
tb_fs_df = trial_balance_pivot_table.merge(
    coa_mapping[['TB Account Name', 'Account Type', 'FS Classification']],
    left_index=True,
    right_on='TB Account Name',
    how='left'
)
```

**Purpose:** Pivot table enriched with account type and financial statement classifications

### 5. segmented_results (dict of DataFrames)

**Source:** Cell 60  
**Transformation:** Slice tb_fs_df by fund

**Structure:** `{'PEMI': DataFrame, 'BSP': DataFrame, ...}` (16 funds)

**Example:**
```python
segmented_results = {
    'PEMI': DataFrame(17 rows × 4 cols),  # TB Account Name, Account Type, FS Classification, PEMI
    'BSP': DataFrame(13 rows × 4 cols),
    'DLSU': DataFrame(14 rows × 4 cols),
    ...
}
```

**Key Operation (inside create_segmented_dfs):**
```python
for fund_code in fund_codes:
    segment = df[base_columns + [fund_code]].copy()
    segment = segment[segment[fund_code] != 0]  # Filter non-zero balances
    results[fund_code] = segment
```

### 6. coa_mapping (DataFrame)

**Source:** Cell 19  
**Dimensions:** 512 rows × 4+ columns

**Columns:**
- `TB Account Name` (str): GL account name
- `Account Type` (str): Asset, Liability, Equity, Revenue, Expense
- `FS Classification` (str): Financial statement line item
- `Is_New_Account` (bool): Added by update function

**Update Logic (Cell 46):**
- If new accounts found in trial balance but missing in COA mapping
- Append new accounts with `Is_New_Account=True`
- Export dated file: `Chart of Accounts Mapping as of MM.DD.YYYY.xlsx`

---

## Functions Reference

### Data Loading Functions

#### `load_reference_data(project_root, folder_name, reference_type)`

**Location:** Cell 12  
**Purpose:** Generic loader for reference data (COA Mapping, Portfolio Mapping)

**Parameters:**
- `project_root` (Path): Absolute path to project root
- `folder_name` (str): Subfolder name (e.g., 'COA Mapping')
- `reference_type` (str): Description for logging (e.g., 'COA')

**Returns:** `dict`
```python
{
    'data': DataFrame or None,
    'metadata': {
        'load_timestamp': str,
        'source_file': str or None,
        'folder': Path,
        'file_count': int
    }
}
```

**Logic:**
1. Constructs path: `project_root / 'data' / 'references' / folder_name`
2. Finds all `.csv` and `.xlsx` files
3. Loads most recently modified file
4. Returns data + metadata

**Error Handling:**
- Returns None if folder doesn't exist
- Logs warnings for empty folders
- Handles both CSV and Excel formats

---

### Data Transformation Functions

#### `create_segmented_dfs(df, base_columns, fund_codes)`

**Location:** Cell 52  
**Purpose:** Split pivot table into per-fund DataFrames

**Parameters:**
- `df` (DataFrame): Input DataFrame (typically `tb_fs_df`)
- `base_columns` (list): Columns to include in all segments (e.g., ['TB Account Name', 'Account Type', 'FS Classification'])
- `fund_codes` (list): Fund identifiers (e.g., ['PEMI', 'BSP', 'DLSU'])

**Returns:** `dict`
```python
{
    'PEMI': DataFrame(17 rows × 4 cols),
    'BSP': DataFrame(13 rows × 4 cols),
    ...
}
```

**Key Logic:**
```python
for fund_code in fund_codes:
    segment = df[base_columns + [fund_code]].copy()
    segment = segment[segment[fund_code] != 0]  # Remove zero balances
    segment.reset_index(drop=True, inplace=True)
    results[fund_code] = segment
```

**Validation:**
- Filters out accounts with zero balance for each fund
- Preserves base columns + fund-specific amount column
- Returns empty DataFrame if fund has no transactions

#### `get_latest_reporting_dates(df, month_col='Date')`

**Location:** Cell 56  
**Purpose:** Extract latest transaction date for each month

**Parameters:**
- `df` (DataFrame): Input DataFrame with date column
- `month_col` (str): Name of date column (default: 'Date')

**Returns:** `tuple(dict, dict)`

**Structure:**
```python
# Structured format
{
    'September': {'latest_date': '2025-09-30'}
}

# Flat format (for export functions)
{
    'September': '2025-09-30'
}
```

**Logic:**
```python
df['Month_Name'] = pd.to_datetime(df[month_col]).dt.strftime('%B')
df['Date_Parsed'] = pd.to_datetime(df[month_col])
latest_date = df.loc[df.groupby('Month_Name')['Date_Parsed'].idxmax()]
```

---

### Export Functions

#### `update_coa_mapping_and_save(coa_mapping, trial_balance_pivot_table, save_path)`

**Location:** Cell 45  
**Purpose:** Append new GL accounts to COA mapping and export

**Parameters:**
- `coa_mapping` (DataFrame): Existing COA mapping
- `trial_balance_pivot_table` (DataFrame): Current pivot table
- `save_path` (str): Directory to save updated mapping (default: '../data/references/COA Mapping folder')

**Returns:** `DataFrame` (updated COA mapping)

**Logic:**
1. Compare GL accounts in pivot table vs. COA mapping
2. Identify missing accounts: `missing_in_coa = pivot_gl_accounts - coa_gl_accounts`
3. If new accounts found:
   - Create new rows with `Is_New_Account=True`
   - Append to existing mapping
   - Export dated file: `Chart of Accounts Mapping as of MM.DD.YYYY.xlsx`
4. If no new accounts: Skip export

**Output File:**
- Location: `data/references/COA Mapping/`
- Naming: `Chart of Accounts Mapping as of 11.21.2025.xlsx`
- Format: Excel (.xlsx)

#### `export_segmented_summary(segmented_dfs, latest_reporting_dates, portfolio_mapping, output_filename)`

**Location:** Cell 96  
**Purpose:** Export segmented summary report (16 fund sheets)

**Parameters:**
- `segmented_dfs` (dict): Dictionary of DataFrames by fund
- `latest_reporting_dates` (dict): Month → Date mapping
- `portfolio_mapping` (DataFrame): Fund metadata
- `output_filename` (str): Output file name (default: 'Segmented_Summary.xlsx')

**Returns:** `str` (output file path)

**Output Structure:**
```
Trial Balance Monthly.xlsx (33 KB)
├── BSP (13 rows)
│   ├── Header Rows 1-3: Fund Name, "Trial Balance Summary", Date
│   ├── Row 5: Column headers
│   └── Data Rows 6+: GL Accounts with amounts
├── DLS-CSB (15 rows)
├── DLSU (14 rows)
├── ... (16 total sheets)
```

**Key Features:**
- Custom headers (Fund Name, Title, Date) in rows 1-3
- Merged cells for header rows
- Bold font for headers and Grand Total
- Number format: `#,##0.00` (thousand separator, 2 decimals)
- Grand Total row (skips 2 rows after data)

**Logic Flow:**
```python
writer = pd.ExcelWriter(output_filepath, engine='openpyxl')

for num_col, df in segmented_dfs.items():
    # Write DataFrame to sheet
    df.to_excel(writer, sheet_name=num_col, startrow=5, header=False, index=False)
    
    # Access worksheet
    worksheet = writer.sheets[num_col]
    
    # Write custom headers (rows 1-3)
    for row_index, value in enumerate(custom_header):
        cell = worksheet.cell(row=row_index + 1, column=1, value=value)
        cell.font = Font(bold=True)
        worksheet.merge_cells(start_row=row_index + 1, start_column=1, end_row=row_index + 1, end_column=2)
    
    # Write column headers (row 5)
    for col_num, column_name in enumerate(df.columns):
        worksheet.cell(row=5, column=col_num + 1, value=column_name)
    
    # Apply number formatting
    for row_num in range(6, 6 + len(df)):
        cell = worksheet.cell(row=row_num, column=4)
        cell.number_format = '#,##0.00'
    
    # Add Grand Total
    grand_total = df[df.columns[-1]].sum()
    total_row = 6 + len(df) + 2
    worksheet.cell(row=total_row, column=3, value="Grand Total")
    worksheet.cell(row=total_row, column=4, value=grand_total)

writer.close()
```

#### `export_financial_report(dataframes, segmented_dfs, latest_reporting_dates, portfolio_mapping, output_filename)`

**Location:** Cell 91  
**Purpose:** Export full financial report (5 main sheets + 16 fund sheets)

**Parameters:**
- `dataframes` (dict): Dictionary of initial 5 DataFrames
- `segmented_dfs` (dict): Dictionary of segmented DataFrames by fund
- `latest_reporting_dates` (dict): Month → Date mapping
- `portfolio_mapping` (DataFrame): Fund metadata
- `output_filename` (str): Output file name (default: 'Trial_Balance.xlsx')

**Returns:** `str` (output file path)

**Output Structure:**
```
Trial_Balance.xlsx (4.5 MB)
├── RD-TB (40,162 rows)          # trial_balance_consolidated
├── COA (509 rows)               # chart_of_accounts_final
├── COA_ref (512 rows)           # coa_mapping
├── TB-Pivot (261 rows)          # trial_balance_pivot_table
├── TB-SF (63 rows)              # tb_fs_df
├── BSP (13 rows)                # Segmented fund data
├── DLS-CSB (15 rows)
├── ... (16 segmented sheets)
```

**Sheet Mapping:**
```python
initial_sheet_map = {
    'trial_balance_consolidated': 'RD-TB',
    'chart_of_accounts_final': 'COA',
    'coa_mapping': 'COA_ref',
    'trial_balance_pivot_table': 'TB-Pivot',
    'tb_fs_df': 'TB-SF',
}
```

**Logic Flow:**
```python
writer = pd.ExcelWriter(output_filepath, engine='openpyxl')

# Write initial 5 DataFrames (raw data)
for df_key, sheet_name in initial_sheet_map.items():
    dataframes[df_key].to_excel(writer, sheet_name=sheet_name, index=False)

# Write segmented DataFrames (with custom headers and formatting)
for num_col, df in segmented_dfs.items():
    # Same logic as export_segmented_summary()
    # Custom headers, formatting, Grand Total

writer.close()
```

---

## Execution Workflow

### 1. GUI-Driven Execution (Recommended)

**Entry Point:** `launch_gui.bat` (double-click in project root)

**Workflow:**
```
User → GUI → Select Year/Month → Click "Process Report"
  ↓
GUI writes config/run_config.json:
{
  "year": "2025",
  "month": "September",
  "data_path": "D:/...absolute path..."
}
  ↓
GUI executes: papermill notebooks/01-rd-trial-balance-mvp.ipynb output.ipynb
  ↓
Notebook reads config → Loads data → Processes → Exports reports
  ↓
GUI displays: 
  - Real-time log output
  - Generated reports list
  - COA mappings list
```

**Key Files:**
- **Launcher:** `launch_gui.bat`
- **GUI Code:** `src/gui/trial_balance_app.py`
- **Config:** `config/run_config.json` (auto-generated)
- **Executed Notebook:** `notebooks/executed_trial_balance_reports/trial_balance_report_YYYYMMDD_HHMMSS.ipynb`

### 2. Direct Notebook Execution (Development)

**Entry Point:** Open notebook in Jupyter/VS Code

**Workflow:**
```
Open notebooks/01-rd-trial-balance-mvp.ipynb
  ↓
Run All Cells (1-101)
  ↓
Cell 13 checks for config/run_config.json:
  - If found: Load user-selected data
  - If not found: Auto-detect latest year/month
  ↓
Process data → Export reports
```

**Execution Order:**
1. **Initialize** (Cells 1-12): Imports, logging, function definitions
2. **Load Data** (Cells 13-19): Trial balance, COA, reference data
3. **Transform** (Cells 24-37): Consolidate, pivot, merge
4. **Validate** (Cells 40-50): Check for new accounts, update COA
5. **Segment** (Cells 52-72): Create per-fund DataFrames
6. **Export** (Cells 91-97): Generate Excel reports

---

## Reproducibility Guide

### Prerequisites

1. **Python 3.12.2** installed
2. **Virtual environment** created and activated
3. **Dependencies** installed from `requirements.txt`

### Setup Steps

#### 1. Environment Setup (First Time Only)

```bash
# Navigate to project root
cd "D:/UserProfile/Documents/@ VFC/pemi-automation/trial-balance"

# Run setup script
scripts/launchers/setup_env_trial_balance.bat

# This creates .venv/ and installs all dependencies
```

**What gets installed:**
- pandas >= 2.2.0
- numpy >= 1.26.0
- openpyxl >= 3.1.0
- papermill >= 2.6.0
- jupyter >= 1.0.0
- jupyterlab >= 4.0.0
- ipykernel >= 6.29.0

#### 2. Data Preparation

**Required Data Structure:**
```
data/raw/Trial Balance/
└── {YEAR}/              # e.g., 2025
    └── {MONTH}/         # e.g., September
        ├── Trial Balance/
        │   ├── 09-01-2025.csv
        │   ├── 09-02-2025.csv
        │   └── ... (all daily files)
        └── Chart of Accounts/
            └── RD - Chart of Accounts.csv
```

**Required Reference Data:**
```
data/references/
├── COA Mapping/
│   └── Chart of Accounts Mapping as of MM.DD.YYYY.xlsx
└── Portfolio Mapping/
    └── Portfolio Mapping.xlsx
```

#### 3. Execution Methods

**Method A: GUI (Recommended for Business Users)**
```bash
# Double-click launch_gui.bat
# OR run from command line:
launch_gui.bat

# Then in GUI:
# 1. Select Year (e.g., 2025)
# 2. Select Month (e.g., September)
# 3. Click "📊 Process Report"
# 4. Wait for completion
# 5. Click "📂 Open Results Folder" to view outputs
```

**Method B: Direct Notebook Execution (Developers)**
```bash
# Activate virtual environment
.venv/Scripts/activate

# Start Jupyter
jupyter notebook notebooks/01-rd-trial-balance-mvp.ipynb

# Run all cells (Kernel → Run All)
```

**Method C: Papermill CLI (Automation)**
```bash
# Activate virtual environment
.venv/Scripts/activate

# Execute notebook with papermill
papermill notebooks/01-rd-trial-balance-mvp.ipynb \
          notebooks/executed_trial_balance_reports/output_$(date +%Y%m%d_%H%M%S).ipynb

# Note: Notebook will auto-detect latest year/month if no config exists
```

### Expected Outputs

After successful execution:

```
data/processed/Trail Balance/{YEAR}/
├── Trial Balance Monthly.xlsx      # 33 KB, 16 sheets (segmented summary)
└── Trial_Balance.xlsx               # 4.5 MB, 21 sheets (full report)

data/references/COA Mapping/
└── Chart of Accounts Mapping as of MM.DD.YYYY.xlsx  # If new accounts found

notebooks/executed_trial_balance_reports/
└── trial_balance_report_YYYYMMDD_HHMMSS.ipynb  # Executed notebook with outputs

logs/
└── trial_balance_YYYYMMDD_HHMMSS.log  # Detailed execution log
```

### Verification Steps

1. **Check log file:**
   ```bash
   # View latest log
   ls -lt logs/ | head -2
   cat logs/trial_balance_YYYYMMDD_HHMMSS.log
   ```

2. **Verify Excel reports:**
   ```bash
   # Check file sizes
   ls -lh "data/processed/Trail Balance/2025/"
   
   # Expected:
   # Trial Balance Monthly.xlsx: ~33 KB
   # Trial_Balance.xlsx: ~4.5 MB
   ```

3. **Open reports in Excel:**
   - Trial Balance Monthly.xlsx should have 16 sheets (one per fund)
   - Trial_Balance.xlsx should have 21 sheets (5 main + 16 funds)

4. **Check COA mapping:**
   ```bash
   # Check for new mapping file
   ls -lt "data/references/COA Mapping/" | head -3
   
   # If new accounts were found, new dated file will be present
   ```

### Troubleshooting

**Issue: "No data found"**
- Check data folder structure matches expected pattern
- Verify CSV file naming: MM-DD-YYYY.csv
- Check logs for folder path that was searched

**Issue: "COA mapping not found"**
- Ensure `data/references/COA Mapping/` contains at least one .xlsx file
- Check file permissions

**Issue: "Import errors"**
- Re-run setup: `scripts/launchers/setup_env_trial_balance.bat`
- Verify virtual environment is activated: `.venv/Scripts/activate`

**Issue: "Excel file not created"**
- Check logs for Python errors
- Verify openpyxl is installed: `pip show openpyxl`
- Ensure output directory has write permissions

### Performance Notes

**Typical Execution Times:**
- Data loading (30 CSVs): ~5-10 seconds
- Data consolidation: ~2-3 seconds
- Pivot table creation: ~1-2 seconds
- Excel export (Trial_Balance.xlsx): ~10-15 seconds
- Excel export (Trial Balance Monthly.xlsx): ~1-2 seconds
- **Total Runtime:** ~20-35 seconds for September 2025 data (40,162 records)

**Memory Usage:**
- Peak: ~500 MB RAM
- Recommended: 2 GB RAM minimum

---

## Configuration Reference

### config/run_config.json

**Purpose:** Bridge between GUI and notebook

**Structure:**
```json
{
  "year": "2025",
  "month": "September",
  "data_path": "D:/UserProfile/Documents/@ VFC/pemi-automation/trial-balance/data/raw/Trial Balance/2025/September"
}
```

**Generated By:** GUI when user clicks "Process Report"

**Read By:** Notebook Cell 13

**Lifecycle:**
- Created: On each GUI execution
- Overwritten: Each time user processes data
- Not tracked: In .gitignore

---

## Logging Configuration

### Log File Format

**Location:** `logs/trial_balance_YYYYMMDD_HHMMSS.log`

**Format:**
```
2025-11-21 13:48:22,123 - INFO - ============================================================
2025-11-21 13:48:22,124 - INFO - LOADING TRIAL BALANCE DATA
2025-11-21 13:48:22,125 - INFO - ============================================================
2025-11-21 13:48:22,126 - INFO - 📂 Project Root: D:\UserProfile\Documents\@ VFC\pemi-automation\trial-balance
2025-11-21 13:48:22,345 - INFO - ✅ Data loaded successfully
```

**Log Levels:**
- **INFO:** Normal operations (data loading, processing steps)
- **WARNING:** Non-critical issues (missing files, auto-detection fallback)
- **ERROR:** Critical issues (missing folders, load failures)

**Logged Events:**
- Project root detection
- Config file read status
- Data folder validation
- File counts and sizes
- Processing milestones
- Export operations
- Success/failure status

---

## Data Quality & Validation

### Validation Checks Performed

1. **File Format Validation:**
   - Check CSV file naming: MM-DD-YYYY.csv
   - Log non-compliant files as warnings

2. **GL Account Validation:**
   - Compare pivot table accounts vs. COA mapping
   - Identify missing accounts: `missing_in_coa = pivot_gl_accounts - coa_gl_accounts`
   - Flag new accounts with `Is_New_Account=True`

3. **Data Completeness:**
   - Verify Trial Balance folder contains CSV files
   - Verify Chart of Accounts folder contains reference file
   - Check for required columns in loaded DataFrames

4. **Date Validation:**
   - Parse dates from filenames using `datetime.strptime()`
   - Catch ValueError for invalid date formats
   - Log skipped files

### Known Limitations

1. **No Balance Validation:** System does not verify debits = credits
2. **Manual Account Classification:** New accounts require manual updates (Account Type, FS Classification)
3. **No Inter-company Eliminations:** Implemented in future phases
4. **No Variance Analysis:** Planned for future iterations
5. **Single Month Processing:** Cannot process multiple months in one run

---

## Extension Points

### Adding New Export Formats

**Location:** Create new function in Cell 95+

**Pattern:**
```python
def export_custom_report(data, output_filename='Custom_Report.xlsx'):
    """
    Custom export function template
    """
    # Define output path
    output_dir = os.path.join('..', 'data', 'processed', 'Custom Reports')
    os.makedirs(output_dir, exist_ok=True)
    output_filepath = os.path.join(output_dir, output_filename)
    
    # Write data
    writer = pd.ExcelWriter(output_filepath, engine='openpyxl')
    # ... your export logic ...
    writer.close()
    
    return output_filepath
```

### Adding New Validations

**Location:** Cell 40-50 (after pivot table creation)

**Pattern:**
```python
# Custom validation logic
def validate_balances(df):
    """
    Add custom validation checks
    """
    # Example: Check for negative asset balances
    asset_accounts = df[df['Account Type'] == 'Asset']
    negative_assets = asset_accounts[asset_accounts[fund_col] < 0]
    
    if len(negative_assets) > 0:
        logger.warning(f"Found {len(negative_assets)} accounts with negative asset balances")
    
    return validation_results
```

### Adding New Segmentations

**Location:** Cell 60-70 (modify `create_segmented_dfs`)

**Example: Segment by Account Type instead of Fund:**
```python
def create_segmented_by_account_type(df, account_type_col='Account Type'):
    """
    Segment data by Account Type (Asset, Liability, etc.)
    """
    results = {}
    
    for account_type in df[account_type_col].unique():
        segment = df[df[account_type_col] == account_type].copy()
        results[account_type] = segment
    
    return results
```

---

## GUI Application Functions

### TrialBalanceApp Class (`src/gui/trial_balance_app.py`)

The GUI application provides a user-friendly interface with input/output location selectors and real-time connection monitoring.

#### Key Features
- Dual location selectors (input data source, output destination)
- Real-time connection status indicators
- Color-coded path displays
- Enhanced reports list with location tracking
- Automatic config generation for notebook execution

---

#### `check_connection(path, location_type="input")`

**Purpose:** Verify that a file system path is accessible and update visual status indicator

**Parameters:**
- `path` (str): Absolute path to check (e.g., `"X:/Trail Balance"` or local folder path)
- `location_type` (str): Either `"input"` or `"output"` to determine which status label to update

**Returns:** `bool`
- `True` if path exists and is accessible
- `False` if path doesn't exist or is inaccessible

**Visual Feedback:**
- Updates `self.input_status_label` or `self.output_status_label` based on `location_type`
- **✓ Connected** (green) - Path exists and is accessible
- **✗ Not Found** (orange) - Path doesn't exist
- **✗ No Access** (red) - Permission or network error

**When Called:**
- On application startup (checks both input and output locations)
- When user changes input location dropdown
- When user changes output location dropdown

**Example Usage:**
```python
# Check shared drive input location
if self.check_connection("X:/Trail Balance", "input"):
    self.log_message("  ✓ Shared drive is accessible", 'INFO')
else:
    self.log_message("  ⚠️ WARNING: Shared drive not accessible!", 'WARNING')
```

**Implementation:**
```python
def check_connection(self, path, location_type="input"):
    """Check if a path is accessible and update status indicator"""
    try:
        path_obj = Path(path)
        if path_obj.exists():
            # Green checkmark - path is accessible
            if location_type == "input":
                self.input_status_label.config(text="✓ Connected", foreground='green')
            else:
                self.output_status_label.config(text="✓ Connected", foreground='green')
            return True
        else:
            # Orange warning - path doesn't exist
            if location_type == "input":
                self.input_status_label.config(text="✗ Not Found", foreground='orange')
            else:
                self.output_status_label.config(text="✗ Not Found", foreground='orange')
            return False
    except Exception as e:
        # Red error - permission or network issue
        if location_type == "input":
            self.input_status_label.config(text="✗ No Access", foreground='red')
        else:
            self.output_status_label.config(text="✗ No Access", foreground='red')
        return False
```

---

#### `on_input_location_changed(event)`

**Purpose:** Handle input location dropdown changes and update connection status

**Behavior:**
- Updates `self.base_path` to point to selected location
- Calls `check_connection()` to verify accessibility
- Logs connection status to processing log
- Updates selected path display

**Locations:**
- **Local Storage:** `{project_root}/data/raw/Trial Balance/{year}/{month}`
- **Shared Drive:** `X:/Trail Balance/data/raw/Trial Balance/{year}/{month}`

---

#### `on_output_location_changed(event)`

**Purpose:** Handle output location dropdown changes and update connection status

**Behavior:**
- Updates output path configuration
- Calls `check_connection()` to verify accessibility
- Logs connection status to processing log
- Updates output path display (blue for shared, green for local)
- Refreshes reports list to show files at new location

**Locations:**
- **Shared Drive:** `X:/Trail Balance/data/processed/Trail Balance`
- **Local Storage:** `{project_root}/data/processed/Trail Balance`

---

#### `refresh_reports_list()`

**Purpose:** Display generated reports with location indicator and file statistics

**Features:**
- Shows location label: **📁 SHARED DRIVE** or **💻 LOCAL STORAGE**
- Lists all Excel files (.xlsx) with file sizes
- Displays total file count and cumulative size
- Shows folder path for reference

**Example Output:**
```
═══ EXCEL REPORTS (📁 SHARED DRIVE) ===
  Trial_Balance.xlsx (4.5 MB)
  Trial Balance Monthly.xlsx (33.0 KB)
  ✓ Total: 2 files (4.53 MB)
  📂 Location: X:\Trail Balance\data\processed\Trail Balance\2025

═══ COA MAPPINGS (💻 LOCAL STORAGE) ===
  Chart of Accounts Mapping as of 09.30.2025.xlsx (85.3 KB)
  ✓ Total: 1 file (0.08 MB)
  📂 Location: D:\...\data\references\COA Mapping
```

---

### Configuration Management

#### `run_config.json` Structure

**Location:** `config/run_config.json`

**Generated By:** GUI application when user clicks "Process Report"

**Schema:**
```json
{
  "year": "2025",
  "month": "September",
  "data_path": "X:\\Trail Balance\\data\\raw\\Trial Balance\\2025\\September",
  "output_base_path": "X:\\Trail Balance\\data\\processed\\Trail Balance"
}
```

**Usage:**
- Notebook reads this config at runtime (Cell 14)
- `data_path` determines input data source location
- `output_base_path` determines where reports are saved
- Dynamically updated when user changes location dropdowns

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-21 | Initial release with GUI integration, dual export functions, COA validation |
| 2.0 | 2025-11-24 | Added input/output location selectors, connection status monitoring, enhanced reports display |

---

## Related Documentation

- **README.md** - Project overview and quick start
- **GETTING_STARTED.md** - Step-by-step user guide
- **OUTPUT_DIRECTORIES.md** - Output file locations reference
- **FILE_INDEX.md** - Complete file inventory
- **requirements.txt** - Python dependencies

---

**For Questions or Issues:**  
Contact: VFC Data Science Team
