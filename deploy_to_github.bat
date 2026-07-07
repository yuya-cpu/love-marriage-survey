@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo GitHub へプッシュ（Render デプロイ準備）
echo ========================================
echo.

where git >nul 2>&1
if errorlevel 1 (
    echo Git がインストールされていません。
    echo https://git-scm.com/download/win からインストールしてください。
    pause
    exit /b 1
)

where gh >nul 2>&1
if errorlevel 1 (
    echo GitHub CLI ^(gh^) が見つかりません。
    echo https://cli.github.com/ からインストール後、gh auth login を実行してください。
    pause
    exit /b 1
)

if not exist ".git" (
    git init
    git branch -M main
)

git add .
git status

echo.
set /p CONFIRM=コミットして GitHub にプッシュしますか？ (y/n): 
if /i not "%CONFIRM%"=="y" exit /b 0

git commit -m "Deploy love-marriage-survey to Render" 2>nul
if errorlevel 1 (
    echo コミットする変更がないか、既にコミット済みです。
)

echo.
echo GitHub リポジトリを作成してプッシュします...
gh repo create love-marriage-survey --public --source=. --remote=origin --push 2>nul
if errorlevel 1 (
    echo リポジトリが既にある場合はプッシュのみ試行します...
    git remote add origin https://github.com/%USERNAME%/love-marriage-survey.git 2>nul
    git push -u origin main
)

echo.
echo ========================================
echo 完了！次は Render で Web Service を作成してください。
echo 詳細: RENDER_DEPLOY_NOW.md
echo ========================================
pause
