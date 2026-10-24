# EchoGuard AI - PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       EchoGuard AI - Starting Development Servers" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$WorkspaceRoot = $PSScriptRoot

Write-Host "Starting Backend API (http://127.0.0.1:8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$WorkspaceRoot'; py -3.12 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

Start-Sleep -Seconds 2

Write-Host "Starting Frontend UI (http://127.0.0.1:5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$WorkspaceRoot\frontend'; npm run dev"

Write-Host "`nBoth servers started!" -ForegroundColor Green
Write-Host "Frontend: http://127.0.0.1:5173" -ForegroundColor Green
Write-Host "Backend Docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
