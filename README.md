# Trial Balance Automation

Automated trial balance validation, reconciliation, and reporting system following the CRISP-DM framework.

## 📚 Documentation

**All documentation is organized in the [`docs/`](docs/) folder.**

👉 **[View Complete Documentation Index](docs/README.md)**

### Quick Links

| For... | Start Here |
|--------|------------|
| 🚀 **First-time users** | [Getting Started Guide](docs/GETTING_STARTED.md) |
| 📖 **Complete technical reference** | [Technical Documentation](docs/TECHNICAL_DOCUMENTATION.md) ⭐ |
| 📂 **Finding output files** | [Output Directories Guide](docs/OUTPUT_DIRECTORIES.md) |
| 📋 **All project files** | [File Index](docs/FILE_INDEX.md) |
| 🔄 **Process workflow** | [Workflow Diagrams](docs/workflow-diagram.md) |

## 📊 Visual Workflow

For a comprehensive visual representation of the automation workflow, see:
- **[Workflow Diagrams](docs/workflow-diagram.md)** - Complete Mermaid flowcharts showing data flow, processing steps, and error handling

## Project Structure (actual)

```
trial-balance/
├── .gitignore
├── .venv/                           # Virtual environment (local)
├── .vscode/                         # VS Code workspace settings
├── config/                          # Configuration files
├── data/
│   ├── raw/
│   │   └── Trial Balance/
│   │       └── 2025/
│   │           └── September/       # Daily TB CSVs and Chart of Accounts
│   ├── processed/                   # Processed outputs (currently empty)
│   └── external/                     # Third-party data sources
├── docs/
│   ├── workflow-diagram.md          # Mermaid diagrams and flowcharts
│   ├── Trail Balance Automation Flowchart.html
│   └── draft/                        # Draft documentation
├── logs/                            # Application logs (created at runtime)
├── models/                          # Model artifacts (if used)
├── notebooks/
│   ├── 01-rd-trial-balance-mvp.ipynb
│   ├── trial_balance_mvp.ipynb
│   └── README.md
├── references/
│   └── README.md                     # Reference data notes
├── reports/
│   ├── trial_balance_outputs/
│   ├── validation_reports/
│   └── variance_analysis/
├── requirements.txt
├── README.md
├── references/                       # Data dictionaries, links
├── reports/                          # Output folders and reports
├── src/
│   ├── data/                         # Data ingestion and loading code
│   ├── features/                     # Feature engineering
│   ├── models/                       # Reconciliation / ML models
│   ├── reconciliation/               # Reconciliation logic
│   ├── reporting/                    # Report generation
│   ├── utils/                        # Helper utilities
│   └── validation/                   # Validation rules and checks
├── tests/                            # Unit and integration tests
```

## Workflow (CRISP-DM Phases)

1. **Business Understanding** → `docs/draft/overview.md`
   - Define objectives, success criteria, stakeholders

2. **Data Understanding** → `notebooks/01_data_exploration/`
   - Profile raw trial balance data
   - Identify data quality issues

3. **Data Preparation** → `src/data/`, `src/validation/`
   - Clean and validate data
   - Apply business rules
   - Check balances (debits = credits)

4. **Modeling** → `src/reconciliation/`, `src/models/`
   - Reconciliation logic
   - Variance analysis
   - Anomaly detection (optional ML)

5. **Evaluation** → `reports/validation_reports/`
   - Validation results
   - Reconciliation sign-off

6. **Deployment** → `src/reporting/`
   - Generate final reports
   - Distribute to stakeholders

See [`docs/draft/crisp-dm.md`](docs/draft/crisp-dm.md) for detailed phase mapping.

## 🚀 Quick Start

📖 **Detailed instructions**: See [GETTING_STARTED.md](docs/GETTING_STARTED.md) for complete setup guide

### First Time Setup

1. **Run the setup script** (ONE TIME ONLY):
   ```bash
   scripts\launchers\setup_env_trial_balance.bat
   ```
   This creates the virtual environment and installs all dependencies.

### For Business Users (Recommended)

**Run the GUI application**:
```bash
launch_gui.bat    ← Double-click this file in the project root!
```

**Steps**:
1. Select **Year** from dropdown (e.g., 2025)
2. Select **Month** from dropdown (e.g., September)
3. Click **"📊 Process Report"** button
4. Wait for completion (real-time log in GUI)
5. Click **"📂 Open Results Folder"** to view outputs

