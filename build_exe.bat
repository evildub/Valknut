@echo off
echo ===================================================
echo   Building Valknut Brand Intelligence Standalone EXE
echo ===================================================

echo [1/5] Closing any running Valknut instances...
taskkill /F /IM ValknutBrandIntelligence.exe 2>nul
timeout /t 1 /nobreak >nul

echo [2/5] Running PyInstaller...
python -m PyInstaller --onedir --noconsole --noconfirm --name "ValknutBrandIntelligence" --icon="valknut.ico" --add-data "data.json;." --add-data "valknut.ico;." --add-data "valknut.png;." --hidden-import "PIL" --hidden-import "PIL.ImageTk" --hidden-import "openpyxl" --hidden-import "bs4" --hidden-import "requests" --hidden-import "curl_cffi" --hidden-import "curl_cffi.requests" --hidden-import "playwright" --hidden-import "playwright.sync_api" main.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PyInstaller build failed with exit code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo [3/5] Copying data.json and application icons into distribution directory...
copy /Y "data.json" "dist\ValknutBrandIntelligence\data.json" >nul
copy /Y "valknut.ico" "dist\ValknutBrandIntelligence\valknut.ico" >nul
copy /Y "valknut.png" "dist\ValknutBrandIntelligence\valknut.png" >nul

echo [4/5] Bundling Security Audit and Analyst Documentation...
copy /Y "SECURITY_AUDIT.md" "dist\ValknutBrandIntelligence\SECURITY_AUDIT.md" >nul
copy /Y "EXE_README.md" "dist\ValknutBrandIntelligence\README.md" >nul

echo [5/5] Build complete! Starting application...
start "" "dist\ValknutBrandIntelligence\ValknutBrandIntelligence.exe"
echo Done!
