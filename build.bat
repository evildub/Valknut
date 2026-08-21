@echo off
setlocal enabledelayedexpansion
title Building Standalone Valknut Brand Intelligence Suite

echo ===============================================================================
echo   Valknut Brand Intelligence - Standalone Executable Builder
echo ===============================================================================
echo.

:: 1. Verify / Install PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [*] Installing PyInstaller...
    python -m pip install "pyinstaller>=6.0.0" --no-warn-script-location
)

echo [*] Cleaning previous build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [*] Compiling standalone package with PyInstaller...
python -m PyInstaller --onedir --noconsole --noconfirm --name "ValknutBrandIntelligence" ^
    --add-data "data.json;." ^
    --hidden-import "PIL" ^
    --hidden-import "PIL.ImageTk" ^
    --hidden-import "openpyxl" ^
    --hidden-import "bs4" ^
    --hidden-import "requests" ^
    --hidden-import "curl_cffi" ^
    --hidden-import "curl_cffi.requests" ^
    --hidden-import "playwright" ^
    --hidden-import "playwright.sync_api" ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo [!] Build encountered an error.
    pause
    exit /b 1
)

echo.
echo [*] Copying default data.json to distribution folder...
if not exist "dist\ValknutBrandIntelligence\data.json" (
    copy "data.json" "dist\ValknutBrandIntelligence\data.json" >nul
)

echo.
echo ===============================================================================
echo   BUILD COMPLETE!
echo ===============================================================================
echo.
echo Your standalone folder is located at:
echo    dist\ValknutBrandIntelligence\
echo.
echo Main Executable:
echo    dist\ValknutBrandIntelligence\ValknutBrandIntelligence.exe
echo.
echo Generating SHA-256 Checksum for Corporate IT / Security Verification...
powershell -Command "Get-FileHash -Algorithm SHA256 dist\ValknutBrandIntelligence\ValknutBrandIntelligence.exe | Format-List"
echo.
echo You can copy the entire 'dist\ValknutBrandIntelligence' folder to any Windows PC without
echo needing Python installed!
echo.
pause
