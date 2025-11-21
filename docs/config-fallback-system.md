# Config + Fallback System Documentation

## Overview

The Trial Balance Automation system uses a **3-tier approach** to determine which data folder to load:

1. **PRIMARY**: User selection via GUI (config file)
2. **FALLBACK**: Auto-detect latest year/month
3. **TERMINAL**: Clear error if no data found

This ensures robust operation whether running from the GUI or directly executing the notebook.

---

## Architecture

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERACTION                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  GUI (src/gui/trial_balance_app.py)                         │
│  ├─ User selects Year: 2025                                 │
│  ├─ User selects Month: September                           │
│  └─ User clicks "Process Report"                            │
│                                                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  CONFIG FILE CREATION                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  GUI validates folder exists:                                │
│  D:\...\data\raw\Trial Balance\2025\September               │
│                                                               │
│  Writes config/run_config.json:                             │
│  {                                                            │
│    "year": "2025",                                           │
│    "month": "September",                                     │
│    "data_path": "D:\\...\\2025\\September"  <- ABSOLUTE    │
│  }                                                            │
│                                                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  NOTEBOOK EXECUTION                          │
│                (via papermill)                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               NOTEBOOK DATA LOADING CELL                     │
│          (Cell 13 with 3-Tier Logic)                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────┐                   │
│  │  TIER 1: Config File (User Selection) │                   │
│  ├────────────────────────────────────────┤                   │
│  │  • Check if config/run_config.json exists              │
│  │  • Load and parse JSON                                  │
│  │  • Extract data_path (absolute or relative)            │
│  │  • Validate path exists                                 │
│  │  • If valid: USE IT ✅                                 │
│  │  • If invalid: Continue to Tier 2                      │
│  └────────────────────────────────────────┘                   │
│                     │                                         │
│                     ▼ (fallback)                             │
│  ┌──────────────────────────────────────┐                   │
│  │  TIER 2: Auto-Detect Latest           │                   │
│  ├────────────────────────────────────────┤                   │
│  │  • Scan data/raw/Trial Balance/                         │
│  │  • Find latest year folder (2025, 2024, ...)           │
│  │  • Find latest month by modification time              │
│  │  • Validate path exists                                 │
│  │  • If valid: USE IT ⚠️  (log warning)                 │
│  │  • If invalid: Continue to Tier 3                      │
│  └────────────────────────────────────────┘                   │
│                     │                                         │
│                     ▼ (error)                                │
│  ┌──────────────────────────────────────┐                   │
│  │  TIER 3: Terminal Error                │                   │
│  ├────────────────────────────────────────┤                   │
│  │  • Log clear error messages                             │
│  │  • Include full paths for debugging                     │
│  │  • Raise FileNotFoundError ❌                          │
│  │  • Notebook execution stops                             │
│  └────────────────────────────────────────┘                   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. GUI (src/gui/trial_balance_app.py)

**Purpose**: Business user interface for folder selection

**Key Method**: `run_notebook_processing()`

**Logic**:
```python
def run_notebook_processing(self):
    # 1. Get user selections
    year = self.selected_year.get()
    month = self.selected_month.get()
    
    # 2. Build absolute path
    data_path = self.base_path / year / month
    
    # 3. Validate folder exists
    if not data_path.exists():
        # Show error dialog, abort
        return
    
    # 4. Validate Trial Balance subfolder
    tb_folder = data_path / "Trial Balance"
    if not tb_folder.exists():
        # Show warning, ask to continue
    
    # 5. Write config with absolute path
    config = {
        'year': year,
        'month': month,
        'data_path': str(data_path)  # ABSOLUTE PATH
    }
    config_path.write_text(json.dumps(config, indent=2))
    
    # 6. Execute notebook via papermill
    papermill.execute_notebook(...)
```

**Path Type**: **Absolute**
- Example: `D:\UserProfile\Documents\@ VFC\pemi-automation\trial-balance\data\raw\Trial Balance\2025\September`

**Validation**:
- ✅ Folder existence check BEFORE writing config
- ✅ Trial Balance subfolder check (warning)
- ✅ Clear error messages to user

---

### 2. Config File (config/run_config.json)

**Purpose**: Bridge between GUI and notebook

**Format**:
```json
{
  "year": "2025",
  "month": "September",
  "data_path": "D:\\UserProfile\\Documents\\@ VFC\\pemi-automation\\trial-balance\\data\\raw\\Trial Balance\\2025\\September"
}
```

**Path Handling**:
- **Absolute paths** (from GUI): Used directly
- **Relative paths** (legacy): Resolved to `../data/raw/Trial Balance/{year}/{month}`

