# Run Frontend Development Server
$ErrorActionPreference = "Stop"

# Ensure Node.js is in the session PATH
$nodeDir = "$env:LOCALAPPDATA\Programs\nodejs"
if (Test-Path "$nodeDir\node.exe") {
    $env:Path = "$nodeDir;$env:Path"
}

$frontendDir = Join-Path $PSScriptRoot "frontend"
Set-Location $frontendDir

Write-Host "Starting QUBIX Frontend..." -ForegroundColor Cyan
Write-Host "URL: http://localhost:5173" -ForegroundColor Green

npm run dev
