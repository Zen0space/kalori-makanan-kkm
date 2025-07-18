#!/usr/bin/env python3
"""
Setup script for rate limiting tables in Turso database.

This script creates the necessary tables and indexes for the rate limiting system.
Run this once to set up your database for API key authentication and rate limiting.
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import get_database
from app.auth import create_test_user_and_key

# Load environment variables
load_dotenv()

def create_tables():
    """Create all necessary tables for rate limiting"""

    conn = get_database()
    cursor = conn.cursor()

    try:
        # Create users table
        print("Creating users table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Users table created")

        # Create index on email
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)
        """)
        print("✅ Users email index created")

        # Create api_keys table
        print("\nCreating api_keys table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                key_hash TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used_at DATETIME,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        print("✅ API keys table created")

        # Create index on key_hash
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash)
        """)
        print("✅ API keys index created")

        # Create rate_limit_logs table
        print("\nCreating rate_limit_logs table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                endpoint TEXT,
                FOREIGN KEY (api_key_id) REFERENCES api_keys(id) ON DELETE CASCADE
            )
        """)
        print("✅ Rate limit logs table created")

        # Create composite index for efficient queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_rate_limit_logs_api_key_timestamp
            ON rate_limit_logs(api_key_id, timestamp)
        """)
        print("✅ Rate limit logs index created")

        # Commit all changes
        conn.commit()
        print("\n✅ All tables created successfully!")

    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error creating tables: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def check_existing_tables():
    """Check which tables already exist"""
    conn = get_database()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN ('users', 'api_keys', 'rate_limit_logs')
            ORDER BY name
        """)

        existing_tables = [row[0] for row in cursor.fetchall()]

        if existing_tables:
            print(f"\n📋 Existing tables found: {', '.join(existing_tables)}")
        else:
            print("\n📋 No rate limiting tables found. Creating fresh setup...")

        return existing_tables

    finally:
        cursor.close()
        conn.close()

def verify_setup():
    """Verify the setup by checking table schemas"""
    conn = get_database()
    cursor = conn.cursor()

    try:
        tables = ['users', 'api_keys', 'rate_limit_logs']

        print("\n🔍 Verifying table schemas:")
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()

            if columns:
                print(f"\n✅ {table} table:")
                for col in columns:
                    col_info = f"  - {col[1]} ({col[2]})"
                    if col[3]:  # NOT NULL
                        col_info += " NOT NULL"
                    if col[5]:  # PRIMARY KEY
                        col_info += " PRIMARY KEY"
                    print(col_info)
            else:
                print(f"\n❌ {table} table not found!")

    finally:
        cursor.close()
        conn.close()

def main():
    """Main setup function"""
    print("🚀 Kalori Makanan API - Rate Limiting Setup")
    print("=" * 50)

    # Check database connection
    print("\n1️⃣ Checking database connection...")
    try:
        conn = get_database()
        conn.close()
        print("✅ Database connection successful")
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\nPlease check your .env file and ensure you have:")
        print("  TURSO_DATABASE_URL=your_database_url")
        print("  TURSO_DATABASE_TOKEN=your_database_token")
        return

    # Check existing tables
    print("\n2️⃣ Checking existing tables...")
    existing_tables = check_existing_tables()

    # Create tables
    print("\n3️⃣ Creating rate limiting tables...")
    try:
        create_tables()
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        return

    # Verify setup
    print("\n4️⃣ Verifying setup...")
    verify_setup()

    # Ask if user wants to create test user
    print("\n5️⃣ Would you like to create a test user and API key? (y/n)")
    choice = input("> ").lower().strip()

    if choice == 'y':
        print("\nCreating test user...")
        try:
            result = create_test_user_and_key()
            print(f"\n✅ Test user created successfully!")
            print(f"📧 Email: test@example.com")
            print(f"🔑 API Key: {result['api_key']}")
            print(f"\n⚠️  {result['message']}")

            # Save to file for convenience
            with open('.test_api_key', 'w') as f:
                f.write(result['api_key'])
            print("\n💾 API key saved to .test_api_key file")

        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                print("\n⚠️  Test user already exists. Use the existing API key.")
            else:
                print(f"\n❌ Error creating test user: {str(e)}")

    print("\n✅ Setup completed successfully!")
    print("\n📚 Next steps:")
    print("1. Start your API: uvicorn app.main:app --reload")
    print("2. Use the API key in your requests: -H 'X-API-Key: your_key'")
    print("3. Check the documentation at: http://localhost:8000/docs")
    print("4. Read RATE_LIMITING.md for detailed information")

if __name__ == "__main__":
    main()
