# Trial Balance Automation - Architecture Documentation

## Overview

The Trial Balance Automation system is built on a **notebook-centric architecture** where Jupyter notebooks serve as the processing engine, orchestrated by Python modules in the `src/` directory. This design balances the flexibility of notebooks with the structure and scalability of traditional software architecture.

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  TIER 1: USER INTERFACE                                     │
│  ┌────────────────┐              ┌────────────────┐        │
│  │   GUI (Tkinter) │              │  CLI Scripts   │        │
│  │  trial_balance_ │              │  run_batch.py  │        │
│  │     app.py      │              │                │        │
│  └────────────────┘              └────────────────┘        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  TIER 2: ORCHESTRATION LAYER (src/orchestration/)          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  NotebookExecutor                                    │   │
│  │  - Load report registry                             │   │
│  │  - Resolve dependencies                             │   │
│  │  - Execute notebooks via papermill                  │   │
│  │  - Error handling & retries                         │   │
│  │  - Logging & metrics                                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  TIER 3: PROCESSING LAYER (notebooks/)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ 01-rd-trial │  │  monthly_   │  │  02-variance │       │
│  │  -balance-  │  │  month_end_ │  │  -analysis.  │       │
│  │  mvp.ipynb  │  │  data_conso │  │   ipynb      │       │
│  │             │  │   .ipynb    │  │              │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│  - Self-documenting (markdown cells)                       │
│  - Parameterized (papermill)                               │
│  - Single responsibility                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  TIER 4: SHARED UTILITIES (src/)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │DataLoader   │  │DataValidator│  │ExcelExporter│       │
│  │- load_all_  │  │- validate_  │  │- add_sheet() │       │
│  │  csv_files()│  │  trial_     │  │- save()      │       │
│  │- load_      │  │  balance()  │  │              │       │
│  │  reference_ │  │- check_     │  │              │       │
│  │  data()     │  │  balance_   │  │              │       │
│  │             │  │  equation() │  │              │       │
│  └─────────────┘  └─────────────┘  └─────────────┘       │
│  - Imported by notebooks                                   │
│  - DRY principle                                           │
│  - Unit testable                                           │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  TIER 5: CONFIGURATION (config/)                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  report_registry.json                                │   │
│  │  - Report definitions                                │   │
│  │  - Dependencies                                      │   │
│  │  - Parameters                                        │   │
│  │  - Output locations                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  notebook_registry.json (for GUI)                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. NotebookExecutor (Orchestration)

**File:** `src/orchestration/notebook_executor.py`

**Responsibilities:**
- Load report registry from `config/report_registry.json`
- Execute notebooks with papermill
- Resolve dependency chains (topological sort)
- Inject parameters
- Handle errors and retries
- Track execution metrics

**Key Methods:**
```python
# Execute single report
executor.execute_report('monthly_consolidation', 
                       parameters={'year': '2025', 'month': 'September'})

# Execute batch with dependencies
executor.execute_batch(['trial_balance_mvp', 'monthly_consolidation'])

# Get execution statistics
stats = executor.get_execution_stats()
```

**Dependency Resolution:**
```
User requests: ['variance_analysis']
  ↓ Dependencies: ['monthly_consolidation']
    ↓ Dependencies: ['trial_balance_mvp']
      ↓ Dependencies: []

Execution order: 
  trial_balance_mvp → monthly_consolidation → variance_analysis
```

---

### 2. DataLoader (Data Access)

**File:** `src/data/loaders.py`

**Responsibilities:**
- Load CSV/Excel files with consistent patterns
- Parse dates from filenames
- Load reference data (COA, Portfolio mappings)
- Consolidate multiple DataFrames
- Extract unique records

**Key Methods:**
```python
loader = DataLoader(base_path='../data/raw/Trial Balance')

# Load all daily files for a month
daily_data = loader.load_all_csv_files(
    folder='2025/September/Trial Balance',
    date_format='%m-%d-%Y'
)  # Returns: {'2025-09-01': df1, '2025-09-02': df2, ...}

# Consolidate into single DataFrame
consolidated = loader.consolidate_data(daily_data)

# Load reference data
coa_mapping = loader.load_reference_data('COA Mapping')

# Extract unique combinations
unique_accounts = loader.get_unique_records(
    df=consolidated,
    columns=['accountname', 'level1accountname']
)
```

