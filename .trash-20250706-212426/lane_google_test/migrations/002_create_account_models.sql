-- Migration: Create Account Management Models
-- Description: Add multi-tenant account management with role-based permissions
-- Version: 002
-- Created: 2024-07-05

-- Create accounts table
CREATE TABLE accounts (
    id VARCHAR(36) PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    
    -- Company information
    company_name VARCHAR(200),
    website VARCHAR(200),
    industry VARCHAR(100),
    
    -- Settings
    settings TEXT, -- JSON string for SQLite
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended')),
    is_trial BOOLEAN DEFAULT TRUE,
    trial_ends_at DATETIME,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    -- Google Ads integration
    google_ads_customer_id VARCHAR(20),
    google_ads_settings TEXT -- JSON string for SQLite
);

-- Create account_users junction table for many-to-many relationship
CREATE TABLE account_users (
    id VARCHAR(36) PRIMARY KEY DEFAULT (lower(hex(randomblob(4))) || '-' || lower(hex(randomblob(2))) || '-4' || substr(lower(hex(randomblob(2))),2) || '-' || substr('89ab',abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || '-' || lower(hex(randomblob(6)))),
    account_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    role VARCHAR(20) DEFAULT 'viewer' CHECK (role IN ('owner', 'admin', 'manager', 'analyst', 'viewer')),
    permissions TEXT, -- JSON string for additional permissions
    
    -- Status
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'pending')),
    invited_by VARCHAR(36),
    invited_at DATETIME,
    joined_at DATETIME,
    
    -- Timestamps
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (invited_by) REFERENCES users(id) ON DELETE SET NULL,
    
    UNIQUE(account_id, user_id)
);

-- Create indexes
CREATE INDEX idx_accounts_slug ON accounts(slug);
CREATE INDEX idx_accounts_status ON accounts(status);
CREATE INDEX idx_accounts_google_ads_customer_id ON accounts(google_ads_customer_id);

CREATE INDEX idx_account_users_account_id ON account_users(account_id);
CREATE INDEX idx_account_users_user_id ON account_users(user_id);
CREATE INDEX idx_account_users_role ON account_users(role);
CREATE INDEX idx_account_users_status ON account_users(status);

-- Create triggers for updated_at
CREATE TRIGGER accounts_updated_at 
    AFTER UPDATE ON accounts
    BEGIN
        UPDATE accounts SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;

CREATE TRIGGER account_users_updated_at 
    AFTER UPDATE ON account_users
    BEGIN
        UPDATE account_users SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END;