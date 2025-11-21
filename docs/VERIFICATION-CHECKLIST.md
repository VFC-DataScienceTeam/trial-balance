# Final Verification Checklist

## ✅ Pre-Flight Checks

Use this checklist to verify the Config + Fallback System is working correctly.

---

## 1️⃣ GUI Launch Test

### Steps:
```bash
cd "d:\UserProfile\Documents\@ VFC\pemi-automation\trial-balance"
scripts\launchers\launch_gui.bat
```

### Expected:
- [ ] GUI window opens successfully
- [ ] Year dropdown is populated (shows 2025)
- [ ] When year selected, month dropdown populates (shows September, MONTHLY, etc.)
- [ ] "Process Report" button is enabled after selections

**Status**: ☐ Pass / ☐ Fail

---

## 2️⃣ GUI Validation Test

### Steps:
1. Launch GUI
2. Select Year: `2025`
3. Select Month: `September`
4. Click "Process Report"

### Expected:
- [ ] Log area shows: "Starting Notebook Execution"
- [ ] Log shows: "Year: 2025"
- [ ] Log shows: "Month: September"
- [ ] Log shows: "Config written: run_config.json"
- [ ] Log shows: "Data Path: D:\...\2025\September"
- [ ] Progress bar animates during execution
- [ ] No "Folder Not Found" error appears

**Status**: ☐ Pass / ☐ Fail

---

## 3️⃣ Config File Creation Test

### Steps:
```bash
cat config/run_config.json
```

### Expected Content:
```json
{
  "year": "2025",
  "month": "September",
  "data_path": "D:\\UserProfile\\Documents\\@ VFC\\pemi-automation\\trial-balance\\data\\raw\\Trial Balance\\2025\\September"
}
```

### Verify:
- [ ] File exists at `config/run_config.json`
- [ ] JSON is valid (no syntax errors)
- [ ] `data_path` is absolute (starts with drive letter)
- [ ] `data_path` points to correct folder

**Status**: ☐ Pass / ☐ Fail

---

## 4️⃣ Notebook Execution Test (via GUI)

### Steps:
1. Launch GUI
2. Select 2025 / September
3. Click "Process Report"
4. Wait for completion

### Expected Log Messages:
- [ ] `Found config file: ../config/run_config.json`
- [ ] `Config loaded successfully`
- [ ] `Data folder validated: D:\...\2025\September`
- [ ] `Source: USER SELECTION`
- [ ] `Trial Balance Files: 30` (or actual count)
- [ ] `DATA LOADED SUCCESSFULLY`
- [ ] `Data loading complete!`

### Check Log File:
```bash
ls logs/trial_balance_*.log
```
- [ ] Log file created with today's timestamp
- [ ] Log contains all expected messages above

**Status**: ☐ Pass / ☐ Fail

---

## 5️⃣ Direct Notebook Test (No Config)

### Steps:
1. Delete config file:
   ```bash
   rm config/run_config.json
   ```
2. Open notebook: `notebooks/01-rd-trial-balance-mvp.ipynb`
3. Run Cell 13 (data loading cell)

### Expected Messages:
- [ ] `Config file not found: ../config/run_config.json`
- [ ] `This is normal for direct notebook execution`
- [ ] `FALLBACK: AUTO-DETECTING LATEST DATA FOLDER`
- [ ] `Latest year found: 2025`
- [ ] `Latest month found: MONTHLY` (or September, depending on modification time)
- [ ] `Source: AUTO DETECT`
- [ ] `DATA LOADED SUCCESSFULLY`

**Status**: ☐ Pass / ☐ Fail

---

## 6️⃣ Automated Test Suite

### Steps:
```bash
python scripts/test_config_workflow.py
```

### Expected Output:
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

**Status**: ☐ Pass / ☐ Fail

---

## 7️⃣ Error Handling Test

### Steps:
1. Edit config file to point to non-existent folder:
   ```json
   {
     "year": "2025",
     "month": "NonExistentMonth",
     "data_path": "D:\\...\\2025\\NonExistentMonth"
   }
   ```
2. Open notebook and run Cell 13