---

### 3. Report Registry (Configuration)

**File:** `config/report_registry.json`

**Structure:**
```json
{
  "reports": [
    {
      "id": "monthly_consolidation",
      "name": "Monthly Month-End Data Consolidation",
      "notebook": "monthly_month_end_data_conso.ipynb",
      "category": "consolidation",
      "parameters": {"year": "auto", "month": "auto"},
      "dependencies": ["trial_balance_mvp"],
      "outputs": [...],
      "status": "active"
    }
  ]
}
```

**Benefits:**
- **Single Source of Truth:** All report metadata in one place
- **No Code Changes:** Add new reports by editing JSON
- **Dependency Tracking:** Explicit dependency chains
- **GUI Integration:** GUI reads same registry

---

### 4. Notebooks (Processing Logic)

**Pattern:**
```python
# Cell 1: Imports
import sys
sys.path.append('../')
from src.data.loaders import DataLoader

# Cell 2: Parameters (injected by papermill)
year = '2025'
month = 'September'

# Cell 3: Load data
loader = DataLoader(...)
data = loader.load_all_csv_files(...)

# Cell 4: Process
consolidated = loader.consolidate_data(data)

# Cell 5: Export
exporter.save()
```

**Benefits:**
- **Self-Documenting:** Markdown cells explain logic
- **Parameterized:** Papermill injects parameters
- **Reusable Utilities:** Import from `src/`
- **Single Responsibility:** One report per notebook

---

## Data Flow

### Example: Monthly Consolidation Report

```
1. USER ACTION
   GUI: Select "Monthly Consolidation" → Set year=2025, month=September → Click "Run"
   
2. ORCHESTRATION
   NotebookExecutor:
     - Load report config from registry
     - Check dependencies: ['trial_balance_mvp']
     - Resolve execution order: [trial_balance_mvp, monthly_consolidation]
     - Inject parameters: {'year': '2025', 'month': 'September'}
   
3. EXECUTION
   Papermill:
     - Execute trial_balance_mvp.ipynb first
     - Wait for completion
     - Execute monthly_month_end_data_conso.ipynb
     - Save executed notebooks to notebooks/executed/YYYYMMDD/
   
4. PROCESSING (Inside Notebook)
   monthly_month_end_data_conso.ipynb:
     - Import DataLoader from src.data.loaders
     - Load all daily TB CSVs using DataLoader.load_all_csv_files()
     - Consolidate using DataLoader.consolidate_data()
     - Extract unique accounts using DataLoader.get_unique_records()
     - Export to Excel using ExcelExporter
   
5. OUTPUT
   Files created:
     - notebooks/executed/20251124/monthly_consolidation_153045.ipynb
     - data/processed/Consolidation/2025/Monthly_Consolidation_September_2025.xlsx
   
6. FEEDBACK
   GUI:
     - Update status: ✅ Completed
     - Display output path
     - Update log window
```

---

## Scalability Strategy

### Adding New Reports

**Step 1: Create Notebook**
```bash
# Start from template or existing notebook
cp templates/report_template.ipynb notebooks/05-new-report.ipynb
```

**Step 2: Register in config/report_registry.json**
```json
{
  "id": "new_report",
  "name": "New Report Name",
  "notebook": "05-new-report.ipynb",
  "category": "analysis",
  "dependencies": ["trial_balance_mvp"],
  "parameters": {"year": "auto", "month": "auto"},
  "status": "active"
}
```

**Step 3: Test Execution**
```python
executor = NotebookExecutor()
executor.execute_report('new_report', parameters={'year': '2025', 'month': 'October'})
```

**Result:** Report immediately available in GUI and CLI, with dependency resolution handled automatically.

---

### Handling Hundreds of Reports

**Strategy 1: Category Organization**
```json
{
  "categories": {
    "trial_balance": [...],    // 10-20 reports
    "consolidation": [...],     // 5-10 reports
    "analysis": [...],          // 20-30 reports
    "validation": [...],        // 10-15 reports
    "reconciliation": [...]     // 10-15 reports
  }
}
```

**Strategy 2: Parallel Execution**
```python
# Reports without dependencies can run in parallel
executor.execute_batch(
    ['balance_validation', 'variance_analysis', 'reconciliation'],
    parallel=True,
    max_workers=4
)
```

