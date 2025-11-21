# Quick Reference: Config + Fallback System

## How to Run the System

### Option 1: GUI (Recommended)
```bash
cd "d:\UserProfile\Documents\@ VFC\pemi-automation\trial-balance"
scripts\launchers\launch_gui.bat
```
1. Select Year from dropdown
2. Select Month from dropdown
3. Click "Process Report"
4. Wait for completion (log shows real-time progress)

### Option 2: Direct Notebook Execution
```bash
cd "d:\UserProfile\Documents\@ VFC\pemi-automation\trial-balance\notebooks"
jupyter notebook 01-rd-trial-balance-mvp.ipynb
# Run All Cells (Shift+Enter through all cells)
```
- Will auto-detect latest year/month if no config file exists

---

## What Happens Under the Hood

### GUI Flow
```
User Selection → Validate Folder → Write Config (absolute path) → Execute Notebook → Load from Config
```

### Direct Execution Flow
```
No Config File → Auto-Detect Latest → Load Data → Process
```

---

## Folder Structure Expected

```
data/raw/Trial Balance/
├── 2025/
│   ├── September/
│   │   ├── Trial Balance/
│   │   │   ├── 09-01-2025.csv
│   │   │   ├── 09-02-2025.csv
│   │   │   └── ... (all daily CSVs)
│   │   └── Chart of Accounts/
│   │       └── RD - Chart of Accounts.csv
│   └── October/
│       └── ... (same structure)
└── 2024/
    └── ... (same structure)
```

---

## Config File Format

**Location**: `config/run_config.json`

**Format**:
```json
{
  "year": "2025",
  "month": "September",
  "data_path": "D:\\...\\data\\raw\\Trial Balance\\2025\\September"
}
```

**Notes**:
- `data_path` should be **absolute** (GUI creates this)
- Relative paths supported for backward compatibility
- Notebook reads this file at Cell 13

---

## Logging

**Location**: `logs/trial_balance_YYYYMMDD_HHMMSS.log`

**Key Messages**:

| Message | Meaning |
|---------|---------|
| `Found config file: ...` | Config file detected (Tier 1) |
| `Data folder validated: ...` | Config path exists and valid |
| `FALLBACK: AUTO-DETECTING...` | No config, using auto-detect (Tier 2) |
| `Auto-detected path: ...` | Auto-detect successful |
| `FATAL: Raw data folder not found` | Neither config nor auto-detect worked (Tier 3) |
| `DATA LOADED SUCCESSFULLY` | Data loading complete |

---

## Troubleshooting

### Problem: GUI doesn't launch
**Solution**: Check Python path in `launch_gui.bat`, ensure virtual environment activated

### Problem: "Folder Not Found" error in GUI
**Solution**: Verify folder exists in `data/raw/Trial Balance/{year}/{month}`

### Problem: Notebook loads wrong month
**Solution**: Either:
- Use GUI to select correct month (creates config)
- Delete `config/run_config.json` and notebook will auto-detect latest

### Problem: FileNotFoundError in notebook
**Solution**: Check:
1. Does `data/raw/Trial Balance/` exist?
2. Are there year folders (2025, 2024)?
3. Are there month folders inside year folders?
4. Do month folders contain `Trial Balance/` subfolder with CSVs?

---

## Testing

### Test all scenarios:
```bash
python scripts/test_config_workflow.py
```

Expected output:
```
✅ PASSED: Absolute Path (GUI)
✅ PASSED: Relative Path (Legacy)
✅ PASSED: Auto-Detect Fallback
```

---

## Files Modified

| File | Changes |
|------|---------|
| `src/gui/trial_balance_app.py` | Added folder validation, writes absolute path to config |
| `notebooks/01-rd-trial-balance-mvp.ipynb` | Cell 13: Added 3-tier fallback logic |
| `config/run_config.json` | Now contains absolute `data_path` |

---

## Key Design Principles

1. **GUI is the primary interface** for business users
2. **Config file bridges GUI and notebook** (absolute paths)
3. **Auto-detect is fallback only** (for direct notebook execution)
4. **Always fail with clear errors** (include full paths)
5. **Log everything** (transparency for debugging)

---

## Need More Details?

See comprehensive documentation: `docs/config-fallback-system.md`
