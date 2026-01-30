
import os
import sys

# Add backend directory to path so imports work
# current file is in QCanvas/backend/reset_db.py
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, backend_dir)
sys.path.insert(0, project_root)

from app.config.database import engine, Base
# Import all models to ensure they are registered with Base.metadata
from app.models import database_models 
from alembic.config import Config
from alembic import command

def reset_database():
    try:
        # Drop all tables
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables
        print("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        
        # Stamp alembic head
        print("Stamping alembic head...")
        alembic_ini_path = os.path.join(project_root, "alembic.ini")
        alembic_cfg = Config(alembic_ini_path)
        
        # Ensure script_location is correct
        # The config should handle it, but we can verify or set it if needed.
        # We shouldn't need to change CWD if we pass the absolute path to ini.
        
        command.stamp(alembic_cfg, "head")
        print("Database reset successfully.")
        
        # Recreate demo account
        import create_demo_account
        print("\nRecreating demo account...")
        create_demo_account.main()
        
    except Exception as e:
        print(f"Error resetting database: {e}")
        print("Please ensure the database server is running.")


if __name__ == "__main__":
    reset_database()
