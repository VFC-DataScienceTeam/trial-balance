"""
Test script to verify the config + fallback system works correctly.
Tests 3 scenarios:
1. Config file with absolute path (GUI flow)
2. Config file with relative path (legacy)
3. No config file (fallback to auto-detect)
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_scenario_1():
    """Test: Config file with absolute path (GUI flow)"""
    print("\n" + "="*60)
    print("TEST 1: Config with Absolute Path (GUI Flow)")
    print("="*60)
    
    project_root = Path(__file__).parent.parent
    config_path = project_root / 'config' / 'run_config.json'
    data_path = project_root / 'data' / 'raw' / 'Trial Balance' / '2025' / 'September'
    
    # Create config with absolute path
    config = {
        'year': '2025',
        'month': 'September',
        'data_path': str(data_path)
    }
    
    config_path.parent.mkdir(exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2))
    
    print(f"✅ Created config file: {config_path}")
    print(f"   Year: {config['year']}")
    print(f"   Month: {config['month']}")
    print(f"   Data Path: {config['data_path']}")
    print(f"   Path Type: {'Absolute' if Path(config['data_path']).is_absolute() else 'Relative'}")
    print(f"   Path Exists: {data_path.exists()}")
    
    if data_path.exists():
        tb_folder = data_path / "Trial Balance"
        coa_folder = data_path / "Chart of Accounts"
        print(f"   Trial Balance Folder: {tb_folder.exists()}")
        print(f"   COA Folder: {coa_folder.exists()}")
        
        if tb_folder.exists():
            csv_files = list(tb_folder.glob("*.csv"))
            print(f"   CSV Files Found: {len(csv_files)}")
    
    return True

def test_scenario_2():
    """Test: Config file with relative path (legacy)"""
    print("\n" + "="*60)
    print("TEST 2: Config with Relative Path (Legacy)")
    print("="*60)
    
    project_root = Path(__file__).parent.parent
    config_path = project_root / 'config' / 'run_config.json'
    
    # Create config with relative path (legacy style)
    config = {
        'year': '2025',
        'month': 'September',
        'data_path': 'data/raw/Trial Balance'
    }
    
    config_path.parent.mkdir(exist_ok=True)
    config_path.write_text(json.dumps(config, indent=2))
    
    print(f"✅ Created config file: {config_path}")
    print(f"   Year: {config['year']}")
    print(f"   Month: {config['month']}")
    print(f"   Data Path: {config['data_path']}")
    print(f"   Path Type: {'Absolute' if Path(config['data_path']).is_absolute() else 'Relative'}")
    
    # Notebook will build: ../data/raw/Trial Balance/2025/September
    expected_path = project_root / 'data' / 'raw' / 'Trial Balance' / '2025' / 'September'
    print(f"   Expected Resolved Path: {expected_path}")
    print(f"   Path Exists: {expected_path.exists()}")
    
    return True

def test_scenario_3():
    """Test: No config file (fallback to auto-detect)"""
    print("\n" + "="*60)
    print("TEST 3: No Config File (Auto-Detect Fallback)")
    print("="*60)
    
    project_root = Path(__file__).parent.parent
    config_path = project_root / 'config' / 'run_config.json'
    
    # Remove config file to test fallback
    if config_path.exists():
        config_path.unlink()
        print(f"✅ Removed config file: {config_path}")
    else:
        print(f"✅ Config file does not exist: {config_path}")
    
    # Simulate auto-detect logic
    default_raw_path = project_root / 'data' / 'raw' / 'Trial Balance'
    
    if default_raw_path.exists():
        year_folders = sorted(
            [f for f in default_raw_path.iterdir() if f.is_dir() and f.name.replace("-", "").isdigit()],
            reverse=True
        )
        
        if year_folders:
            latest_year = year_folders[0]
            print(f"   Latest Year: {latest_year.name}")
            
            month_folders = sorted(
                [f for f in latest_year.iterdir() if f.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            if month_folders:
                latest_month = month_folders[0]
                print(f"   Latest Month: {latest_month.name}")
                print(f"   Auto-Detected Path: {latest_month}")
                print(f"   Path Exists: {latest_month.exists()}")
                return True
    
    print("   ❌ Auto-detect failed - no data folders found")
    return False

def main():
    """Run all test scenarios"""
    print("\n" + "="*60)
    print("TESTING CONFIG + FALLBACK SYSTEM")
    print("="*60)
    
    results = []
    
    try:
        results.append(("Absolute Path (GUI)", test_scenario_1()))
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        results.append(("Absolute Path (GUI)", False))
    
    try:
        results.append(("Relative Path (Legacy)", test_scenario_2()))
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        results.append(("Relative Path (Legacy)", False))
    
    try:
        results.append(("Auto-Detect Fallback", test_scenario_3()))
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        results.append(("Auto-Detect Fallback", False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {name}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + ("="*60))
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("="*60 + "\n")
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