**Strategy 3: Scheduled Execution**
```python
# Cron job: Daily at 6am
0 6 * * * cd /path/to/project && python scripts/run_daily_reports.py

# scripts/run_daily_reports.py
executor = NotebookExecutor()
daily_reports = executor.list_reports(schedule='daily')
executor.execute_batch([r['id'] for r in daily_reports])
```

---

## Directory Structure

```
trial-balance/
├── config/
│   ├── report_registry.json          # Orchestration registry (dependencies, params)
│   └── notebook_registry.json        # GUI registry (display metadata)
│
├── src/
│   ├── data/
│   │   ├── __init__.py
│   │   └── loaders.py                # DataLoader, ExcelExporter
│   ├── orchestration/
│   │   ├── __init__.py
│   │   └── notebook_executor.py      # NotebookExecutor
│   ├── validation/
│   │   ├── __init__.py
│   │   └── validators.py             # DataValidator (future)
│   └── gui/
│       └── trial_balance_app.py      # Tkinter GUI
│
├── notebooks/
│   ├── 01-rd-trial-balance-mvp.ipynb
│   ├── monthly_month_end_data_conso.ipynb
│   ├── 02-variance-analysis.ipynb    # Planned
│   └── executed/                     # Papermill outputs
│       └── 20251124/
│           ├── trial_balance_mvp_090000.ipynb
│           └── monthly_consolidation_091500.ipynb
│
├── data/
│   ├── raw/
│   │   └── Trial Balance/
│   │       └── 2025/September/
│   ├── processed/
│   │   ├── Trail Balance/
│   │   └── Consolidation/
│   └── references/
│       ├── COA Mapping/
│       └── Portfolio Mapping/
│
├── scripts/
│   ├── run_batch.py                  # CLI for batch execution
│   └── create_report.py              # Scaffold new reports
│
├── tests/
│   ├── test_loaders.py
│   └── test_notebook_executor.py
│
└── docs/
    ├── ARCHITECTURE.md               # This file
    ├── DEVELOPMENT_GUIDE.md
    └── REPORT_CATALOG.md
```

---

## Key Design Principles

### 1. Separation of Concerns
- **Notebooks:** Business logic and data transformations
- **src/:** Reusable utilities and orchestration
- **config/:** Configuration and metadata
- **GUI/CLI:** User interfaces

### 2. Notebook-Centric
- Notebooks are **first-class citizens**
- Notebooks own the processing logic
- Code modules support notebooks (not vice versa)

### 3. Declarative Configuration
- Report definitions in JSON (not hardcoded)
- Dependencies declared explicitly
- Parameters defined per report

### 4. DRY Principle
- Shared code in `src/` modules
- Notebooks import utilities
- No copy-paste between notebooks

### 5. Testability
- Utilities in `src/` are unit testable
- Notebooks tested via papermill execution
- Integration tests via NotebookExecutor

---

## Benefits of This Architecture

### For Data Scientists
✅ Work in familiar notebook environment  
✅ No complex framework to learn  
✅ Self-documenting (markdown cells)  
✅ Quick iteration and prototyping  

### For IT/DevOps
✅ Orchestration without touching notebooks  
✅ Dependency management  
✅ Centralized logging and monitoring  
✅ Version control for all components  

### For Organization
✅ Scales to hundreds of reports  
✅ New reports added via config (no code changes)  
✅ Clear ownership boundaries  
✅ Reproducible execution  

---

## Future Enhancements

### Phase 1: Current State ✅
- DataLoader utilities
- NotebookExecutor orchestrator
- Report registry with dependencies
- GUI integration

### Phase 2: Next Steps 🔄
- CLI tools (run_batch.py, create_report.py)
- Unit tests for src/ modules
- Automated testing via pytest
- CI/CD pipeline

### Phase 3: Advanced Features 📋
- Parallel execution for independent reports
- Retry logic for failed notebooks
- Scheduling (Airflow/cron integration)
- Monitoring dashboard
- Email/Slack notifications

---

## See Also

- [Development Guide](DEVELOPMENT_GUIDE.md) - How to create new reports
- [Report Catalog](REPORT_CATALOG.md) - All available reports
- [User Guide](../README.md) - How to use the system
