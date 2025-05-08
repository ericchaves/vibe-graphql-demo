import sqlite3
import os

DATABASE_FILE = 'database.db'
SCHEMA_FILE = 'schema.sql'

def init_db():
    """Initializes the SQLite database from the schema.sql file."""
    if os.path.exists(DATABASE_FILE):
        print(f"Database file '{DATABASE_FILE}' already exists. Skipping initialization.")
        return

    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        with open(SCHEMA_FILE, 'r') as f:
            schema_sql = f.read()

        cursor.executescript(schema_sql)
        conn.commit()
        print(f"Database '{DATABASE_FILE}' initialized successfully from '{SCHEMA_FILE}'.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
    except FileNotFoundError:
        print(f"Error: Schema file '{SCHEMA_FILE}' not found.")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_db()
