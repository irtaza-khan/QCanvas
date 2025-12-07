import sys
import os
import argparse
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.database import SessionLocal
from app.models.database_models import (
    User, Project, File, Job, Conversion, ConversionStats, 
    Simulation, Session, ApiActivity
)

# Map table names to models and default columns to show
TABLE_MAP = {
    "users": {
        "model": User,
        "columns": ["id", "username", "email", "role", "is_active", "created_at"]
    },
    "projects": {
        "model": Project,
        "columns": ["id", "name", "user_id", "is_public", "created_at"]
    },
    "files": {
        "model": File,
        "columns": ["id", "project_id", "filename", "is_main", "created_at"]
    },
    "jobs": {
        "model": Job,
        "columns": ["id", "user_id", "status", "backend", "shots", "created_at"]
    },
    "conversions": {
        "model": Conversion,
        "columns": ["id", "user_id", "source_framework", "target_framework", "status", "created_at"]
    },
    "simulations": {
        "model": Simulation,
        "columns": ["id", "user_id", "backend", "shots", "status", "created_at"]
    },
    "sessions": {
        "model": Session,
        "columns": ["id", "user_id", "session_type", "ip_address", "expires_at"]
    },
    "api_activity": {
        "model": ApiActivity,
        "columns": ["id", "user_id", "method", "endpoint", "status_code", "response_time_ms", "created_at"]
    }
}

def print_table(title, headers, rows):
    print(f"\n=== {title} ===")
    if not rows:
        print("No records found.")
        return

    # Convert all values to string
    str_rows = [[str(val) for val in row] for row in rows]
    
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in str_rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(val))
    
    # Create format string
    fmt = " | ".join([f"{{:<{w}}}" for w in widths])
    
    # Print header
    separator = "-" * (sum(widths) + 3 * (len(widths) - 1))
    print(separator)
    print(fmt.format(*headers))
    print(separator)
    
    # Print rows
    for row in str_rows:
        print(fmt.format(*row))
    print(separator)

def get_column_value(obj, col_name):
    val = getattr(obj, col_name)
    if hasattr(val, 'strftime'):
        return val.strftime("%Y-%m-%d %H:%M:%S")
    return val

def show_data(table_name=None, limit=15):
    db = SessionLocal()
    try:
        if table_name:
            if table_name not in TABLE_MAP:
                print(f"Error: Table '{table_name}' not found. Available tables: {', '.join(TABLE_MAP.keys())}")
                return
            
            config = TABLE_MAP[table_name]
            model = config["model"]
            columns = config["columns"]
            
            # Query
            query = db.query(model).order_by(model.created_at.desc())
            items = query.limit(limit).all()
            
            # Prepare rows
            rows = [[get_column_value(item, col) for col in columns] for item in items]
            print_table(f"Latest {limit} {table_name}", columns, rows)
            
        else:
            # Show summary of all tables
            print("Usage: python show_db_data.py [table_name] [--limit N]")
            print("Available tables:", ", ".join(TABLE_MAP.keys()))
            print("\n--- Summary ---")
            for name, config in TABLE_MAP.items():
                count = db.query(config["model"]).count()
                print(f"{name}: {count} records")

    except Exception as e:
        print(f"Error fetching data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect database tables")
    parser.add_argument("table", nargs="?", help="Name of the table to inspect")
    parser.add_argument("--limit", type=int, default=15, help="Number of records to show")
    
    args = parser.parse_args()
    show_data(args.table, args.limit)
