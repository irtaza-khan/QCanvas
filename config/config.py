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

# Global builder prelude flags (used by all converters)
# Controls whether classical variables and mathematical constants are emitted
# in the standard prelude. Adjust here to affect all conversion outputs.
INCLUDE_VARS: bool = True
INCLUDE_CONSTANTS: bool = True

import os
import sys
from datetime import datetime
from typing import Any

# Ensure logs directory and a per-run log file exist
_PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
LOG_ROOT_DIR = os.path.join(_PROJECT_ROOT, "logs")
os.makedirs(LOG_ROOT_DIR, exist_ok=True)

def _month_dir_for(dt: datetime) -> str:
    """Return directory path logs/YYYY/Mon for the given datetime, creating it if needed."""
    year = dt.strftime("%Y")
    month_abbr = dt.strftime("%b")  # Jan, Feb, ...
    month_dir = os.path.join(LOG_ROOT_DIR, year, month_abbr)
    os.makedirs(month_dir, exist_ok=True)
    return month_dir

_RUN_DT = datetime.now()
_RUN_TIMESTAMP = _RUN_DT.strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = os.path.join(_month_dir_for(_RUN_DT), f"run_{_RUN_TIMESTAMP}.log")
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
    now = datetime.now()
    ts = now.strftime("%Y-%m-%d_%H-%M-%S")
    safe = "".join(ch for ch in name if ch.isalnum() or ch in ("-", "_")) or "run"
    LOG_FILE = os.path.join(_month_dir_for(now), f"{safe}_{ts}_{_SESSION_COUNTER:02d}.log")
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