**Output Locations**:
- 📊 **Excel Reports**: `data/processed/Trail Balance/{year}/Trial Balance Monthly.xlsx`
- 📋 **COA Mappings**: `data/references/COA Mapping/Chart of Accounts Mapping as of MM.DD.YYYY.xlsx`
- 📓 **Executed Notebooks**: `notebooks/executed_trial_balance_reports/`
- 📄 **Logs**: `logs/trial_balance_YYYYMMDD_HHMMSS.log`

📖 **See**: [OUTPUT_DIRECTORIES.md](docs/OUTPUT_DIRECTORIES.md) for complete details

---

### For Data Scientists / Developers

1. **Place raw data** in proper structure:
   ```
   data/raw/Trial Balance/
   └── {YEAR}/
       └── {MONTH}/
           ├── Trial Balance/
           │   ├── MM-DD-YYYY.csv (daily files)
           │   └── ...
           └── Chart of Accounts/
               └── RD - Chart of Accounts.csv
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the notebook**:
   - Open `notebooks/01-rd-trial-balance-mvp.ipynb`
   - Run all cells (auto-detects latest year/month if no config file)

4. **Outputs**:
   - Logs: `logs/trial_balance_YYYYMMDD_HHMMSS.log`
   - Reports: `data/processed/Trail Balance/{year}/`
   - Updated COA: `data/references/COA Mapping/`

📖 **See**: 
- [config-fallback-system.md](docs/config-fallback-system.md) for architecture details
- [TECHNICAL_DOCUMENTATION.md](docs/TECHNICAL_DOCUMENTATION.md) for complete technical reference

## Key Features

### Data Source Management
- **Dual Location Selectors**: Choose where to load input data and save outputs
  - Input: Local storage or shared drive (X:\Trail Balance)
  - Output: Local storage or shared drive (X:\Trail Balance)
- **Real-time Connection Monitoring**: Visual status indicators for data source accessibility
  - ✓ Connected (green) - Location ready to use
  - ✗ Not Found (orange) - Path doesn't exist
  - ✗ No Access (red) - Network or permission issue
- **Enhanced Reports Display**: View file locations, counts, and sizes at a glance

### Core Functionality
- **GUI-based operation**: User-friendly interface for business users
- **3-tier fallback system**: Config file → Auto-detect → Clear error
- **Automated validation**: Balance checks, GL account matching, business rules
- **Reconciliation**: Period-over-period, inter-company eliminations
- **Variance analysis**: Identify and explain significant variances
- **Comprehensive logging**: Real-time progress tracking and audit trail
- **Robust error handling**: Clear, actionable error messages with full paths

## System Architecture

### Config + Fallback System

The system uses a **3-tier approach** to determine which data folder to load:

1. **PRIMARY (Tier 1)**: User selection via GUI
   - GUI validates folder exists
   - Writes absolute path to `config/run_config.json`
   - Notebook reads config and loads data

2. **FALLBACK (Tier 2)**: Auto-detect latest year/month
   - Used when no config file exists (direct notebook execution)
   - Finds latest year folder (numeric, descending)
   - Finds latest month folder (by modification time)

3. **TERMINAL (Tier 3)**: Clear error if no data found
   - Logs full paths for debugging
   - Raises `FileNotFoundError` with actionable guidance

**Benefits**:
- ✅ Works in both GUI and direct notebook modes
- ✅ Robust error handling with clear messages
- ✅ Comprehensive logging at each tier
- ✅ Absolute paths eliminate ambiguity

📖 **See**: [config-fallback-system.md](docs/config-fallback-system.md) for complete architecture details

---

## 📚 Complete Documentation

All documentation is organized in the [`docs/`](docs/) folder:

- **[Documentation Index](docs/README.md)** - Complete guide to all documentation
- **[Getting Started](docs/GETTING_STARTED.md)** - Step-by-step user guide
- **[Technical Documentation](docs/TECHNICAL_DOCUMENTATION.md)** - Comprehensive technical reference
- **[Output Location Guide](docs/OUTPUT_LOCATION_GUIDE.md)** - Input/output location selection and connection monitoring
- **[File Index](docs/FILE_INDEX.md)** - Complete file inventory
- **[Output Directories](docs/OUTPUT_DIRECTORIES.md)** - Output locations guide
- **[Workflow Diagrams](docs/workflow-diagram.md)** - Visual process flows
- **[Changelog](CHANGELOG.md)** - Version history and release notes

**For technical details**, see [TECHNICAL_DOCUMENTATION.md](docs/TECHNICAL_DOCUMENTATION.md) which includes:
- Complete data inventory
- DataFrame transformations
- Functions reference with code examples
- Reproducibility guide
- Extension points for customization

