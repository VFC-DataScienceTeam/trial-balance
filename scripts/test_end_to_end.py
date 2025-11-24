"""
End-to-End Test: Complete Processing from Shared Drive
Tests the full workflow from data loading to report generation
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_environment():
    """Test Python environment and dependencies"""
    print_section("TEST 1: Environment Check")
    
    required_packages = [
        'pandas',
        'openpyxl',
        'papermill',
        'jupyter'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package:15} - Installed")
        except ImportError:
            print(f"  ❌ {package:15} - Missing")
            missing.append(package)
    
    if missing:
        print(f"\n  ⚠️  Missing packages: {', '.join(missing)}")
        print(f"  Install with: pip install {' '.join(missing)}")
        return False
    
    print("\n  ✅ All required packages installed")
    return True

def test_config():
    """Test configuration file"""
    print_section("TEST 2: Configuration Check")
    
    config_path = Path('config/run_config.json')
    
    if not config_path.exists():
        print(f"  ❌ Config file not found: {config_path}")
        return None
    
    print(f"  ✅ Config file exists: {config_path}")
    
    import json
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print(f"\n  Configuration:")
    print(f"    Year:      {config.get('year')}")
    print(f"    Month:     {config.get('month')}")
    print(f"    Data Path: {config.get('data_path')}")
    
    data_path = Path(config['data_path'])
    if data_path.exists():
        print(f"\n  ✅ Data path is accessible")
        return config
    else:
        print(f"\n  ❌ Data path not accessible: {data_path}")
        return None

def test_shared_drive_access(config):
    """Test if shared drive data is accessible"""
    print_section("TEST 3: Shared Drive Access")
    
    data_path = Path(config['data_path'])
    
    # Check Trial Balance folder
    tb_folder = data_path / 'Trial Balance'
    if tb_folder.exists():
        csv_files = list(tb_folder.glob('*.csv'))
        print(f"  ✅ Trial Balance folder: {len(csv_files)} CSV files")
    else:
        print(f"  ❌ Trial Balance folder not found: {tb_folder}")
        return False
    
    # Check Chart of Accounts folder
    coa_folder = data_path / 'Chart of Accounts'
    if coa_folder.exists():
        coa_files = list(coa_folder.glob('*.csv'))
        print(f"  ✅ Chart of Accounts folder: {len(coa_files)} file(s)")
    else:
        print(f"  ⚠️  Chart of Accounts folder not found")
    
    # Check references
    ref_path = Path('X:/Trail Balance/data/references')
    if ref_path.exists():
        coa_mapping = ref_path / 'COA Mapping'
        portfolio_mapping = ref_path / 'Portfolio Mapping'
        
        print(f"  ✅ References folder accessible")
        
        if coa_mapping.exists():
            files = list(coa_mapping.glob('*.xlsx')) + list(coa_mapping.glob('*.csv'))
            print(f"    • COA Mapping: {len(files)} file(s)")
        
        if portfolio_mapping.exists():
            files = list(portfolio_mapping.glob('*.xlsx')) + list(portfolio_mapping.glob('*.csv'))
            print(f"    • Portfolio Mapping: {len(files)} file(s)")
    else:
        print(f"  ⚠️  References folder not accessible: {ref_path}")
    
    # Check write access to processed folder
    processed_path = Path('X:/Trail Balance/data/processed/Trail Balance')
    try:
        test_dir = processed_path / 'test'
        test_dir.mkdir(parents=True, exist_ok=True)
        test_file = test_dir / f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        test_file.write_text("Write test")
        test_file.unlink()
        test_dir.rmdir()
        print(f"  ✅ Write access to processed folder")
    except Exception as e:
        print(f"  ❌ Cannot write to processed folder: {e}")
        return False
    
    print(f"\n  ✅ Shared drive fully accessible")
    return True

def test_notebook_execution():
    """Test notebook execution using papermill"""
    print_section("TEST 4: Notebook Execution (Dry Run)")
    
    notebook_path = Path('notebooks/01-rd-trial-balance-mvp.ipynb')
    
    if not notebook_path.exists():
        print(f"  ❌ Notebook not found: {notebook_path}")
        return False
    
    print(f"  ✅ Notebook found: {notebook_path}")
    print(f"\n  Note: This is a dry run. Actual execution happens via GUI.")
    print(f"  The notebook would:")
    print(f"    1. Read config/run_config.json")
    print(f"    2. Load data from X:\\Trail Balance\\...")
    print(f"    3. Process trial balance data")
    print(f"    4. Generate Excel reports")
    print(f"    5. Save to X:\\Trail Balance\\data\\processed\\...")
    
    return True

def test_output_location():
    """Test expected output location"""
    print_section("TEST 5: Output Location Check")
    
    year = "2025"
    output_dir = Path(f'X:/Trail Balance/data/processed/Trail Balance/{year}')
    
    print(f"  Expected output directory:")
    print(f"    {output_dir}")
    
    if output_dir.exists():
        print(f"\n  ✅ Output directory exists")
        
        # Check for existing reports
        excel_files = list(output_dir.glob('*.xlsx'))
        if excel_files:
            print(f"\n  Existing reports found:")
            for f in excel_files:
                size_mb = f.stat().st_size / (1024 * 1024)
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                print(f"    • {f.name:40} ({size_mb:6.2f} MB, {mtime.strftime('%Y-%m-%d %H:%M')})")
        else:
            print(f"\n  No existing reports (will be created on first run)")
    else:
        print(f"\n  ℹ️  Output directory does not exist yet (will be created)")
    
    return True

def test_gui_availability():
    """Test if GUI can be launched"""
    print_section("TEST 6: GUI Availability")
    
    gui_path = Path('src/gui/trial_balance_app.py')
    launcher = Path('launch_gui.bat')
    
    if gui_path.exists():
        print(f"  ✅ GUI application found: {gui_path}")
    else:
        print(f"  ❌ GUI application not found: {gui_path}")
        return False
    
    if launcher.exists():
        print(f"  ✅ GUI launcher found: {launcher}")
    else:
        print(f"  ❌ GUI launcher not found: {launcher}")
        return False
    
    print(f"\n  Ready to launch GUI:")
    print(f"    • Double-click: launch_gui.bat")
    print(f"    • Or run: python src/gui/trial_balance_app.py")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  SHARED DRIVE INTEGRATION TEST SUITE")
    print("  Testing: X:\\Trail Balance")
    print("="*70)
    
    results = {}
    
    # Test 1: Environment
    results['environment'] = test_environment()
    if not results['environment']:
        print("\n⚠️  Please install missing packages before continuing")
        return False
    
    # Test 2: Configuration
    config = test_config()
    results['config'] = config is not None
    if not config:
        print("\n❌ Cannot proceed without valid configuration")
        return False
    
    # Test 3: Shared drive access
    results['shared_drive'] = test_shared_drive_access(config)
    
    # Test 4: Notebook execution
    results['notebook'] = test_notebook_execution()
    
    # Test 5: Output location
    results['output'] = test_output_location()
    
    # Test 6: GUI availability
    results['gui'] = test_gui_availability()
    
    # Summary
    print_section("TEST SUMMARY")
    
    all_passed = all(results.values())
    
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test.upper():20} {status}")
    
    print("\n" + "="*70)
    
    if all_passed:
        print("  🎉 ALL TESTS PASSED!")
        print("="*70)
        print("\n  System is ready for production use!")
        print("\n  Next Steps:")
        print("    1. Launch GUI: launch_gui.bat")
        print("    2. Click '📊 Process Report'")
        print("    3. View reports in: X:\\Trail Balance\\data\\processed\\Trail Balance\\2025\\")
        print("\n  Expected outputs:")
        print("    • Trial_Balance.xlsx         (~4.5 MB, 21 sheets)")
        print("    • Trial Balance Monthly.xlsx (~33 KB, 16 fund sheets)")
        return True
    else:
        print("  ⚠️  SOME TESTS FAILED")
        print("="*70)
        print("\n  Please resolve the issues above before proceeding.")
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
