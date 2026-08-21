@echo off
echo ===================================================
echo   Building Valknut Brand Intelligence Standalone EXE
echo ===================================================

echo [1/5] Closing any running Valknut instances...
taskkill /F /IM "Valknut Brand Intelligence.exe" 2>nul
taskkill /F /IM ValknutBrandIntelligence.exe 2>nul
timeout /t 1 /nobreak >nul

echo [2/5] Running PyInstaller...
python -m PyInstaller --onedir --noconsole --noconfirm --name "Valknut Brand Intelligence" --icon="%~dp0valknut.ico" --add-data "data.json;." --add-data "valknut.ico;." --add-data "valknut.png;." --hidden-import "PIL" --hidden-import "PIL.ImageTk" --hidden-import "openpyxl" --hidden-import "bs4" --hidden-import "requests" --hidden-import "curl_cffi" --hidden-import "curl_cffi.requests" --hidden-import "playwright" --hidden-import "playwright.sync_api" main.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PyInstaller build failed with exit code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo [3/5] Copying data.json into distribution directory...
copy /Y "data.json" "dist\Valknut Brand Intelligence\data.json" >nul

echo [4/5] Bundling Security Audit and Analyst Documentation...
copy /Y "SECURITY_AUDIT.md" "dist\Valknut Brand Intelligence\SECURITY_AUDIT.md" >nul
copy /Y "EXE_README.md" "dist\Valknut Brand Intelligence\README.md" >nul

echo [5/5] Build complete! Starting application...
start "" "dist\Valknut Brand Intelligence\Valknut Brand Intelligence.exe"
echo Done!
