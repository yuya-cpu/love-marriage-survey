# ステップ1: GitHub にアップロード（ログ出力版）
$LogFile = Join-Path $PSScriptRoot "step1_log.txt"
Start-Transcript -Path $LogFile -Force | Out-Null

$ErrorActionPreference = "Continue"
$ProjectDir = $PSScriptRoot
Set-Location $ProjectDir

Write-Host "========================================"
Write-Host " ステップ1: GitHub にアップロード"
Write-Host "========================================"
Write-Host "  フォルダ: $ProjectDir"
Write-Host ""

try {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Host "NG: Git がインストールされていません。"
        exit 1
    }

    if (-not (Test-Path ".git")) {
        Write-Host "[1/5] Git リポジトリを初期化..."
        git init
        git branch -M main
    } else {
        Write-Host "[1/5] Git リポジトリ: 既存"
    }

    Write-Host "[2/5] 機密ファイルの除外を確認..."
    git check-ignore -v .env 2>&1
    git check-ignore -v credentials/service-account.json 2>&1

    Write-Host "[3/5] ファイルをステージング..."
    git add .
    git status

    $staged = git diff --cached --name-only
    $sensitive = $staged | Where-Object { $_ -match '^\.env$|^credentials/' }
    if ($sensitive) {
        Write-Host "NG: 機密ファイルがステージされています！"
        $sensitive | ForEach-Object { Write-Host "  - $_" }
        git reset HEAD 2>$null
        exit 1
    }

    $porcelain = git status --porcelain
    if ($porcelain) {
        Write-Host "[4/5] コミット..."
        git commit -m "Deploy love marriage survey"
    } else {
        Write-Host "[4/5] コミット: 変更なし"
    }

    Write-Host "[5/5] GitHub にプッシュ..."

    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Write-Host "NG: GitHub CLI (gh) が未インストールです。"
        Write-Host "https://cli.github.com/ からインストール後、再実行してください。"
        exit 1
    }

    gh auth status 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "gh auth login が必要です。ターミナルで gh auth login を実行してください。"
        exit 1
    }

    $repoName = "love-marriage-survey"
    $createOut = gh repo create $repoName --public --source=. --remote=origin --push 2>&1
    $createOut | ForEach-Object { Write-Host $_ }

    if ($LASTEXITCODE -ne 0 -or ($createOut -join " ") -match "already exists|name already") {
        Write-Host "既存リポジトリへ push を試みます..."
        $remote = git remote get-url origin 2>$null
        if (-not $remote) {
            $username = gh api user -q .login 2>$null
            if ($username) {
                git remote add origin "https://github.com/$username/$repoName.git"
            }
        }
        git push -u origin main 2>&1
    }

    $url = gh repo view --json url -q .url 2>$null
    if ($url) {
        Write-Host ""
        Write-Host "========================================"
        Write-Host " ステップ1 完了！"
        Write-Host " リポジトリ URL: $url"
        Write-Host "========================================"
    } else {
        Write-Host "URL 取得失敗。git remote -v を確認してください。"
        git remote -v 2>&1
    }
} catch {
    Write-Host "エラー: $_"
    exit 1
} finally {
    Stop-Transcript | Out-Null
}
