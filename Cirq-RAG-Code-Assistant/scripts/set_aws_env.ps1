# Optional: Set AWS credentials for Cirq-RAG-Code-Assistant (Windows PowerShell).
# Option A (recommended): Use a .env file - the app loads it automatically.
# Option B: Set variables in this session only.

param(
    [switch]$CreateEnv   # If set, copy .env.example to .env in project root (if .env does not exist)
)

$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$envExample = Join-Path $projectRoot ".env.example"
$envFile = Join-Path $projectRoot ".env"

if ($CreateEnv -and -not (Test-Path $envFile) -and (Test-Path $envExample)) {
    Copy-Item $envExample $envFile
    Write-Host "Created .env from .env.example. Edit .env in the project root and add your AWS credentials."
    Write-Host "  $envFile"
} elseif ($CreateEnv -and (Test-Path $envFile)) {
    Write-Host ".env already exists: $envFile"
} elseif ($CreateEnv) {
    Write-Host ".env.example not found at $envExample"
}

Write-Host ""
Write-Host "On Windows, the app reads .env from the project root (no 'set' needed in the file)."
Write-Host "To set credentials in this session only (PowerShell), run:"
Write-Host '  $env:AWS_ACCESS_KEY_ID = "your_access_key_id_here"'
Write-Host '  $env:AWS_SECRET_ACCESS_KEY = "your_secret_access_key_here"'
Write-Host '  $env:AWS_DEFAULT_REGION = "us-east-1"'
Write-Host ""
Write-Host "Recommended: copy .env.example to .env, edit .env with your keys, then run the app."
