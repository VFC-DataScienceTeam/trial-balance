"""
Test Script: Verify Shared Drive Access and Data Structure
Tests if the system can access and read data from X:\Trail Balance
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

def test_shared_drive_access():
    """Test if shared drive path exists and is accessible"""
    print("="*70)
    print("TESTING SHARED DRIVE ACCESS")
    print("="*70)
    
    shared_path = Path('X:/Trail Balance')
    
    print(f"\n1. Testing path: {shared_path}")
    if shared_path.exists():
        print(f"   ✅ Path exists and is accessible")
        return shared_path
    else:
        print(f"   ❌ Path does NOT exist or is not accessible")
        print(f"\n   Troubleshooting:")
        print(f"   - Check if drive X: is mapped")
        print(f"   - Verify network connectivity")
        print(f"   - Check folder permissions")
        return None

def test_folder_structure(base_path):
    """Test if expected folder structure exists"""
    print(f"\n2. Testing folder structure...")
    
    expected_folders = {
        'raw': base_path / 'raw',
        'processed': base_path / 'processed',
        'references': base_path / 'references',
    }
    
    results = {}
    for name, path in expected_folders.items():
        exists = path.exists()
        results[name] = exists
        status = "✅" if exists else "❌"
        print(f"   {status} {name}: {path}")
    
    return results

def find_trial_balance_data(base_path):
    """Find and list trial balance data folders"""
    print(f"\n3. Searching for Trial Balance data...")
    
    raw_tb_path = base_path / 'raw' / 'Trial Balance'
    
    if not raw_tb_path.exists():
        print(f"   ❌ Trial Balance folder not found: {raw_tb_path}")
        return []
    
    print(f"   ✅ Found: {raw_tb_path}")
    
    # Find year folders
    year_folders = sorted([f for f in raw_tb_path.iterdir() if f.is_dir() and f.name.isdigit()],
                         reverse=True)
    
    if not year_folders:
        print(f"   ⚠️  No year folders found")
        return []
    
    print(f"\n   Year folders found: {[f.name for f in year_folders]}")
    
    # Scan each year for months
    data_locations = []
    for year_folder in year_folders:
        month_folders = sorted([f for f in year_folder.iterdir() if f.is_dir()])
        
        for month_folder in month_folders:
            tb_folder = month_folder / 'Trial Balance'
            coa_folder = month_folder / 'Chart of Accounts'
            
            if tb_folder.exists():
                csv_files = list(tb_folder.glob('*.csv'))
                coa_files = list(coa_folder.glob('*.csv')) if coa_folder.exists() else []
                
                data_locations.append({
                    'year': year_folder.name,
                    'month': month_folder.name,
                    'path': month_folder,
                    'tb_files': len(csv_files),
                    'coa_files': len(coa_files),
                    'tb_folder': tb_folder,
                    'coa_folder': coa_folder
                })
    
    return data_locations

def test_data_loading(data_location):
    """Test loading actual data from a location"""
    print(f"\n4. Testing data loading from: {data_location['year']}/{data_location['month']}")
    
    tb_folder = data_location['tb_folder']
    coa_folder = data_location['coa_folder']
    
    # Test Trial Balance CSV loading
    print(f"\n   Trial Balance Files:")
    csv_files = sorted(tb_folder.glob('*.csv'))
    
    if not csv_files:
        print(f"   ❌ No CSV files found in {tb_folder}")
        return False
    
    loaded_count = 0
    total_records = 0
    
    for i, csv_file in enumerate(csv_files[:3]):  # Test first 3 files
        try:
            df = pd.read_csv(csv_file)
            loaded_count += 1
            total_records += len(df)
            print(f"   ✅ {csv_file.name}: {len(df)} records, {len(df.columns)} columns")
            
            # Show first few column names
            if i == 0:
                print(f"      Columns: {', '.join(df.columns[:5].tolist())}...")
        except Exception as e:
            print(f"   ❌ Failed to load {csv_file.name}: {e}")
            return False
    
    if len(csv_files) > 3:
        print(f"   ... and {len(csv_files) - 3} more CSV files")
    
    # Test Chart of Accounts loading
    print(f"\n   Chart of Accounts:")
    coa_files = list(coa_folder.glob('*.csv'))
    
    if coa_files:
        try:
            coa_df = pd.read_csv(coa_files[0])
            print(f"   ✅ {coa_files[0].name}: {len(coa_df)} records, {len(coa_df.columns)} columns")
        except Exception as e:
            print(f"   ❌ Failed to load COA: {e}")
    else:
        print(f"   ⚠️  No COA files found")
    
    print(f"\n   Summary:")
    print(f"   - TB Files: {len(csv_files)} total, {loaded_count} tested successfully")
    print(f"   - Total Records Tested: {total_records:,}")
    
    return True

def test_references(base_path):
    """Test if reference data exists"""
    print(f"\n5. Testing reference data...")
    
    ref_path = base_path / 'references'
    
    if not ref_path.exists():
        print(f"   ❌ References folder not found: {ref_path}")
        return False
    
    # Test COA Mapping
    coa_mapping_path = ref_path / 'COA Mapping'
    if coa_mapping_path.exists():
        coa_files = list(coa_mapping_path.glob('*.xlsx')) + list(coa_mapping_path.glob('*.csv'))
        if coa_files:
            print(f"   ✅ COA Mapping: {len(coa_files)} file(s)")
            for f in coa_files[:2]:
                print(f"      - {f.name}")
        else:
            print(f"   ⚠️  COA Mapping folder exists but no files found")
    else:
        print(f"   ❌ COA Mapping folder not found")
    
    # Test Portfolio Mapping
    portfolio_mapping_path = ref_path / 'Portfolio Mapping'
    if portfolio_mapping_path.exists():
        portfolio_files = list(portfolio_mapping_path.glob('*.xlsx')) + list(portfolio_mapping_path.glob('*.csv'))
        if portfolio_files:
            print(f"   ✅ Portfolio Mapping: {len(portfolio_files)} file(s)")
            for f in portfolio_files[:2]:
                print(f"      - {f.name}")
        else:
            print(f"   ⚠️  Portfolio Mapping folder exists but no files found")
    else:
        print(f"   ❌ Portfolio Mapping folder not found")
    
    return True

def test_write_access(base_path):
    """Test if we can write to processed folder"""
    print(f"\n6. Testing write access...")
    
    processed_path = base_path / 'processed' / 'Trail Balance' / 'test'
    
    try:
        processed_path.mkdir(parents=True, exist_ok=True)
        
        test_file = processed_path / 'test_write.txt'
        test_file.write_text(f"Write test at {datetime.now()}")
        
        if test_file.exists():
            print(f"   ✅ Write access confirmed")
            print(f"      Test file created: {test_file}")
            
            # Clean up
            test_file.unlink()
            processed_path.rmdir()
            print(f"      Test file cleaned up")
            return True
        else:
            print(f"   ❌ Could not verify file creation")
            return False
            
    except Exception as e:
        print(f"   ❌ Write test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("SHARED DRIVE ACCESS TEST SUITE")
    print("Target: X:\\Trail Balance")
    print("="*70)
    
    # Test 1: Basic access
    shared_path = test_shared_drive_access()
    if not shared_path:
        print("\n" + "="*70)
        print("❌ FAILED: Cannot access shared drive")
        print("="*70)
        return False
    
    # Test 2: Folder structure
    folder_results = test_folder_structure(shared_path)
    
    # Test 3: Find data
    data_locations = find_trial_balance_data(shared_path)
    
    if not data_locations:
        print("\n   ⚠️  No trial balance data found")
    else:
        print(f"\n   ✅ Found {len(data_locations)} data location(s):")
        for loc in data_locations:
            print(f"      - {loc['year']}/{loc['month']}: {loc['tb_files']} TB files, {loc['coa_files']} COA files")
        
        # Test 4: Load data from latest location
        if data_locations:
            test_data_loading(data_locations[0])
    
    # Test 5: References
    test_references(shared_path)
    
    # Test 6: Write access
    test_write_access(shared_path)
    
    # Final summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    if shared_path and data_locations:
        print("✅ PASSED: Shared drive is accessible and contains data")
        print(f"\n   Ready to process:")
        for loc in data_locations[:3]:
            print(f"   - {loc['year']}/{loc['month']}: {loc['tb_files']} files")
        print(f"\n   Configuration for .env file:")
        print(f"   TB_RAW_PATH=X:\\Trail Balance\\raw\\Trial Balance")
        print(f"   TB_PROCESSED_PATH=X:\\Trail Balance\\processed\\Trail Balance")
        print(f"   TB_REFERENCES_PATH=X:\\Trail Balance\\references")
        return True
    else:
        print("❌ FAILED: Issues detected with shared drive access or data")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
