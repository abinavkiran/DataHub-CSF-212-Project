@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0sync_credentials_env.ps1"
exit /b %errorlevel%
