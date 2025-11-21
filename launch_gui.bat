@echo off
REM Quick launcher for Trial Balance GUI
REM This file stays in the root for easy access

cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Launch the GUI using pythonw (no console window)
start "Trial Balance Processor" pythonw.exe "%~dp0src\gui\trial_balance_app.py"

exit
