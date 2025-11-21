# Trial Balance Automation - Output Directories

## 📊 Report Output Locations

This document describes where each type of report and output file is saved by the Trial Balance Automation system.

---

## 1. 📈 Main Excel Report (Trial Balance Monthly)

**Location:** `data/processed/Trail Balance/{year}/`

**File Name:** `Trial Balance Monthly.xlsx`

**Example Path:**
```
data/processed/Trail Balance/2025/Trial Balance Monthly.xlsx
```

**Contents:**
- Multiple sheets with segmented trial balance data
- Pivot tables by GL Account and Fund Name
- Latest reporting dates for each month
- Formatted with custom headers and totals

**Created By:** 
- Cell 97 in notebook (`export_segmented_summary` function)
- Function: `export_segmented_summary_with_details()`

**Notes:**
- Saves in year-specific folder (no month subfolder)
- Overwrites previous file with same name in that year

---

## 2. 📋 Updated COA Mapping (Chart of Accounts)

**Location:** `data/references/COA Mapping/`

**File Name:** `Chart of Accounts Mapping as of MM.DD.YYYY.xlsx`

**Example Path:**
```
data/references/COA Mapping/Chart of Accounts Mapping as of 11.21.2025.xlsx
```

**Contents:**
- Original COA mapping data
- New GL accounts discovered during processing
- `Is_New_Account` column (TRUE/FALSE indicator)
- TB Account Name, Account Type, FS Classification columns

**Created By:**
- Cell 45 in notebook (`update_coa_mapping_and_save` function)
- Triggered when new GL accounts are found

**Notes:**
- Only created if new accounts are discovered
- Uses current date in filename
- Does NOT overwrite; creates new dated file each time

---

## 3. 📓 Executed Notebooks (Papermill Output)

**Location:** `notebooks/executed_trial_balance_reports/`

**File Name:** `trial_balance_report_YYYYMMDD_HHMMSS.ipynb`

**Example Path:**
```
notebooks/executed_trial_balance_reports/trial_balance_report_20251121_134527.ipynb
```

**Contents:**
- Complete executed notebook with all cells
- All outputs, charts, tables preserved
- Execution metadata from papermill

**Created By:**
- GUI application when "📊 Process Report" is clicked
- Managed by papermill execution engine

**Notes:**
- New file created for each run (timestamped)
- Never overwrites previous executions
- Useful for audit trail and debugging

---

## 4. 📝 Log Files

**Location:** `logs/`

**File Name:** `trial_balance_YYYYMMDD_HHMMSS.log`

**Example Path:**
```
logs/trial_balance_20251121_134527.log
```

**Contents:**
- Complete execution log
- INFO, WARNING, ERROR messages
- Timestamps for each operation
- Data loading summary
- Processing steps and results

**Created By:**
- Cell 6 in notebook (logging configuration)

**Notes:**
- New log file for each notebook execution
- Includes project root, paths, file counts
- Useful for troubleshooting

---

## 5. ⚙️ Configuration File (GUI → Notebook)

**Location:** `config/`

**File Name:** `run_config.json`

**Example Path:**
```
config/run_config.json
```

**Contents:**
```json
{
  "year": "2025",
  "month": "September",
  "data_path": "D:\\...\\data\\raw\\Trial Balance\\2025\\September"
}
```

**Created By:**
- GUI application when user selects year/month
- Written before notebook execution

**Notes:**
- Temporary configuration file
- Overwritten on each GUI run
- Contains absolute path to selected data folder

---

## Directory Structure Summary

```
trial-balance/
│
├── data/
│   ├── processed/
│   │   └── Trail Balance/          ← 📈 Main Excel Reports
│   │       ├── 2025/
│   │       │   └── Trial Balance Monthly.xlsx
│   │       └── 2024/
│   │           └── Trial Balance Monthly.xlsx
│   │
│   └── references/
│       └── COA Mapping/             ← 📋 Updated COA Mappings
│           ├── Chart of Accounts Mapping as of 11.21.2025.xlsx
│           └── Chart of Accounts Mapping as of 11.20.2025.xlsx
│
├── notebooks/
│   └── executed_trial_balance_reports/  ← 📓 Executed Notebooks
│       ├── trial_balance_report_20251121_134527.ipynb
│       └── trial_balance_report_20251120_092315.ipynb
│
├── logs/                            ← 📝 Log Files
│   ├── trial_balance_20251121_134527.log
│   └── trial_balance_20251120_092315.log
│
└── config/                          ← ⚙️ Config File
    └── run_config.json
```

---

## Quick Reference

| Report Type | Directory | File Naming | Overwrites? |
|------------|-----------|-------------|-------------|
| **Excel Report** | `data/processed/Trail Balance/{year}/` | `Trial Balance Monthly.xlsx` | ✅ Yes (per year) |
| **COA Mapping** | `data/references/COA Mapping/` | `Chart of Accounts Mapping as of MM.DD.YYYY.xlsx` | ❌ No (dated) |
| **Executed Notebook** | `notebooks/executed_trial_balance_reports/` | `trial_balance_report_YYYYMMDD_HHMMSS.ipynb` | ❌ No (timestamped) |
| **Log File** | `logs/` | `trial_balance_YYYYMMDD_HHMMSS.log` | ❌ No (timestamped) |
| **Config File** | `config/` | `run_config.json` | ✅ Yes (each run) |

---

## GUI Features

### "📊 Generated Reports & COA Mappings" Display

The GUI automatically shows:

**Excel Reports Section:**
- All `Trial Balance Monthly.xlsx` files from `data/processed/Trail Balance/{year}/`
- All `Trial_Balance.xlsx` files (full financial reports)
- Sorted by modification date (newest first)
- Shows: Date, Year, Filename, Size

**COA Mappings Section:**
- Up to 5 most recent COA mapping files from `data/references/COA Mapping/`
- Shows: Date, Filename, Size
- Displays "(No COA mappings found)" if none exist

### "📂 Open Results Folder" Button

When you click **"📂 Open Results Folder"** in the GUI, it opens:

**Primary Location:** `data/processed/Trail Balance/`

This folder contains all the year subfolders with the main Excel reports.

**What You'll See:**
- Folders for each year (2025, 2024, etc.)
- Inside each year folder: Excel report files

---

## Need to Find Files?

### To find the latest Excel report:
```
data/processed/Trail Balance/2025/Trial Balance Monthly.xlsx
```

### To find all executed notebooks:
```
notebooks/executed_trial_balance_reports/
```

### To find the latest COA mapping:
```
data/references/COA Mapping/
(Look for the file with the most recent date)
```

### To check logs for errors:
```
logs/
(Most recent timestamp = latest execution)
```

---

**Last Updated:** 2025-11-21
