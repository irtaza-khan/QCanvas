import os
import re
from datetime import datetime


def parse_year_month_from_filename(filename: str):
    """Extract (year, month_abbr) from known log filename patterns.

    Supported examples:
    - run_2025-10-03_19-31-52.log
    - convert_qiskit_2025-10-07_18-31-25_10.log
    - convert_cirq_2025-10-03_19-32-01_01.log
    - convert_pennylane_2025-10-07_18-25-17_01.log
    """
    m = re.search(r"_(\d{4})-(\d{2})-(\d{2})_", filename)
    if not m:
        return None
    year = m.group(1)
    month_num = int(m.group(2))
    month_abbr = datetime(1900, month_num, 1).strftime("%b")
    return year, month_abbr


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def migrate_logs(log_root: str):
    """Move logs from logs/ flat root into logs/YYYY/Mon/ based on filename date.

    Only moves files that match the expected patterns and are currently in log_root.
    """
    entries = [e for e in os.listdir(log_root) if os.path.isfile(os.path.join(log_root, e))]
    moved = 0
    skipped = 0
    for name in entries:
        parsed = parse_year_month_from_filename(name)
        if not parsed:
            skipped += 1
            continue
        year, month_abbr = parsed
        dest_dir = os.path.join(log_root, year, month_abbr)
        ensure_dir(dest_dir)
        src = os.path.join(log_root, name)
        dst = os.path.join(dest_dir, name)
        # If already in place, skip
        if os.path.abspath(src) == os.path.abspath(dst):
            continue
        # If destination exists, prefer keeping the existing to avoid overwrite
        if os.path.exists(dst):
            skipped += 1
            continue
        os.replace(src, dst)
        moved += 1
    return moved, skipped


if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    log_root = os.path.join(project_root, "logs")
    ensure_dir(log_root)
    moved, skipped = migrate_logs(log_root)
    print(f"Log migration complete. Moved={moved}, Skipped={skipped}")

#!/usr/bin/env python3
# TODO: Implement script
