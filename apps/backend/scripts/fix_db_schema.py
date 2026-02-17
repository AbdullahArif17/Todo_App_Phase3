import sys
import os
import traceback

# Redirect output
sys.stdout = open('fix_result_final.txt', 'w')
sys.stderr = sys.stdout

print("Starting fix_db_schema.py...")

try:
    # 1. Setup paths
    # Assuming script is in <root>/scripts/fix_db_schema.py
    # or <root>/apps/backend/scripts/fix_db_schema.py
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Assuming backend root is one level up
    backend_root = os.path.dirname(script_dir)
    
    # If backend root is not named 'backend' and we are in monorepo, 
    # we might need to adjust. But let's assume specific structure.
    
    sys.path.insert(0, backend_root)
    print(f"Added {backend_root} to python path.")

    # 2. Load environment variables
    # Check current directory first, then fallback
    env_path = os.path.join(backend_root, '.env')
    print(f"Loading .env from: {env_path}")
    
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value
                    if key == "DATABASE_URL":
                        safe = value.split('@')[-1] if '@' in value else "..."
                        print(f"Loaded DATABASE_URL pointing to: ...@{safe}")
    else:
        print(f"WARNING: .env file not found at {env_path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"Files in cwd: {os.listdir(os.getcwd())}")

    # 3. Import engine AFTER loading env vars
    from sqlalchemy import text, inspect
    try:
        from src.database import engine
    except ImportError:
        # Try finding 'backend' namespace if running from root
        sys.path.insert(0, os.path.join(backend_root, 'src'))
        from src.database import engine
    
    print(f"Engine created: {engine}")

    def fix_constraints():
        print("\n--- Starting Constraint Fix (FINAL) ---")
        with engine.connect() as conn:
            # 1. Inspect TodoTask FKs
            print("Inspecting TodoTask FKs...")
            inspector = inspect(conn)
            fks = inspector.get_foreign_keys('todotask')
            print(f"Current FKs on 'todotask': {fks}")

            try:
                for fk in fks:
                    if fk['constrained_columns'] == ['user_id']:
                        fk_name = fk['name']
                        print(f"Dropping constraint: {fk_name}")
                        conn.execute(text(f"ALTER TABLE todotask DROP CONSTRAINT IF EXISTS \"{fk_name}\""))
                
                print("Adding correct FK pointing to 'users'...")
                conn.execute(text("ALTER TABLE todotask ADD CONSTRAINT todotask_users_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)"))
                print("TodoTask FK updated successfully.")
            except Exception as e:
                print(f"Error updating TodoTask FK: {e}")

            # 2. Fix Templates FK
            print("\nFixing Templates FK...")
            try:
                templ_fks = inspector.get_foreign_keys('templates')
                print(f"Current FKs on 'templates': {templ_fks}")
                
                for fk in templ_fks:
                    if fk['constrained_columns'] == ['user_id']:
                         fk_name = fk['name']
                         print(f"Dropping constraint: {fk_name}")
                         conn.execute(text(f"ALTER TABLE templates DROP CONSTRAINT IF EXISTS \"{fk_name}\""))

                print("Adding correct FK pointing to 'users'...")
                conn.execute(text("ALTER TABLE templates ADD CONSTRAINT templates_users_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)"))
                print("Templates FK updated successfully.")
            except Exception as e:
                print(f"Error updating Templates FK: {e}")

            # 3. Clean up 'user' table
            print("\nChecking tables...")
            tables = inspector.get_table_names()
            if 'user' in tables and 'users' in tables:
                print("Both 'user' and 'users' tables exist.")
                count_user = conn.execute(text("SELECT count(*) FROM \"user\"")).scalar()
                count_users = conn.execute(text("SELECT count(*) FROM users")).scalar()
                
                if count_user == 0:
                    print("Dropping empty 'user' table...")
                    conn.execute(text("DROP TABLE IF EXISTS \"user\" RESTRICT"))
                    print("Dropped 'user' table.")
                elif count_users > 0:
                    print("Renaming 'user' to 'user_backup'...")
                    conn.execute(text("ALTER TABLE \"user\" RENAME TO user_backup"))
            
            conn.commit()
            print("\n--- Fix Completed Successfully ---")

    if __name__ == "__main__":
        fix_constraints()

except Exception as e:
    print(f"\nCRITICAL SCRIPT FAILURE: {e}")
    traceback.print_exc()
finally:
    print("Script finished.")
