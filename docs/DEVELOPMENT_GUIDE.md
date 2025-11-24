# Development Guide - Trial Balance Automation

## Quick Start for Developers

This guide shows you how to create new reports, use the orchestration system, and extend the platform.

---

## Creating a New Report

### Method 1: Start from Existing Notebook

**Step 1: Copy Template**
```bash
# Copy an existing notebook
cp notebooks/monthly_month_end_data_conso.ipynb notebooks/06-your-new-report.ipynb
```

**Step 2: Modify Notebook Structure**

Keep this standard structure:

```python
# Cell 1: Imports
import sys
sys.path.append('../')

import pandas as pd
import logging
from pathlib import Path
from datetime import datetime

# Import reusable utilities
from src.data.loaders import DataLoader, ExcelExporter

# Cell 2: Setup Logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cell 3: Parameters (will be injected by papermill)
year = '2025'
month = 'September'

# Optional parameters with defaults
threshold = 0.01
comparison_months = 2

logger.info(f"📅 Processing: {month} {year}")

# Cell 4: Load Data
loader = DataLoader(base_path='../data/raw/Trial Balance')
data = loader.load_trial_balance_data(year, month)

# Cell 5: Process Data
# Your custom logic here
result = process_data(data)

# Cell 6: Export Results
output_dir = Path('../reports/your_report_type') / year
output_dir.mkdir(parents=True, exist_ok=True)

exporter = ExcelExporter(output_path=output_dir / f'Report_{month}_{year}.xlsx')
exporter.add_sheet(result, 'Results', freeze_panes=(1, 0))
saved_path = exporter.save()

logger.info(f"✅ Report saved: {saved_path}")
```

**Step 3: Register in config/report_registry.json**

```json
{
  "id": "your_new_report",
  "name": "Your New Report Name",
  "notebook": "06-your-new-report.ipynb",
  "category": "analysis",
  "description": "What this report does and why it's useful",
  "schedule": "monthly",
  "parameters": {
    "year": "auto",
    "month": "auto",
    "threshold": 0.01
  },
  "dependencies": ["trial_balance_mvp"],
  "outputs": [
    {
      "name": "Report_{month}_{year}.xlsx",
      "description": "Description of output",
      "location": "reports/your_report_type/{year}/"
    }
  ],
  "requires": [
    "Trial Balance data",
    "Any other required inputs"
  ],
  "execution_time": "estimated time",
  "status": "active"
}
```

**Step 4: Test Execution**

```python
from src.orchestration.notebook_executor import NotebookExecutor

executor = NotebookExecutor()

# Test with specific parameters
output = executor.execute_report(
    'your_new_report',
    parameters={'year': '2025', 'month': 'September', 'threshold': 0.05}
)

print(f"Report executed: {output}")
```

---

## Using DataLoader in Notebooks

### Loading Daily Files

```python
from src.data.loaders import DataLoader

loader = DataLoader(base_path='../data/raw/Trial Balance')

# Method 1: Load all files for a month
daily_data = loader.load_trial_balance_data('2025', 'September')
# Returns: {'2025-09-01': df1, '2025-09-02': df2, ...}

# Method 2: Load from custom folder
custom_data = loader.load_all_csv_files(
    folder='path/to/your/folder',
    date_format='%Y%m%d'  # Adjust to your filename format
)

# Method 3: Load without date parsing
raw_files = loader.load_all_csv_files(
    folder='path/to/folder',
    date_format=None  # Keys will be filenames
)
```

### Consolidating Data

```python
# Consolidate all daily files into one DataFrame
consolidated = loader.consolidate_data(
    data_dict=daily_data,
    add_date_column=True,     # Add 'Date' column
    date_column_name='Date'
)

# Add your own metadata columns
consolidated['Month'] = month
consolidated['Year'] = year
consolidated['Processing_Date'] = datetime.now().strftime('%Y-%m-%d')
```

### Extracting Unique Records

```python
# Get unique combinations of specific columns
unique_accounts = loader.get_unique_records(
    df=consolidated,
    columns=['accountname', 'level1accountname', 'Account Type'],
    sort_by=['accountname']  # Optional sorting
)
```

