@echo off
setlocal
title Aurea Launcher

set "PROJECT_ROOT=%~dp0"
set "BACKEND_DIR=%PROJECT_ROOT%aurea-v2\backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"
set "PYTHON_EXE=%BACKEND_DIR%\.venv\Scripts\python.exe"

echo.
echo  Starting Aurea locally...
echo.

if not exist "%PYTHON_EXE%" (
  echo Backend virtual environment is not set up yet.
  echo.
  echo Run these commands once in PowerShell:
  echo   cd /d "%BACKEND_DIR%"
  echo   python -m venv .venv
  echo   .venv\Scripts\python -m pip install -r requirements.txt
  echo.
  pause
  exit /b 1
)

if not exist "%FRONTEND_DIR%\node_modules" (
  echo Frontend dependencies are not installed yet.
  echo.
  echo Run these commands once in PowerShell:
  echo   cd /d "%FRONTEND_DIR%"
  echo   npm install
  echo.
  pause
  exit /b 1
)

start "Aurea Backend" /D "%BACKEND_DIR%" cmd /k .venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
start "Aurea Frontend" /D "%FRONTEND_DIR%" cmd /k npm run dev

echo Backend:  http://127.0.0.1:8000/health
echo Frontend: http://localhost:3000
echo.
echo Keep the two opened terminal windows running while using the app.
timeout /t 3 /nobreak >nul
start "" http://localhost:3000
endlocal
