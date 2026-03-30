@echo off
setlocal
set "PORT=8090"
if not "%~1"=="" set "PORT=%~1"

call ..\sync_credentials_env.cmd
if errorlevel 1 exit /b %errorlevel%

echo Starting DB dashboard at http://localhost:%PORT%
docker compose run --rm -p %PORT%:%PORT% dev-env python -m uvicorn live_demo_workspace.db_dashboard:app --host 0.0.0.0 --port %PORT%
