# Launchers Directory

## Active Files

### `setup_env_trial_balance.bat`
**Purpose**: First-time environment setup
**When to use**: Run this ONCE when setting up the project for the first time
**What it does**:
- Creates Python virtual environment in `.venv/`
- Installs all dependencies from `requirements.txt`
- Registers Jupyter kernel for notebook execution

**How to run**:
```bash
# From project root
scripts\launchers\setup_env_trial_balance.bat
```

---

## Main Application Launcher

⚠️ **DO NOT use files in this directory to launch the GUI**

**Instead, use the launcher in the project root**:
```
trial-balance\launch_gui.bat  ← Use this one!
```

The root launcher is the official, up-to-date version that:
- ✅ Activates the virtual environment automatically
- ✅ Launches the GUI from the correct working directory
- ✅ Handles all paths correctly for papermill execution

---

## Cleaned Up Files

The following outdated files have been **removed**:
- ❌ `launch_gui.bat` (duplicate - use root version instead)
- ❌ `run_trial_balance_app.bat` (outdated launcher)
- ❌ `test_gui.bat` (testing file no longer needed)
- ❌ `run_trial_balance_report.bat` (old CLI approach - replaced by GUI)

---

## Project Structure

```
trial-balance/
├── launch_gui.bat              ← 🚀 START HERE (Main launcher)
├── requirements.txt            ← Dependencies list
├── .venv/                      ← Virtual environment (created by setup)
├── src/
│   └── gui/
│       └── trial_balance_app.py  ← GUI application code
├── notebooks/
│   └── 01-rd-trial-balance-mvp.ipynb  ← Main processing notebook
└── scripts/
    └── launchers/
        └── setup_env_trial_balance.bat  ← First-time setup only
```

---

## Quick Start Guide

### First Time Setup:
1. Run `scripts\launchers\setup_env_trial_balance.bat`
2. Wait for installation to complete

### Daily Use:
1. Double-click `launch_gui.bat` (in project root)
2. Select Year and Month
3. Click "📊 Process Report"
4. Done! 🎉
