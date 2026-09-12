@echo off
title Personal AI Assistant - 1-Click Installer
echo ==================================================
echo    Personal AI Desktop Assistant Setup
echo ==================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b
)

echo [1/3] Installing required packages...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b
)

echo [2/3] Setting up configuration...
if not exist .env (
    copy .env.example .env
    echo Created .env configuration file.
)

echo [3/3] Creating Desktop Shortcut...
set SCRIPT_DIR=%~dp0
set TARGET_BAT=%SCRIPT_DIR%Start_Terminal_Assistant.bat
set SHORTCUT_PATH=%USERPROFILE%\Desktop\Personal AI Assistant.lnk

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%TARGET_BAT%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Save()"

echo.
echo ==================================================
echo    Setup Completed Successfully!
echo    A shortcut has been created on your Desktop:
echo    "Personal AI Assistant"
echo ==================================================
echo.
pause
