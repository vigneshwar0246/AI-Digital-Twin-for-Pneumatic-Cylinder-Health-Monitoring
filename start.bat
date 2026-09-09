@echo off
setlocal

rem Fixed local development addresses.
set "PROJECT_ROOT=%~dp0"
set "BACKEND_URL=http://127.0.0.1:8000"
set "FRONTEND_URL=http://127.0.0.1:5173"
set "PYTHON_EXE=%PROJECT_ROOT%.venv\Scripts\python.exe"

if not exist "%PYTHON_EXE%" (
    echo ERROR: Python environment not found at "%PYTHON_EXE%".
    echo Create it and install dependencies first:
    echo   python -m venv .venv
    echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)

where npm.cmd >nul 2>nul
if errorlevel 1 (
    echo ERROR: npm.cmd was not found. Install Node.js and try again.
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%frontend\node_modules" (
    echo ERROR: Frontend packages are not installed.
    echo Run: cd /d "%PROJECT_ROOT%frontend" ^&^& npm.cmd install
    pause
    exit /b 1
)

echo Starting backend at %BACKEND_URL% ...
start "Digital Twin Backend - port 8000" /D "%PROJECT_ROOT%" cmd.exe /k "set CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173&& "%PYTHON_EXE%" -m uvicorn backend.api.main:app --host 127.0.0.1 --port 8000"

echo Starting frontend at %FRONTEND_URL% ...
start "Digital Twin Frontend - port 5173" /D "%PROJECT_ROOT%frontend" cmd.exe /k "npm.cmd run dev"

echo Waiting for both services, then the browser will open ...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$urls = @('%BACKEND_URL%/api/v1/health', '%FRONTEND_URL%'); foreach ($url in $urls) { $ready = $false; for ($i = 0; $i -lt 60; $i++) { try { Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 2 | Out-Null; $ready = $true; break } catch { Start-Sleep -Seconds 1 } }; if (-not $ready) { Write-Host ('Timed out waiting for ' + $url); exit 1 } }"

if errorlevel 1 (
    echo One or both services did not become ready. Check the backend and frontend windows.
    pause
    exit /b 1
)

echo Digital Twin is ready at %FRONTEND_URL%.
start "" "%FRONTEND_URL%"
endlocal
