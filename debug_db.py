import sys
import os

print("Starting debug_db.py...")

try:
    current_dir = os.getcwd()
    sys.path.append(os.path.join(current_dir, 'apps', 'backend'))
    print(f"Added {sys.path[-1]} to python path.")

    from sqlalchemy import inspect, text
    print("Imported SQLAlchemy.")

    from src.database import engine
    print(f"Imported Engine: {engine}")

    def check_db():
        print("Connecting to DB...")
        with engine.connect() as conn:
            print("Connected.")
            inspector = inspect(conn) # Inspect existing connection
            
            tables = inspector.get_table_names()
            print("Tables:", tables)

            if 'user' in tables:
                count = conn.execute(text("SELECT count(*) FROM \"user\"")).scalar()
                print(f"Rows in 'user': {count}")
                # Check for the specific user
                uid = 'bdd2d5ed-4279-42f2-b236-724cbd8a93b3'
                count_user = conn.execute(text(f"SELECT count(*) FROM \"user\" WHERE id = '{uid}'")).scalar()
                print(f"User {uid} in 'user': {count_user}")

            if 'users' in tables:
                count = conn.execute(text("SELECT count(*) FROM users")).scalar()
                print(f"Rows in 'users': {count}")
                 # Check for the specific user
                uid = 'bdd2d5ed-4279-42f2-b236-724cbd8a93b3'
                count_user = conn.execute(text(f"SELECT count(*) FROM users WHERE id = '{uid}'")).scalar()
                print(f"User {uid} in 'users': {count_user}")
            
            # Check FKs on conversations
            if 'conversations' in tables:
                fks = inspector.get_foreign_keys('conversations')
                print("\nForeign Keys on 'conversations':")
                for fk in fks:
                    print(fk)

    if __name__ == "__main__":
        check_db()

except Exception as e:
    import traceback
    traceback.print_exc()
