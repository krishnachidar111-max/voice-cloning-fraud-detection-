@echo off
setlocal
echo ========================================================
echo       EchoGuard AI - Pre-Flight Check & Server Startup
echo ========================================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    where py >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python 3.11+ is not found in PATH.
        pause
        exit /b 1
    )
)
echo [OK] Python is available.

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not found in PATH.
    pause
    exit /b 1
)
echo [OK] Node.js is available.

if exist "%~dp0models\head.joblib" (
    echo [OK] Detector head model artifact verified.
) else (
    echo [WARN] models\head.joblib not found. System will start in FALLBACK mode.
    echo Run: python scripts\train_head.py to generate it.
)

echo.
echo Starting Backend API at http://127.0.0.1:8000 ...
start "EchoGuard AI - Backend" cmd /k "cd /d "%~dp0" && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 /nobreak >nul

echo Starting Frontend UI at http://127.0.0.1:5173 ...
start "EchoGuard AI - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================================
echo Servers successfully launched!
echo Frontend:    http://127.0.0.1:5173
echo Backend API: http://127.0.0.1:8000/docs
echo ========================================================
echo.
pause
