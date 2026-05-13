Set-Location $PSScriptRoot\..
$env:COZE_WORKSPACE_PATH = (Resolve-Path .).Path
$env:PYTHONPATH = Join-Path (Resolve-Path .).Path "src"
if (Test-Path .\.env) {
  Get-Content .\.env | ForEach-Object {
    if ($_ -match '^\s*([^#][^=]*)=(.*)$') {
      Set-Item -Path "Env:$($matches[1].Trim())" -Value $matches[2].Trim()
    }
  }
}
.\.venv\Scripts\python.exe src\main.py -m bp --json-file payload_bp_simple.json
