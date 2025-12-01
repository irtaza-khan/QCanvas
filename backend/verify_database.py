"""
Verify users table exists in the database.
"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, backend_dir)

from sqlalchemy import inspect, text
from app.config.database import engine
from app.config.settings import settings

def verify_users_table():
    """Check if users table exists and show its structure."""
    print("=" * 60)
    print("QCanvas Database Verification")
    print("=" * 60)
    print(f"\nConnecting to: {settings.DATABASE_URL}")
    print()
    
    try:
        # Get database inspector
        inspector = inspect(engine)
        
        # Check if users table exists
        tables = inspector.get_table_names()
        print(f"✅ Found {len(tables)} table(s) in database:")
        for table in tables:
            print(f"   - {table}")
        
        if 'users' in tables:
            print("\n✅ Users table EXISTS!")
            
            # Get column information
            print("\n📋 Users table structure:")
            print("-" * 60)
            columns = inspector.get_columns('users')
            for col in columns:
                null_str = "NULL" if col['nullable'] else "NOT NULL"
                print(f"  {col['name']:<20} {str(col['type']):<20} {null_str}")
            
            # Get indexes
            print("\n🔍 Indexes:")
            print("-" * 60)
            indexes = inspector.get_indexes('users')
            for idx in indexes:
                unique_str = "UNIQUE" if idx['unique'] else ""
                cols = ", ".join(idx['column_names'])
                print(f"  {idx['name']:<30} ({cols}) {unique_str}")
            
            # Count rows
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                print(f"\n📊 Total users in database: {count}")
            
            print("\n" + "=" * 60)
            print("✅ Database verification PASSED!")
            print("=" * 60)
            
        else:
            print("\n❌ Users table NOT FOUND!")
            print("   Run: python -m alembic upgrade head")
            
    except Exception as e:
        print(f"\n❌ Error connecting to database:")
        print(f"   {str(e)}")
        print("\n   Make sure:")
        print("   1. Docker Postgres is running (docker-compose ps)")
        print("   2. Database credentials are correct")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(verify_users_table())
