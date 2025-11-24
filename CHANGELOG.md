# Changelog

All notable changes to the Trial Balance Automation project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2025-11-24

### Added
- **Input Location Selector** - Users can now choose whether to load raw data from local storage or shared drive
  - Dropdown menu: "Load Data From" with options for Local Storage (default) or Shared Drive
  - Dynamic path updates based on selection
  - Integration with config generation (writes to `data_path` in run_config.json)
  - Commit: `391ba64`

- **Connection Status Indicators** - Real-time monitoring of data source accessibility
  - Visual status labels next to both input and output location dropdowns
  - Three status types:
    - ✓ Connected (green) - Location is accessible
    - ✗ Not Found (orange) - Path doesn't exist
    - ✗ No Access (red) - Permission or network error
  - Automatic checks on startup and when locations change
  - Logged status messages in processing log
  - New `check_connection()` method in TrialBalanceApp class
  - Commit: `ed5f8ad`

- **Enhanced Reports Display** - Improved visibility of generated files
  - Reports list now shows which location files are stored in:
    - 📁 SHARED DRIVE indicator for X:\ drive files
    - 💻 LOCAL STORAGE indicator for project folder files
  - File count summaries for each report type
  - Total file sizes displayed in MB
  - Folder path display for easy navigation
  - Auto-refreshes when output location changes
  - Commit: `391ba64`

### Fixed
- **Notebook Syntax Errors** - Resolved duplicate return statements in export functions
  - Fixed `export_financial_report()` function (Cell 91)
  - Fixed `export_segmented_summary()` function (Cell 96)
  - Issue: Two return statements on same line causing SyntaxError
  - Solution: Separated return statements into proper lines
  - Commit: `3542250`

### Changed
- **OUTPUT_LOCATION_GUIDE.md** - Updated to v2.0
  - Added comprehensive coverage of input location selector
  - Documented connection status indicators
  - Added troubleshooting section for connection issues
  - Updated workflow examples with both input and output selections
  - Added visual GUI component diagram showing status indicators

- **GETTING_STARTED.md** - Enhanced user instructions
  - Added connection status explanation in Step 2
  - Documented what each status indicator means
  - Added troubleshooting table for connection issues
  - Updated input files section to mention both locations

- **TECHNICAL_DOCUMENTATION.md** - Added GUI functions reference
  - Documented `check_connection()` method with full signature
  - Added `on_input_location_changed()` documentation
  - Updated `on_output_location_changed()` with connection checking info
  - Added `refresh_reports_list()` feature documentation
  - Documented run_config.json schema with both path fields

---

## [1.0.0] - 2025-11-21

### Added
- **Output Location Selector** - First release of location flexibility feature
  - Dropdown menu: "Save Output To" with two options:
    - Shared Drive (X:\Trail Balance) - Default
    - Local Storage (Project Folder)
  - Color-coded path display (blue for shared, green for local)
  - Dynamic config generation updates `output_base_path` in run_config.json
  - "Open Results Folder" button opens correct location based on selection
  - Notebook export functions read from config instead of hardcoded paths
  - Commit: `a454eeb`

- **Clear Log Button** - GUI enhancement for log management
  - Added button to clear processing log display
  - Allows users to reset log view between operations
  - Commit: `df836f1`

- **Documentation Organization** - Restructured project docs
  - Created `docs/` folder structure
  - Moved all documentation to organized locations
  - Added OUTPUT_LOCATION_GUIDE.md (comprehensive 344-line guide)
  - Created GETTING_STARTED.md for business users
  - Created TECHNICAL_DOCUMENTATION.md for developers
  - Added FILE_INDEX.md and OUTPUT_DIRECTORIES.md
  - Commit: `c86942c`

- **Shared Drive Integration** - Full support for network drive access
  - Tested read/write operations to X:\Trail Balance
  - Verified 30 CSV files accessible in September 2025 folder
  - Confirmed output writing to shared drive
  - Created test scripts for validation

### Changed
- **Project Structure** - Improved organization
  - All markdown docs moved to `docs/` folder
  - Created `docs/draft/` for work-in-progress documentation
  - Updated README.md to reference new documentation structure

