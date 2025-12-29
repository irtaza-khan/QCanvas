<#
.SYNOPSIS
    Windows compatible setup and run script for QCanvas.
    Equivalent to setup.sh and run.sh combined.

.DESCRIPTION
    This script handles the installation of dependencies and the starting/stopping
    of the frontend and backend services for QCanvas on Windows.

.USAGE
    .\win_runner.ps1 install   - Installs Python and Node.js dependencies
    .\win_runner.ps1 start     - Starts the backend and frontend services
    .\win_runner.ps1 stop      - Stops the services
#>

param (
    [Parameter(Mandatory=$false)]
    [ValidateSet("install", "start", "stop", "restart")]
    [string]$Action
)

# Configuration
$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot
$VenvDir = Join-Path $ScriptDir "venv"
$FrontendDir = Join-Path $ScriptDir "frontend"
$BackendDir = Join-Path $ScriptDir "backend"
$LogsDir = Join-Path $ScriptDir "logs"
$FrontendPidFile = Join-Path $ScriptDir "frontend.pid"
$BackendPidFile = Join-Path $ScriptDir "backend.pid"

# Helper to check commands
function Test-CommandType ($Command) {
    return (Get-Command $Command -ErrorAction SilentlyContinue)
}

function Install-Services {
    Write-Host "Wrapper: Starting installation..." -ForegroundColor Cyan

    # 1. Python Virtual Environment
    if (-not (Test-Path $VenvDir)) {
        Write-Host "Creating Python virtual environment (venv)..."
        try {
            python -m venv $VenvDir
        } catch {
            Write-Error "Failed to create venv. Ensure 'python' is in your PATH."
        }
    } else {
        Write-Host "venv already exists." -ForegroundColor Gray
    }

    $PipExe = Join-Path $VenvDir "Scripts\pip.exe"

    if (-not (Test-Path $PipExe)) {
        Write-Error "pip.exe not found in venv. setup failed."
    }

    # 2. Upgrade pip
    Write-Host "Upgrading pip..."
    & $PipExe install --upgrade pip

    # 3. Install Requirements
    $ReqFile = Join-Path $ScriptDir "requirements.txt"
    if (Test-Path $ReqFile) {
        Write-Host "Installing Python requirements..."
        & $PipExe install -r $ReqFile
    } else {
        Write-Warning "requirements.txt not found. Skipping python deps."
    }

    # 4. Frontend Install
    if (Test-Path $FrontendDir) {
        Write-Host "Installing frontend dependencies..."
        Push-Location $FrontendDir
        try {
            cmd /c "npm install"
            if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
        } finally {
            Pop-Location
        }
    } else {
        Write-Warning "Frontend directory not found!"
    }

    Write-Host "Installation complete." -ForegroundColor Green
}

function Start-Services {
    Write-Host "Wrapper: Starting services..." -ForegroundColor Cyan

    # Check existing PIDs
    if ((Test-Path $FrontendPidFile) -or (Test-Path $BackendPidFile)) {
        Write-Error "Services appear to be running (PID files exist). Run '.\win_runner.ps1 stop' first."
    }

    # Ensure logs dir
    if (-not (Test-Path $LogsDir)) { New-Item -ItemType Directory -Path $LogsDir | Out-Null }

    # 1. Frontend
    if (Test-Path $FrontendDir) {
        Write-Host "Building frontend..."
        Push-Location $FrontendDir
        try {
            cmd /c "npm run build"
            if ($LASTEXITCODE -ne 0) { throw "npm build failed" }
            
            Write-Host "Starting frontend (background)..."
            $FrontLog = Join-Path $LogsDir "frontend.log"
            
            # Start npm as background process
            $Args = "/c npm run start > `"$FrontLog`" 2>&1"
            $P = Start-Process -FilePath "cmd.exe" -ArgumentList $Args -PassThru -WindowStyle Hidden
            $P.Id | Out-File $FrontendPidFile -Encoding ascii
        } finally {
            Pop-Location
        }
    } else {
        Write-Error "Frontend directory not found."
    }

    # 2. Backend
    if (Test-Path $BackendDir) {
        Write-Host "Starting backend (background)..."
        $PythonExe = Join-Path $VenvDir "Scripts\python.exe"
        if (-not (Test-Path $PythonExe)) {
            Write-Error "Virtual environment python not found at $PythonExe. Run 'install' first."
        }

        $BackLog = Join-Path $LogsDir "backend.log"
        $BackErr = Join-Path $LogsDir "backend.err.log"
        
        # uvicorn command
        # Mirrors: python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        $ArgsList = "-m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
        
        $P = Start-Process -FilePath $PythonExe -ArgumentList $ArgsList -WorkingDirectory $BackendDir -PassThru -RedirectStandardOutput $BackLog -RedirectStandardError $BackErr -WindowStyle Hidden
        $P.Id | Out-File $BackendPidFile -Encoding ascii
    }

    Write-Host "Services started." -ForegroundColor Green
    Write-Host "Logs: logs\frontend.log, logs\backend.log"
}

function Stop-Services {
    Write-Host "Stopping services..." -ForegroundColor Yellow
    
    # Kill Frontend via PID
    if (Test-Path $FrontendPidFile) {
        $Id = Get-Content $FrontendPidFile
        Write-Host "Killing Frontend PID: $Id"
        Stop-Process -Id $Id -ErrorAction SilentlyContinue
        Remove-Item $FrontendPidFile -ErrorAction SilentlyContinue
    }
    # Backup kill node
    Stop-Process -Name "node" -ErrorAction SilentlyContinue

    # Kill Backend via PID
    if (Test-Path $BackendPidFile) {
        $Id = Get-Content $BackendPidFile
        Write-Host "Killing Backend PID: $Id"
        Stop-Process -Id $Id -ErrorAction SilentlyContinue
        Remove-Item $BackendPidFile -ErrorAction SilentlyContinue
    }
    # Backup kill uvicorn/python
    # Using WMI to find uvicorn specifically to avoid killing other python scripts
    Get-CimInstance Win32_Process | Where-Object { $_.Name -eq "python.exe" -and $_.CommandLine -like "*uvicorn*" } | ForEach-Object { 
        Write-Host "Killing uvicorn process: $($_.ProcessId)"
        Stop-Process -Id $_.ProcessId -ErrorAction SilentlyContinue 
    }

    Write-Host "All services stopped." -ForegroundColor Green
}

# Main entry
if ([string]::IsNullOrWhiteSpace($Action)) {
    Write-Host "Usage: .\win_runner.ps1 {install|start|stop|restart}"
    exit 1
}

switch ($Action) {
    "install" { Install-Services }
    "start"   { Start-Services }
    "stop"    { Stop-Services }
    "restart" { Stop-Services; Start-Services }
    Default   { Write-Host "Invalid action. Usage: .\win_runner.ps1 {install|start|stop|restart}" }
}
