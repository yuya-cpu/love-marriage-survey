@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo 恋愛・結婚観アンケート（Python版）
echo ========================================
echo.

set PYEXE=

REM 1. python を試す（実行できるものだけ採用）
where python >nul 2>&1
if not errorlevel 1 (
    python --version >nul 2>&1
    if not errorlevel 1 set PYEXE=python
)

REM 2. py ランチャーを試す
if not defined PYEXE (
    where py >nul 2>&1
    if not errorlevel 1 (
        py --version >nul 2>&1
        if not errorlevel 1 set PYEXE=py
    )
)

REM 3. ポータブル版
if not defined PYEXE (
    if exist "python_portable\python.exe" set PYEXE=python_portable\python.exe
)

if not defined PYEXE (
    echo [原因] python コマンドはあるが実行できない状態です。
    echo.
    echo これは Windows の「Microsoft Store ダミー」が原因のことが多いです。
    echo.
    echo 【対処法 A】Store ダミーをオフにして本物を入れる
    echo   1. 設定 - アプリ - アプリ実行エイリアス
    echo   2. python.exe と python3.exe を OFF
    echo   3. https://www.python.org/downloads/ からインストール
    echo      ※ "Add python.exe to PATH" にチェック
    echo   4. PC を再起動して start.bat を再実行
    echo.
    echo 【対処法 B】インストール不要のポータブル版を使う
    echo   PowerShell で以下を実行:
    echo   powershell -ExecutionPolicy Bypass -File install_portable_python.ps1
    echo   完了後 start_portable.bat をダブルクリック
    echo.
    pause
    exit /b 1
)

echo 使用する Python: %PYEXE%
%PYEXE% --version
if errorlevel 1 (
    echo [エラー] Python の実行に失敗しました。
    pause
    exit /b 1
)

echo.
echo パッケージをインストール中...
%PYEXE% -m pip install -r requirements.txt -q
if errorlevel 1 (
    echo [エラー] pip install に失敗しました。
    echo 手動で試す: %PYEXE% -m pip install flask
    pause
    exit /b 1
)

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP: =%

echo.
echo ========================================
echo  起動します。ブラウザで開いてください:
echo.
echo    http://localhost:5000
echo.
echo  スマホ（同じWi-Fi）: http://%IP%:5000
echo  回答一覧:            http://localhost:5000/results
echo.
echo  ※ この窓を閉じると停止します
echo ========================================
echo.

%PYEXE% app.py
if errorlevel 1 (
    echo.
    echo ポート5000で失敗。8080で再試行...
    set PORT=8080
    echo  → http://localhost:8080
    %PYEXE% app.py
)
pause
