@echo off
setlocal

set "PORT=%~1"
if "%PORT%"=="" set "PORT=8000"

set "SCRIPT_DIR=%~dp0"
set "REPO_ROOT=%SCRIPT_DIR%.."
set "BACKEND_DIR=%REPO_ROOT%\backend"
set "VENV_PYTHON=%BACKEND_DIR%\.venv\Scripts\python.exe"

if not exist "%VENV_PYTHON%" (
  echo Backend virtual environment was not found at:
  echo %VENV_PYTHON%
  exit /b 1
)

cd /d "%BACKEND_DIR%"
echo Running FastAPI backend on http://127.0.0.1:%PORT%
echo Press Ctrl+C in this window to stop the backend.
"%VENV_PYTHON%" -m uvicorn app.main:app --host 127.0.0.1 --port %PORT%
