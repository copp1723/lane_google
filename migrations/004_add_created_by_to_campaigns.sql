-- Migration: Add created_by foreign key to campaigns table
-- Description: Add created_by field to link campaigns to the users who created them
-- Version: 004
-- Created: 2025-07-07

-- Add created_by column to campaigns table
ALTER TABLE campaigns ADD COLUMN created_by VARCHAR(36);

-- Create index for better query performance
CREATE INDEX idx_campaigns_created_by ON campaigns(created_by);

-- Note: In SQLite, we can't add foreign key constraints to existing tables
-- In PostgreSQL, you would add: 
-- ALTER TABLE campaigns ADD CONSTRAINT fk_campaigns_created_by 
--     FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;

-- For SQLite, the foreign key constraint is enforced at the application level
-- through the SQLAlchemy model definition
