#!/usr/bin/env bash
# setup_and_run.sh
# Single script to install dependencies, build frontend, and run frontend + backend on Ubuntu.
# Defaults can be overridden with environment variables before calling the script.
# Example:
#   FRONTEND_BUILD_CMD="npm run build" FRONTEND_START_CMD="npm run start" ./setup_and_run.sh

set -euo pipefail

# -------------------------
# Configurable variables
# -------------------------
FRONTEND_DIR="${FRONTEND_DIR:-frontend}"
VENV_DIR="${VENV_DIR:-venv}"
REQUIREMENTS_FILE="${REQUIREMENTS_FILE:-requirements.txt}"

# Default frontend commands (override by exporting FRONTEND_BUILD_CMD / FRONTEND_START_CMD)
FRONTEND_BUILD_CMD="${FRONTEND_BUILD_CMD:-npm run build}"
FRONTEND_START_CMD="${FRONTEND_START_CMD:-npm run start}"

# Backend / uvicorn
BACKEND_MODULE="${BACKEND_MODULE:-app.main:app}"
BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"
BACKEND_PORT="${BACKEND_PORT:-8000}"

# Logs
LOG_DIR="${LOG_DIR:-logs}"
FRONTEND_LOG="$LOG_DIR/frontend.log"
BACKEND_LOG="$LOG_DIR/backend.log"

# Tools to apt-install
APT_PACKAGES=(nodejs npm python3-venv python3-full build-essential)

# -------------------------
# Helper utilities
# -------------------------
info()  { echo -e "\033[1;34m[INFO]\033[0m $*"; }
warn()  { echo -e "\033[1;33m[WARN]\033[0m $*"; }
fatal() { echo -e "\033[1;31m[FATAL]\033[0m $*"; exit 1; }

ROOT_DIR="$(pwd)"
SUDO=""
if [ "$(id -u)" -ne 0 ]; then
  SUDO="sudo"
fi

# -------------------------
# 1) apt update & install
# -------------------------
info "Updating apt and installing required packages (nodejs, npm, python3-venv, ...)."
$SUDO apt update -y
$SUDO apt install -y "${APT_PACKAGES[@]}"

# Verify python3 exists
if ! command -v python3 >/dev/null 2>&1; then
  fatal "python3 not found after install. Aborting."
fi

# -------------------------
# 2) Create & activate venv
# -------------------------
if [ ! -d "$VENV_DIR" ]; then
  info "Creating Python venv at ./$VENV_DIR"
  python3 -m venv "$VENV_DIR"
else
  info "Virtualenv $VENV_DIR already exists — reusing."
fi

# Activate venv for subsequent pip installs and runtime
# Use absolute path to the venv python for reliability
VENV_PY="$ROOT_DIR/$VENV_DIR/bin/python"
VENV_PIP="$ROOT_DIR/$VENV_DIR/bin/pip"

if [ ! -x "$VENV_PY" ]; then
  fatal "Cannot find python in venv ($VENV_PY). Did venv creation fail?"
fi

info "Upgrading pip inside venv..."
"$VENV_PIP" install --upgrade pip

# -------------------------
# 3) Install Python requirements
# -------------------------
if [ -f "$REQUIREMENTS_FILE" ]; then
  info "Installing Python requirements from $REQUIREMENTS_FILE..."
  "$VENV_PIP" install -r "$REQUIREMENTS_FILE"
else
  warn "Requirements file '$REQUIREMENTS_FILE' not found — skipping pip install."
fi

# -------------------------
# 4) Frontend: npm install
# -------------------------
if [ -d "$FRONTEND_DIR" ]; then
  info "Running npm install in $FRONTEND_DIR..."
  pushd "$FRONTEND_DIR" >/dev/null
  # Ensure npm exists
  if ! command -v npm >/dev/null 2>&1; then
    fatal "npm not found in PATH after apt install. Aborting."
  fi
  npm install
  popd >/dev/null
else
  warn "Frontend directory '$FRONTEND_DIR' not found. Skipping npm install/build/start."
fi

# -------------------------
# 5) Build frontend (if requested)
# -------------------------
if [ -d "$FRONTEND_DIR" ]; then
  info "Running frontend build: '$FRONTEND_BUILD_CMD' (in $FRONTEND_DIR)"
  pushd "$FRONTEND_DIR" >/dev/null
  # run build command as given (it may be 'npm run build' or something else)
  # split command safely:
  eval "$FRONTEND_BUILD_CMD"
  popd >/dev/null
fi

# -------------------------
# 6) Prepare logs & start services
# -------------------------
mkdir -p "$LOG_DIR"

# Start frontend (if directory exists)
FRONTEND_PID=""
if [ -d "$FRONTEND_DIR" ]; then
  info "Starting frontend with: (cd $FRONTEND_DIR && $FRONTEND_START_CMD)"
  pushd "$FRONTEND_DIR" >/dev/null
  # Use setsid to detach / nohup so processes survive after script exits (if desired)
  # Output is redirected to log file
  setsid bash -c "$FRONTEND_START_CMD" > "$ROOT_DIR/$FRONTEND_LOG" 2>&1 &
  FRONTEND_PID=$!
  popd >/dev/null
  info "Frontend started (PID: $FRONTEND_PID). Log: $FRONTEND_LOG"
else
  warn "Frontend not started (directory missing)."
fi

# Start backend with venv python & uvicorn
info "Starting backend uvicorn: python -m uvicorn $BACKEND_MODULE --reload --host $BACKEND_HOST --port $BACKEND_PORT"
setsid "$VENV_PY" -m uvicorn "$BACKEND_MODULE" --reload --host "$BACKEND_HOST" --port "$BACKEND_PORT" > "$BACKEND_LOG" 2>&1 &
BACKEND_PID=$!
info "Backend started (PID: $BACKEND_PID). Log: $BACKEND_LOG"

# Pause briefly to allow processes to initialize
sleep 1

# Show status and tails (optional)
echo
info "Summary:"
[ -n "$FRONTEND_PID" ] && echo "  Frontend PID: $FRONTEND_PID (log -> $FRONTEND_LOG)" || echo "  Frontend: not running"
echo "  Backend PID : $BACKEND_PID (log -> $BACKEND_LOG)"
echo
info "To view logs live:"
echo "  tail -f $FRONTEND_LOG $BACKEND_LOG"
echo
info "If you want to stop the processes after this script ran, use:"
[ -n "$FRONTEND_PID" ] && echo "  kill $FRONTEND_PID"
echo "  kill $BACKEND_PID"
echo
info "If you want this script to keep streaming logs until you Ctrl+C, re-run with:"
echo "  ./setup_and_run.sh --tail"
echo
# Optional: support --tail argument to block and stream logs
if [ "${1:-}" = "--tail" ] || [ "${2:-}" = "--tail" ]; then
  info "Tailing logs (press Ctrl+C to exit):"
  tail -f "$FRONTEND_LOG" "$BACKEND_LOG"
fi

info "Done."
