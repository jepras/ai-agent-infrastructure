# Requires: pip install python-dotenv psycopg2-binary
import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables from .env file
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path=env_path)

EXPECTED_TABLES = [
    "accounts",
    "alembic_version",
    "deals_created",
    "email_analysis_logs",
    "sessions",
    "usage_limits",
    "usage_tracking",
    "user_credentials",
    "user_profiles",
    "users",
    "webhook_subscriptions",
]


def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise Exception("DATABASE_URL environment variable not set")
    return psycopg2.connect(db_url)


def check_tables(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public';
        """
        )
        tables = set(row[0] for row in cur.fetchall())
        print(f"Tables found: {tables}")
        missing = [t for t in EXPECTED_TABLES if t not in tables]
        if missing:
            print(f"❌ Missing tables: {missing}")
        else:
            print("✅ All expected tables exist.")


def main():
    try:
        conn = get_db_connection()
        print("✅ Connected to database!")
        check_tables(conn)
        conn.close()
    except Exception as e:
        print(f"❌ Database connection or check failed: {e}")


if __name__ == "__main__":
    main()
