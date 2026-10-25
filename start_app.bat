@echo off
setlocal enabledelayedexpansion
title QUBIX - Application Launcher

echo =====================================================================
echo                 QUBIX - Smart Document Verification System          
echo =====================================================================
echo.

set "ROOT_DIR=%~dp0"
cd /d "%ROOT_DIR%"

:: 1. Check directory structure
if not exist "backend" (
    echo [ERROR] 'backend' directory not found at: %ROOT_DIR%backend
    echo Please make sure you are running start_app.bat from the project root.
    pause
    exit /b 1
)

if not exist "frontend" (
    echo [ERROR] 'frontend' directory not found at: %ROOT_DIR%frontend
    echo Please make sure you are running start_app.bat from the project root.
    pause
    exit /b 1
)

:: 2. Locate Python executable
set "PYTHON_CMD="
python --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=python"
) else (
    py -3.11 --version >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        set "PYTHON_CMD=py -3.11"
    ) else (
        if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
            set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        ) else if exist "%ProgramFiles%\Python311\python.exe" (
            set "PYTHON_CMD=%ProgramFiles%\Python311\python.exe"
        )
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERROR] Python is not found or not in PATH.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Or run via PowerShell: winget install Python.Python.3.11
    pause
    exit /b 1
)
echo [OK] Python located: %PYTHON_CMD%

:: 3. Locate Node.js & npm
set "NODE_CMD="
set "NPM_CMD="
node --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "NODE_CMD=node"
    set "NPM_CMD=npm"
) else (
    if exist "%LOCALAPPDATA%\Programs\nodejs\node.exe" (
        set "NODE_CMD=%LOCALAPPDATA%\Programs\nodejs\node.exe"
        set "NPM_CMD=%LOCALAPPDATA%\Programs\nodejs\npm.cmd"
        set "PATH=%LOCALAPPDATA%\Programs\nodejs;%PATH%"
    ) else if exist "%ProgramFiles%\nodejs\node.exe" (
        set "NODE_CMD=%ProgramFiles%\nodejs\node.exe"
        set "NPM_CMD=%ProgramFiles%\nodejs\npm.cmd"
        set "PATH=%ProgramFiles%\nodejs;%PATH%"
    )
)

if "%NODE_CMD%"=="" (
    echo [ERROR] Node.js is not found or not in PATH.
    echo Please install Node.js (LTS) from https://nodejs.org/
    echo Or run via PowerShell: winget install OpenJS.NodeJS.LTS
    pause
    exit /b 1
)
echo [OK] Node.js located: %NODE_CMD%

:: 4. Ensure environment configuration (.env)
if not exist "backend\.env" (
    if exist "backend\.env.example" (
        echo [INFO] Creating backend\.env from template...
        copy "backend\.env.example" "backend\.env" >nul
        echo [OK] Environment template created.
    ) else (
        echo [WARNING] backend\.env.example not found; continuing with defaults.
    )
)

:: 5. Set up Python Virtual Environment
if not exist "backend\venv\Scripts\python.exe" (
    echo [INFO] Creating Python virtual environment in backend\venv...
    %PYTHON_CMD% -m venv "backend\venv"
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
)

:: 6. Install Backend Dependencies
if not exist "backend\venv\.installed" (
    echo [INFO] Installing backend dependencies from requirements.txt...
    "backend\venv\Scripts\python.exe" -m pip install -r "backend\requirements.txt"
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install backend dependencies.
        pause
        exit /b 1
    )
    echo installed > "backend\venv\.installed"
    echo [OK] Backend dependencies installed.
) else (
    echo [OK] Backend dependencies verified.
)

:: 7. Install Frontend Dependencies
if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend dependencies via npm...
    cd /d "%ROOT_DIR%frontend"
    call "%NPM_CMD%" install
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install frontend npm packages.
        cd /d "%ROOT_DIR%"
        pause
        exit /b 1
    )
    cd /d "%ROOT_DIR%"
    echo [OK] Frontend dependencies installed.
) else (
    echo [OK] Frontend dependencies verified.
)

:: 8. Launch Backend in separate window
echo [INFO] Starting FastAPI Backend on http://127.0.0.1:8000...
start "QUBIX - Backend (FastAPI)" cmd /k "cd /d %ROOT_DIR%backend && .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

:: 9. Launch Frontend in separate window
echo [INFO] Starting React Frontend on http://localhost:5173...
start "QUBIX - Frontend (React Vite)" cmd /k "set PATH=%LOCALAPPDATA%\Programs\nodejs;%ProgramFiles%\nodejs;!PATH! && cd /d %ROOT_DIR%frontend && npm run dev"

:: 10. Completed notification & open browser
echo.
echo =====================================================================
echo                   QUBIX is now starting up!                      
echo =====================================================================
echo.
echo   * Web Dashboard:       http://localhost:5173
echo   * Backend REST API:    http://127.0.0.1:8000
echo   * Interactive API Doc: http://127.0.0.1:8000/docs
echo.
echo Opening browser in 3 seconds...
timeout /t 3 >nul
start http://localhost:5173
echo.
echo Press any key to close this launcher window (servers remain running)...
pause >nul
