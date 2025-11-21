# How the Batch File and Paths Work

## 📁 File Structure Overview

```
trial-balance/                              ← PROJECT ROOT
├── src/
│   └── gui/
│       └── trial_balance_app.py           ← GUI application
├── notebooks/
│   ├── 01-rd-trial-balance-mvp.ipynb      ← Main notebook
│   └── executed_trial_balance_reports/    ← Output notebooks
├── data/
│   └── raw/
│       └── Trial Balance/
│           └── 2025/
│               └── September/             ← Data files
├── scripts/
│   └── launchers/
│       └── launch_gui.bat                 ← Launcher
└── launch_trial_balance.bat               ← Root launcher
```

---

## 🔧 How `launch_gui.bat` Works

### Step-by-Step Execution:

```batch
1. Set SCRIPT_DIR = scripts/launchers/        # Where batch file lives
2. Set PROJECT_ROOT = scripts/launchers/../.. # Go up 2 dirs = project root
3. cd /d PROJECT_ROOT                         # Change to project root
4. call .venv\Scripts\activate.bat            # Activate Python environment
5. start /D PROJECT_ROOT python src\gui\trial_balance_app.py  # Launch GUI FROM project root
```

### Key Point:
The `/D` flag ensures Python runs **with project root as working directory**, which is critical for paths to work correctly.

---

## 🗺️ Path Resolution in the Application

### 1. **GUI Application Paths** (`src/gui/trial_balance_app.py`)

```python
# Calculate project root from GUI file location
self.project_root = Path(__file__).parent.parent.parent
# __file__ = src/gui/trial_balance_app.py
# .parent  = src/gui/
# .parent  = src/
# .parent  = trial-balance/ (PROJECT ROOT) ✅

# All paths are now absolute from project root
self.base_path = self.project_root / 'data' / 'raw' / 'Trial Balance'
notebook_path = self.project_root / 'notebooks' / '01-rd-trial-balance-mvp.ipynb'
output_dir = self.project_root / 'notebooks' / 'executed_trial_balance_reports'
```

**Why absolute paths?**
- Works regardless of current working directory
- No ambiguity about location
- Prevents "file not found" errors

---

### 2. **Notebook Paths** (`notebooks/01-rd-trial-balance-mvp.ipynb`)

```python
def load_trial_balance_data(base_path='../data/raw/Trial Balance'):
    # Notebook is in: notebooks/
    # ../ goes up to: trial-balance/ (project root)
    # Then: data/raw/Trial Balance ✅
```

**Why relative path in notebook?**
- Notebooks typically run from their own directory
- `../` goes up one level to project root
- Papermill executes notebook with proper working directory

---

## 🔄 How Papermill Execution Works

When GUI clicks "📊 Process Report":

```python
# 1. GUI builds command
cmd = [
    'papermill',
    str(notebook_path),  # Absolute: C:/.../trial-balance/notebooks/01-rd-trial-balance-mvp.ipynb
    str(output_path),     # Absolute: C:/.../trial-balance/notebooks/executed_trial_balance_reports/...
    '-p', 'year', '2025',
    '-p', 'month', 'September'
]

# 2. Papermill executes notebook
# - Opens notebook at absolute path
# - Injects parameters (year, month)
# - Executes each cell sequentially
# - Notebook's relative paths (../) work because papermill preserves context
# - Saves output to absolute path
```

---

## 📊 Data Flow

```
User clicks "Process Report"
    ↓
GUI (src/gui/trial_balance_app.py)
    ↓ (uses absolute paths)
Papermill command executed
    ↓
Notebook (notebooks/01-rd-trial-balance-mvp.ipynb)
    ↓ (uses relative paths from notebooks/)
Loads data from (../data/raw/Trial Balance/2025/September/)
    ↓
Processes data (consolidate, pivot, match COA)
    ↓
Exports results to:
    - reports/trial_balance_outputs/         (Excel files)
    - data/references/COA Mapping/           (Updated COA)
    - notebooks/executed_trial_balance_reports/ (Executed notebook)
```

---

## ✅ Why This Works

### Before (Broken after reorganization):
```python
# GUI was in notebooks/, used relative paths
self.base_path = Path('./data/raw/Trial Balance')
# Worked when GUI was in notebooks/
# BROKE when GUI moved to src/gui/
```

### After (Fixed with absolute paths):
```python
# GUI calculates project root dynamically
self.project_root = Path(__file__).parent.parent.parent
self.base_path = self.project_root / 'data' / 'raw' / 'Trial Balance'
# Works from ANY location ✅
```

---

## 🎯 Testing the Paths

### Test 1: Check GUI finds data folder
```bash
cd "d:\UserProfile\Documents\@ VFC\pemi-automation\trial-balance"
python src/gui/trial_balance_app.py
# Should show year/month dropdowns populated ✅
```

### Test 2: Check notebook can load data
```bash
cd notebooks
jupyter notebook 01-rd-trial-balance-mvp.ipynb
# Run cells - should find ../data/raw/Trial Balance/ ✅
```

### Test 3: Check batch file launches correctly
```bash
# Double-click: scripts/launchers/launch_gui.bat
# Should open GUI with data folders visible ✅
```

---

## 🐛 Common Issues & Solutions

### Issue: "Base path not found"
**Cause:** Working directory is wrong  
**Solution:** 
- Batch file uses `/D PROJECT_ROOT` to set working directory
- GUI uses absolute paths calculated from `__file__`

### Issue: Notebook can't find data
**Cause:** Notebook uses relative path `../data/...`  
**Solution:** 
- Papermill executes from project root
- Notebook's `../` correctly resolves to project root
- No changes needed to notebook paths

### Issue: GUI launches but dropdowns are empty
**Cause:** Data folder doesn't exist or has no year folders  
**Solution:**
- Check: `data/raw/Trial Balance/2025/September/` exists
- Verify folder structure matches expected layout
- Check GUI log window for error messages

---

## 📝 Summary

| Component | Location | Path Type | Base Path |
|-----------|----------|-----------|-----------|
| **Batch File** | `scripts/launchers/` | N/A | Sets CWD to project root |
| **GUI App** | `src/gui/` | Absolute | Calculates from `__file__` |
| **Notebook** | `notebooks/` | Relative | `../` from notebook location |
| **Data Files** | `data/raw/` | N/A | Target for all paths |

### The Magic:
1. Batch file launches Python **from project root**
2. GUI calculates project root **dynamically**
3. Notebook uses **relative paths** that work from project root
4. Papermill preserves **execution context**

**Result:** Everything works regardless of where the code lives! ✅