**Lifetime**:
- Created by GUI on "Process Report" button
- Read by notebook at start of data loading cell
- Persistent across runs (not deleted after use)

---

### 3. Notebook (notebooks/01-rd-trial-balance-mvp.ipynb)

**Cell 13**: Data Loading with 3-Tier Fallback

#### Tier 1: Config File (User Selection)

```python
config_path = Path("../config/run_config.json")

if config_path.exists():
    logger.info(f"Found config file: {config_path}")
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        
        # Handle absolute paths (GUI) or relative paths (legacy)
        if "data_path" in config and Path(config["data_path"]).is_absolute():
            data_path = Path(config["data_path"])
        else:
            year = config.get("year")
            month = config.get("month")
            data_path = Path("../data/raw/Trial Balance") / year / month
        
        # Validate path exists
        if data_path and data_path.exists():
            config_source = "user_selection"
            logger.info(f"Data folder validated: {data_path}")
        else:
            logger.warning(f"Config path does not exist: {data_path}")
            data_path = None  # Trigger fallback
    
    except Exception as e:
        logger.error(f"Error reading config: {e}")
        data_path = None  # Trigger fallback
```

**Outcome**:
- ✅ SUCCESS: `data_path` set, `config_source = "user_selection"`
- ⚠️  FALLBACK: `data_path = None`, continue to Tier 2

---

#### Tier 2: Auto-Detect Latest (Fallback)

```python
if data_path is None:
    logger.info("FALLBACK: AUTO-DETECTING LATEST DATA FOLDER")
    
    default_raw_path = Path("../data/raw/Trial Balance")
    
    # Find latest year (numeric folders, sorted descending)
    year_folders = sorted(
        [f for f in default_raw_path.iterdir() 
         if f.is_dir() and f.name.replace("-", "").isdigit()],
        reverse=True
    )
    
    if not year_folders:
        raise FileNotFoundError(f"No year folders found in {default_raw_path}")
    
    latest_year_folder = year_folders[0]
    year = latest_year_folder.name
    
    # Find latest month (by modification time)
    month_folders = sorted(
        [f for f in latest_year_folder.iterdir() if f.is_dir()],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    if not month_folders:
        raise FileNotFoundError(f"No month folders found in {latest_year_folder}")
    
    latest_month_folder = month_folders[0]
    month = latest_month_folder.name
    data_path = latest_month_folder
    config_source = "auto_detect"
    
    logger.info(f"Auto-detected path: {data_path}")
```

**Outcome**:
- ✅ SUCCESS: `data_path` set, `config_source = "auto_detect"`
- ❌ ERROR: Raise `FileNotFoundError`, continue to Tier 3

---

#### Tier 3: Terminal Error

```python
if not default_raw_path.exists():
    error_msg = f"FATAL: Raw data folder not found: {default_raw_path}"
    logger.error(error_msg)
    logger.error(f"   Please check your project structure!")
    logger.error(f"   Current working directory: {Path.cwd()}")
    raise FileNotFoundError(error_msg)
```

**Outcome**:
- ❌ FATAL ERROR: Notebook execution stops
- 📝 LOG: Clear error messages with full paths
- 🖥️  TERMINAL: Error visible to user

---

## Usage Scenarios

### Scenario 1: GUI Workflow (Normal Operation)

**Steps**:
1. User launches GUI: `launch_gui.bat`
2. User selects Year: `2025`, Month: `September`
3. User clicks "Process Report"
4. GUI validates folder, writes config with absolute path
5. Notebook loads config, uses `data_path` directly
6. Processing completes successfully

**Log Output**:
```
Found config file: ../config/run_config.json
Config loaded successfully
   Year: 2025
   Month: September
   Data Path: D:\...\2025\September
Data folder validated: D:\...\2025\September
Source: USER SELECTION
```

---

### Scenario 2: Direct Notebook Execution (No Config)

**Steps**:
1. User opens notebook in Jupyter/VS Code
2. User runs all cells
3. No config file exists
4. Notebook auto-detects latest year/month
5. Processing completes with warning

**Log Output**:
```
Config file not found: ../config/run_config.json
   This is normal for direct notebook execution
FALLBACK: AUTO-DETECTING LATEST DATA FOLDER
Latest year found: 2025
Latest month found: September
Auto-detected path: D:\...\2025\September
Source: AUTO DETECT
```

---

### Scenario 3: Missing Data Folder (Error Handling)

**Steps**:
1. Config points to non-existent folder
2. Auto-detect also fails
3. Clear error raised

