"""
Simple Launcher for Trial Balance GUI
Double-click this file to launch the application GUI.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Trial Balance GUI application"""
    # Get the src/gui directory
    project_root = Path(__file__).parent.parent
    app_script = project_root / "src" / "gui" / "trial_balance_app.py"
    
    # Check if the app script exists
    if not app_script.exists():
        print(f"ERROR: Application not found at {app_script}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Launch the GUI application
    try:
        print("Launching Trial Balance GUI...")
        print(f"Location: {app_script}")
        print("\nIf you see this console window only, the GUI should appear separately.")
        print("Look for the GUI window on your taskbar or minimize this window.\n")
        
        # Run the application from project root
        subprocess.run([sys.executable, str(app_script)], cwd=str(project_root))
        
    except Exception as e:
        print(f"\nERROR: Failed to launch application")
        print(f"Details: {str(e)}")
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
