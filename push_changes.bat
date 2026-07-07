@echo off
chcp 65001 >nul
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "%~dp0push_changes.ps1"
pause
