# 🚀 Getting Started - Trial Balance Automation

## Step-by-Step Guide for Business Users

### ⚙️ Step 1: First-Time Setup (Do This Once)

1. Open the project folder:
   ```
   D:\UserProfile\Documents\@ VFC\pemi-automation\trial-balance\
   ```

2. Navigate to:
   ```
   scripts\launchers\
   ```

3. **Double-click**: `setup_env_trial_balance.bat`

4. Wait for installation to complete (may take 2-5 minutes)

✅ You're done with setup! You never need to run this again.

---

### 📊 Step 2: Daily Usage - Process Reports

1. **Go back to the project root folder**:
   ```
   D:\UserProfile\Documents\@ VFC\pemi-automation\trial-balance\
   ```

2. **Double-click**: `launch_gui.bat` 
   
   🎯 This is the ONLY file you need for daily work!

3. **In the GUI window**:
   - Select **Year** (e.g., 2025)
   - Select **Month** (e.g., September)
   - **Choose Output Location**:
     - **Shared Drive (X:\Trail Balance)** - Save to shared drive (default, recommended for team access)
     - **Local Storage (Project Folder)** - Save to your computer (for personal/backup copies)
   - 💡 The path display below shows exactly where reports will be saved
   - Click **"📊 Process Report"**

4. **Wait for processing** (watch the log window)
   - Processing time: ~1-3 minutes depending on data size
   - Green "✅" messages = success
   - Red "❌" messages = error (contact IT)

5. **View Results**:
   - Check "📊 Generated Reports" list in GUI
   - Click **"📂 Open Results Folder"** to see Excel files

---

## 📁 Where Are My Files?

### Input Files (What You Provide):
```
data/raw/Trial Balance/
└── 2025/
    └── September/
        ├── Trial Balance/
        │   ├── 09-01-2025.csv
        │   ├── 09-02-2025.csv
        │   └── ... (all daily files)
        └── Chart of Accounts/
            └── RD - Chart of Accounts.csv
```

### Output Files (What Gets Generated):

#### Reports Location (You Choose!):

**Option 1: Shared Drive (Default)**
```
X:\Trail Balance\data\processed\Trail Balance\2025\
├── Trial_Balance.xlsx
└── Trial Balance Monthly.xlsx
```

**Option 2: Local Storage**
```
D:\UserProfile\Documents\@ VFC\pemi-automation\trial-balance\data\processed\Trail Balance\2025\
├── Trial_Balance.xlsx
└── Trial Balance Monthly.xlsx
```

#### Other Output Files (Always Local):

| Report Type | Location | Filename Example |
|------------|----------|------------------|
| **📋 COA Mapping** | `data/references/COA Mapping/` | `Chart of Accounts Mapping as of 09.30.2025.xlsx` |
| **📓 Executed Notebook** | `notebooks/executed_trial_balance_reports/` | `trial_balance_report_20251121_143022.ipynb` |
| **📄 Log File** | `logs/` | `trial_balance_20251121_143022.log` |

📖 See `OUTPUT_DIRECTORIES.md` for complete details.

---

## 🔧 Troubleshooting

### Problem: GUI won't open
**Solution**: 
1. Make sure you ran `setup_env_trial_balance.bat` first
2. Check if Python is installed: Open Command Prompt and type `python --version`

### Problem: "Virtual environment not found"
**Solution**: 
Run `scripts\launchers\setup_env_trial_balance.bat` again

### Problem: "Data folder not found"
**Solution**: 
1. Check that your CSV files are in the correct folder structure (see above)
2. Make sure the Year/Month folders match what you selected in GUI
3. Look at the log window for the exact path it's trying to load

### Problem: Processing fails midway
**Solution**: 
1. Check the log file in `logs/` folder (newest file)
2. Look for red error messages
3. Common issues:
   - Missing CSV files
   - Corrupted data in CSV
   - Missing Chart of Accounts file
   - New GL accounts not in COA mapping

### Problem: Can't find the Excel report
**Solution**: 
Click **"📂 Open Results Folder"** button in GUI - it opens the exact location!

### Problem: Reports not saving to shared drive
**Solution**: 
1. Check dropdown is set to "Shared Drive (X:\Trail Balance)"
2. Verify path display shows blue text with X:\ drive
3. Ensure shared drive is accessible (open File Explorer → X:\Trail Balance)
4. Check processing log for "💾 Output Location: Shared Drive" message

### Problem: Want to save reports to both locations
**Solution**: 
1. Process with "Shared Drive" selected first
2. Change dropdown to "Local Storage"
3. Process again - this creates a local backup copy

---

## 📞 Need Help?

**Check these files**:
1. `README.md` - Complete project documentation
2. `OUTPUT_DIRECTORIES.md` - Where all files are saved
3. `scripts/launchers/README.md` - Explanation of launcher files
4. Log files in `logs/` folder - Detailed execution history

**Contact**: VFC Data Science Team

---

## 🎓 For Developers

If you need to modify the notebook or GUI code:

1. **Notebook**: `notebooks/01-rd-trial-balance-mvp.ipynb`
2. **GUI Code**: `src/gui/trial_balance_app.py`
3. **Dependencies**: `requirements.txt`

All processing logic lives in the notebook. The GUI just:
- Lets users select year/month
- Writes config file
- Runs notebook via papermill
- Shows results

⚠️ **DO NOT modify output paths in the notebook** - they follow a standard structure.
