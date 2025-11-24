# Data Source & Output Location Selection Guide

**Feature Version:** 2.0  
**Date Added:** November 21, 2025  
**Last Updated:** November 24, 2025  
**Purpose:** Choose where to load input data and save output reports with connection status monitoring

---

## Overview

The GUI now provides complete control over both input and output locations:

### **Load Data From** (Input Location)
- **Local Storage** (Project Folder) - Default, load from local disk
- **Shared Drive** (X:\Trail Balance) - Load from network shared drive

### **Save Output To** (Output Location)
- **Shared Drive** (X:\Trail Balance) - For team collaboration and central storage
- **Local Storage** (Project Folder) - For personal copies or when offline

### **Connection Status Indicators**
- **✓ Connected** (Green) - Location is accessible
- **✗ Not Found** (Orange) - Path doesn't exist  
- **✗ No Access** (Red) - Permission or network error

---

## How to Use

### Step 1: Launch the GUI
Double-click `launch_gui.bat` in the project root folder.

### Step 2: Select Input Location
In the GUI window, you'll see a dropdown labeled **"Load Data From:"**

**Two options are available:**

#### Option 1: Local Storage (Project Folder) - **DEFAULT**
```
✓ Default option
✓ Load from local disk
✓ Faster access
✓ Works offline
```

**Connection Status:** Green checkmark (✓ Connected) appears if accessible

#### Option 2: Shared Drive (X:\Trail Balance)
```
✓ Team collaboration
✓ Centralized data source
✓ Network drive access
✓ Multiple users can access same data
```

**Connection Status:** Shows ✓ Connected / ✗ Not Found / ✗ No Access

---

### Step 3: Select Output Location
Below the input selector, you'll see **"Save Output To:"**

**Two options are available:**

#### Option 1: Shared Drive (X:\Trail Balance) - **DEFAULT**
```
✓ Recommended for daily operations
✓ Team members can access reports
✓ Centralized storage
✓ Automatic backup (IT managed)
```

**Path Preview (Blue Text):**
```
X:\Trail Balance\data\processed\Trail Balance\
```

**Connection Status:** Shows ✓ Connected / ✗ Not Found / ✗ No Access

#### Option 2: Local Storage (Project Folder)
```
✓ Personal backup copy
✓ Works offline
✓ Faster write speed
✓ Local disk space used
```

**Path Preview (Green Text):**
```
D:\UserProfile\Documents\@ VFC\pemi-automation\trial-balance\data\processed\Trail Balance\
```

**Connection Status:** Shows ✓ Connected / ✗ Not Found / ✗ No Access

### Step 4: Verify Connection Status
**Before processing**, check the connection indicators:
- Both should show **✓ Connected** (green)
- If you see **✗ Not Found** or **✗ No Access**, fix the issue first
- Shared drive issues typically mean network not connected or drive not mapped

### Step 5: Process Reports
1. Select Year and Month as usual
2. Verify both locations show **✓ Connected**
3. Click "📊 Process Report"
4. Watch the processing log - you'll see:
   ```
   📂 Input data will be loaded from: Shared Drive
     ✓ Shared drive is accessible
   💾 Output will be saved to: Shared Drive
     ✓ Shared drive is accessible
   📂 Output base path: X:\Trail Balance\data\processed\Trail Balance
   ```

### Step 6: Access Results
Click **"📂 Open Results Folder"** - the button automatically opens the location you selected!

---

## Connection Status Monitoring

### Understanding Status Indicators

| Indicator | Color | Meaning | Action |
|-----------|-------|---------|--------|
| **✓ Connected** | Green | Path is accessible | Safe to proceed |
| **✗ Not Found** | Orange | Path doesn't exist | Check path, create folder if needed |
| **✗ No Access** | Red | Permission/network error | Check network, permissions, drive mapping |

### Automatic Checks

The GUI automatically checks connection status:
1. **On startup** - Both locations checked immediately
2. **When changing dropdown** - New location checked instantly
3. **Logs status** - Messages appear in Processing Log

### Example Log Messages

**Successful Connection:**
```
📂 Input data will be loaded from: Shared Drive
  ✓ Shared drive is accessible
```

**Connection Problem:**
```
📂 Input data will be loaded from: Shared Drive
  ⚠️ WARNING: Shared drive not accessible! Check network connection.
```

### Troubleshooting Connection Issues

