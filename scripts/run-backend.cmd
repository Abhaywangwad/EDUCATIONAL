@echo off
setlocal

if /I not "%~1"=="--child" (
  start "HLGS Backend" /D "%CD%" "%~f0" --child %~1 "%CD%"
  exit /b 0
)

shift
set "PORT=%~1"
if "%PORT%"=="" set "PORT=8000"
shift

set "REPO_ROOT=%~1"
if "%REPO_ROOT%"=="" set "REPO_ROOT=%CD%"
set "BACKEND_DIR=%REPO_ROOT%\backend"
set "VENV_PYTHON=%BACKEND_DIR%\.venv\Scripts\python.exe"
set "VENV_CFG=%BACKEND_DIR%\.venv\pyvenv.cfg"
set "LOG_FILE=%BACKEND_DIR%\backend.runner.log"
set "BASE_PYTHON="

if not exist "%VENV_PYTHON%" (
  echo Backend virtual environment was not found at:
  echo %VENV_PYTHON%
  exit /b 1
)

if not exist "%VENV_CFG%" (
  echo Virtual environment config was not found at:
  echo %VENV_CFG%
  exit /b 1
)

for /f "tokens=1,* delims==" %%A in ('findstr /b /c:"executable =" "%VENV_CFG%"') do (
  for /f "tokens=* delims= " %%P in ("%%B") do set "BASE_PYTHON=%%P"
)

if "%BASE_PYTHON%"=="" (
  echo Could not resolve the base Python executable from:
  echo %VENV_CFG%
  exit /b 1
)

cd /d "%BACKEND_DIR%"
set "PYTHONPATH=%BACKEND_DIR%\.venv\Lib\site-packages;%BACKEND_DIR%"
> "%LOG_FILE%" echo [%date% %time%] Starting backend runner on port %PORT%
echo Running FastAPI backend on http://127.0.0.1:%PORT%
echo Press Ctrl+C in this window to stop the backend.
"%BASE_PYTHON%" -m run_server %PORT% >> "%LOG_FILE%" 2>&1
echo [%date% %time%] Backend process exited with code %ERRORLEVEL%>> "%LOG_FILE%"
if not "%ERRORLEVEL%"=="0" (
  echo Backend exited with code %ERRORLEVEL%.
  echo See log file:
  echo %LOG_FILE%
  type "%LOG_FILE%"
  pause
)
