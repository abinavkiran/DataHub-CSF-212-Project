@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0datahub.ps1" %*
exit /b %errorlevel%
