import sys
import os
from sqlalchemy import text
from src.database import engine

# Add path
sys.path.append(os.path.join(os.getcwd(), 'apps', 'backend'))

def fix_constraints():
    print("Starting constraint fix...")
    with engine.connect() as conn:
        # Fix TodoTask FK
        print("Fixing TodoTask FK...")
        try:
            conn.execute(text("ALTER TABLE todotask DROP CONSTRAINT IF EXISTS todotask_user_id_fkey"))
            conn.execute(text("ALTER TABLE todotask ADD CONSTRAINT todotask_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)"))
            print("TodoTask FK updated to point to 'users'.")
        except Exception as e:
            print(f"Error updating TodoTask FK: {e}")

        # Fix Templates FK if it exists
        print("Fixing Templates FK...")
        try:
            conn.execute(text("ALTER TABLE templates DROP CONSTRAINT IF EXISTS templates_user_id_fkey"))
            conn.execute(text("ALTER TABLE templates ADD CONSTRAINT templates_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)"))
            print("Templates FK updated to point to 'users'.")
        except Exception as e:
            # Maybe templates table doesn't catch existing constraint name
            print(f"Note on Templates: {e}")

        # Clean up old 'user' table if it exists and is empty/unused
        print("Checking old 'user' table...")
        try:
             # Check if we can drop it safely
             conn.execute(text("DROP TABLE IF EXISTS \"user\" RESTRICT")) 
             # RESTRICT ensures we don't drop it if other things still depend on it
             print("Dropped old 'user' table (if it existed and had no dependencies).")
        except Exception as e:
             print(f"Could not drop 'user' table (likely still has dependencies): {e}")
        
        conn.commit()
        print("Constraint fix completed!")

if __name__ == "__main__":
    try:
        fix_constraints()
    except Exception as e:
        print(f"Script failed: {e}")
