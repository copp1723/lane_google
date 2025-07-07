-- Migration: Create Enhanced User Model
-- Description: Update user table with enterprise features and role-based access control
-- Version: 001
-- Created: 2024-07-05

-- Drop existing user table if it exists (be careful in production)
DROP TABLE IF EXISTS users CASCADE;

-- Create enhanced users table
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    
    -- Authentication
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(32) NOT NULL DEFAULT (lower(hex(randomblob(16)))),
    
    -- Profile information
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    company VARCHAR(200),
    department VARCHAR(100),
    
    -- Role and permissions
    role VARCHAR(20) DEFAULT 'viewer' CHECK (role IN ('admin', 'manager', 'analyst', 'viewer')),
    permissions TEXT, -- JSON string for SQLite
    
    -- Account status
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('active', 'inactive', 'suspended', 'pending')),
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    last_activity DATETIME,
    
    -- Security
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until DATETIME,
    password_changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Google Ads integration
    google_ads_customer_ids TEXT, -- JSON string for SQLite
    google_ads_refresh_token VARCHAR(500)
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Create trigger for updated_at
CREATE TRIGGER users_updated_at 
    AFTER UPDATE ON users
    BEGIN
        UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;