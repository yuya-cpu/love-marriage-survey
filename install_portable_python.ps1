# インストール不要の Python（ポータブル版）をセットアップ
# 使い方: PowerShell で右クリック →「PowerShell で実行」

$ErrorActionPreference = "Stop"
$Version = "3.12.4"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$PortableDir = Join-Path $Root "python_portable"
$ZipFile = Join-Path $Root "python-embed.zip"
$Url = "https://www.python.org/ftp/python/$Version/python-$Version-embed-amd64.zip"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " ポータブル Python セットアップ" -ForegroundColor Cyan
Write-Host "（システムへのインストール不要）" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path (Join-Path $PortableDir "python.exe")) {
    Write-Host "既にセットアップ済みです。" -ForegroundColor Green
} else {
    Write-Host "[1/4] Python をダウンロード中..." -ForegroundColor Yellow
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $Url -OutFile $ZipFile -UseBasicParsing

    Write-Host "[2/4] 展開中..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path $PortableDir | Out-Null
    Expand-Archive -Path $ZipFile -DestinationPath $PortableDir -Force
    Remove-Item $ZipFile -Force

    Write-Host "[3/4] pip をセットアップ中..." -ForegroundColor Yellow
    $pthFile = Get-ChildItem "$PortableDir\python*._pth" | Select-Object -First 1
    $pthContent = Get-Content $pthFile.FullName
    $pthContent = $pthContent -replace "#import site", "import site"
    if ($pthContent -notcontains ".\Lib\site-packages") {
        $pthContent += ".\Lib\site-packages"
    }
    Set-Content -Path $pthFile.FullName -Value $pthContent -Encoding ASCII
    New-Item -ItemType Directory -Force -Path "$PortableDir\Lib\site-packages" | Out-Null

    $getPip = Join-Path $Root "get-pip.py"
    Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPip -UseBasicParsing
    & "$PortableDir\python.exe" $getPip --no-warn-script-location
    Remove-Item $getPip -Force

    Write-Host "[4/4] Flask をインストール中..." -ForegroundColor Yellow
    & "$PortableDir\python.exe" -m pip install flask --no-warn-script-location -q
}

Write-Host ""
Write-Host "セットアップ完了！" -ForegroundColor Green
Write-Host "次に start_portable.bat をダブルクリックしてください。" -ForegroundColor Green
Write-Host ""
Read-Host "Enter キーで終了"