- **GUI Layout** - Enhanced user interface
  - Added output location dropdown to selection frame
  - Added output path display with color coding
  - Improved visual feedback for user actions

---

## [0.1.0] - Initial Development

### Added
- **Core MVP Notebook** - `01-rd-trial-balance-mvp.ipynb`
  - Loads daily trial balance CSVs from year/month folders
  - Consolidates data with date column added
  - Creates pivot tables (GL Account × Fund Name)
  - Validates GL accounts against COA mapping
  - Exports updated COA mapping with new accounts flagged
  - Generates two Excel reports:
    - Trial_Balance.xlsx (5 main sheets + 16 fund sheets)
    - Trial Balance Monthly.xlsx (16 segmented fund sheets)

- **GUI Application** - `src/gui/trial_balance_app.py`
  - Tkinter-based user interface
  - Year and month selectors
  - Process Report button triggers notebook execution
  - Real-time processing log display
  - Reports list showing generated files

- **Data Loading Functions**
  - `load_reference_data()` - Generic reference data loader
  - `load_trial_balance_data()` - Daily CSV loader with date parsing
  - Support for both CSV and XLSX formats
  - Auto-detection of most recent files

- **Export Functions**
  - `export_financial_report()` - Full report with 21 sheets
  - `export_segmented_summary()` - Monthly report with 16 fund sheets
  - Custom formatting (bold headers, merged cells, number formats)
  - Grand total calculations

- **Logging System**
  - Timestamped log files in `logs/`
  - Dual output (file and console)
  - INFO/WARNING/ERROR level messages
  - File operation tracking

- **Project Infrastructure**
  - Virtual environment setup (.venv)
  - requirements.txt with all dependencies
  - Batch scripts for environment setup and GUI launch
  - Standardized folder structure (CRISP-DM aligned)

---

## Release Notes

### v2.0.0 Highlights
This major release focuses on **data source flexibility and connection reliability**. Users can now:
- Choose where to load input data (local or shared drive)
- See real-time connection status before processing
- Get visual feedback if locations are unavailable
- Process data from any accessible location
- View detailed file information in reports list

**Migration Notes:**
- No breaking changes; existing workflows continue to work
- New features are opt-in via dropdown selections
- Default behavior unchanged (local input, shared output)

### v1.0.0 Highlights
The first stable release introduced **output location flexibility**, allowing teams to:
- Save reports to shared drive for team access
- Save reports locally for personal copies or offline work
- Switch between locations without code changes
- Automatically update notebook config paths

**Breaking Changes from v0.1.0:**
- Export functions now read output path from config (previously hardcoded)
- run_config.json schema updated to include `output_base_path`

---

## Commit History

| Commit | Date | Description |
|--------|------|-------------|
| `ed5f8ad` | 2025-11-24 | ✨ Add connection status indicators for data sources |
| `3542250` | 2025-11-24 | 🐛 Fix syntax error: separate duplicate return statements |
| `391ba64` | 2025-11-24 | ✨ Add input location selector and enhanced reports display |
| `a454eeb` | 2025-11-21 | ✨ Add output location selector with dynamic config |
| `df836f1` | 2025-11-21 | ✨ Add Clear Log button to GUI |
| `c86942c` | 2025-11-21 | 📚 Organize documentation into docs folder |

---

## Future Roadmap

### Planned Features
- [ ] Automated balance validation (debits = credits check)
- [ ] Variance analysis between dates
- [ ] Automated email reporting
- [ ] Historical data comparison
- [ ] Advanced error recovery
- [ ] Unit test coverage
- [ ] Production refactoring (notebook → src/ modules)
- [ ] CLI interface option
- [ ] Database integration for audit trail

### Under Consideration
- Multi-user concurrent processing locks
- Cloud storage integration (OneDrive, SharePoint)
- Real-time shared drive sync monitoring
- Automated backup scheduling
- Report scheduling/automation

---

## Contact & Support

**Repository:** https://github.com/VFC-DataScienceTeam/trial-balance  
**Team:** VFC Data Science Team  
**Documentation:** See `docs/` folder for detailed guides

---

*Last Updated: November 24, 2025*
