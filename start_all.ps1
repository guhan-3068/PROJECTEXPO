# Start both Backend and Frontend in separate windows
$ErrorActionPreference = "Stop"

$nodeDir = "$env:LOCALAPPDATA\Programs\nodejs"
$pythonDir = "$env:LOCALAPPDATA\Programs\Python\Python311"
$backendDir = Join-Path $PSScriptRoot "backend"
$frontendDir = Join-Path $PSScriptRoot "frontend"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "         Starting QUBIX Backend & Frontend        " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Launch Backend in separate window
Write-Host "[1/2] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$host.UI.RawUI.WindowTitle = 'QUBIX - Backend'; `$env:Path = '$nodeDir;$pythonDir;$pythonDir\Scripts;' + `$env:Path; Set-Location '$backendDir'; Write-Host 'FastAPI Backend running on http://127.0.0.1:8000' -ForegroundColor Green; & '.\venv\Scripts\python.exe' -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 }"

# 2. Launch Frontend in separate window
Write-Host "[2/2] Starting React Frontend on http://localhost:5173..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "& { `$host.UI.RawUI.WindowTitle = 'QUBIX - Frontend'; `$env:Path = '$nodeDir;' + `$env:Path; Set-Location '$frontendDir'; Write-Host 'React Frontend running on http://localhost:5173' -ForegroundColor Green; npm run dev }"

Write-Host "`n[SUCCESS] Servers launched in separate windows!" -ForegroundColor Green
Write-Host "  * Web Application:    http://localhost:5173" -ForegroundColor Yellow
Write-Host "  * API Documentation:  http://127.0.0.1:8000/docs" -ForegroundColor Yellow
Write-Host "`nOpening browser in 2 seconds..." -ForegroundColor Gray

Start-Sleep -Seconds 2
Start-Process "http://localhost:5173"
