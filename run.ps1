# Python でアンケートを起動
# 使い方: powershell -ExecutionPolicy Bypass -File run.ps1

Set-Location $PSScriptRoot

$py = $null
if (Get-Command python -ErrorAction SilentlyContinue) { $py = "python" }
elseif (Get-Command py -ErrorAction SilentlyContinue) { $py = "py" }
elseif (Test-Path ".\python_portable\python.exe") { $py = ".\python_portable\python.exe" }

if (-not $py) {
    Write-Host "[エラー] Python が見つかりません。" -ForegroundColor Red
    Write-Host "python.org からインストールするか、install_portable_python.ps1 を実行してください。"
    Read-Host "Enter で終了"
    exit 1
}

Write-Host "使用する Python: $py" -ForegroundColor Cyan
& $py --version

Write-Host "Flask をインストール中..." -ForegroundColor Yellow
& $py -m pip install -r requirements.txt -q

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " http://localhost:5000 をブラウザで開く" -ForegroundColor Green
Write-Host " 回答一覧: http://localhost:5000/results" -ForegroundColor Green
Write-Host " 終了: Ctrl+C" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

& $py app.py
