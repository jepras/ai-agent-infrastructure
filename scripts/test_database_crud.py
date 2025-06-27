# Requires: pip install python-dotenv psycopg2-binary
import os
from dotenv import load_dotenv
import psycopg2
import uuid

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)


def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise Exception("DATABASE_URL environment variable not set")
    return psycopg2.connect(db_url)


def main():
    test_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    test_name = "Test User"
    test_updated_name = "Updated User"
    print(f"\n--- CRUD Test for users table ---\nTest email: {test_email}")
    try:
        conn = get_db_connection()
        conn.autocommit = True
        with conn.cursor() as cur:
            # Insert
            cur.execute(
                """
                INSERT INTO users (email, name) VALUES (%s, %s) RETURNING id;
            """,
                (test_email, test_name),
            )
            user_id = cur.fetchone()[0]
            print(f"✅ Inserted user with id: {user_id}")

            # Read
            cur.execute("SELECT email, name FROM users WHERE id = %s;", (user_id,))
            row = cur.fetchone()
            if row and row[0] == test_email and row[1] == test_name:
                print("✅ Read user: data matches")
            else:
                print("❌ Read user: data does not match")

            # Update
            cur.execute(
                "UPDATE users SET name = %s WHERE id = %s;",
                (test_updated_name, user_id),
            )
            cur.execute("SELECT name FROM users WHERE id = %s;", (user_id,))
            updated_name = cur.fetchone()[0]
            if updated_name == test_updated_name:
                print("✅ Update user: name updated")
            else:
                print("❌ Update user: name not updated")

            # Delete
            cur.execute("DELETE FROM users WHERE id = %s;", (user_id,))
            cur.execute("SELECT id FROM users WHERE id = %s;", (user_id,))
            if cur.fetchone() is None:
                print("✅ Delete user: user removed")
            else:
                print("❌ Delete user: user still exists")
        conn.close()
    except Exception as e:
        print(f"❌ CRUD test failed: {e}")


if __name__ == "__main__":
    main()