### Loading Reference Data

```python
# Load latest COA mapping
coa_mapping = loader.load_reference_data('COA Mapping')

# Load latest Portfolio mapping
portfolio_mapping = loader.load_reference_data('Portfolio Mapping')

# The method automatically:
# - Finds the latest file by modification time
# - Supports both CSV and Excel
# - Logs what was loaded
```

---

## Using ExcelExporter

### Basic Export

```python
from src.data.loaders import ExcelExporter

# Create exporter
exporter = ExcelExporter(output_path='output/Report.xlsx')

# Add sheets
exporter.add_sheet(df1, 'Summary', freeze_panes=(1, 0), autofilter=True)
exporter.add_sheet(df2, 'Details', freeze_panes=(1, 0))

# Save file
saved_path = exporter.save()
print(f"Saved to: {saved_path}")
```

### Multiple Sheets with Formatting

```python
# Summary sheet
summary_df = pd.DataFrame({
    'Metric': ['Total Records', 'Unique Accounts', 'Processing Date'],
    'Value': [len(data), len(unique), datetime.now().strftime('%Y-%m-%d')]
})

exporter = ExcelExporter(output_path=f'reports/Monthly_Report_{month}.xlsx')

# Add multiple sheets
exporter.add_sheet(summary_df, 'Summary', autofilter=False)
exporter.add_sheet(unique_accounts, 'Unique Accounts', freeze_panes=(1, 0))
exporter.add_sheet(consolidated_data, 'All Data', freeze_panes=(1, 0))

exporter.save()
```

---

## Using NotebookExecutor

### Execute Single Report

```python
from src.orchestration.notebook_executor import NotebookExecutor

executor = NotebookExecutor()

# Execute with default parameters (from registry)
output = executor.execute_report('monthly_consolidation')

# Execute with custom parameters
output = executor.execute_report(
    'monthly_consolidation',
    parameters={'year': '2024', 'month': 'December'}
)

# Execute with custom output location
output = executor.execute_report(
    'monthly_consolidation',
    parameters={'year': '2025', 'month': 'September'},
    output_notebook='custom/path/executed_notebook.ipynb'
)
```

### Execute Batch Reports

```python
# Execute multiple reports in dependency order
results = executor.execute_batch([
    'trial_balance_mvp',
    'monthly_consolidation',
    'variance_analysis'
])

# Results is a dict: {'report_id': 'path/to/executed/notebook.ipynb', ...}

# With shared parameters
results = executor.execute_batch(
    ['trial_balance_mvp', 'monthly_consolidation'],
    parameters={'year': '2025', 'month': 'October'}
)

# Continue on error (don't stop batch)
results = executor.execute_batch(
    ['report1', 'report2', 'report3'],
    stop_on_error=False
)
```

### Get Execution Statistics

```python
# Get execution history
history = executor.get_execution_history()

# Get history for specific report
tb_history = executor.get_execution_history(report_id='trial_balance_mvp')

# Get statistics
stats = executor.get_execution_stats()
print(f"Success rate: {stats['success_rate']:.1%}")
print(f"Average duration: {stats['average_duration']:.1f}s")
print(f"By report: {stats['by_report']}")

# Save execution log
executor.save_execution_log('logs/execution_log.json')
```

### List Available Reports

```python
# List all reports
all_reports = executor.list_reports()

# List by category
analysis_reports = executor.list_reports(category='analysis')

# List by status
active_reports = executor.list_reports(status='active')
planned_reports = executor.list_reports(status='planned')

# Get specific report config
report = executor.get_report_config('monthly_consolidation')
print(f"Dependencies: {report['dependencies']}")
print(f"Parameters: {report['parameters']}")
```

---

## Report Registry Reference

### Required Fields

```json
{
  "id": "unique_identifier",           // REQUIRED: Unique ID (no spaces)
  "name": "Display Name",              // REQUIRED: Human-readable name
  "notebook": "filename.ipynb",        // REQUIRED: Notebook filename
  "status": "active"                   // REQUIRED: active|planned|deprecated
}
```

