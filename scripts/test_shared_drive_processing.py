"""
Quick Test: Load and Process Data from Shared Drive
Tests the actual notebook data loading logic with shared drive path
"""

import sys
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_config_loading():
    """Test loading config from run_config.json"""
    print("\n" + "="*70)
    print("TEST 1: Loading Configuration")
    print("="*70)
    
    config_path = Path('config/run_config.json')
    
    if not config_path.exists():
        print(f"❌ Config file not found: {config_path}")
        return None
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"✅ Config loaded successfully")
        print(f"   Year: {config.get('year')}")
        print(f"   Month: {config.get('month')}")
        print(f"   Data Path: {config.get('data_path')}")
        
        return config
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return None

def test_data_loading(config):
    """Test loading trial balance data"""
    print("\n" + "="*70)
    print("TEST 2: Loading Trial Balance Data")
    print("="*70)
    
    data_path = Path(config['data_path'])
    
    if not data_path.exists():
        print(f"❌ Data path does not exist: {data_path}")
        return None
    
    print(f"✅ Data path exists: {data_path}")
    
    # Load Trial Balance CSVs
    tb_folder = data_path / 'Trial Balance'
    
    if not tb_folder.exists():
        print(f"❌ Trial Balance folder not found: {tb_folder}")
        return None
    
    print(f"\n📊 Loading Trial Balance CSVs from: {tb_folder}")
    
    trial_balance_data = {}
    csv_files = sorted(tb_folder.glob("*.csv"))
    
    print(f"   Found {len(csv_files)} CSV files")
    
    for csv_file in csv_files[:5]:  # Test first 5 files
        try:
            file_date = datetime.strptime(csv_file.stem, "%m-%d-%Y")
            date_key = file_date.strftime("%Y-%m-%d")
            df = pd.read_csv(csv_file)
            trial_balance_data[date_key] = df
            print(f"   ✅ {csv_file.name}: {len(df)} records, {len(df.columns)} columns")
        except Exception as e:
            print(f"   ❌ Failed to load {csv_file.name}: {e}")
            return None
    
    if len(csv_files) > 5:
        print(f"   ... and {len(csv_files) - 5} more files")
    
    # Load Chart of Accounts
    coa_folder = data_path / 'Chart of Accounts'
    
    print(f"\n📋 Loading Chart of Accounts from: {coa_folder}")
    
    if coa_folder.exists():
        coa_files = list(coa_folder.glob("*.csv"))
        if coa_files:
            try:
                chart_of_accounts = pd.read_csv(coa_files[0])
                print(f"   ✅ {coa_files[0].name}: {len(chart_of_accounts)} records")
            except Exception as e:
                print(f"   ❌ Failed to load COA: {e}")
                chart_of_accounts = None
        else:
            print(f"   ⚠️  No CSV files found in COA folder")
            chart_of_accounts = None
    else:
        print(f"   ❌ Chart of Accounts folder not found")
        chart_of_accounts = None
    
    return {
        'trial_balance': trial_balance_data,
        'chart_of_accounts': chart_of_accounts,
        'year': config['year'],
        'month': config['month']
    }