### Expected:
- [ ] `Config path does not exist: D:\...\NonExistentMonth`
- [ ] `Will try fallback methods...`
- [ ] `FALLBACK: AUTO-DETECTING LATEST DATA FOLDER`
- [ ] Falls back to auto-detect successfully
- [ ] OR raises clear FileNotFoundError if auto-detect also fails

**Status**: ☐ Pass / ☐ Fail

---

## 8️⃣ Path Resolution Test

### Verify Absolute Paths:
1. Check GUI code:
   ```bash
   grep "str(data_path)" src/gui/trial_balance_app.py
   ```
   - [ ] Should find: `'data_path': str(data_path)  # Absolute path`

2. Check config file:
   ```bash
   cat config/run_config.json | grep data_path
   ```
   - [ ] Path should start with drive letter (e.g., `D:\`)

3. Check notebook handles absolute paths:
   - [ ] Cell 13 contains: `if "data_path" in config and Path(config["data_path"]).is_absolute():`

**Status**: ☐ Pass / ☐ Fail

---

## 9️⃣ Logging Test

### Steps:
1. Run GUI processing (2025/September)
2. Check log file:
   ```bash
   cat logs/trial_balance_*.log | tail -50
   ```

### Expected Sections:
- [ ] `============================================================`
- [ ] `LOADING TRIAL BALANCE DATA`
- [ ] Config detection messages
- [ ] `DATA LOADING SUMMARY`
- [ ] `Source: USER SELECTION`
- [ ] `Year: 2025`, `Month: September`
- [ ] `DATA LOADED SUCCESSFULLY`

**Status**: ☐ Pass / ☐ Fail

---

## 🔟 Documentation Completeness

### Check Files Exist:
- [ ] `docs/config-fallback-system.md` (architecture)
- [ ] `docs/QUICKSTART-CONFIG-FALLBACK.md` (quick reference)
- [ ] `docs/IMPLEMENTATION-SUMMARY.md` (this summary)
- [ ] `scripts/test_config_workflow.py` (test script)
- [ ] Updated `README.md` (Quick Start section)

**Status**: ☐ Pass / ☐ Fail

---

## ✅ Final Verification

### All Tests Must Pass:
- [ ] 1️⃣ GUI Launch Test
- [ ] 2️⃣ GUI Validation Test
- [ ] 3️⃣ Config File Creation Test
- [ ] 4️⃣ Notebook Execution Test (via GUI)
- [ ] 5️⃣ Direct Notebook Test (No Config)
- [ ] 6️⃣ Automated Test Suite
- [ ] 7️⃣ Error Handling Test
- [ ] 8️⃣ Path Resolution Test
- [ ] 9️⃣ Logging Test
- [ ] 🔟 Documentation Completeness

---

## 🎯 Overall Status

**Total Tests**: 10  
**Tests Passed**: _____ / 10  
**Tests Failed**: _____ / 10  

**System Ready for Production**: ☐ Yes / ☐ No

---

## 📝 Notes

Use this section to record any issues or observations during testing:

```
[Date] [Test #] [Issue/Observation]

Example:
2025-01-15 | Test 4 | Notebook took 2 minutes to process 30 CSV files
2025-01-15 | Test 7 | Auto-detect correctly fell back when config was invalid
```

---

## 🔧 If Any Test Fails

### Debugging Steps:
1. **Check log files**: `logs/trial_balance_*.log`
2. **Verify folder structure**: `data/raw/Trial Balance/2025/September/`
3. **Check Python environment**: `python --version` (should be 3.12.2)
4. **Verify dependencies**: `pip list | grep papermill`
5. **Review error messages**: Full error traceback in log or terminal
6. **Check config file**: `cat config/run_config.json`
7. **Run test script**: `python scripts/test_config_workflow.py`

### Common Issues:

| Issue | Solution |
|-------|----------|
| GUI doesn't launch | Check Python path in `launch_gui.bat` |
| "Folder Not Found" | Verify `data/raw/Trial Balance/2025/September/` exists |
| Notebook FileNotFoundError | Run test script to diagnose |
| Config has relative path | GUI should write absolute, check GUI code |
| Auto-detect picks wrong month | Use GUI for explicit selection |

---

**Verification Performed By**: _________________  
**Date**: _________________  
**Result**: ☐ All Pass / ☐ Some Failures (see notes)
