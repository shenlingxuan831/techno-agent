# Recreate .venv with Python 3.12 (MinerU requires Python <3.14)
# Usage: powershell -ExecutionPolicy Bypass -File scripts/recreate_venv_py312.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path $PSScriptRoot -Parent
Set-Location $RepoRoot

$Py312 = $env:KT_PYTHON
if (-not $Py312) {
    $candidates = @(
        "E:\Python312\python.exe",
        "C:\Python312\python.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { $Py312 = $c; break }
    }
}
if (-not $Py312 -or -not (Test-Path $Py312)) {
    Write-Error "Python 3.12 not found. Install 3.12 or set KT_PYTHON to python.exe path."
}

$ver = & $Py312 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if ($ver -ne "3.12" -and $ver -ne "3.13") {
    Write-Error "KT_PYTHON must be 3.12 or 3.13 (MinerU needs <3.14). Got: $ver"
}

Write-Host "==> Using Python: $Py312 ($(& $Py312 --version))"

$OldVenv = Join-Path $RepoRoot ".venv"
$Backup = Join-Path $RepoRoot ".venv_py314_backup"
if (Test-Path $OldVenv) {
    if (Test-Path $Backup) { Remove-Item -Recurse -Force $Backup }
    Write-Host "==> Backup old venv to .venv_py314_backup"
    Rename-Item $OldVenv $Backup
}

Write-Host "==> Create new .venv"
& $Py312 -m venv $OldVenv

$Py = Join-Path $OldVenv "Scripts\python.exe"
$PipIndex = "https://mirrors.aliyun.com/pypi/simple/"

Write-Host "==> Upgrade pip"
& $Py -m pip install -U pip -i $PipIndex

Write-Host "==> Install project dependencies (may take several minutes)"
& $Py -m pip install -e . -i $PipIndex

Write-Host ""
Write-Host "Done. New venv Python version:"
& $Py --version
Write-Host ""
Write-Host "Next: powershell -ExecutionPolicy Bypass -File scripts\install_extract_deps.ps1"