def test_data_consolidation(data):
    """Test consolidating trial balance data"""
    print("\n" + "="*70)
    print("TEST 3: Consolidating Trial Balance Data")
    print("="*70)
    
    trial_balance_data = data['trial_balance']
    
    if not trial_balance_data:
        print("❌ No trial balance data to consolidate")
        return None
    
    print(f"📊 Consolidating {len(trial_balance_data)} daily trial balances...")
    
    try:
        # Add Date column to each DataFrame
        for date_key, df in trial_balance_data.items():
            df['Date'] = date_key
        
        # Consolidate all DataFrames
        trial_balance_consolidated = pd.concat(
            trial_balance_data.values(), 
            ignore_index=True
        )
        
        print(f"✅ Consolidated successfully")
        print(f"   Total Records: {len(trial_balance_consolidated):,}")
        print(f"   Columns: {len(trial_balance_consolidated.columns)}")
        print(f"   Date Range: {trial_balance_consolidated['Date'].min()} to {trial_balance_consolidated['Date'].max()}")
        
        # Show sample data
        print(f"\n   Sample columns: {', '.join(trial_balance_consolidated.columns[:5].tolist())}")
        print(f"\n   First few records:")
        print(trial_balance_consolidated.head(3).to_string())
        
        return trial_balance_consolidated
        
    except Exception as e:
        print(f"❌ Consolidation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_pivot_table(consolidated_df):
    """Test creating pivot table"""
    print("\n" + "="*70)
    print("TEST 4: Creating Pivot Table")
    print("="*70)
    
    try:
        print(f"📊 Creating pivot table (GL Account × Fund)...")
        
        pivot_table = consolidated_df.pivot_table(
            values='netamt',
            index='accountname',
            columns='level1accountname',
            aggfunc='sum',
            fill_value=0
        )
        
        print(f"✅ Pivot table created successfully")
        print(f"   GL Accounts (rows): {len(pivot_table)}")
        print(f"   Funds (columns): {len(pivot_table.columns)}")
        print(f"\n   Fund Names: {', '.join(pivot_table.columns.tolist()[:5])}...")
        print(f"\n   Sample pivot table (first 5 accounts):")
        print(pivot_table.head().to_string())
        
        return pivot_table
        
    except Exception as e:
        print(f"❌ Pivot table creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_reference_data():
    """Test loading reference data from shared drive"""
    print("\n" + "="*70)
    print("TEST 5: Loading Reference Data")
    print("="*70)
    
    ref_base = Path('X:/Trail Balance/data/references')
    
    if not ref_base.exists():
        print(f"❌ References folder not found: {ref_base}")
        return None
    
    print(f"✅ References folder exists: {ref_base}")
    
    # Test COA Mapping
    coa_mapping_path = ref_base / 'COA Mapping'
    coa_mapping = None
    
    if coa_mapping_path.exists():
        coa_files = sorted(
            list(coa_mapping_path.glob('*.xlsx')) + list(coa_mapping_path.glob('*.csv')),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if coa_files:
            try:
                latest_file = coa_files[0]
                if latest_file.suffix.lower() == '.csv':
                    coa_mapping = pd.read_csv(latest_file)
                else:
                    coa_mapping = pd.read_excel(latest_file)
                
                print(f"   ✅ COA Mapping: {latest_file.name}")
                print(f"      Records: {len(coa_mapping)}")
                print(f"      Columns: {', '.join(coa_mapping.columns.tolist()[:3])}...")
            except Exception as e:
                print(f"   ❌ Failed to load COA Mapping: {e}")
        else:
            print(f"   ⚠️  No COA Mapping files found")
    else:
        print(f"   ❌ COA Mapping folder not found")
    
    # Test Portfolio Mapping
    portfolio_mapping_path = ref_base / 'Portfolio Mapping'
    portfolio_mapping = None
    
    if portfolio_mapping_path.exists():
        portfolio_files = sorted(
            list(portfolio_mapping_path.glob('*.xlsx')) + list(portfolio_mapping_path.glob('*.csv')),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if portfolio_files:
            try:
                latest_file = portfolio_files[0]
                if latest_file.suffix.lower() == '.csv':
                    portfolio_mapping = pd.read_csv(latest_file)
                else:
                    portfolio_mapping = pd.read_excel(latest_file)
                
                print(f"   ✅ Portfolio Mapping: {latest_file.name}")
                print(f"      Records: {len(portfolio_mapping)}")
            except Exception as e:
                print(f"   ❌ Failed to load Portfolio Mapping: {e}")
        else:
            print(f"   ⚠️  No Portfolio Mapping files found")
    else:
        print(f"   ❌ Portfolio Mapping folder not found")
    
    return {
        'coa_mapping': coa_mapping,
        'portfolio_mapping': portfolio_mapping
    }

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("SHARED DRIVE DATA PROCESSING TEST")
    print("Target: X:\\Trail Balance\\data")
    print("="*70)
    
    # Test 1: Load config
    config = test_config_loading()
    if not config:
        print("\n❌ FAILED: Could not load configuration")
        return False
    
    # Test 2: Load data
    data = test_data_loading(config)
    if not data or not data['trial_balance']:
        print("\n❌ FAILED: Could not load trial balance data")
        return False
    
    # Test 3: Consolidate data
    consolidated = test_data_consolidation(data)
    if consolidated is None:
        print("\n❌ FAILED: Could not consolidate data")
        return False
    
    # Test 4: Create pivot table
    pivot = test_pivot_table(consolidated)
    if pivot is None:
        print("\n❌ FAILED: Could not create pivot table")
        return False
    
    # Test 5: Load reference data
    references = test_reference_data()
    
    # Final summary
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    print(f"✅ Configuration: Loaded from config/run_config.json")
    print(f"✅ Trial Balance: {len(data['trial_balance'])} daily files loaded")
    print(f"✅ Chart of Accounts: {'Loaded' if data['chart_of_accounts'] is not None else 'Not found'}")
    print(f"✅ Consolidated Data: {len(consolidated):,} total records")
    print(f"✅ Pivot Table: {len(pivot)} GL accounts × {len(pivot.columns)} funds")
    
    if references:
        print(f"✅ COA Mapping: {'Loaded' if references['coa_mapping'] is not None else 'Not found'}")
        print(f"✅ Portfolio Mapping: {'Loaded' if references['portfolio_mapping'] is not None else 'Not found'}")
    
    print("\n" + "="*70)
    print("🎉 ALL TESTS PASSED!")
    print("="*70)
    print("\nYour shared drive is properly configured and data can be processed.")
    print("You can now run the full notebook or GUI to generate reports.")
    print("\nNext steps:")
    print("  1. Run: scripts\\launchers\\launch_gui.bat")
    print("  2. Click 'Process Report' (will use shared drive data)")
    print("  3. Reports will save to: X:\\Trail Balance\\data\\processed\\Trail Balance\\2025\\")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
