import sys
import os
from sqlalchemy import text, inspect

# Add path to find src
sys.path.append(os.path.join(os.getcwd(), 'apps', 'backend'))

from src.database import engine

def fix_schema():
    print("Starting schema fix...")
    with engine.connect() as conn:
        inspector = inspect(conn)
        tables = inspector.get_table_names()
        print(f"Existing tables: {tables}")
        
        has_user = 'user' in tables
        has_users = 'users' in tables
        
        if not has_user and not has_users:
            print("Neither 'user' nor 'users' table found. Start the app to create tables first.")
            return

        print("Step 1: Safely dropping existing FK constraint on conversations (if exists)...")
        # We use a try-except block or check if it exists, but DROP IF EXISTS is cleaner in Postgres
        try:
            conn.execute(text("ALTER TABLE conversations DROP CONSTRAINT IF EXISTS conversations_user_id_fkey"))
        except Exception as e:
            print(f"Note: Error trying to drop constraint (might not exist): {e}")

        # Now conversations is decoupled.
        
        if has_user:
            print("Found table 'user' (singular).")
            if has_users:
                print("Found table 'users' (plural) as well.")
                
                # Check if users is empty
                count = conn.execute(text("SELECT count(*) FROM users")).scalar()
                print(f"Table 'users' has {count} rows.")
                
                if count == 0:
                    print("Dropping empty 'users' table...")
                    conn.execute(text("DROP TABLE users"))
                    print("Renaming 'user' to 'users'...")
                    conn.execute(text("ALTER TABLE \"user\" RENAME TO users"))
                else:
                    print("Table 'users' is NOT empty. Renaming it to 'users_backup' to be safe.")
                    conn.execute(text("ALTER TABLE users RENAME TO users_backup"))
                    print("Renaming 'user' to 'users'...")
                    conn.execute(text("ALTER TABLE \"user\" RENAME TO users"))
            else:
                 # Only 'user' exists. Rename it.
                 print("Renaming 'user' to 'users'...")
                 conn.execute(text("ALTER TABLE \"user\" RENAME TO users"))
        
        elif has_users:
             print("Only 'users' table found. Assuming it is the correct one.")

        print("Step 2: Re-adding FK constraint 'conversations_user_id_fkey' to 'users' table...")
        # Validate that 'users' table exists now
        inspector = inspect(conn)
        if 'users' not in inspector.get_table_names():
             print("CRITICAL: 'users' table missing after operations. Aborting FK creation.")
             return

        conn.execute(text("ALTER TABLE conversations ADD CONSTRAINT conversations_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)"))
        
        conn.commit()
        print("Schema fix completed successfully!")

if __name__ == "__main__":
    try:
        fix_schema()
    except Exception as e:
        print(f"Error executing schema fix: {e}")
        import traceback
        traceback.print_exc()
