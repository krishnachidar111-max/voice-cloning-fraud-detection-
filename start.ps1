# EchoGuard AI - Unified One-Command PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       EchoGuard AI - Pre-Flight Check & Server Startup" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$WorkspaceRoot = $PSScriptRoot

# 1. Check Python
$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {
    $PythonCmd = Get-Command py -ErrorAction SilentlyContinue
}
if (-not $PythonCmd) {
    Write-Host "[ERROR] Python 3.11+ is not found in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.11 or 3.12 and add it to PATH." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Python detected: $($PythonCmd.Source)" -ForegroundColor Green

# 2. Check Node.js
$NodeCmd = Get-Command node -ErrorAction SilentlyContinue
if (-not $NodeCmd) {
    Write-Host "[ERROR] Node.js is not found in PATH." -ForegroundColor Red
    Write-Host "Please install Node.js v20+ and npm." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Node.js detected: $($NodeCmd.Source)" -ForegroundColor Green

# 3. Check Detector Model Artifact
$ModelPath = Join-Path $WorkspaceRoot "models\head.joblib"
if (Test-Path $ModelPath) {
    Write-Host "[OK] Detector head model artifact verified ($ModelPath)." -ForegroundColor Green
} else {
    Write-Host "[WARN] models/head.joblib not found. System will run in FALLBACK heuristic mode." -ForegroundColor Yellow
    Write-Host "Run `python scripts/train_head.py` to train and register the detector head." -ForegroundColor Yellow
}

# 4. Launch Backend Server
Write-Host "`nStarting Backend API (http://127.0.0.1:8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$WorkspaceRoot'; python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

Start-Sleep -Seconds 2

# 5. Launch Frontend Server
Write-Host "Starting Frontend UI (http://127.0.0.1:5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$WorkspaceRoot\frontend'; npm run dev"

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host " Both servers launching!" -ForegroundColor Green
Write-Host " Frontend Web UI:    http://127.0.0.1:5173" -ForegroundColor Green
Write-Host " Backend API Docs:   http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host " WebSocket Gateway:  ws://127.0.0.1:8000/ws/audio/{session_id}" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
