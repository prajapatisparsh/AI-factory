# Start the AI Factory API server (FastAPI + uvicorn)
# PowerShell - run from repo root: .\start_api.ps1

Set-Location $PSScriptRoot

Write-Host ""
Write-Host "Starting AI Factory API on http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend expects it at http://localhost:8000" -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop." -ForegroundColor Gray
Write-Host ""

poetry run uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload
