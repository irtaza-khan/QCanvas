"""
Global configuration for QCanvas.

Centralizes runtime flags and tunables to avoid scattering constants
throughout the codebase. Import from this module rather than redefining
per-file settings.

Also provides a simple logging facility that writes all verbose
messages to per-run log files under the `logs/` directory regardless of
the VERBOSE console flag.
"""

# Verbose logging for parsers/converters (set to False to silence)
VERBOSE: bool = True

import os
import sys
from datetime import datetime
from typing import Any

# Ensure logs directory and a per-run log file exist
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
LOG_DIR = os.path.join(_PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

_RUN_TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = os.path.join(LOG_DIR, f"run_{_RUN_TIMESTAMP}.log")
_SESSION_COUNTER = 0

# Emit a header for this run
def _emit_log_header() -> None:
    header_lines = [
        "=" * 80,
        "QCanvas Run Log",
        f"Start Time: {datetime.now().isoformat(timespec='seconds')}",
        f"Process: pid={os.getpid()} python={sys.version.split()[0]}",
        f"Working Dir: {os.getcwd()}",
        f"Verbose Console: {VERBOSE}",
        "=" * 80,
        "",
    ]
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n".join(header_lines))

if not os.path.exists(LOG_FILE):
    _emit_log_header()


def new_log_session(name: str = "run") -> str:
    """Rotate to a new per-session log file with a friendly name.

    Example: new_log_session("convert_qiskit") → logs/convert_qiskit_2025-10-03_19-30-12_01.log
    Returns the path to the new log file.
    """
    global LOG_FILE, _SESSION_COUNTER
    _SESSION_COUNTER += 1
    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    safe = "".join(ch for ch in name if ch.isalnum() or ch in ("-", "_")) or "run"
    LOG_FILE = os.path.join(LOG_DIR, f"{safe}_{ts}_{_SESSION_COUNTER:02d}.log")
    _emit_log_header()
    return LOG_FILE


def _write_log_line(message: str) -> None:
    """Append a single line to the current run log file."""
    try:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception:
        # Never break the app due to logging
        pass


def vprint(*args: Any, **kwargs: Any) -> None:
    """Verbose print routed to console (when VERBOSE) and always to log file.

    Usage:
        from config.config import vprint
        vprint("message", var=val)
    """
    # Build a single string like print would
    sep = kwargs.get("sep", " ")
    end = kwargs.get("end", "\n")
    msg = sep.join(str(a) for a in args)

    # Console output controlled by VERBOSE
    if VERBOSE:
        # Use built-in print with the original kwargs
        print(msg, end=end)

    # Always write to log file without the trailing end
    _write_log_line(msg)

# Placeholder for future configuration keys, e.g.:
# ENABLE_CONTROL_FLOW_SNIPPETS: bool = False
# INCLUDE_CONSTANTS_IN_PREAMBLE: bool = False