**If Shared Drive shows ✗ No Access:**
1. Open File Explorer → Navigate to `X:\`
2. If you can't access X:\ drive, it's not mapped
3. Contact IT to map the shared drive
4. After mapping, restart the GUI

**If Shared Drive shows ✗ Not Found:**
1. Check if the specific folder exists: `X:\Trail Balance`
2. Verify you have the correct drive letter
3. Check network connection (VPN if working remotely)

**If Local Storage shows ✗ Not Found:**
1. The project folder structure might be incomplete
2. Run the setup script to create required folders
3. Check if you have write permissions to the folder

---

## Use Cases

### Input Location: When to Use Each

**Use Shared Drive for Input When:**
- ✅ Data is centrally maintained on shared drive
- ✅ Multiple users need to process same data
- ✅ Working with live, up-to-date data
- ✅ Team collaboration on same dataset

**Use Local Storage for Input When:**
- ✅ Working with test data
- ✅ Processing historical data archived locally
- ✅ Shared drive is slow or unavailable
- ✅ Need faster read performance

### Output Location: When to Use Each

**Use Shared Drive for Output When:**
- ✅ Reports need to be accessible by team members
- ✅ Standard month-end processing
- ✅ Reports will be reviewed by others

✅ **Permanent storage**
- Official records that need to be archived
- Compliance and audit requirements
- Version control by IT team

✅ **Collaboration**
- Multiple people processing different months
- Shared reference for meetings
- Consistent file location across team

### When to Use Local Storage

✅ **Testing & Development**
- Testing new data files
- Experimenting with parameters
- Don't want to clutter shared drive

✅ **Offline Work**
- Shared drive is unavailable
- Working remotely without VPN
- Network issues

✅ **Personal Backup**
- Keep a local copy for reference
- Quick access without network
- Redundancy

✅ **Performance**
- Processing large datasets
- Local SSD is faster than network drive
- Copy to shared drive later

---

## Technical Details

### Configuration File
When you select an output location, the GUI writes it to:
```
config/run_config.json
```

**Example content:**
```json
{
  "year": "2025",
  "month": "September",
  "data_path": "X:\\Trail Balance\\data\\raw\\Trial Balance\\2025\\September",
  "output_base_path": "X:\\Trail Balance\\data\\processed\\Trail Balance"
}
```

The notebook reads `output_base_path` to determine where to save reports.

### What Gets Saved Where

| File Type | Shared Drive Option | Local Storage Option |
|-----------|---------------------|----------------------|
| **Trial_Balance.xlsx** | X:\Trail Balance\data\processed\Trail Balance\{YEAR}\ | {project}\data\processed\Trail Balance\{YEAR}\ |
| **Trial Balance Monthly.xlsx** | X:\Trail Balance\data\processed\Trail Balance\{YEAR}\ | {project}\data\processed\Trail Balance\{YEAR}\ |
| **COA Mapping** | Always local: {project}\data\references\COA Mapping\ | Always local: {project}\data\references\COA Mapping\ |
| **Executed Notebooks** | Always local: {project}\notebooks\executed_trial_balance_reports\ | Always local: {project}\notebooks\executed_trial_balance_reports\ |
| **Log Files** | Always local: {project}\logs\ | Always local: {project}\logs\ |

**Note:** Only the main Excel reports honor the output location setting. Reference files, logs, and executed notebooks always save locally for faster access and debugging.

### Directory Structure Created

Both locations follow the same structure:
```
{selected_base_path}/
└── Trail Balance/
    └── 2025/                    ← Year-based folders
        ├── Trial_Balance.xlsx
        └── Trial Balance Monthly.xlsx