### Optional Fields

```json
{
  "category": "analysis",              // Grouping category
  "description": "What it does",       // Long description
  "schedule": "daily",                 // daily|weekly|monthly
  "parameters": {                      // Default parameters
    "year": "auto",
    "month": "auto",
    "threshold": 0.01
  },
  "dependencies": [                    // Reports that must run first
    "trial_balance_mvp"
  ],
  "outputs": [                         // Expected output files
    {
      "name": "Report.xlsx",
      "description": "What it contains",
      "location": "reports/type/"
    }
  ],
  "requires": [                        // Human-readable prerequisites
    "Trial Balance CSVs"
  ],
  "execution_time": "2-4 minutes"      // Estimated duration
}
```

---

## Notebook Best Practices

### 1. Always Use Markdown Cells

```markdown
# Section Title

Explain what this section does and why.

## Subsection

More detailed explanation.
```

### 2. Parameter Cell Pattern

Always have a dedicated cell for parameters:

```python
# Parameters (injected by papermill)
year = '2025'          # Year to process
month = 'September'    # Month to process
threshold = 0.01       # Balance threshold for validation
input_location = 'shared_drive'   # Data source
output_location = 'shared_drive'  # Output destination

# Log parameters
logger.info(f"Parameters: year={year}, month={month}, threshold={threshold}")
```

### 3. Error Handling

```python
try:
    data = loader.load_trial_balance_data(year, month)
    
    if not data:
        raise ValueError(f"No data found for {month} {year}")
    
    # Process data
    result = process_data(data)
    
except FileNotFoundError as e:
    logger.error(f"❌ File not found: {e}")
    raise
except Exception as e:
    logger.error(f"❌ Unexpected error: {e}")
    raise
```

### 4. Comprehensive Logging

```python
# At start
logger.info(f"📅 Processing: {month} {year}")

# During loading
logger.info(f"📂 Loading from: {folder_path}")

# After operations
logger.info(f"✓ Loaded {len(data):,} records")

# On completion
logger.info(f"✅ Report completed successfully!")

# On errors
logger.error(f"❌ Failed to process: {error}")
```

### 5. Display Sample Data

```python
# Show sample of data
print("\n📊 Sample Data:")
consolidated_df.head(10)

# Show summary statistics
print("\n📈 Summary Statistics:")
print(f"Total records: {len(df):,}")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
print(f"Unique accounts: {df['accountname'].nunique():,}")
```

---

## Testing Your Report

### Manual Testing

```python
# Test in notebook first
%run notebooks/06-your-new-report.ipynb

# Test via executor
from src.orchestration.notebook_executor import NotebookExecutor

executor = NotebookExecutor()
output = executor.execute_report('your_new_report')
```

### Automated Testing

Create `tests/test_your_report.py`:

```python
import pytest
from src.orchestration.notebook_executor import NotebookExecutor

def test_report_execution():
    """Test report executes without errors"""
    executor = NotebookExecutor()
    
    # Execute report
    output = executor.execute_report(
        'your_new_report',
        parameters={'year': '2025', 'month': 'September'}
    )
    
    # Check output exists
    assert Path(output).exists()
    
    # Check execution was successful
    history = executor.get_execution_history('your_new_report')
    assert history[-1]['status'] == 'success'
```

Run tests:
```bash
pytest tests/test_your_report.py -v
```

---

## Debugging Tips

### 1. Check Logs

```python
# In notebook: Set logging to DEBUG
logging.basicConfig(level=logging.DEBUG)

# View execution log
executor = NotebookExecutor()
history = executor.get_execution_history('your_report')
print(history[-1])  # Last execution details
```

### 2. Inspect Executed Notebooks

```bash
# View executed notebooks (with outputs)
ls notebooks/executed/20251124/

# Open in Jupyter to see outputs
jupyter notebook notebooks/executed/20251124/your_report_153045.ipynb
```

### 3. Test Data Loading Separately

