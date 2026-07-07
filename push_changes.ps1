# 変更をコミットして GitHub にプッシュ
$ErrorActionPreference = "Stop"
$ProjectDir = $PSScriptRoot
Set-Location $ProjectDir

Write-Host "========================================"
Write-Host " 変更をコミットしてプッシュ"
Write-Host "========================================"
Write-Host "  フォルダ: $ProjectDir"
Write-Host ""

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "NG: Git がインストールされていません。"
    exit 1
}

$files = @(
    "app.py",
    "response_schema.py",
    "templates/survey.html",
    "survey_data.py"
)

Write-Host "[1/4] 変更ファイルをステージング..."
foreach ($file in $files) {
    if (Test-Path $file) {
        git add $file
        Write-Host "  + $file"
    } else {
        Write-Host "  ! 見つかりません: $file"
    }
}

$staged = git diff --cached --name-only
if (-not $staged) {
    Write-Host "コミットする変更がありません。"
    git status
    exit 0
}

Write-Host ""
Write-Host "[2/4] ステージ済み:"
$staged | ForEach-Object { Write-Host "  - $_" }

Write-Host ""
Write-Host "[3/4] コミット..."
$commitMessage = @"
Q1/Q2の「その他」自由記述を任意順位で保存し、プライバシー表記をゼミ研究に更新

- q1_other_text / q2_other_text を rank2 限定から任意順位に対応
- FORM_PRIVACY_NOTICE を「卒業研究」から「ゼミ研究」に変更
"@
git commit -m $commitMessage

Write-Host ""
Write-Host "[4/4] プッシュ..."
$branch = git branch --show-current
if (-not $branch) { $branch = "main" }

$remote = git remote get-url origin 2>$null
if (-not $remote) {
    Write-Host "NG: origin リモートが設定されていません。"
    Write-Host "先に step1_github_push.bat を実行するか、git remote add origin を設定してください。"
    exit 1
}

git push -u origin $branch
$hash = git rev-parse --short HEAD

Write-Host ""
Write-Host "========================================"
Write-Host " 完了"
Write-Host "  ブランチ: $branch"
Write-Host "  コミット: $hash"
Write-Host "  リモート: $remote"
Write-Host "========================================"