```

Folders are created automatically if they don't exist.

---

## Workflow Examples

### Example 1: Standard Month-End Processing (Full Shared Drive)
```
1. Load Data From: "Shared Drive (X:\Trail Balance)"  → ✓ Connected
2. Save Output To: "Shared Drive (X:\Trail Balance)"  → ✓ Connected
3. Year: 2025, Month: September
4. Process Report
5. Result: Reads from X:\...\raw\ and saves to X:\...\processed\2025\
6. Team members access from X:\ drive
```

### Example 2: Load from Shared Drive, Save Locally (Backup)
```
1. Load Data From: "Shared Drive (X:\Trail Balance)"  → ✓ Connected
2. Save Output To: "Local Storage (Project Folder)"   → ✓ Connected  
3. Process Report
4. Result: Reads from shared drive, creates local backup
5. Good for: Personal backup, working offline later
```

### Example 3: Create Both Shared and Local Copies
```
1. Load Data From: "Shared Drive (X:\Trail Balance)"
2. Save Output To: "Shared Drive (X:\Trail Balance)"
3. Process Report → Saves to X:\ drive
4. Change output dropdown to: "Local Storage (Project Folder)"
5. Process Report again → Saves to local disk
6. Result: Two identical copies in different locations
```

### Example 3: Test Data Processing Locally First
```
1. Select: "Local Storage (Project Folder)"
2. Process test data
3. Review results locally
4. If satisfied, switch to: "Shared Drive (X:\Trail Balance)"
5. Process final data for team access
```

---

## Troubleshooting

### Problem: Dropdown is grayed out
**Cause:** GUI hasn't fully loaded  
**Solution:** Wait 1-2 seconds after launch, dropdown will become active

### Problem: Path display doesn't change
**Cause:** Event handler not triggered  
**Solution:** Click away from dropdown, then click it again and select option

### Problem: Reports still saving to wrong location
**Cause:** Old config file cached  
**Solution:** 
1. Close GUI
2. Delete `config/run_config.json`
3. Relaunch GUI and select location again

### Problem: Shared drive path shows "Access Denied"
**Cause:** Network permissions or drive not mapped  
**Solution:**
1. Open File Explorer
2. Navigate to X:\Trail Balance
3. If you can't access it, contact IT to map the drive
4. Retry processing after drive is accessible

### Problem: "Open Results Folder" opens wrong location
**Cause:** GUI state not synchronized  
**Solution:** Close and relaunch GUI, then process again

---

## Best Practices

### ✅ DO:
- Use **Shared Drive** for official month-end reports
- Use **Local Storage** for testing and development
- Check the path display (color-coded) before processing
- Create local backups of critical reports before re-processing
- Document which location you used in your workflow notes

### ❌ DON'T:
- Process the same month/year to both locations without renaming files (they'll overwrite)
- Forget to switch back to Shared Drive after testing locally
- Assume reports are in both locations - check the path display
- Process to local storage and expect team members to access it

---

## Visual Guide

### GUI Components

```
┌──────────────────────────────────────────────────────────┐
│  Select Year:      [2025 ▼]                             │
│  Select Month:     [September ▼]                         │
│                                                           │
│  Load Data From:   [Shared Drive... ▼]  ✓ Connected  │  ← Input Location + Status
│  Selected Path:    X:\Trail Balance\...\September        │
│                                                           │
│  Save Output To:   [Shared Drive... ▼]  ✓ Connected  │  ← Output Location + Status
│  Output Path:      X:\Trail Balance\data\...            │  ← Blue = Shared, Green = Local
│                                                           │
│  [📊 Process Report]  [📂 Open Results Folder]          │
└──────────────────────────────────────────────────────────┘
```

### Color Coding

- **🔵 Blue Text** = Shared Drive selected (X:\Trail Balance\...)
- **🟢 Green Text** = Local Storage selected (D:\UserProfile\...)

---

## Implementation Notes (For Developers)

### GUI Changes (`src/gui/trial_balance_app.py`)

**Lines 91-99:** Dropdown creation
```python
self.output_location = tk.StringVar(value="shared_drive")
output_combo = ttk.Combobox(self.selection_frame, textvariable=self.output_location, state='readonly')
output_combo['values'] = ('Shared Drive (X:\\Trail Balance)', 'Local Storage (Project Folder)')
output_combo.bind('<<ComboboxSelected>>', self.on_output_location_changed)
```

**Lines 233-244:** Event handler
```python
def on_output_location_changed(self, event):
    selection = self.output_location.get()
    if "Shared Drive" in selection:
        output_path = "X:\\Trail Balance\\data\\processed\\Trail Balance\\"
        self.output_path_label.config(text=output_path, foreground='blue')
    else:
        output_path = str(self.project_root / 'data' / 'processed' / 'Trail Balance')
        self.output_path_label.config(text=output_path, foreground='green')
```

**Lines 411-428:** Config writing
```python
selection = self.output_location.get()
if "Shared Drive" in selection:
    output_base_path = "X:\\Trail Balance\\data\\processed\\Trail Balance"
else:
    output_base_path = str(self.project_root / 'data' / 'processed' / 'Trail Balance')

config = {
    'year': year,
    'month': month,
    'data_path': str(data_path),
    'output_base_path': output_base_path  # New key
}
```

### Notebook Changes (`01-rd-trial-balance-mvp.ipynb`)

**Cell 91 & Cell 96:** Both export functions updated
```python
# Read output_base_path from config if available, otherwise use default
default_base_dir = os.path.join('..', 'data', 'processed', 'Trail Balance')
base_dir = config.get('output_base_path', default_base_dir)

print(f"📂 Output base path: {base_dir}")

# Output directory now only contains the year
output_dir = os.path.join(base_dir, year)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-21 | Initial release with output location dropdown, color-coded display, dynamic config |
| 2.0 | 2025-11-24 | Added input location selector, connection status indicators, real-time monitoring |

---

## FAQ

**Q: Can I change the shared drive path (X:\Trail Balance)?**  
A: Yes, edit line 237 in `src/gui/trial_balance_app.py` and line 414 to change the shared drive path.

**Q: Can I add a third output location (e.g., USB drive)?**  
A: Yes, add another option to the dropdown values (line 94) and update the event handler (lines 233-244) and config writer (lines 411-428).

**Q: Does this work with the shared drive input data?**  
A: Yes! Input and output locations are independent. You can read from X:\Trail Balance\data\raw\ and save to local storage, or vice versa.

**Q: What if I want all files (logs, COA, notebooks) on shared drive?**  
A: You would need to modify the notebook to honor output_base_path for those files as well. Currently only the main Excel reports use the selected location.

**Q: Can I automate this with a script?**  
A: Yes! Set the `output_base_path` key directly in `config/run_config.json` before running the notebook with papermill.

---

**Need Help?** Contact the VFC Data Science Team or check `docs/GETTING_STARTED.md` for general usage guidance.
