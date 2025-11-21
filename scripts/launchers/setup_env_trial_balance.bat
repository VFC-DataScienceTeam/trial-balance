@echo off
ECHO ----------------------------------------------------
ECHO Setting up Project Environment (Trial Balance Reporting)
ECHO ----------------------------------------------------

REM --- Auto-detect base directory (project root is 2 levels up from scripts/launchers/) ---
set SCRIPT_DIR=%~dp0
set BASE_DIR=%SCRIPT_DIR%..\..
set VENV_PATH=%BASE_DIR%\.venv
set REQ_FILE=%BASE_DIR%\requirements.txt

REM --- Go to project root ---
cd /d "%BASE_DIR%"

REM 1. Create Virtual Environment
if not exist "%VENV_PATH%\Scripts\activate" (
    ECHO Creating Virtual Environment in .venv...
    python -m venv "%VENV_PATH%"
) else (
    ECHO Virtual Environment already exists. Skipping creation.
)

REM 2. Activate VENV and Install Packages
ECHO Activating VENV and Installing Packages from requirements.txt...
call "%VENV_PATH%\Scripts\activate"

if exist "%REQ_FILE%" (
    pip install -r "%REQ_FILE%"
) else (
    ECHO ERROR: requirements.txt not found! Please create it with your package list.
    pause
    exit /b
)

REM 3. Register VENV as a Jupyter Kernel (for Papermill)
ECHO Registering VENV as Jupyter Kernel (python3)...
python -m ipykernel install --user --name=python3 --display-name "Project VENV (papermill)"

ECHO ----------------------------------------------------
ECHO ✅ SUCCESS: Environment setup complete!
ECHO Run 'run_trial_balance_report.bat' to execute the automation.
ECHO ----------------------------------------------------
pause