**Log Output**:
```
Config path does not exist: D:\...\2025\October
   Will try fallback methods...
FALLBACK: AUTO-DETECTING LATEST DATA FOLDER
FATAL: No month folders found in D:\...\2025
   Please check your project structure!
   Current working directory: D:\...\notebooks
FileNotFoundError: FATAL: No month folders found...
```

---

## Testing

### Test Script: `scripts/test_config_workflow.py`

**Purpose**: Validates all 3 scenarios

**Run**:
```bash
python scripts/test_config_workflow.py
```

**Tests**:
1. ✅ Config with absolute path (GUI flow)
2. ✅ Config with relative path (legacy)
3. ✅ No config (auto-detect fallback)

**Expected Output**:
```
============================================================
TEST SUMMARY
============================================================
✅ PASSED: Absolute Path (GUI)
✅ PASSED: Relative Path (Legacy)
✅ PASSED: Auto-Detect Fallback

============================================================
✅ ALL TESTS PASSED
============================================================
```

---

## File Locations

| File | Purpose |
|------|---------|
| `src/gui/trial_balance_app.py` | GUI application with config writing |
| `config/run_config.json` | Config file bridge (created by GUI) |
| `notebooks/01-rd-trial-balance-mvp.ipynb` | Notebook with Cell 13 fallback logic |
| `scripts/test_config_workflow.py` | Test script for all scenarios |
| `docs/config-fallback-system.md` | This documentation file |

---

## Design Decisions

### Why Absolute Paths in Config?

**Problem**: Notebook working directory is `notebooks/`, GUI working directory is project root
**Solution**: Absolute paths eliminate ambiguity

**Benefits**:
- ✅ No path resolution confusion
- ✅ Works regardless of working directory
- ✅ Clear error messages with full paths
- ✅ Easier debugging

### Why Keep Relative Path Support?

**Reason**: Backward compatibility with any existing scripts or manual config files

**Handling**:
- Detect via `Path.is_absolute()`
- Resolve relative to `../data/raw/Trial Balance/{year}/{month}`
- Log both original and resolved paths

### Why Auto-Detect as Fallback?

**Use Case**: Direct notebook execution without GUI (data scientists, debugging)

**Logic**:
- Find latest year (numeric folders, descending)
- Find latest month (by modification time, descending)
- Log clearly that fallback was used

**Tradeoff**: May load unexpected data if multiple year/month folders exist

---

## Error Handling Strategy

### Validation Layers

| Layer | Location | Action on Error |
|-------|----------|-----------------|
| **1. GUI** | Before config write | Show error dialog, abort |
| **2. Notebook Config** | After reading config | Log warning, try fallback |
| **3. Notebook Auto-Detect** | After fallback attempt | Raise FileNotFoundError |

### Error Message Format

**Good Error Message**:
```
❌ FATAL: Raw data folder not found: D:\...\data\raw\Trial Balance
   Please check your project structure!
   Current working directory: D:\...\notebooks
```

**Why**:
- ✅ Clear severity indicator (FATAL)
- ✅ Full path for debugging
- ✅ Actionable guidance
- ✅ Context (current working directory)

---

## Future Enhancements

### Potential Improvements

1. **Config History**: Store last 5 selections for quick re-run
2. **Date Range Validation**: Check if CSVs match expected date range
3. **Multi-Month Processing**: Allow selecting multiple months at once
4. **Config Schema Validation**: Validate config JSON against schema
5. **GUI Config Editor**: Allow manual config editing from GUI

### Breaking Changes to Avoid

- ❌ Don't remove relative path support (breaks existing workflows)
- ❌ Don't change config file location (hardcoded in multiple places)
- ❌ Don't remove auto-detect (breaks direct notebook execution)

---

## Troubleshooting

### Issue: "Config path does not exist"

**Cause**: GUI wrote config with folder that was deleted/moved

**Solution**: Re-run GUI and reselect folder, or delete config file to trigger auto-detect

---

### Issue: "Auto-detect finds wrong month"

**Cause**: Multiple month folders, auto-detect picks latest by modification time

**Solution**: Use GUI to explicitly select correct month (creates config)

---

### Issue: "FileNotFoundError: No year folders found"

**Cause**: `data/raw/Trial Balance/` folder empty or doesn't exist

**Solution**: Verify project structure, ensure data files are present

---

## Summary

The 3-tier fallback system provides:
- ✅ **Robust operation**: Works in GUI mode, direct notebook mode, and error scenarios
- ✅ **Clear debugging**: Comprehensive logging at each tier
- ✅ **User-friendly**: GUI validates before writing config
- ✅ **Fallback safety**: Auto-detect when config missing
- ✅ **Error clarity**: Terminal errors with full paths and guidance

**Key Principle**: Always fail gracefully with clear, actionable error messages.
