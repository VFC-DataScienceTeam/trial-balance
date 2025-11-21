"""
Quick launcher for Trial Balance GUI
This file stays in the root for easy access
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Trial Balance GUI application"""
    project_root = Path(__file__).parent
    app_script = project_root / "src" / "gui" / "trial_balance_app.py"
    
    if not app_script.exists():
        print(f"ERROR: Application not found at {app_script}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    try:
        print("Launching Trial Balance GUI...")
        subprocess.run([sys.executable, str(app_script)], cwd=str(project_root))
    except Exception as e:
        print(f"\nERROR: Failed to launch application")
        print(f"Details: {str(e)}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
