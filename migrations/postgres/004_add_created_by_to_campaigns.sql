-- Migration: Add created_by foreign key to campaigns table (PostgreSQL)
-- Description: Add created_by field to link campaigns to the users who created them
-- Version: 004
-- Created: 2025-07-07

-- Add created_by column to campaigns table
ALTER TABLE campaigns 
    ADD COLUMN IF NOT EXISTS created_by UUID;

-- Add foreign key constraint
ALTER TABLE campaigns
    ADD CONSTRAINT fk_campaigns_created_by 
        FOREIGN KEY (created_by) 
        REFERENCES users(id) 
        ON DELETE SET NULL;

-- Create index for better query performance
CREATE INDEX IF NOT EXISTS idx_campaigns_created_by ON campaigns(created_by);

-- Add comment for documentation
COMMENT ON COLUMN campaigns.created_by IS 'Foreign key to users.id - tracks which user created the campaign';
