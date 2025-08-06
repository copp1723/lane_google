#!/usr/bin/env python3
"""
Create Admin User Script
Run this locally to create your first admin user
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from werkzeug.security import generate_password_hash
import sqlite3
import psycopg2
from datetime import datetime

def create_admin_sqlite():
    """Create admin user in SQLite database"""
    db_path = 'instance/lane_mcp.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at {db_path}")
        print("Creating new database...")
        os.makedirs('instance', exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Admin credentials
    email = 'admin@lane-ai.com'
    password = 'LaneAI2025!'  # Change this!
    password_hash = generate_password_hash(password)
    
    # Check if admin exists
    cursor.execute('SELECT email FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        print(f"⚠️  Admin user {email} already exists")
        print("Updating password...")
        cursor.execute('''
            UPDATE users 
            SET password_hash = ?, updated_at = ?
            WHERE email = ?
        ''', (password_hash, datetime.now(), email))
    else:
        # Insert admin user
        cursor.execute('''
            INSERT INTO users (email, password_hash, first_name, last_name, role, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (email, password_hash, 'Admin', 'User', 'admin', datetime.now(), True))
        print(f"✅ Created admin user: {email}")
    
    conn.commit()
    conn.close()
    
    return email, password

def create_admin_postgres():
    """Create admin user in PostgreSQL database"""
    # Try to get database URL from environment
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        print("❌ No PostgreSQL DATABASE_URL found")
        return None, None
    
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                role VARCHAR(50) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        ''')
        
        # Admin credentials
        email = 'admin@lane-ai.com'
        password = 'LaneAI2025!'
        password_hash = generate_password_hash(password)
        
        # Check if admin exists
        cursor.execute('SELECT email FROM users WHERE email = %s', (email,))
        if cursor.fetchone():
            print(f"⚠️  Admin user {email} already exists")
            print("Updating password...")
            cursor.execute('''
                UPDATE users 
                SET password_hash = %s, updated_at = %s
                WHERE email = %s
            ''', (password_hash, datetime.now(), email))
        else:
            # Insert admin user
            cursor.execute('''
                INSERT INTO users (email, password_hash, first_name, last_name, role, created_at, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (email, password_hash, 'Admin', 'User', 'admin', datetime.now(), True))
            print(f"✅ Created admin user: {email}")
        
        conn.commit()
        conn.close()
        
        return email, password
    except Exception as e:
        print(f"❌ PostgreSQL error: {e}")
        return None, None

def main():
    print("🔐 Creating Admin User for Lane AI")
    print("===================================\n")
    
    # Try SQLite first (for local development)
    print("Attempting SQLite (local)...")
    email, password = create_admin_sqlite()
    
    if email and password:
        print("\n✅ SUCCESS - Admin User Created!")
        print("================================")
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print("\n⚠️  IMPORTANT: Change this password after first login!")
        print("\n🚀 You can now login at:")
        print("   Local: http://localhost:5173/login")
        print("   Production: https://lane-google.onrender.com/login")
    else:
        # Try PostgreSQL (for production)
        print("\nAttempting PostgreSQL (production)...")
        email, password = create_admin_postgres()
        
        if email and password:
            print("\n✅ SUCCESS - Admin User Created!")
            print("================================")
            print(f"📧 Email: {email}")
            print(f"🔑 Password: {password}")
            print("\n⚠️  IMPORTANT: Change this password after first login!")
        else:
            print("\n❌ Could not create admin user")
            print("Please check your database configuration")

if __name__ == '__main__':
    main()