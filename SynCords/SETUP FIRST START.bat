@echo off
setlocal

:: Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed. Downloading and installing...
    start "" "https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe"
    echo Please install Python and re-run this script.
    exit /b
)

:: Get the directory of the script
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Run the Python script
echo Running test1.py...
python setup.py

endlocal
exit

