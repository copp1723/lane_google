#!/usr/bin/env python3
"""
Simple PostgreSQL migration runner for Lane Google
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Get database URL from environment
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/lane_google')

def run_migrations():
    """Run all SQL migrations in order"""
    
    # Connect to database
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        print(f"Connected to database: {DATABASE_URL}")
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        return False
    
    # Create migrations table if not exists
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                filename VARCHAR(255) UNIQUE NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("Migrations table ready")
    except Exception as e:
        print(f"Failed to create migrations table: {e}")
        return False
    
    # Get list of migration files
    migration_dir = os.path.join(os.path.dirname(__file__), 'migrations')
    migration_files = sorted([f for f in os.listdir(migration_dir) if f.endswith('.sql')])
    
    # Check which migrations have been applied
    cur.execute("SELECT filename FROM migrations")
    applied_migrations = {row[0] for row in cur.fetchall()}
    
    # Run pending migrations
    for migration_file in migration_files:
        if migration_file in applied_migrations:
            print(f"✓ {migration_file} (already applied)")
            continue
        
        file_path = os.path.join(migration_dir, migration_file)
        
        try:
            with open(file_path, 'r') as f:
                migration_sql = f.read()
            
            print(f"→ Applying {migration_file}...")
            cur.execute(migration_sql)
            
            # Record migration as applied
            cur.execute("INSERT INTO migrations (filename) VALUES (%s)", (migration_file,))
            print(f"✓ {migration_file} applied successfully")
            
        except Exception as e:
            print(f"✗ Failed to apply {migration_file}: {e}")
            # Continue with next migration
    
    # Close connection
    cur.close()
    conn.close()
    
    print("\nMigration complete!")
    return True

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success = run_migrations()
    sys.exit(0 if success else 1)