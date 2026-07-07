@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo ポータブル Python でアンケート起動
echo （システムへのインストール不要）
echo ========================================
echo.

if not exist "python_portable\python.exe" (
    echo [1回目] セットアップを実行します...
    echo.
    powershell -ExecutionPolicy Bypass -File "%~dp0install_portable_python.ps1"
    echo.
    if not exist "python_portable\python.exe" (
        echo セットアップに失敗しました。インターネット接続を確認してください。
        pause
        exit /b 1
    )
)

call "%~dp0start.bat"
