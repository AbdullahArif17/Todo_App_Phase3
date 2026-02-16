import sys
import os
from sqlalchemy import text, inspect

# Add path
sys.path.append(os.path.join(os.getcwd(), 'apps', 'backend'))

from src.database import engine

def inspect_db():
    print("Starting Deep Inspection...")
    with engine.connect() as conn:
        inspector = inspect(conn)
        tables = inspector.get_table_names()
        print(f"Tables found: {tables}")
        
        has_user = 'user' in tables
        has_users = 'users' in tables
        
        print(f"Has 'user' table: {has_user}")
        print(f"Has 'users' table: {has_users}")
        
        if has_user:
             count = conn.execute(text("SELECT count(*) FROM \"user\"")).scalar()
             print(f"Rows in 'user': {count}")
        if has_users:
             count = conn.execute(text("SELECT count(*) FROM users")).scalar()
             print(f"Rows in 'users': {count}")

        # Check FKs
        for table_name in ['conversations', 'todotask', 'templates']:
            if table_name in tables:
                print(f"\nForeign Keys for '{table_name}':")
                fks = inspector.get_foreign_keys(table_name)
                for fk in fks:
                    print(f"  - Constraint: {fk['name']}")
                    print(f"    Points to table: {fk['referred_table']}")
                    print(f"    Columns: {fk['constrained_columns']} -> {fk['referred_columns']}")

if __name__ == "__main__":
    try:
        inspect_db()
    except Exception as e:
        print(f"Error: {e}")
