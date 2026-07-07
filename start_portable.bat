@echo off
chcp 65001 >nul
cd /d "%~dp0"

if not exist "python_portable\python.exe" (
    echo ポータブル Python が未セットアップです。
    echo install_portable_python.ps1 を先に実行してください。
    echo.
    echo PowerShell で:
    echo   powershell -ExecutionPolicy Bypass -File install_portable_python.ps1
    pause
    exit /b 1
)

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP: =%

echo ========================================
echo アンケートサーバー起動（ポータブル版）
echo ========================================
echo.
echo  回答用: http://localhost:5000
echo  スマホ: http://%IP%:5000
echo  回答一覧: http://localhost:5000/results
echo.
echo  この窓を閉じると停止します
echo ========================================
echo.

python_portable\python.exe app.py
pause
