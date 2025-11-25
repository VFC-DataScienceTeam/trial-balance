@echo off
REM Launcher that captures GUI stdout/stderr to logs/launch_gui.log
cd /d "%~dp0"
mkdir "logs" 2>nul

REM Activate venv if present
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Choose python executable
set PYEXEC=
if exist "%~dp0.venv\Scripts\pythonw.exe" (
    set PYEXEC=%~dp0.venv\Scripts\pythonw.exe
) else if exist "%~dp0.venv\Scripts\python.exe" (
    set PYEXEC=%~dp0.venv\Scripts\python.exe
) else (
    where pythonw.exe >nul 2>&1
    if %ERRORLEVEL%==0 (
        set PYEXEC=pythonw.exe
    ) else (
        where python >nul 2>&1
        if %ERRORLEVEL%==0 (
            set PYEXEC=python
        ) else (
            echo ERROR: No Python interpreter found on PATH and no .venv present.
            pause
            exit /b 1
        )
    )
)

echo Using Python: %PYEXEC% > "logs\launch_gui.log"
echo Launching PEMI Report Automation (output appended to logs\launch_gui.log)... >> "logs\launch_gui.log"

REM Start the GUI and redirect stdout/stderr to the log (use start to detach)
start "Trial Balance Processor" %PYEXEC% "%~dp0src\gui\trial_balance_app.py" >> "logs\launch_gui.log" 2>>&1

echo Launched (check logs\launch_gui.log) && exit /b 0
