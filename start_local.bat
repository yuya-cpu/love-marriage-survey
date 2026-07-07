@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo ローカル起動（Google Sheets 連携）
echo ========================================
echo.

set PYEXE=
where python >nul 2>&1 && python --version >nul 2>&1 && set PYEXE=python
if not defined PYEXE where py >nul 2>&1 && py --version >nul 2>&1 && set PYEXE=py
if not defined PYEXE (
    echo Python が見つかりません。start.bat の対処法を参照してください。
    pause
    exit /b 1
)

if not exist "credentials\service-account.json" (
    echo credentials\service-account.json がありません。
    pause
    exit /b 1
)

echo パッケージをインストール中...
%PYEXE% -m pip install -r requirements.txt -q --no-warn-script-location

echo.
echo 認証ファイルを修復中...
%PYEXE% fix_credentials.py
if errorlevel 1 (
    echo.
    echo Python 3.14 をお使いの場合、3.12 のインストールを推奨します。
    echo https://www.python.org/downloads/release/python-31210/
    pause
    exit /b 1
)

echo.
echo 接続テスト中...
%PYEXE% test_sheets_connection.py
if errorlevel 1 (
    echo.
    echo .env の GOOGLE_SPREADSHEET_ID を設定してから再実行してください。
    pause
    exit /b 1
)

echo.
echo ========================================
echo  http://localhost:5000
echo  回答一覧: http://localhost:5000/results
echo ========================================
echo.

%PYEXE% app.py
pause
