#!/usr/bin/env python3
"""
Database Migration Runner
Executes SQL migration files in order
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path
from typing import List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.config.settings import settings

logger = logging.getLogger(__name__)

class MigrationRunner:
    """Handles database migrations"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.migrations_dir = Path(__file__).parent
        
        # Parse database URL for SQLite
        if database_url.startswith('sqlite:///'):
            self.db_path = database_url.replace('sqlite:///', '')
        else:
            raise ValueError("Currently only SQLite migrations are supported")
    
    def get_migration_files(self) -> List[Path]:
        """Get all migration files in order"""
        migration_files = []
        for file in self.migrations_dir.glob('*.sql'):
            if file.name.startswith(('001_', '002_', '003_', '004_')):
                migration_files.append(file)
        
        # Sort by filename to ensure order
        migration_files.sort(key=lambda x: x.name)
        return migration_files
    
    def create_migrations_table(self, conn: sqlite3.Connection):
        """Create migrations tracking table"""
        conn.execute('''
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(10) PRIMARY KEY,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                filename VARCHAR(200) NOT NULL
            )
        ''')
        conn.commit()
    
    def is_migration_applied(self, conn: sqlite3.Connection, version: str) -> bool:
        """Check if migration is already applied"""
        cursor = conn.execute(
            'SELECT COUNT(*) FROM schema_migrations WHERE version = ?',
            (version,)
        )
        return cursor.fetchone()[0] > 0
    
    def apply_migration(self, conn: sqlite3.Connection, migration_file: Path):
        """Apply a single migration file"""
        version = migration_file.name[:3]  # Extract version (001, 002, etc.)
        
        if self.is_migration_applied(conn, version):
            logger.info(f"Migration {version} already applied, skipping")
            return
        
        logger.info(f"Applying migration {version}: {migration_file.name}")
        
        try:
            # Read and execute migration SQL
            with open(migration_file, 'r') as f:
                sql_content = f.read()
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement:
                    conn.execute(statement)
            
            # Record migration as applied
            conn.execute(
                'INSERT INTO schema_migrations (version, filename) VALUES (?, ?)',
                (version, migration_file.name)
            )
            
            conn.commit()
            logger.info(f"Migration {version} applied successfully")
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Error applying migration {version}: {str(e)}")
            raise
    
    def run_migrations(self):
        """Run all pending migrations"""
        logger.info(f"Running migrations on database: {self.db_path}")
        
        # Ensure database directory exists
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        conn.execute('PRAGMA foreign_keys = ON')  # Enable foreign key constraints
        
        try:
            # Create migrations table
            self.create_migrations_table(conn)
            
            # Get migration files
            migration_files = self.get_migration_files()
            
            if not migration_files:
                logger.info("No migration files found")
                return
            
            logger.info(f"Found {len(migration_files)} migration files")
            
            # Apply each migration
            for migration_file in migration_files:
                self.apply_migration(conn, migration_file)
            
            logger.info("All migrations completed successfully")
            
        except Exception as e:
            logger.error(f"Migration failed: {str(e)}")
            raise
        finally:
            conn.close()
    
    def rollback_migration(self, version: str):
        """Rollback a specific migration (basic implementation)"""
        logger.warning(f"Rollback not implemented for version {version}")
        logger.warning("For SQLite, consider restoring from backup")
    
    def migration_status(self):
        """Show migration status"""
        conn = sqlite3.connect(self.db_path)
        
        try:
            # Create migrations table if it doesn't exist
            self.create_migrations_table(conn)
            
            # Get applied migrations
            cursor = conn.execute(
                'SELECT version, filename, applied_at FROM schema_migrations ORDER BY version'
            )
            applied_migrations = cursor.fetchall()
            
            # Get available migrations
            migration_files = self.get_migration_files()
            
            print("\nMigration Status:")
            print("=" * 50)
            
            for migration_file in migration_files:
                version = migration_file.name[:3]
                applied = any(m[0] == version for m in applied_migrations)
                status = "✓ Applied" if applied else "✗ Pending"
                print(f"{version}: {migration_file.name} - {status}")
            
            if applied_migrations:
                print(f"\nLast applied migration: {applied_migrations[-1][0]}")
            else:
                print("\nNo migrations have been applied yet")
                
        finally:
            conn.close()


def main():
    """Main migration runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Database Migration Runner')
    parser.add_argument('command', choices=['migrate', 'status', 'rollback'], 
                       help='Migration command to run')
    parser.add_argument('--version', help='Version for rollback command')
    parser.add_argument('--database-url', help='Database URL (overrides config)')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Get database URL
    database_url = args.database_url or settings.database.url
    
    # Create migration runner
    runner = MigrationRunner(database_url)
    
    try:
        if args.command == 'migrate':
            runner.run_migrations()
        elif args.command == 'status':
            runner.migration_status()
        elif args.command == 'rollback':
            if not args.version:
                logger.error("Rollback requires --version argument")
                sys.exit(1)
            runner.rollback_migration(args.version)
            
    except Exception as e:
        logger.error(f"Migration command failed: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()