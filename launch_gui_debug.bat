@echo off
REM Debug launcher for PEMI Report Automation (keeps console open)
cd /d "%~dp0"
echo Working directory: %CD%
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo Activated .venv
) else (
    echo .venv not found or missing activate.bat
)

REM Determine python executable to use (prefer venv pythonw)
set PYEXEC=
if exist "%~dp0.venv\Scripts\pythonw.exe" (
    set PYEXEC="%~dp0.venv\Scripts\pythonw.exe"
) else if exist "%~dp0.venv\Scripts\python.exe" (
    set PYEXEC="%~dp0.venv\Scripts\python.exe"
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

echo Using Python: %PYEXEC%

echo Launching GUI now...
%PYEXEC% "%~dp0src\gui\trial_balance_app.py"

echo GUI process exited with ERRORLEVEL=%ERRORLEVEL%
pause
