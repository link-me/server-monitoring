$ErrorActionPreference = 'Stop'

if (-not (Test-Path '.venv')) {
  python -m venv .venv
}
.\.venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt

$port = 8015
Write-Host "Starting server-monitoring on port $port" -ForegroundColor Cyan
uvicorn src.app:app --host 127.0.0.1 --port $port --reload