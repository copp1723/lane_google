-- Migration: Enhance Campaign Model
-- Description: Add new fields for enhanced campaign management and analytics
-- Version: 003
-- Created: 2024-07-05

-- Add new columns to existing campaigns table
ALTER TABLE campaigns ADD COLUMN account_id VARCHAR(36);
ALTER TABLE campaigns ADD COLUMN google_ads_campaign_id VARCHAR(20);
ALTER TABLE campaigns ADD COLUMN budget_amount DECIMAL(10,2);
ALTER TABLE campaigns ADD COLUMN daily_budget DECIMAL(10,2);
ALTER TABLE campaigns ADD COLUMN budget_delivery_method VARCHAR(20) DEFAULT 'standard';
ALTER TABLE campaigns ADD COLUMN bidding_strategy VARCHAR(50);
ALTER TABLE campaigns ADD COLUMN target_cpa DECIMAL(10,2);
ALTER TABLE campaigns ADD COLUMN target_roas DECIMAL(5,2);
ALTER TABLE campaigns ADD COLUMN start_date DATE;
ALTER TABLE campaigns ADD COLUMN end_date DATE;
ALTER TABLE campaigns ADD COLUMN tracking_template VARCHAR(500);
ALTER TABLE campaigns ADD COLUMN final_url_suffix VARCHAR(200);
ALTER TABLE campaigns ADD COLUMN geo_targeting TEXT; -- JSON string
ALTER TABLE campaigns ADD COLUMN language_targeting TEXT; -- JSON string
ALTER TABLE campaigns ADD COLUMN device_targeting TEXT; -- JSON string
ALTER TABLE campaigns ADD COLUMN schedule_targeting TEXT; -- JSON string
ALTER TABLE campaigns ADD COLUMN negative_keywords TEXT; -- JSON string
ALTER TABLE campaigns ADD COLUMN conversion_tracking TEXT; -- JSON string
ALTER TABLE campaigns ADD COLUMN labels TEXT; -- JSON string
ALTER TABLE campaigns ADD COLUMN notes TEXT;
ALTER TABLE campaigns ADD COLUMN approval_status VARCHAR(20) DEFAULT 'pending';
ALTER TABLE campaigns ADD COLUMN approval_notes TEXT;
ALTER TABLE campaigns ADD COLUMN approved_by VARCHAR(36);
ALTER TABLE campaigns ADD COLUMN approved_at DATETIME;
ALTER TABLE campaigns ADD COLUMN last_sync_at DATETIME;
ALTER TABLE campaigns ADD COLUMN sync_errors TEXT;

-- Update existing status values if needed
UPDATE campaigns SET status = 'draft' WHERE status IS NULL;

-- Add foreign key constraints
CREATE INDEX idx_campaigns_account_id ON campaigns(account_id);
CREATE INDEX idx_campaigns_google_ads_campaign_id ON campaigns(google_ads_campaign_id);
CREATE INDEX idx_campaigns_approval_status ON campaigns(approval_status);
CREATE INDEX idx_campaigns_approved_by ON campaigns(approved_by);
CREATE INDEX idx_campaigns_start_date ON campaigns(start_date);
CREATE INDEX idx_campaigns_end_date ON campaigns(end_date);

-- Note: In SQLite, we can't add foreign key constraints to existing tables
-- In PostgreSQL, you would add: FOREIGN KEY (account_id) REFERENCES accounts(id)
-- For now, we'll enforce this at the application level