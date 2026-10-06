$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath 'frontend/dist/index.html')) {
    throw 'Build the UI first: cd frontend; pnpm run build. See docs/UI_STARTUP.md.'
}
& '.\.venv\Scripts\python.exe' -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
