# Output Location Selection Guide

**Feature Version:** 1.0  
**Date Added:** November 21, 2025  
**Purpose:** Allow users to choose where trial balance reports are saved

---

## Overview

The Output Location Selector gives you flexibility to save trial balance reports to either:
- **Shared Drive** (X:\Trail Balance) - For team collaboration and central storage
- **Local Storage** (Your computer) - For personal copies or when offline

---

## How to Use

### Step 1: Launch the GUI
Double-click `launch_gui.bat` in the project root folder.

### Step 2: Select Output Location
In the GUI window, you'll see a dropdown labeled **"Save Output To:"**

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

### Step 3: Process Reports
1. Select Year and Month as usual
2. Click "📊 Process Report"
3. Watch the processing log - you'll see:
   ```
   💾 Output Location: Shared Drive
   📂 Output base path: X:\Trail Balance\data\processed\Trail Balance
   ```

### Step 4: Access Results
Click **"📂 Open Results Folder"** - the button automatically opens the location you selected!

---

## Use Cases

### When to Use Shared Drive

✅ **Daily reporting workflow**
- Reports need to be accessible by team members
- Standard month-end processing
- Reports will be reviewed by others

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

### Example 1: Standard Month-End Processing
```
1. Select: "Shared Drive (X:\Trail Balance)"
2. Year: 2025, Month: September
3. Process Report
4. Result: Reports saved to X:\Trail Balance\data\processed\Trail Balance\2025\
5. Team members access from X:\ drive
```

### Example 2: Create Both Shared and Local Copies
```
1. Select: "Shared Drive (X:\Trail Balance)"
2. Process Report → Saves to X:\ drive
3. Change dropdown to: "Local Storage (Project Folder)"
4. Process Report again → Saves to local disk
5. Result: Two identical copies in different locations
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
┌─────────────────────────────────────────────────┐
│  Select Year:      [2025 ▼]                    │
│  Select Month:     [September ▼]                │
│  Data Path:        D:\...\2025\September        │
│                                                  │
│  Save Output To:   [Shared Drive (X:\Trail...) ▼]│  ← Output Location Dropdown
│  Output Path:      X:\Trail Balance\data\...    │  ← Path Display (Blue = Shared, Green = Local)
│                                                  │
│  [📊 Process Report]  [📂 Open Results Folder]  │
└─────────────────────────────────────────────────┘
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
| 1.0 | 2025-11-21 | Initial release with dropdown selector, color-coded display, and dynamic config writing |

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
