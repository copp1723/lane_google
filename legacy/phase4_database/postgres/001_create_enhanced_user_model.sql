-- Migration: Create Enhanced User Model for PostgreSQL
-- Description: Create user table with enterprise features and role-based access control
-- Version: 001
-- Created: 2024-07-05

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Drop existing user table if it exists (be careful in production)
DROP TABLE IF EXISTS users CASCADE;

-- Create custom types
CREATE TYPE user_role AS ENUM ('admin', 'manager', 'analyst', 'viewer');
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'pending');

-- Create enhanced users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    
    -- Authentication
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(32) NOT NULL DEFAULT substring(md5(random()::text) from 1 for 32),
    
    -- Profile information
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    company VARCHAR(200),
    department VARCHAR(100),
    
    -- Role and permissions
    role user_role DEFAULT 'viewer',
    permissions JSONB,
    
    -- Account status
    status user_status DEFAULT 'pending',
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    last_activity TIMESTAMP WITH TIME ZONE,
    
    -- Security
    failed_login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    password_changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Google Ads integration
    google_ads_customer_ids JSONB,
    google_ads_refresh_token VARCHAR(500)
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_google_ads_customer_ids ON users USING GIN(google_ads_customer_ids);

-- Create function for updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE users IS 'User accounts with enterprise features and role-based access control';
COMMENT ON COLUMN users.role IS 'User role for permission management';
COMMENT ON COLUMN users.permissions IS 'Additional granular permissions as JSON';
COMMENT ON COLUMN users.google_ads_customer_ids IS 'List of accessible Google Ads customer IDs';
COMMENT ON COLUMN users.google_ads_refresh_token IS 'Encrypted Google Ads refresh token';