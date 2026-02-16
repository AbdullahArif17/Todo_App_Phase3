import sys
import os
import traceback

# Redirect stdout to a file to capture output reliably
sys.stdout = open('fix_result.txt', 'w')
sys.stderr = sys.stdout

print("Starting fix_fk_constraints_v2.py...")

try:
    # Add path to find src
    current_dir = os.getcwd()
    sys.path.append(os.path.join(current_dir, 'apps', 'backend'))
    print(f"Added {sys.path[-1]} to python path.")

    from sqlalchemy import text, inspect
    from src.database import engine
    print(f"Imported Engine: {engine}")

    def fix_constraints():
        print("\n--- Starting Constraint Fix ---")
        with engine.connect() as conn:
            # 1. Identify FKs on TodoTask
            print("Inspecting TodoTask FKs...")
            inspector = inspect(conn)
            fks = inspector.get_foreign_keys('todotask')
            print(f"Current FKs on 'todotask': {fks}")

            # 2. Fix TodoTask FK
            print("\nFixing TodoTask FK...")
            try:
                # Drop all existing FKs on user_id to be safe
                for fk in fks:
                    if fk['constrained_columns'] == ['user_id']:
                        fk_name = fk['name']
                        print(f"Dropping constraint: {fk_name}")
                        conn.execute(text(f"ALTER TABLE todotask DROP CONSTRAINT IF EXISTS \"{fk_name}\""))
                
                # Add correct FK pointing to 'users'
                print("Adding correct FK pointing to 'users'...")
                conn.execute(text("ALTER TABLE todotask ADD CONSTRAINT todotask_users_id_fkey FOREIGN KEY (user_id) REFERENCES users(id)"))
                print("TodoTask FK updated successfully.")
            except Exception as e:
                print(f"Error updating TodoTask FK: {e}")
                traceback.print_exc()

            # 3. Fix Templates FK
            print("\nFixing Templates FK...")
            try:
                # Inspect first
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
                traceback.print_exc()

            # 4. Check on 'user' vs 'users' tables
            print("\nChecking tables...")
            tables = inspector.get_table_names()
            if 'user' in tables and 'users' in tables:
                print("Both 'user' and 'users' tables exist. 'user' is likely duplicative/stale.")
                
                # Check if 'user' is empty
                count = conn.execute(text("SELECT count(*) FROM \"user\"")).scalar()
                print(f"Rows in 'user' table: {count}")
                
                if count == 0:
                    print("Dropping empty 'user' table...")
                    conn.execute(text("DROP TABLE IF EXISTS \"user\" RESTRICT"))
                    print("Dropped 'user' table.")
                else:
                    print("Table 'user' is NOT empty. Renaming to 'user_backup' to avoid confusion.")
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
