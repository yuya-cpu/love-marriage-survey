@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo アンケートサーバー 診断
echo ========================================
echo.

echo [1/4] Python の確認...
where python >nul 2>&1
if errorlevel 1 (
    echo   NG - Python が見つかりません
    echo   → https://www.python.org/downloads/ をインストール
    echo   → インストール時 "Add Python to PATH" にチェック
    goto :end
)
for /f "delims=" %%v in ('python --version 2^>^&1') do echo   OK - %%v

echo.
echo [2/4] Flask の確認...
python -c "import flask; print('  OK - Flask', flask.__version__)" 2>nul
if errorlevel 1 (
    echo   NG - Flask 未インストール。インストール中...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo   NG - pip install に失敗しました
        goto :end
    )
)

echo.
echo [3/4] ポート 5000 の確認...
netstat -ano | findstr ":5000" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo   注意 - ポート5000は既に使用中です
    netstat -ano | findstr ":5000" | findstr "LISTENING"
) else (
    echo   OK - ポート5000は空いています（サーバー未起動）
)

echo.
echo [4/4] アプリのインポート確認...
python -c "import app; print('  OK - app.py は正常')" 2>nul
if errorlevel 1 (
    echo   NG - app.py の読み込みに失敗
    python -c "import app"
    goto :end
)

echo.
echo ========================================
echo 診断完了。問題なければ start.bat を実行してください。
echo ========================================

:end
echo.
pause
