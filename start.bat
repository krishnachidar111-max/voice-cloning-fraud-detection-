@echo off
echo ========================================================
echo          EchoGuard AI - Launching Development Servers
echo ========================================================
echo.
echo Starting Backend API at http://127.0.0.1:8000 ...
start "EchoGuard AI - Backend" cmd /k "cd /d "%~dp0" && py -3.12 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload || python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 /nobreak >nul

echo Starting Frontend UI at http://127.0.0.1:5173 ...
start "EchoGuard AI - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Servers started!
echo Frontend: http://127.0.0.1:5173
echo Backend API Docs: http://127.0.0.1:8000/docs
echo.
pause
