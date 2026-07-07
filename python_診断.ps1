# Python インストール問題の診断スクリプト
# 使い方: PowerShell で右クリック →「PowerShell で実行」
# または: powershell -ExecutionPolicy Bypass -File python_診断.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Python インストール問題 診断" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

function Test-Cmd($label, $script) {
    Write-Host "[$label]" -ForegroundColor Yellow
    try {
        Invoke-Expression $script 2>&1 | ForEach-Object { Write-Host "  $_" }
    } catch {
        Write-Host "  エラー: $_" -ForegroundColor Red
    }
    Write-Host ""
}

Test-Cmd "1. python コマンド" "where.exe python"
Test-Cmd "2. py ランチャー" "where.exe py"
Test-Cmd "3. python バージョン" "python --version"
Test-Cmd "4. py バージョン" "py --version"
Test-Cmd "5. OS情報" "systeminfo | findstr /B /C:`"OS Name`" /C:`"OS Version`" /C:`"System Type`""
Test-Cmd "6. Python レジストリ" 'reg query "HKLM\SOFTWARE\Python\PythonCore" /s'
Test-Cmd "7. winget" "winget --version"
Test-Cmd "8. 標準インストール先" 'Test-Path "$env:LOCALAPPDATA\Programs\Python"'
Test-Cmd "9. フォルダ内容" 'Get-ChildItem "$env:LOCALAPPDATA\Programs\Python" -ErrorAction SilentlyContinue'
Test-Cmd "10. Store スタブ" 'Get-Command python -ErrorAction SilentlyContinue | Select-Object Source'

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " よくある原因と対処" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host @"

A) Microsoft Store のダミーだけ
   → 設定 → アプリ → アプリ実行エイリアス
   → python.exe / python3.exe を OFF
   → python.org から再インストール

B) PATH が通っていない
   → インストール時「Add python.exe to PATH」にチェック
   → PCを再起動

C) 権限・ウイルス対策でブロック
   → 管理者としてインストーラを実行
   → Windows Defender のブロック履歴を確認

D) ディスク容量不足
   → 空き容量 500MB 以上を確保

E) Windows Sモード
   → 設定 → システム → バージョン情報 → Sモードの解除

F) Python を入れずにアンケートを使う
   → install_portable_python.ps1 を実行（インストール不要版）
   → または アンケート（Python不要）.html をダブルクリック

"@

Write-Host "診断完了。上の出力をスクリーンショットまたはコピーで共有してください。" -ForegroundColor Green
Write-Host ""
Read-Host "Enter キーで終了"
