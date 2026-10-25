# Run Backend FastAPI Server
$ErrorActionPreference = "Stop"

$pythonDir = "$env:LOCALAPPDATA\Programs\Python\Python311"
if (Test-Path "$pythonDir\python.exe") {
    $env:Path = "$pythonDir;$pythonDir\Scripts;$env:Path"
}

$backendDir = Join-Path $PSScriptRoot "backend"
Set-Location $backendDir

Write-Host "Starting QUBIX Backend..." -ForegroundColor Cyan
Write-Host "API: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Green

& ".\venv\Scripts\python.exe" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