```python
# Test DataLoader in isolation
from src.data.loaders import DataLoader

loader = DataLoader('../data/raw/Trial Balance')
data = loader.load_trial_balance_data('2025', 'September')

print(f"Loaded {len(data)} files")
print(f"Keys: {list(data.keys())}")
print(f"Sample shape: {list(data.values())[0].shape}")
```

### 4. Validate Registry

```python
# Check report is registered
from src.orchestration.notebook_executor import NotebookExecutor

executor = NotebookExecutor()
report = executor.get_report_config('your_report')

if not report:
    print("❌ Report not found in registry!")
else:
    print(f"✓ Found: {report['name']}")
    print(f"  Dependencies: {report.get('dependencies', [])}")
    print(f"  Status: {report.get('status')}")
```

---

## Common Patterns

### Pattern 1: Month-over-Month Comparison

```python
# Load current month
current_data = loader.load_trial_balance_data(year, month)
current_consolidated = loader.consolidate_data(current_data)

# Load previous month
prev_month = get_previous_month(month, year)
prev_data = loader.load_trial_balance_data(prev_month['year'], prev_month['month'])
prev_consolidated = loader.consolidate_data(prev_data)

# Compare
comparison = compare_dataframes(current_consolidated, prev_consolidated)
```

### Pattern 2: Multi-Sheet Excel Report

```python
exporter = ExcelExporter(output_path=f'reports/{report_name}.xlsx')

# Sheet 1: Executive Summary
exporter.add_sheet(summary_df, 'Summary')

# Sheet 2: Details by Category
for category in categories:
    filtered = data[data['Category'] == category]
    exporter.add_sheet(filtered, category, freeze_panes=(1, 0))

# Sheet 3: Raw Data
exporter.add_sheet(raw_data, 'Raw Data', freeze_panes=(1, 0))

exporter.save()
```

### Pattern 3: Validation with Threshold

```python
# Define validation rules
def validate_balance(df, tolerance=0.01):
    """Check if debits equal credits"""
    by_fund = df.groupby('Fund')['netamt'].sum()
    unbalanced = by_fund[abs(by_fund) > tolerance]
    
    if not unbalanced.empty:
        logger.warning(f"⚠️ Unbalanced funds: {list(unbalanced.index)}")
        return False
    
    logger.info("✓ All funds balanced")
    return True

# Use in notebook
is_valid = validate_balance(consolidated_df, threshold=0.01)
```

---

## CLI Usage (Future)

Once CLI scripts are created:

```bash
# Execute single report
python scripts/run_report.py monthly_consolidation --year 2025 --month September

# Execute batch by category
python scripts/run_batch.py --category analysis --year 2025 --month September

# Execute specific reports
python scripts/run_batch.py --reports trial_balance_mvp monthly_consolidation

# With custom parameters
python scripts/run_report.py variance_analysis \
    --year 2025 --month September \
    --comparison-months 3 \
    --threshold 0.05
```

---

## Contributing

### Code Style

- Use descriptive variable names
- Add docstrings to functions
- Follow PEP 8 style guidelines
- Add type hints where helpful

### Commit Messages

```bash
# Good commit messages
git commit -m "✨ Add variance analysis report"
git commit -m "🐛 Fix date parsing in DataLoader"
git commit -m "📝 Update documentation for NotebookExecutor"
git commit -m "♻️ Refactor data loading logic"

# Use emojis:
# ✨ New feature
# 🐛 Bug fix
# 📝 Documentation
# ♻️ Refactoring
# ✅ Tests
# 🎨 UI/Styling
```

### Pull Request Checklist

- [ ] Notebook runs without errors
- [ ] Report registered in `config/report_registry.json`
- [ ] Documentation updated
- [ ] Example execution included
- [ ] Tests added (if applicable)

---

## Next Steps

1. **Try creating a simple report** following this guide
2. **Review existing notebooks** for patterns
3. **Read [ARCHITECTURE.md](ARCHITECTURE.md)** for system design
4. **Check [REPORT_CATALOG.md](REPORT_CATALOG.md)** for report examples

---

## Getting Help

- Check existing notebooks for examples
- Review execution logs: `notebooks/executed/`
- Read architecture documentation
- Ask team members for code review
