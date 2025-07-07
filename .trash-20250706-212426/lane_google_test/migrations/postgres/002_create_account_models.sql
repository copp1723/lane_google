-- Migration: Create Account Management Models for PostgreSQL
-- Description: Add multi-tenant account management with role-based permissions
-- Version: 002
-- Created: 2024-07-05

-- Create custom types
CREATE TYPE account_status AS ENUM ('active', 'inactive', 'suspended');
CREATE TYPE account_user_role AS ENUM ('owner', 'admin', 'manager', 'analyst', 'viewer');
CREATE TYPE account_user_status AS ENUM ('active', 'inactive', 'pending');

-- Create accounts table
CREATE TABLE accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    
    -- Company information
    company_name VARCHAR(200),
    website VARCHAR(200),
    industry VARCHAR(100),
    
    -- Settings
    settings JSONB DEFAULT '{}',
    
    -- Status
    status account_status DEFAULT 'active',
    is_trial BOOLEAN DEFAULT TRUE,
    trial_ends_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Google Ads integration
    google_ads_customer_id VARCHAR(20),
    google_ads_settings JSONB DEFAULT '{}'
);

-- Create account_users junction table for many-to-many relationship
CREATE TABLE account_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role account_user_role DEFAULT 'viewer',
    permissions JSONB,
    
    -- Status
    status account_user_status DEFAULT 'active',
    invited_by UUID,
    invited_at TIMESTAMP WITH TIME ZONE,
    joined_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_account_users_account
        FOREIGN KEY (account_id) 
        REFERENCES accounts(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_account_users_user
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE,
    
    CONSTRAINT fk_account_users_invited_by
        FOREIGN KEY (invited_by) 
        REFERENCES users(id) 
        ON DELETE SET NULL,
    
    CONSTRAINT unique_account_user
        UNIQUE(account_id, user_id)
);

-- Create indexes
CREATE INDEX idx_accounts_slug ON accounts(slug);
CREATE INDEX idx_accounts_status ON accounts(status);
CREATE INDEX idx_accounts_google_ads_customer_id ON accounts(google_ads_customer_id);
CREATE INDEX idx_accounts_settings ON accounts USING GIN(settings);

CREATE INDEX idx_account_users_account_id ON account_users(account_id);
CREATE INDEX idx_account_users_user_id ON account_users(user_id);
CREATE INDEX idx_account_users_role ON account_users(role);
CREATE INDEX idx_account_users_status ON account_users(status);

-- Create triggers for updated_at
CREATE TRIGGER update_accounts_updated_at BEFORE UPDATE ON accounts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_account_users_updated_at BEFORE UPDATE ON account_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add comments
COMMENT ON TABLE accounts IS 'Multi-tenant account management';
COMMENT ON TABLE account_users IS 'Many-to-many relationship between accounts and users';
COMMENT ON COLUMN accounts.settings IS 'Account-specific settings and preferences';
COMMENT ON COLUMN account_users.permissions IS 'Additional permissions beyond role-based access';